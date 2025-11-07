import streamlit as st
from ocr_visualization import visualize_ocr_comparison

def render():
    st.title("OCR Provider Comparison")
    
    if st.session_state.ocr_results:
        tab1, tab2 = st.tabs(["📊 Quality Metrics", "🔄 Results Comparison"])
        
        with tab1:
            st.subheader("OCR Quality Metrics")
            for provider, data in st.session_state.ocr_results.items():
                with st.expander(f"{provider} Quality Metrics", expanded=True):
                    display_quality_metrics(data.get("quality_score"), data.get("metrics"))
        
        with tab2:
            st.subheader("Results Comparison")
            visualize_ocr_comparison(st.session_state.ocr_results)
    else:
        st.info("Process a document with multiple providers to compare results.")
        st.markdown("""
            ### How to Compare Results:
            1. Go to the OCR page
            2. Run OCR with different providers
            3. Return here to view the comparison
        """)

    st.markdown("---")
    st.caption(
        "Developed by Adnuri Mohamidi with AI assistance :orange_heart: #OpenToWork #HireMe", 
        help="cyberariani@gmail.com"
    )

def display_quality_metrics(score, metrics):
    """Display quality metrics for a provider"""
    if score and metrics:
        color = "🟢" if score >= 0.8 else "🟡" if score >= 0.5 else "🔴"
        st.markdown(f"**Overall Score:** {color} {score:.1%}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Content Metrics**")
            for name, value in {
                "Words": metrics.get("word_count", 0),
                "Lines": metrics.get("line_count", 0),
                "Characters": metrics.get("char_count", 0)
            }.items():
                st.metric(name, value)
        
        with col2:
            st.markdown("**Quality Scores**")
            for name, value in {
                "Confidence": metrics.get("confidence_score", 0),
                "Structure": metrics.get("structure_score", 0),
                "Format": metrics.get("format_retention", 0)
            }.items():
                st.metric(name, f"{value:.1%}")