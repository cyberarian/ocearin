from constants import OCR_METRICS, OCR_PERFORMANCE_METRICS

def clamp(val, minval=0.0, maxval=1.0):
    return max(minval, min(maxval, val))

def evaluate_ocr_quality(text, provider, metadata=None):
    """Evaluate OCR quality with provider-specific metrics and improved robustness."""
    # Defensive: handle empty or non-string text
    if not isinstance(text, str) or not text.strip():
        return 0.0, {
            "word_count": 0,
            "line_count": 0,
            "char_count": 0,
            "avg_line_length": 0.0,
            "confidence_score": 0.0,
            "structure_score": 0.0,
            "format_retention": 0.0
        }

    metrics = {
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
        "char_count": len(text),
        "avg_line_length": len(text) / max(len(text.splitlines()), 1),
        "confidence_score": OCR_PERFORMANCE_METRICS["providers"].get(provider, {}).get("base_conf", 0.5),
        "structure_score": 0.0,
        "format_retention": 0.0
    }

    # Use metadata if available (e.g., expected language, page count)
    if metadata:
        # Example: adjust confidence if language mismatch
        expected_lang = metadata.get("language")
        if expected_lang and expected_lang.lower() not in text.lower():
            metrics["confidence_score"] *= 0.8  # penalize if expected language not found

    # Provider-specific heuristics (can be refactored to use OCR_METRICS for extensibility)
    provider_logic = {
        "Mistral": {
            "structure_score": 0.9 if any(tag in text.lower() for tag in ["#", "##", "table", "---"]) else 0.7,
            "format_retention": 0.9 if "```" in text or "*" in text else 0.6
        },
        "Google": {
            "structure_score": 0.8 if any(marker in text for marker in ["Title:", "Heading:", "List:"]) else 0.6,
            "format_retention": 0.8 if metrics["line_count"] > 5 else 0.6
        },
        "NVIDIA": {
            "structure_score": 0.95 if any(tag in text.lower() for tag in ["#", "##", "table", "-"]) else 0.75,
            "format_retention": 0.9 if any(marker in text for marker in ["```", "*", ">", "- "]) else 0.7
        },
        "Tesseract": {
            "structure_score": 0.5,
            "format_retention": 0.4
        },
        "PyMuPDF": {
            "structure_score": 0.8,
            "format_retention": 0.7
        },
        "PyPDF2": {
            "structure_score": 0.6,
            "format_retention": 0.5
        }
    }

    logic = provider_logic.get(provider)
    if logic:
        metrics["structure_score"] = logic["structure_score"]
        metrics["format_retention"] = logic["format_retention"]
    else:
        # Unknown provider: fallback to average values
        metrics["structure_score"] = 0.5
        metrics["format_retention"] = 0.5

    # Clamp all scores to [0, 1]
    for k in ["confidence_score", "structure_score", "format_retention"]:
        metrics[k] = clamp(metrics[k])

    # Calculate quality score using weights
    weights = OCR_PERFORMANCE_METRICS.get("weights", {"confidence": 0.4, "structure": 0.3, "format": 0.3})
    quality_score = (
        metrics["confidence_score"] * weights.get("confidence", 0.4) +
        metrics["structure_score"] * weights.get("structure", 0.3) +
        metrics["format_retention"] * weights.get("format", 0.3)
    )

    # Clamp final quality score
    quality_score = clamp(quality_score)

    return quality_score, metrics