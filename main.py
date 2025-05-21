import streamlit as st
from utils import initialize_session_state
from app.ui.components import Navigation
from app.pages import home, ocr, about, compare

def main():
    # Initialize session state
    initialize_session_state()
    
    # Verify API keys are loaded
    if not all(key in st.secrets for key in ["MISTRAL_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"]):
        st.error("Missing API keys in .streamlit/secrets.toml")
        return
        
    # Set up page with custom width
    st.set_page_config(
        page_title="^di OCEARIN Ajah", 
        page_icon="📄", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load custom CSS
    with open('.streamlit/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Additional styling for width control
    st.markdown("""
        <style>
        .appview-container {
            width: 100%;
        }
        .block-container {
            max-width: 65rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Force viewport settings
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] {
                max-width: 100vw;
                padding: 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Add navigation
    selected_page = Navigation.render_navbar()
    
    # Route to appropriate page content
    if selected_page == "home":
        home.render()
    elif selected_page == "ocr":
        ocr.render()
    elif selected_page == "compare":
        compare.render()
    elif selected_page == "about":
        about.render()
    else:
        home.render()  # Default to home

if __name__ == "__main__":
    main()