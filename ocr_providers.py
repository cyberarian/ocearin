import streamlit as st
import json
import io
import os
import sys
import base64  # Add this import
import zipfile  # Add this import
from mistralai import Mistral
import google.generativeai as genai
import pytesseract
import fitz
import PyPDF2
import groq
from PIL import Image
from utils import prepare_file_for_mistral, render_pdf_pages, process_ocr_response
from ocr_evaluation import evaluate_ocr_quality

@st.cache_resource
def get_vlm_client(provider):
    """Initialize OCR provider client"""
    try:
        # Debug: Print available secrets
        st.write("Available API keys:", list(st.secrets.keys()))
        
        if provider == "Mistral":
            api_key = st.secrets.get("MISTRAL_API_KEY")
            if not api_key:
                st.error("Mistral API key not found")
                return None
            return Mistral(api_key=api_key)
            
        elif provider == "Google":
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                st.error("Google API key not found")
                return None
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
            
        elif provider == "Tesseract":
            if sys.platform.startswith('win'):
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            return pytesseract
            
        elif provider == "PyMuPDF":
            return fitz
            
        elif provider == "PyPDF2":
            return PyPDF2
            
        elif provider == "Groq":
            api_key = st.secrets.get("GROQ_API_KEY")
            if not api_key:
                st.error("Groq API key not found")
                return None
            return groq.Groq(api_key=api_key)
            
    except Exception as e:
        st.error(f"Error initializing {provider}: {str(e)}")
        st.write("Full error:", str(e))  # Debug info
        return None

def process_mistral(client, file_bytes, file_name, model):
    try:
        prepared_bytes, prepared_name = prepare_file_for_mistral(file_bytes, file_name)
        
        with st.spinner("Uploading file to Mistral..."):
            uploaded_file = client.files.upload(
                file={"file_name": prepared_name, "content": prepared_bytes},
                purpose="ocr"
            )
            
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        ocr_response = client.ocr.process( # Assuming client.ocr.process is a valid method in your mistralai lib version
            model=model,
            document={
                "type": "document_url",
                "document_url": signed_url.url,
                "include_image_base64": True,
                "layout_info": True,
                "tables": True
            }
        )
        
        response_dict = ocr_response.model_dump() if hasattr(ocr_response, 'model_dump') else json.loads(str(ocr_response))
        return process_ocr_response(response_dict, os.path.splitext(file_name)[0])
    except Exception as e:
        st.error(f"Mistral processing error: {str(e)}")
        return None

def process_google(client, file_bytes, file_name, model):
    try:
        prompt = "Extract all text and describe any images from this document in markdown format. For each image, provide a detailed description and include its position in the document."
        
        if file_name.lower().endswith('.pdf'):
            images = render_pdf_pages(file_bytes, end_page=5)
            all_text = []
            extracted_images = []
            
            for i, image in enumerate(images):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                
                # Save image with a unique name
                img_name = f"image_{i+1}.png"
                extracted_images.append((img_name, img_bytes.getvalue()))
                
                response = client.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_bytes.getvalue()}
                ])
                all_text.append(response.text)
                
                if i == 4:
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
            
            combined_text = "\n\n".join(all_text)
            
            # Create downloadable markdown file
            markdown_content = f"# {os.path.splitext(file_name)[0]}\n\n{combined_text}"
            
            # Save markdown and images to zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                zip_file.writestr('content.md', markdown_content)
                for img_name, img_data in extracted_images:
                    zip_file.writestr(f"images/{img_name}", img_data)
            
            # Add download button
            st.download_button(
                label="Download Markdown with Images",
                data=zip_buffer.getvalue(),
                file_name=f"{os.path.splitext(file_name)[0]}_ocr.zip",
                mime="application/zip"
            )
            
            return combined_text
        else:
            img_bytes = io.BytesIO(file_bytes)
            response = client.generate_content([prompt, {"mime_type": "image/png", "data": file_bytes}])
            
            # Create markdown content for single image
            markdown_content = f"# {os.path.splitext(file_name)[0]}\n\n{response.text}"
            
            # Add download button for single file
            st.download_button(
                label="Download Markdown",
                data=markdown_content,
                file_name=f"{os.path.splitext(file_name)[0]}_ocr.md",
                mime="text/markdown"
            )
            
            return response.text
    except Exception as e:
        st.error(f"Google processing error: {str(e)}")
        return None

def process_tesseract(client, file_bytes, file_name):
    try:
        if file_name.lower().endswith('.pdf'):
            images = render_pdf_pages(file_bytes, end_page=5)
            all_text = []
            
            for i, image in enumerate(images):
                text = client.image_to_string(image, lang='eng')
                all_text.append(text)
                
                if i == 4:
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
                    
            return "\n\n".join(all_text)
        else:
            image = Image.open(io.BytesIO(file_bytes))
            return client.image_to_string(image, lang='eng')
    except Exception as e:
        st.error(f"Tesseract processing error: {str(e)}")
        return None

