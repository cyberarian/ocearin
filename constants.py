OCR_METRICS = {
    "text_quality": {
        "good": 0.8,
        "medium": 0.5,
        "poor": 0.3
    },
    "confidence_thresholds": {
        "high": 0.9,
        "medium": 0.7,
        "low": 0.5
    }
}

OCR_PERFORMANCE_METRICS = {
    "providers": {
        "Mistral": {
            "ideal_for": ["Complex documents", "Tables", "Mixed layouts"],
            "strengths": ["Structure preservation", "Layout understanding", "Image extraction"],
            "base_conf": 0.85
        },
        "Google": {
            "ideal_for": ["Images", "Handwriting", "Screenshots"],
            "strengths": ["Visual understanding", "Multiple languages", "Context awareness"],
            "base_conf": 0.80
        },
        "Tesseract": {
            "ideal_for": ["Simple documents", "Clear text", "Basic layouts"],
            "strengths": ["Speed", "Offline processing", "Language support"],
            "base_conf": 0.60
        },
        "PyMuPDF": {
            "ideal_for": ["Clean PDFs", "Digital documents", "Text extraction"],
            "strengths": ["Fast processing", "Layout preservation", "PDF handling"],
            "base_conf": 0.95
        },
        "PyPDF2": {
            "ideal_for": ["Basic PDFs", "Text extraction", "Simple documents"],
            "strengths": ["Simple processing", "Memory efficient", "Basic extraction"],
            "base_conf": 0.70
        }
    },
    "weights": {
        "confidence": 0.4,
        "structure": 0.3,
        "format": 0.3
    }
}
