import streamlit as st
from ocr_visualization import visualize_ocr_comparison

def render():
    st.title("Provider Comparison")
    
    if st.session_state.ocr_results:
        tab1, tab2 = st.tabs(["📊 Quality Metrics", "🔄 Compare Results"])
        
        with tab1:
            st.subheader("OCR Quality Assessment")
            for provider, data in st.session_state.ocr_results.items():
                with st.expander(f"{provider} Quality Metrics", expanded=True):
                    display_quality_metrics(data.get("quality_score"), data.get("metrics"))
        
        with tab2:
            st.subheader("Results Comparison")
            visualize_ocr_comparison(st.session_state.ocr_results)
    else:
        st.info("Process a document with multiple providers to see comparison")
        st.markdown("""
            ### How to Compare:
            1. Go to OCR page
            2. Process your document with different providers
            3. Return here to see the comparison
        """)

    # Move footer outside of the conditional blocks
    st.markdown("---")
    st.caption(
        "Dikembangkan oleh Adnuri Mohamidi dengan bantuan AI :orange_heart: #OpenToWork #HireMe", 
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