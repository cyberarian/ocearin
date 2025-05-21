from constants import OCR_METRICS, OCR_PERFORMANCE_METRICS

def evaluate_ocr_quality(text, provider, metadata=None):
    """Evaluate OCR quality with provider-specific metrics"""
    metrics = {
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
        "char_count": len(text),
        "avg_line_length": len(text) / max(len(text.splitlines()), 1),
        "confidence_score": OCR_PERFORMANCE_METRICS["providers"][provider]["base_conf"],
        "structure_score": 0.0,
        "format_retention": 0.0
    }
    
    # Evaluate structure score
    if provider == "Mistral":
        metrics["structure_score"] = 0.9 if any(tag in text.lower() for tag in ["#", "##", "table", "---"]) else 0.7
        metrics["format_retention"] = 0.9 if "```" in text or "*" in text else 0.6
    elif provider == "Google":
        metrics["structure_score"] = 0.8 if any(marker in text for marker in ["Title:", "Heading:", "List:"]) else 0.6
        metrics["format_retention"] = 0.8 if len(text.splitlines()) > 5 else 0.6
    elif provider == "Groq":  # Add Groq handling
        metrics["structure_score"] = 0.9 if any(tag in text.lower() for tag in ["#", "##", "table", "-"]) else 0.7
        metrics["format_retention"] = 0.9 if any(marker in text for marker in ["```", "*", ">", "- "]) else 0.6
    elif provider == "Tesseract":
        metrics["structure_score"] = 0.5
        metrics["format_retention"] = 0.4
    else:  # PyMuPDF or PyPDF2
        metrics["structure_score"] = 0.8 if provider == "PyMuPDF" else 0.6
        metrics["format_retention"] = 0.7 if provider == "PyMuPDF" else 0.5

    # Calculate quality score using weights
    weights = OCR_PERFORMANCE_METRICS["weights"]
    quality_score = (
        metrics["confidence_score"] * weights["confidence"] +
        metrics["structure_score"] * weights["structure"] +
        metrics["format_retention"] * weights["format"]
    )
    
    return quality_score, metrics