import streamlit as st
import json
import io
import logging
import os
import sys
import base64
import zipfile
from mistralai import Mistral
import requests
import google.generativeai as genai
import pytesseract
import fitz
import PyPDF2
from PIL import Image
from utils import prepare_file_for_mistral, render_pdf_pages, process_ocr_response
from ocr_evaluation import evaluate_ocr_quality
from constants import OCR_MODELS

logging.basicConfig(level=logging.INFO)

MAX_PDF_PAGES = 5

@st.cache_resource
def get_vlm_client(provider):
    """Initialize OCR provider client"""
    try:
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
            return genai.GenerativeModel('gemini-2.5-flash')
        elif provider == "Tesseract":
            if sys.platform.startswith('win'):
                # Use environment variable for Tesseract path, with a fallback
                pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
            return pytesseract
        elif provider == "PyMuPDF":
            return fitz
        elif provider == "PyPDF2":
            return PyPDF2
        elif provider == "NVIDIA":
            api_key = st.secrets.get("NVIDIA_API_KEY")
            if not api_key:
                st.error("NVIDIA API key not found")
                return None
            # For NVIDIA, the "client" is just the API key for the requests header
            return api_key
    except Exception as e:
        st.error(f"Error initializing {provider}: {str(e)}")
        logging.error(f"Error initializing {provider}: {e}", exc_info=True)
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

def _process_pdf_pages(file_bytes, processing_function):
    """Helper to iterate through PDF pages and apply a processing function."""
    images = render_pdf_pages(file_bytes, end_page=MAX_PDF_PAGES)
    if not images:
        return None

    all_text = []
    for i, image in enumerate(images):
        text = processing_function(image)
        if text:
            all_text.append(text)
        if i == MAX_PDF_PAGES - 1 and len(images) == MAX_PDF_PAGES:
            all_text.append(f"\n\n---\n\n*Note: Document truncated to first {MAX_PDF_PAGES} pages.*")
            break
    return "\n\n".join(all_text)

def process_google(client, file_bytes, file_name, model):
    prompt = "Extract all text and describe any images from this document in markdown format. For each image, provide a detailed description and include its position in the document."
    try:
        if file_name.lower().endswith('.pdf'):
            def process_page(image):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                response = client.generate_content([prompt, {"mime_type": "image/png", "data": img_bytes.getvalue()}])
                return response.text
            return _process_pdf_pages(file_bytes, process_page)
        else:
            response = client.generate_content([prompt, {"mime_type": "image/png", "data": file_bytes}])
            return response.text
    except Exception as e:
        st.error(f"Google processing error: {str(e)}")
        return None

def process_tesseract(client, file_bytes, file_name):
    try:
        if file_name.lower().endswith('.pdf'):
            return _process_pdf_pages(file_bytes, lambda img: client.image_to_string(img, lang='eng'))
        else:
            image = Image.open(io.BytesIO(file_bytes))
            return client.image_to_string(image, lang='eng')
    except Exception as e:
        st.error(f"Tesseract processing error: {str(e)}")
        return None

def process_pymupdf(client, file_bytes, file_name):
    if not file_name.lower().endswith('.pdf'):
        return "PyMuPDF only supports PDF files"
    try:
        doc = client.open(stream=file_bytes, filetype="pdf")
        all_text = []
        num_pages_to_process = min(len(doc), MAX_PDF_PAGES)
        for i in range(num_pages_to_process):
            text = doc[i].get_text()
            all_text.append(text)
        if len(doc) > MAX_PDF_PAGES:
            all_text.append(f"\n\n---\n\n*Note: Document truncated to first {MAX_PDF_PAGES} pages.*")
        doc.close()
        return "\n\n".join(all_text)
    except Exception as e:
        st.error(f"PyMuPDF processing error: {str(e)}")
        return None

def process_pypdf2(client, file_bytes, file_name):
    if not file_name.lower().endswith('.pdf'):
        return "PyPDF2 only supports PDF files"
    try:
        pdf_reader = client.PdfReader(io.BytesIO(file_bytes))
        all_text = []
        num_pages_to_process = min(len(pdf_reader.pages), MAX_PDF_PAGES)
        for i in range(num_pages_to_process):
            text = pdf_reader.pages[i].extract_text()
            all_text.append(text)
        if len(pdf_reader.pages) > MAX_PDF_PAGES:
            all_text.append(f"\n\n---\n\n*Note: Document truncated to first {MAX_PDF_PAGES} pages.*")
        return "\n\n".join(all_text)
    except Exception as e:
        st.error(f"PyPDF2 processing error: {str(e)}")
        return None