def process_pymupdf(client, file_bytes, file_name):
    try:
        if file_name.lower().endswith('.pdf'):
            doc = client.open(stream=file_bytes, filetype="pdf")
            all_text = []
            
            for i in range(min(len(doc), 5)):
                text = doc[i].get_text()
                all_text.append(text)
                
                if i == 4:
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
                    
            doc.close()
            return "\n\n".join(all_text)
        else:
            return "PyMuPDF only supports PDF files"
    except Exception as e:
        st.error(f"PyMuPDF processing error: {str(e)}")
        return None

def process_pypdf2(client, file_bytes, file_name):
    try:
        if file_name.lower().endswith('.pdf'):
            pdf_reader = client.PdfReader(io.BytesIO(file_bytes))
            all_text = []
            
            for i in range(min(len(pdf_reader.pages), 5)):
                text = pdf_reader.pages[i].extract_text()
                all_text.append(text)
                
                if i == 4:
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
                    
            return "\n\n".join(all_text)
        else:
            return "PyPDF2 only supports PDF files"
    except Exception as e:
        st.error(f"PyPDF2 processing error: {str(e)}")
        return None

def process_groq(client, file_bytes, file_name, model):
    """Process file with Groq OCR"""
    try:
        if file_name.lower().endswith('.pdf'):
            images = render_pdf_pages(file_bytes, end_page=5)
            all_text = []
            
            system_prompt = """You are an expert OCR system. Extract text from images while preserving:
            1. Document structure and formatting
            2. Headers and sections
            3. Tables and lists
            4. Special characters and symbols
            Output in markdown format."""
            
            for i, image in enumerate(images):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
                
                chat_completion = client.chat.completions.create(
                    model=model,  # Use the model parameter passed to the function
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract text from this image: data:image/png;base64,{img_base64}"}
                    ],
                    temperature=0.3,
                    max_tokens=4096
                )
                
                all_text.append(chat_completion.choices[0].message.content)
                
                if i == 4:  # Limit to 5 pages
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
                    
            return "\n\n".join(all_text)
            
        else:  # Single image
            img_bytes = io.BytesIO()
            Image.open(io.BytesIO(file_bytes)).save(img_bytes, format='PNG')
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
            
            chat_completion = client.chat.completions.create(
                model=model,  # Use the model parameter passed to the function
                messages=[
                    {"role": "system", "content": "Extract text from the image in markdown format."},
                    {"role": "user", "content": f"Extract text from this image: data:image/png;base64,{img_base64}"}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            
            return chat_completion.choices[0].message.content
            
    except Exception as e:
        st.error(f"Groq processing error: {str(e)}")
        return None

def process_file_ocr(file_bytes, file_name, provider):
    """Main OCR processing function"""
    if not file_bytes:
        st.error("Empty file provided")
        return None

    try:
        client = get_vlm_client(provider)
        if not client:
            return None

        result = None
        with st.spinner(f"Processing with {provider}..."):
            if provider == "Mistral":
                result = process_mistral(client, file_bytes, file_name, "mistral-ocr-latest")
            elif provider == "Google":
                result = process_google(client, file_bytes, file_name, "gemini-2.5-flash-preview-04-17")
            elif provider == "Tesseract":
                result = process_tesseract(client, file_bytes, file_name)
            elif provider == "PyMuPDF":
                result = process_pymupdf(client, file_bytes, file_name)
            elif provider == "PyPDF2":
                result = process_pypdf2(client, file_bytes, file_name)
            elif provider == "Groq":
                result = process_groq(client, file_bytes, file_name, "meta-llama/llama-4-maverick-17b-128e-instruct") # Changed to a valid Groq vision model

            if result:
                try:
                    quality_score, metrics = evaluate_ocr_quality(result, provider)
                    
                    st.session_state.ocr_results[provider] = {
                        "text": result,
                        "quality_score": float(quality_score),
                        "metrics": {k: float(v) if isinstance(v, (int, float)) else v 
                                  for k, v in metrics.items()}
                    }
                    
                    st.session_state.app_state["quality"] = {
                        "score": float(quality_score),
                        "metrics": metrics
                    }
                    st.session_state.app_state["result"] = result
                    
                except Exception as e:
                    st.warning(f"Could not calculate quality metrics: {str(e)}")
                    st.session_state.app_state["result"] = result

            return result

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.write(f"Detailed error: {e}")
        return None