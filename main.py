import streamlit as st
import os
import json
import base64
from mistralai import Mistral
import google.generativeai as genai
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF for PDF rendering
import PyPDF2  # PyPDF2 for PDF text extraction
import sys
from content import get_app_title, get_app_content

# Update poppler path configuration
POPPLER_PATH = os.path.join(os.getcwd(), "poppler", "Library", "bin")
if sys.platform.startswith('win'):
    if not os.path.exists(POPPLER_PATH):
        st.error("""
            Poppler is not found. Please:
            1. Download Poppler for Windows from: https://github.com/oschwartz10612/poppler-windows/releases/
            2. Extract it to 'poppler' folder so the path is: poppler/Library/bin/pdfinfo.exe
        """)
        st.stop()
    os.environ["PATH"] += os.pathsep + POPPLER_PATH

# Page config
st.set_page_config(
    page_title="^di OCEARIN Ajah",
    page_icon="📄",
    layout="wide"
)

# Add custom CSS for scrollable containers
st.markdown("""
    <style>
        .scrollable-text {
            height: 600px;
            overflow-y: auto;
            border: 1px solid #2D2D2D;
            padding: 1rem;
            background-color: #1E1E1E;
            border-radius: 12px;
            font-size: 0.95em;
            line-height: 1.6;
            font-family: 'Roboto', sans-serif;
            color: #FAFAFA;
        }
        .stTextArea textarea {
            font-family: 'Roboto Mono', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            color: #FAFAFA;
            background-color: #1E1E1E;
            border: 1px solid #2D2D2D;
            border-radius: 8px;
        }
        code {
            padding: 0.2em 0.4em;
            background-color: #2D2D2D;
            border-radius: 4px;
            font-size: 0.9em;
            color: #1E88E5;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize different VLM clients
@st.cache_resource
def get_vlm_client(provider):
    """Get client based on selected VLM provider"""
    try:
        if provider == "Mistral":
            api_key = st.secrets.get("MISTRAL_API_KEY")
            return Mistral(api_key=api_key)
        elif provider == "Google":
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in secrets")
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-2.0-flash')
        elif provider == "Tesseract":
            # Set Tesseract path based on environment
            if sys.platform.startswith('win'):
                tesseract_path = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
                if not os.path.exists(tesseract_path):
                    st.error("Tesseract not found. Please install Tesseract-OCR and set TESSERACT_PATH environment variable.")
                    return None
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                # Linux environment (Streamlit Cloud)
                pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
            return pytesseract
        elif provider == "PyMuPDF":
            return fitz  # Return fitz module as client
        elif provider == "PyPDF2":
            return PyPDF2  # Return PyPDF2 module as client
        return None
    except Exception as e:
        st.error(f"Error initializing {provider} client: {str(e)}")
        return None

def process_ocr_response(response_dict, base_name):
    """
    Process OCR response to extract markdown content and images
    
    Args:
        response_dict (dict): OCR response data
        base_name (str): Base filename for output
        
    Returns:
        str: Extracted markdown content
    """
    # Create a directory for images if any are found
    image_dir = f"{base_name}_images"
    has_images = False
    
    # Check if the response contains images - structure based on API documentation
    for page in response_dict.get('pages', []):
        if page.get('images') and len(page.get('images', [])) > 0:
            has_images = True
            break
            
    if has_images:
        os.makedirs(image_dir, exist_ok=True)
        print(f"  Created image directory: {image_dir}")
    
    # Process each page to extract markdown and handle images
    all_content = []
    
    for page_idx, page in enumerate(response_dict.get('pages', [])):
        # Limit to first 5 pages
        if page_idx >= 5:
            all_content.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
            break
            
        page_markdown = page.get('markdown', '')
        page_images = page.get('images', [])
        
        # Process images in this page
        if page_images:
            print(f"  Found {len(page_images)} images on page {page_idx + 1}")
            
            # Create a dictionary to map image IDs to their base64 data
            image_data_dict = {}
            
            for img_idx, image in enumerate(page_images):
                # Get image ID and base64 data
                image_id = image.get('id')
                image_base64 = image.get('image_base64')
                
                if not image_id or not image_base64:
                    print(f"  Warning: Image {img_idx} is missing id or base64 data, skipping")
                    continue
                
                # Save the image to a file
                image_format = image.get('format', 'png')
                image_filename = f"{base_name}_page{page_idx + 1}_img{img_idx + 1}.{image_format}"
                image_path = os.path.join(image_dir, image_filename)
                
                try:
                    # Handle base64 data
                    if image_base64.startswith('data:image'):
                        # Extract the base64 string after the comma
                        b64_data = image_base64.split(',', 1)[1]
                    else:
                        # If it's already just the base64 data without prefix
                        b64_data = image_base64
                        
                    # Decode and save the image
                    with open(image_path, 'wb') as img_file:
                        img_file.write(base64.b64decode(b64_data))
                    print(f"  Saved image to {image_path}")
                    
                    # Add an entry to the dictionary mapping image ID to the local file path
                    # This will be used to replace the image references in the markdown
                    image_data_dict[image_id] = f"./{os.path.basename(image_dir)}/{image_filename}"
                    
                except Exception as e:
                    print(f"  Error saving image: {str(e)}")
            
            # Replace image references in the markdown
            for img_id, img_path in image_data_dict.items():
                # Format expected by the Mistral OCR API is ![id](id)
                page_markdown = page_markdown.replace(f"![{img_id}]({img_id})", f"![Image {img_id}]({img_path})")
        
        # Add processed page markdown to the content list
        all_content.append(page_markdown)
    
    # Join all pages with double newlines
    content = "\n\n".join(all_content)
    
    return content

# Initialize session state variables for persistence
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = []
if "preview_src" not in st.session_state:
    st.session_state["preview_src"] = []
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = []

def prepare_file_for_mistral(file_bytes, file_name):
    """Prepare file for Mistral OCR by converting if needed"""
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
        # Convert image to PDF for Mistral
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Save as PDF
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF', resolution=300.0)
        return pdf_bytes.getvalue(), f"{os.path.splitext(file_name)[0]}.pdf"
    
    return file_bytes, file_name

def process_mistral(client, file_bytes, file_name, model):
    """Process file with Mistral OCR"""
    try:
        # Prepare file (convert image to PDF if needed)
        prepared_bytes, prepared_name = prepare_file_for_mistral(file_bytes, file_name)
        
        # Upload file
        with st.spinner("Uploading file..."):
            uploaded_file = client.files.upload(
                file={
                    "file_name": prepared_name,
                    "content": prepared_bytes,
                },
                purpose="ocr"
            )
            
        # Get signed URL and process
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        
        ocr_response = client.ocr.process(
            model=model,
            document={
                "type": "document_url",
                "document_url": signed_url.url
            },
            include_image_base64=True
        )
        
        # Process response
        if hasattr(ocr_response, 'model_dump'):
            response_dict = ocr_response.model_dump()
        else:
            response_dict = json.loads(str(ocr_response))
            
        return process_ocr_response(response_dict, os.path.splitext(file_name)[0])
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def render_pdf_pages(file_bytes, start_page=None, end_page=None):
    """Convert PDF pages to list of images using PyMuPDF."""
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        images = []
        
        # Handle page range
        start = start_page - 1 if start_page else 0
        end = end_page if end_page else len(pdf_document)
        
        for page_num in range(start, end):
            page = pdf_document[page_num]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            images.append(Image.open(io.BytesIO(img_bytes)))
            
        pdf_document.close()
        return images
    except Exception as e:
        st.error(f"Error converting PDF: {str(e)}")
        return None

def process_google(client, file_bytes, file_name, model):
    """Process file with Google Gemini"""
    try:
        prompt_text = "Extract all text from this image in markdown format. Preserve document structure and formatting."
        
        if file_name.lower().endswith('.pdf'):
            images = render_pdf_pages(file_bytes, end_page=5)  # Limit to first 5 pages
            all_text = []
            
            for i, image in enumerate(images):
                with st.spinner(f"Processing page {i+1}/{len(images)}..."):
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    
                    response = client.generate_content([
                        prompt_text,
                        {"mime_type": "image/png", "data": img_byte_arr.getvalue()}
                    ])
                    all_text.append(response.text)
                
                if i == 4:
                    all_text.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                    break
            
            return "\n\n".join(all_text)
        else:
            response = client.generate_content([
                prompt_text,
                {"mime_type": "image/png", "data": file_bytes}
            ])
            return response.text
            
    except Exception as e:
        st.error(f"Google processing error: {str(e)}")
        return None

def process_tesseract(client, file_bytes, file_name):
    """Process file with Tesseract OCR"""
    try:
        if file_name.lower().endswith('.pdf'):
            images = render_pdf_pages(file_bytes, end_page=5)  # Limit to first 5 pages
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
    """Process file with PyMuPDF"""
    try:
        if file_name.lower().endswith('.pdf'):
            doc = client.open(stream=file_bytes, filetype="pdf")
            all_text = []
            
            for i in range(min(len(doc), 5)):  # Limit to first 5 pages
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
    """Process file with PyPDF2"""
    try:
        if file_name.lower().endswith('.pdf'):
            pdf_reader = client.PdfReader(io.BytesIO(file_bytes))
            all_text = []
            
            for i in range(min(len(pdf_reader.pages), 5)):  # Limit to first 5 pages
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
    """Process file with selected provider"""
    try:
        client = get_vlm_client(provider)
        if not client:
            return None

        # Clear previous results
        st.session_state["ocr_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
            
        with st.spinner(f"Processing with {provider}..."):
            if provider == "Mistral":
                return process_mistral(client, file_bytes, file_name, "mistral-ocr-latest")
            elif provider == "Google":
                return process_google(client, file_bytes, file_name, "gemini-2.0-flash")
            elif provider == "Tesseract":
                return process_tesseract(client, file_bytes, file_name)
            elif provider == "PyMuPDF":
                return process_pymupdf(client, file_bytes, file_name)
            elif provider == "PyPDF2":
                return process_pypdf2(client, file_bytes, file_name)
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def render_pdf_page(file_bytes, page_num):
    """Render a specific page of a PDF as an image using PyMuPDF."""
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        page = pdf_document[page_num - 1]  # PyMuPDF uses 0-based indexing
        pix = page.get_pixmap()
        pdf_document.close()
        return pix.tobytes("png")
    except Exception as e:
        st.error(f"Error rendering PDF page: {str(e)}")
        return None

def main():
    st.title(get_app_title())
    st.markdown(get_app_content(), unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.write("Upload PDF documents or images to extract text and process with OCR.")
        
        # Update provider selection with all options
        provider_options = [
            "Mistral",
            "Google", 
            "Tesseract",
            "PyMuPDF",  # Add PyMuPDF
            "PyPDF2"    # Add PyPDF2
        ]
        
        provider = st.selectbox(
            "Select OCR Provider",
            options=provider_options,
            help="Choose the OCR provider"
        )
        
        # Update provider info messages
        if provider in ["PyMuPDF", "PyPDF2"]:
            st.info(f"Using {provider} - PDF text extraction only (no OCR capabilities)")
        elif provider == "Tesseract":
            st.info("Using local Tesseract OCR - no API key required")
        else:
            st.info(f"Using {provider} AI-powered OCR")
        
        # Bilingual Privacy Notice
        st.warning("""
            **Pemberitahuan Privasi**
            - Berkas yang diunggah akan diproses di server cloud
            - Jangan mengunggah informasi sensitif atau rahasia
            """
        )
        
        privacy_consent = st.checkbox(
            "Saya memahami dan menerima implikasi privasi",
            help="Anda harus menyetujui ini untuk memproses dokumen"
        )
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
            help="Upload a PDF or image file to process",
            disabled=not privacy_consent
        )
        
        if uploaded_file:
            st.write("File Details:")
            st.write({
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            })
            
            process_button = st.button(
                f"Process with {provider}",
                disabled=not privacy_consent
            )
    
    # Main area content
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Document Preview")
            file_bytes = uploaded_file.getvalue()
            
            if uploaded_file.type.startswith('image'):
                st.image(file_bytes, caption="Uploaded Image", use_container_width=True)
            elif uploaded_file.type == "application/pdf":
                try:
                    # Read PDF with PyMuPDF for page count
                    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
                    num_pages = len(pdf_document)
                    pdf_document.close()
                    
                    st.write(f"PDF document with {num_pages} pages")
                    
                    # Add page selector
                    page_num = st.selectbox(
                        "Select page to preview", 
                        range(1, num_pages + 1),
                        format_func=lambda x: f"Page {x}"
                    )
                    
                    # Render selected page as an image
                    page_image = render_pdf_page(file_bytes, page_num)
                    if page_image:
                        st.image(
                            page_image,
                            caption=f"PDF Page {page_num}/{num_pages}",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error previewing PDF: {str(e)}")
        
        # Process and show results
        if process_button:
            with col2:
                try:
                    with st.spinner("Processing document..."):
                        result = process_file_ocr(
                            file_bytes=uploaded_file.getvalue(),
                            file_name=uploaded_file.name,
                            provider=provider
                        )
                    
                    if result:
                        st.subheader("Extracted Content")
                        
                        # Create tabs for different content types
                        tab1, tab2, tab3 = st.tabs(["Text", "Images", "Raw Markdown"])
                        
                        with tab1:
                            st.markdown(f'<div class="scrollable-text">{result}</div>', unsafe_allow_html=True)
                        
                        with tab2:
                            with st.container():
                                # Display extracted images
                                base_name = os.path.splitext(uploaded_file.name)[0]
                                image_dir = f"{base_name}_images"
                                if os.path.exists(image_dir):
                                    images = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
                                    if images:
                                        st.write("Extracted Images:")
                                        for img_file in images:
                                            img_path = os.path.join(image_dir, img_file)
                                            st.image(img_path, caption=img_file, use_container_width=True)
                                    else:
                                        st.info("No images were extracted from this document")
                                else:
                                    st.info("No images were extracted from this document")
                        
                        with tab3:
                            # Remove extra container, just use text area directly
                            st.text_area(
                                "Raw Markdown Content", 
                                result, 
                                height=550,
                                key="raw_markdown"
                            )
                        
                        # Download buttons
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                label="Download Text Results",
                                data=result,
                                file_name=f"{base_name}_ocr.md",
                                mime="text/markdown"
                            )
                        
                        # Add ZIP download if images exist
                        if os.path.exists(image_dir) and os.listdir(image_dir):
                            with col_dl2:
                                import shutil
                                zip_path = f"{base_name}_images.zip"
                                shutil.make_archive(base_name + "_images", 'zip', image_dir)
                                with open(zip_path, 'rb') as f:
                                    st.download_button(
                                        label="Download Extracted Images",
                                        data=f,
                                        file_name=f"{base_name}_images.zip",
                                        mime="application/zip"
                                    )
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()