def process_nvidia(api_key, file_bytes, file_name, model):
    """Process file with NVIDIA OCR"""
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    tool_name = "markdown_no_bbox"

    def _extract_text_from_message(message):
        """
        Robustly extract text/markdown from a variety of NVIDIA response shapes.
        Returns a string if found, otherwise None.
        """
        if not message:
            return None
            
        # Handle tool_calls first since this is where NVIDIA commonly puts the text
        if isinstance(message, dict):
            tool_calls = message.get('tool_calls', [])
            if tool_calls and isinstance(tool_calls, list):
                for call in tool_calls:
                    if isinstance(call, dict):
                        func = call.get('function', {})
                        if isinstance(func, dict):
                            args = func.get('arguments', '')
                            if isinstance(args, str):
                                try:
                                    # Parse the arguments JSON string
                                    parsed = json.loads(args)
                                    # Handle both array and object responses
                                    if isinstance(parsed, list):
                                        texts = [item.get('text', '') for item in parsed if isinstance(item, dict)]
                                        return '\n\n'.join(text for text in texts if text)
                                    elif isinstance(parsed, dict):
                                        return parsed.get('text', '')
                                except json.JSONDecodeError:
                                    pass  # If not valid JSON, continue with other extraction methods

        # Rest of the extraction logic
        if isinstance(message, str):
            return message.strip() or None

        content = message.get('content') if isinstance(message, dict) else None
        if isinstance(content, str):
            return content.strip() or None
        if isinstance(content, list):
            parts_text = []
            for part in content:
                if isinstance(part, str):
                    parts_text.append(part.strip())
                elif isinstance(part, dict):
                    for key in ('markdown_text', 'text', 'content', 'body', 'markdown', 'output_text'):
                        v = part.get(key)
                        if isinstance(v, str) and v.strip():
                            parts_text.append(v.strip())
                            break
            if parts_text:
                return "\n\n".join(parts_text)

        # Other possible keys: 'parts', 'outputs', 'segments'
        for list_key in ('parts', 'outputs', 'segments'):
            parts = message.get(list_key)
            if isinstance(parts, list):
                parts_text = []
                for p in parts:
                    if isinstance(p, str):
                        parts_text.append(p.strip())
                    elif isinstance(p, dict):
                        for key in ('markdown_text', 'text', 'content', 'body', 'output_text'):
                            v = p.get(key)
                            if isinstance(v, str) and v.strip():
                                parts_text.append(v.strip())
                                break
                if parts_text:
                    return "\n\n".join(parts_text)

        # As a last resort, try top-level keys on the choice itself
        for key in ('text', 'message', 'response', 'output'):
            v = message.get(key) if isinstance(message, dict) else None
            if isinstance(v, str) and v.strip():
                return v.strip()

        # Fallback: try to stringify the message (useful for debugging)
        try:
            return json.dumps(message)
        except Exception:
            return None

    def process_image_bytes(image_bytes):
        b64_str = base64.b64encode(image_bytes).decode("ascii")
        media_tag = f'<img src="data:image/png;base64,{b64_str}" />'
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": media_tag}],
            "tools": [{"type": "function", "function": {"name": tool_name}}],
            "tool_choice": {"type": "function", "function": {"name": tool_name}},
            "max_tokens": 4096,
            "temperature": 0.2,
        }

        try:
            response = requests.post(invoke_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            response_body = response.json()
            
            choices = response_body.get('choices', [])
            if not choices:
                logging.debug("NVIDIA response had no choices", extra={"response_body": response_body})
                return "[NVIDIA: No choices in response]"

            # Attempt multiple ways to extract the text from the first choice
            first_choice = choices[0]
            # Common location: choice.get('message')
            message = first_choice.get('message') if isinstance(first_choice, dict) else None
            content_text = _extract_text_from_message(message)
            if content_text:
                return content_text

            # Sometimes content sits directly under 'content' or 'text' on the choice
            for key in ('content', 'text', 'response', 'output'):
                v = first_choice.get(key) if isinstance(first_choice, dict) else None
                if isinstance(v, str) and v.strip():
                    return v

                if isinstance(v, (dict, list)):
                    extracted = _extract_text_from_message({'content': v} if not isinstance(v, str) else {'content': str(v)})
                    if extracted:
                        return extracted

            # Nothing found — log response for debugging and return a clear message
            logging.debug("NVIDIA response parsing failed; full body logged for inspection.", extra={"response_body": response_body})
            return "[NVIDIA: No content found in response]"
        except requests.RequestException as e:
            logging.error(f"NVIDIA API request failed: {e}")
            st.error(f"NVIDIA API request failed: {e}")
            if getattr(e, "response", None):
                try:
                    st.error(f"Response body: {e.response.text}")
                except Exception:
                    pass
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse NVIDIA response: {e}")
            st.error(f"Failed to parse NVIDIA response: {e}")
            return None

    try:
        if file_name.lower().endswith('.pdf'):
            def process_page(image):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                return process_image_bytes(img_bytes.getvalue())
            return _process_pdf_pages(file_bytes, process_page)
        else:
            return process_image_bytes(file_bytes)
    except Exception as e:
        st.error(f"NVIDIA processing error: {str(e)}")
        logging.error(f"NVIDIA processing error: {e}", exc_info=True)
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
                result = process_mistral(client, file_bytes, file_name, OCR_MODELS["Mistral"])
            elif provider == "Google":
                result = process_google(client, file_bytes, file_name, OCR_MODELS["Google"])
            elif provider == "Tesseract":
                result = process_tesseract(client, file_bytes, file_name)
            elif provider == "PyMuPDF":
                result = process_pymupdf(client, file_bytes, file_name)
            elif provider == "PyPDF2":
                result = process_pypdf2(client, file_bytes, file_name)
            elif provider == "NVIDIA":
                result = process_nvidia(client, file_bytes, file_name, OCR_MODELS["NVIDIA"])

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
        logging.error(f"Error processing file: {e}", exc_info=True)
        return None