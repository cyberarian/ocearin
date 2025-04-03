import streamlit as st
import json, io, os
from mistralai import Mistral
import google.generativeai as genai
import pytesseract
import fitz
import PyPDF2
from utils import prepare_file_for_mistral, render_pdf_pages, process_ocr_response
from ocr_evaluation import evaluate_ocr_quality
import sys
from PIL import Image  # Add this import

@st.cache_resource
def get_vlm_client(provider):
    try:
        if provider == "Mistral":
            return Mistral(api_key=st.secrets.get("MISTRAL_API_KEY"))
        elif provider == "Google":
            api_key = st.secrets.get("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        elif provider == "Tesseract":
            if sys.platform.startswith('win'):
                pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_PATH', 
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe')
            return pytesseract
        elif provider == "PyMuPDF":
            return fitz
        elif provider == "PyPDF2":
            return PyPDF2
        return None
    except Exception as e:
        st.error(f"Error initializing {provider}: {str(e)}")
        return None

def process_mistral(client, file_bytes, file_name, model):
    try:
        prepared_bytes, prepared_name = prepare_file_for_mistral(file_bytes, file_name)
        
        with st.spinner("Uploading file..."):
            uploaded_file = client.files.upload(
                file={"file_name": prepared_name, "content": prepared_bytes},
                purpose="ocr"
            )
            
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        ocr_response = client.ocr.process(
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
        prompt = "Extract all text from this image in markdown format. Preserve document structure and formatting."
        
        if file_name.lower().endswith('.pdf'):
            images = render_pdf_pages(file_bytes, end_page=5)
            all_text = []
            
            for i, image in enumerate(images):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                response = client.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_bytes.getvalue()}
                ])
                all_text.append(response.text)
                
                if i == 4:
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
                    
            return "\n\n".join(all_text)
        else:
            response = client.generate_content([prompt, {"mime_type": "image/png", "data": file_bytes}])
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
                result = process_google(client, file_bytes, file_name, "gemini-2.5-pro-exp-03-25")
            elif provider == "Tesseract":
                result = process_tesseract(client, file_bytes, file_name)
            elif provider == "PyMuPDF":
                result = process_pymupdf(client, file_bytes, file_name)
            elif provider == "PyPDF2":
                result = process_pypdf2(client, file_bytes, file_name)

            if result:
                # Add debug info
                st.write(f"Text extracted ({len(result)} characters)")
                
                try:
                    quality_score, metrics = evaluate_ocr_quality(result, provider)
                    
                    # Ensure metrics are numbers, not numpy types
                    metrics = {k: float(v) if isinstance(v, (int, float)) else v 
                             for k, v in metrics.items()}
                    
                    quality_data = {
                        "score": float(quality_score),
                        "metrics": metrics
                    }
                    
                    # Update both session states
                    st.session_state.ocr_results[provider] = {
                        "text": result,
                        "quality_score": quality_score,
                        "metrics": metrics
                    }
                    
                    # Update app state
                    st.session_state.app_state["quality"] = quality_data
                    st.session_state.app_state["result"] = result
                    
                except Exception as e:
                    st.warning(f"Could not calculate quality metrics: {str(e)}")
                    st.session_state.app_state["result"] = result

            return result

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.write(f"Detailed error: {e}")  # Add detailed error info
        return None