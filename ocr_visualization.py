import streamlit as st
import pandas as pd
import io
from PIL import Image, ImageDraw
import fitz
from constants import OCR_PERFORMANCE_METRICS

def visualize_ocr_comparison(results):
    """Generate comparison visualization with detailed metrics"""
    st.write("### OCR Performance Comparison")
    
    # Summary metrics in columns
    cols = st.columns(len(results))
    for idx, (provider, data) in enumerate(results.items()):
        with cols[idx]:
            metrics = data["metrics"]
            score = data["quality_score"]
            
            # Color coding
            score_color = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
            
            # Display metrics
            st.metric(
                label=f"{provider} {score_color}",
                value=f"{score:.2%}",
                delta=f"{metrics['word_count']} words"
            )
            
            # Show provider strengths
            provider_info = OCR_PERFORMANCE_METRICS["providers"][provider]
            st.write("**Best for:**")
            for strength in provider_info["strengths"][:2]:  # Show top 2 strengths
                st.write(f"- {strength}")
    
    # Detailed comparison table
    st.write("#### Detailed Analysis")
    df = pd.DataFrame([{
        "Provider": provider,
        "Quality": f"{data['quality_score']:.1%}",
        "Words": data['metrics']['word_count'],
        "Lines": data['metrics']['line_count'],
        "Structure": f"{data['metrics']['structure_score']:.1%}",
        "Format": f"{data['metrics']['format_retention']:.1%}"
    } for provider, data in results.items()])
    
    st.dataframe(df.set_index("Provider"), use_container_width=True)
    
    # Show recommendations
    st.write("#### Recommendations")
    best_provider = max(results.items(), key=lambda x: x[1]["quality_score"])[0]
    st.success(f"🏆 Best performer: **{best_provider}**")
    
    for provider, data in results.items():
        if data["quality_score"] < 0.6:
            st.warning(f"⚠️ {provider}: Consider alternatives for better results")

def visualize_ocr_results(page_image, parsed_elements):
    """Visualize detected elements on page"""
    try:
        img = Image.open(io.BytesIO(page_image))
        draw = ImageDraw.Draw(img)
        
        colors = {
            'text': '#00FF00',
            'table': '#0000FF',
            'image': '#FF0000',
            'heading': '#FFA500'
        }
        
        for element in parsed_elements:
            bbox = element.get('bbox')
            element_type = element.get('type', 'text')
            if bbox:
                draw.rectangle(bbox, outline=colors.get(element_type, '#FFFFFF'), width=2)
        
        return img
    except Exception as e:
        st.error(f"Error visualizing OCR results: {str(e)}")
        return None

def visualize_provider_parsing(provider, file_bytes, file_name, page_num=1):
    """Generate provider-specific parsing visualization"""
    try:
        pdf_doc = fitz.open(stream=file_bytes)
        page = pdf_doc[page_num-1]
        elements = []
        
        # Get text blocks with provider-specific handling
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block.get("type") == 0:  # Text
                if provider in ["Mistral", "Google"]:
                    first_line = block["lines"][0] if block.get("lines") else None
                    is_heading = first_line and any(span["size"] > 12 for span in first_line["spans"])
                    
                    elements.append({
                        "type": "heading" if is_heading else "text",
                        "bbox": block["bbox"],
                        "color": "#FFA500" if is_heading else "#00FF00",
                        "label": "Heading" if is_heading else "Text"
                    })
                else:
                    elements.append({
                        "type": "text",
                        "bbox": block["bbox"],
                        "color": "#00FF00",
                        "label": "Text"
                    })
            
            elif block.get("type") == 1:  # Image
                elements.append({
                    "type": "image",
                    "bbox": block["bbox"],
                    "color": "#FF0000",
                    "label": "Image"
                })
                
        pdf_doc.close()
        return elements
        
    except Exception as e:
        st.error(f"Error in parsing visualization: {str(e)}")
        return []

def draw_parsing_visualization(file_bytes, page_num, elements):
    """Draw parsing visualization on page image"""
    try:
        with fitz.open(stream=file_bytes) as pdf_doc:
            page = pdf_doc[page_num - 1]
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            draw = ImageDraw.Draw(img)
            
            for elem in elements:
                bbox = elem["bbox"]
                draw.rectangle(
                    bbox,
                    outline=elem["color"],
                    width=2
                )
                
                # Add label if there's space
                if bbox[1] > 15:
                    draw.text(
                        (bbox[0], bbox[1]-15),
                        elem["label"],
                        fill=elem["color"]
                    )
            
            return img
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None