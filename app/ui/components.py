import streamlit as st
from streamlit_option_menu import option_menu  # Change import

class Navigation:
    @staticmethod
    def render_navbar():
        # Use option_menu instead of st_navbar
        selected = option_menu(
            menu_title=None,
            options=["Home", "OCR", "Compare", "About"],
            icons=["house", "file-text", "graph-up", "info-circle"],
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#1E1E1E"
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
                    "--hover-color": "#2D2D2D"
                },
                "nav-link-selected": {
                    "background-color": "#2D2D2D",
                    "color": "#FFFFFF",
                }
            }
        )
        
        # Convert selected option to page ID
        pages = ["home", "ocr", "compare", "about"]
        return pages[pages.index(selected.lower())] if selected else "home"

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
        # ... tab content rendering code ...
