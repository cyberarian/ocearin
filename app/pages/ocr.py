import streamlit as st
import os
import io  # Add io import
from utils import render_pdf_page, safe_pdf_open
from ocr_providers import process_file_ocr

def render():
    st.title("OCR Processing")
    
    # How-to guide
    st.info("""
        📋 **How to use:**
        1. Upload your document (PDF/Image)
        2. Fill in optional metadata
        3. Select an OCR provider
        4. Accept privacy terms
        5. Click Process to start
    """)

    # Upload and Provider Selection Row
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.markdown("### 📤 Upload Document")
        uploaded_file = st.file_uploader(
            "PDF or Image files",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
        )

    with col2:
        st.markdown("### 📝 Document Metadata")
        doc_title = st.text_input("Title (optional)", key="doc_title")
        doc_lang = st.selectbox(
            "Language",
            ["English", "Indonesian", "Auto-detect"],
            index=0,
            key="doc_lang"
        )

    with col3:
        st.markdown("### 🤖 Select Provider")
        
        # Initialize last_provider in session state if it doesn't exist
        if "last_provider" not in st.session_state:
            st.session_state.last_provider = None
            
        provider = st.selectbox(
            "OCR Provider",
            options=["NVIDIA", "Mistral", "Google", "Tesseract", "PyMuPDF", "PyPDF2"],
            help="Choose your OCR provider"
        )
        
        # Clear results if provider changed
        if st.session_state.last_provider != provider:
            if "result" in st.session_state.app_state:
                del st.session_state.app_state["result"]
            if "quality" in st.session_state.app_state:
                del st.session_state.app_state["quality"]
            if provider in st.session_state.ocr_results:
                del st.session_state.ocr_results[provider]
            st.session_state.last_provider = provider
        
        # Show provider status
        api_key_exists = False
        if provider == "Mistral":
            api_key_exists = bool(st.secrets.get("MISTRAL_API_KEY"))
        elif provider == "Google":
            api_key_exists = bool(st.secrets.get("GEMINI_API_KEY"))
        elif provider == "NVIDIA":
            api_key_exists = bool(st.secrets.get("NVIDIA_API_KEY"))

        if provider in ["Mistral", "Google", "NVIDIA"]: # Cloud providers
            if api_key_exists:
                st.info(f"✓ {provider} API key found")
            else:
                st.error(f"✗ {provider} API key missing")

            privacy_consent = st.checkbox(
                "I understand cloud processing implications",
                help="Required for cloud-based providers"
            )
        else:
            privacy_consent = True
        
        process_button = st.button(
            "Process Document", 
            type="primary",
            disabled=not (uploaded_file and privacy_consent)
        )

    # Document Preview and Results Row
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        
        st.markdown("---")
        col_preview, col_results = st.columns([1, 1])

        with col_preview:
            st.markdown("### 📄 Document Preview")
            if uploaded_file.type.startswith('image'):
                st.image(file_bytes, caption="Uploaded Image", use_container_width=True)
            elif uploaded_file.type == "application/pdf":
                num_pages = safe_pdf_open(file_bytes)
                if num_pages > 0:
                    page_num = st.select_slider("Preview Page", options=range(1, num_pages + 1), format_func=lambda x: f"Page {x}/{num_pages}")
                    page_image = render_pdf_page(file_bytes, page_num)
                    if page_image:
                        st.image(page_image, use_container_width=True)

        with col_results:
            st.markdown("### 📋 Extracted Content")
            if process_button:
                process_file_ocr(file_bytes, uploaded_file.name, provider)
            
            # Display results from session state
            if st.session_state.app_state.get("result"):
                st.markdown(st.session_state.app_state["result"])
                # The download button logic from the original file was complex and tied to UI.
                # For now, we display the text. A refactor could move download logic here.

    # Footer
    st.markdown("---")
    st.caption(
        "Dikembangkan oleh Adnuri Mohamidi dengan bantuan AI :orange_heart: #OpenToWork #HireMe", 
        help="cyberariani@gmail.com"
    )