import os
import io
import base64
import streamlit as st
from PIL import Image
import fitz

def initialize_session_state():
    """Initialize session state with default values"""
    if "app_state" not in st.session_state:
        st.session_state.app_state = {
            "result": None,
            "file_info": None,
            "processing": {
                "num_pages": 0,
                "current_page": 1,
                "provider": None,
                "parsed_elements": {},
                "images_dir": None,
                "current_file": None
            },
            "quality": None
        }
    
    if "ocr_results" not in st.session_state:
        st.session_state.ocr_results = {}

def prepare_file_for_mistral(file_bytes, file_name):
    """Prepare file for Mistral OCR by converting if needed"""
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF', resolution=300.0)
        return pdf_bytes.getvalue(), f"{os.path.splitext(file_name)[0]}.pdf"
    
    return file_bytes, file_name

def render_pdf_pages(file_bytes, start_page=None, end_page=None):
    """Convert PDF pages to list of images"""
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        images = []
        
        # Handle page range
        start = start_page - 1 if start_page else 0
        end = min(end_page if end_page else len(pdf_document), 5)  # Limit to 5 pages
        
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

def safe_pdf_open(file_bytes):
    """Safely open PDF and get page count"""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            return len(pdf)
    except Exception as e:
        st.error(f"Error opening PDF: {str(e)}")
        return 0

def process_ocr_response(response_dict, base_name):
    """Process OCR response to extract markdown and images"""
    image_dir = f"{base_name}_images"
    extracted_images = []
    
    try:
        has_images = False
        if not os.path.exists(image_dir):
            os.makedirs(image_dir, exist_ok=True)
            
        # Process pages and extract images
        all_content = []
        for page_idx, page in enumerate(response_dict.get('pages', [])):
            if page_idx >= 5:  # Limit to first 5 pages
                all_content.append("\n\n---\n\n*Note: Document truncated to first 5 pages.*")
                break
                
            page_content = process_page_content(page, base_name, image_dir, page_idx)
            all_content.append(page_content)
            
        # Update session state
        st.session_state.app_state["processing"]["images"] = {
            "dir": image_dir,
            "files": [f for f in os.listdir(image_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        }
        
        return "\n\n".join(all_content)
    except Exception as e:
        st.error(f"Error processing OCR response: {str(e)}")
        return None

def process_page_content(page, base_name, image_dir, page_idx):
    """Process individual page content and images"""
    page_content = page.get('markdown', '')
    page_images = page.get('images', [])
    
    if not page_images:
        return page_content
        
    image_data_dict = {}
    for img_idx, image in enumerate(page_images):
        image_id = image.get('id')
        image_base64 = image.get('image_base64')
        
        if not image_id or not image_base64:
            continue
            
        # Save image and update references
        image_info = save_image(image, base_name, image_dir, page_idx, img_idx)
        if image_info:
            image_data_dict[image_id] = image_info
            
    # Update markdown with image references
    for img_id, img_path in image_data_dict.items():
        page_content = page_content.replace(
            f"![{img_id}]({img_id})", 
            f"![Image {img_id}]({img_path})"
        )
    
    return page_content

def save_image(image, base_name, image_dir, page_idx, img_idx):
    """Save image and return path"""
    try:
        image_base64 = image.get('image_base64', '')
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
            
        image_format = image.get('format', 'png')
        image_filename = f"{base_name}_page{page_idx + 1}_img{img_idx + 1}.{image_format}"
        image_path = os.path.join(image_dir, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_base64))
            
        return f"./{os.path.basename(image_dir)}/{image_filename}"
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

def render_pdf_page(file_bytes, page_num, show_parsing=False):
    """Render PDF page with optional parsing visualization"""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf_document:
            page = pdf_document[page_num - 1]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            
            if show_parsing:
                from ocr_visualization import visualize_ocr_results
                parsed_elements = extract_page_elements(page)
                return visualize_ocr_results(img_bytes, parsed_elements)
                
            return img_bytes
    except Exception as e:
        st.error(f"Error rendering PDF page: {str(e)}")
        return None

def extract_page_elements(page):
    """Extract page elements for visualization"""
    elements = []
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if block.get("type") == 0:  # Text
            is_heading = False
            if block.get("lines"):
                first_line = block["lines"][0]
                is_heading = any(span["size"] > 12 for span in first_line["spans"])
            
            elements.append({
                "type": "heading" if is_heading else "text",
                "bbox": block.get('bbox')
            })
        elif block.get("type") == 1:  # Image
            elements.append({
                "type": "image",
                "bbox": block.get('bbox')
            })
    
    return elements