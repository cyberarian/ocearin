import streamlit as st
import os
from content import get_app_title, get_app_content
from utils import initialize_session_state, render_pdf_page, safe_pdf_open
from ocr_providers import process_file_ocr
from ocr_visualization import visualize_ocr_comparison
from constants import OCR_METRICS  # Add this import
import fitz

def main():
    # Initialize session state
    initialize_session_state()
    
    # Set up page
    st.set_page_config(page_title="^di OCEARIN Ajah", page_icon="📄", layout="wide")
    
    # Display app title and content
    st.title(get_app_title())
    st.markdown(get_app_content(), unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.write("Upload PDF documents or images to extract text and process with OCR.")
        
        provider_options = ["Mistral", "Google", "Tesseract", "PyMuPDF", "PyPDF2"]
        provider = st.selectbox("Select OCR Provider", options=provider_options)
        
        if provider in ["PyMuPDF", "PyPDF2"]:
            st.info(f"Using {provider} - PDF text extraction only (no OCR capabilities)")
        elif provider == "Tesseract":
            st.info("Using local Tesseract OCR - no API key required")
        else:
            st.info(f"Using {provider} AI-powered OCR")
        st.warning("""
            **Pemberitahuan Privasi**
            - Berkas yang diunggah akan diproses di server cloud
            - Jangan mengunggah dokumen yang sensitif atau rahasia
            """
        )
        privacy_consent = st.checkbox("Saya memahami dan menerima implikasi privasi", 
            help="Anda harus menyetujui ini untuk memproses dokumen")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
            disabled=not privacy_consent
        )
        
        if uploaded_file:
            st.write("File Details:", {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            })
            
            process_button = st.button(f"Process with {provider}", disabled=not privacy_consent)

    # Main content area
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        file_bytes = uploaded_file.getvalue()
        
        with col1:
            st.subheader("Document Preview")
            if uploaded_file.type.startswith('image'):
                st.image(file_bytes, caption="Uploaded Image", use_container_width=True)
            elif uploaded_file.type == "application/pdf":
                show_parsing = st.checkbox("Show OCR parsing visualization")
                num_pages = safe_pdf_open(file_bytes)
                st.write(f"PDF document with {num_pages} pages")
                
                page_num = st.selectbox(
                    "Select page to preview", 
                    range(1, num_pages + 1),
                    format_func=lambda x: f"Page {x}"
                )
                
                page_image = render_pdf_page(file_bytes, page_num, show_parsing)
                if page_image:
                    st.image(page_image, caption=f"PDF Page {page_num}/{num_pages}" + 
                            (" (with OCR parsing)" if show_parsing else ""))
        
        if process_button:
            with st.spinner(f"Processing with {provider}..."):
                result = process_file_ocr(file_bytes, uploaded_file.name, provider)
                if result and isinstance(result, str):
                    # Make sure result is properly set
                    if "quality" in st.session_state.app_state:
                        st.success(f"Text extracted successfully with {provider}")
                    else:
                        st.warning("Text extracted but quality metrics unavailable")

        # Show results
        if st.session_state.app_state.get("result"):
            with col2:
                st.subheader("Extracted Content")
                result_text = st.session_state.app_state.get("result")
                
                tab1, tab2, tab3, tab4 = st.tabs(["Text", "Images", "Quality", "Compare"])
                
                with tab1:
                    st.markdown(
                        f'<div class="scrollable-text">{result_text}</div>', 
                        unsafe_allow_html=True
                    )
                
                with tab2:
                    if "images" in st.session_state.app_state["processing"]:
                        # Image display logic
                        img_data = st.session_state.app_state["processing"]["images"]
                        if img_data["files"]:
                            st.write(f"Found {len(img_data['files'])} images")
                            for img_file in sorted(img_data["files"]):
                                st.image(os.path.join(img_data["dir"], img_file))
                
                with tab3:
                    quality = st.session_state.app_state.get("quality")
                    if quality and isinstance(quality, dict):
                        # Display quality metrics with icons
                        st.write("### OCR Quality Assessment")
                        quality_color = (
                            "🟢" if quality.get("score", 0) >= OCR_METRICS["text_quality"]["good"]
                            else "🟡" if quality.get("score", 0) >= OCR_METRICS["text_quality"]["medium"]
                            else "🔴"
                        )
                        st.write(f"Overall Quality: {quality_color} {quality.get('score', 0):.2%}")
                        
                        # Show detailed metrics in columns
                        if "metrics" in quality and quality["metrics"]:
                            metrics = quality["metrics"]
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("#### Text Metrics")
                                st.metric("Word Count", metrics.get("word_count", 0))
                                st.metric("Line Count", metrics.get("line_count", 0))
                                st.metric("Char Count", metrics.get("char_count", 0))
                            
                            with col2:
                                st.write("#### Quality Scores")
                                st.metric("Confidence", f"{metrics.get('confidence_score', 0):.1%}")
                                st.metric("Structure", f"{metrics.get('structure_score', 0):.1%}")
                                st.metric("Format", f"{metrics.get('format_retention', 0):.1%}")
                        else:
                            st.info("Detailed metrics not available for this provider")
                    else:
                        st.info("Process a document to see quality metrics")
                
                with tab4:
                    if st.session_state.ocr_results:
                        visualize_ocr_comparison(st.session_state.ocr_results)
                    else:
                        st.info("Process with multiple providers to see comparison")
                        # Add provider selection for comparison
                        other_providers = [p for p in ["Mistral", "Google", "Tesseract", "PyMuPDF", "PyPDF2"] 
                                         if p != provider]
                        compare_with = st.multiselect(
                            "Compare with other providers",
                            other_providers
                        )
                        
                        if compare_with and st.button("Run Comparison"):
                            for compare_provider in compare_with:
                                with st.spinner(f"Processing with {compare_provider}..."):
                                    compare_result = process_file_ocr(file_bytes, uploaded_file.name, compare_provider)
                                    if compare_result:
                                        st.success(f"Completed {compare_provider} processing")

if __name__ == "__main__":
    main()