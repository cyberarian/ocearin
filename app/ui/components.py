import streamlit as st
from streamlit_option_menu import option_menu  # Change import

class Navigation:
    @staticmethod
    def render_navbar():
        # Map display names to page IDs
        page_mapping = {
            "Home": "home",
            "OCR": "ocr",
            "Quality Metrics": "compare",  # Changed from "Quality Metrics" to "Compare"
            "About": "about"
        }
        
        # Use option_menu with custom styles
        selected = option_menu(
            menu_title=None,
            options=list(page_mapping.keys()),  # Use display names
            icons=["house", "file-text", "graph-up", "info-circle"],
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#1E1E1E",
                    "font-family": "'Geo', sans-serif"  # Add font-family
                },
                "icon": {
                    "font-size": "20px",
                    "color": "#FAFAFA"
                },
                "nav-link": {
                    "color": "#FAFAFA",
                    "font-size": "14px",
                    "text-align": "center",
                    "margin": "0px",
                    "padding": "15px",
                    "--hover-color": "#2D2D2D",
                    "font-family": "'Iceland', sans-serif"  # Add font-family
                },
                "nav-link-selected": {
                    "background-color": "#2D2D2D",
                    "color": "#FFFFFF",
                    "font-family": "'Iceland', sans-serif"  # Add font-family
                }
            }
        )
        
        # Convert selected display name to page ID
        return page_mapping.get(selected, "home")

class OCRInterface:
    @staticmethod
    def render_provider_selector():
        provider_options = [
            "Mistral", "Google", "Tesseract", "PyMuPDF", "PyPDF2"
        ]
        return st.selectbox(
            "Select OCR Provider",
            options=provider_options,
            help="Choose the OCR provider"
        )
    
    @staticmethod
    def render_results_tabs(results, quality_metrics):
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Text", "Images", "Quality", "Comparison", "Debug"
        ])

        with tab1:
            st.markdown("### Extracted Text")
            st.markdown(results.get("text", "No text extracted"))
            
            if results.get("text"):
                st.download_button(
                    "📥 Download Text",
                    results["text"],
                    file_name="extracted_text.md",
                    mime="text/markdown"
                )

        with tab2:
            st.markdown("### Extracted Images")
            if "images" in results:
                for idx, img in enumerate(results["images"]):
                    st.image(img, caption=f"Image {idx+1}")
            else:
                st.info("No images extracted")

        with tab3:
            st.markdown("### Quality Metrics")
            if quality_metrics:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Overall Score", f"{quality_metrics['score']:.1%}")
                    st.metric("Word Count", quality_metrics['metrics']['word_count'])
                with col2:
                    st.metric("Structure Score", f"{quality_metrics['metrics']['structure_score']:.1%}")
                    st.metric("Format Score", f"{quality_metrics['metrics']['format_retention']:.1%}")
            else:
                st.info("No quality metrics available")

        with tab4:
            st.markdown("### Provider Comparison")
            if "comparisons" in st.session_state:
                for provider, score in st.session_state.comparisons.items():
                    st.metric(provider, f"{score:.1%}")
            else:
                st.info("Process with multiple providers to see comparison")

        with tab5:
            st.markdown("### Debug Information")
            st.json(results)
