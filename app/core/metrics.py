from constants import OCR_METRICS, OCR_PERFORMANCE_METRICS
import re

class OCRMetricsAnalyzer:
    def __init__(self, provider):
        self.provider = provider
        
    def evaluate_quality(self, text, metadata=None):
        """Enhanced OCR quality evaluation with provider-specific metrics"""
        metrics = self._calculate_base_metrics(text)
        quality_score = self._calculate_quality_score(metrics)
        return quality_score, metrics
    
    def _calculate_base_metrics(self, text):
        """Calculate base text metrics"""
        metrics = {
            "word_count": len(text.split()),
            "line_count": len(text.splitlines()),
            "char_count": len(text),
            "avg_line_length": len(text) / max(len(text.splitlines()), 1),
            "confidence_score": OCR_PERFORMANCE_METRICS["providers"][self.provider]["base_conf"],
            "structure_score": self._calculate_structure_score(text),
            "format_retention": self._calculate_format_retention(text)
        }
        return metrics
    
    def _calculate_structure_score(self, text):
        """Calculate structure preservation score"""
        structure_indicators = {
            "headers": len(re.findall(r'^#+\s+.+$', text, re.MULTILINE)),
            "lists": len(re.findall(r'^\s*[-*]\s+.+$', text, re.MULTILINE)),
            "tables": len(re.findall(r'\|.*\|', text, re.MULTILINE)),
            "sections": len(re.findall(r'^={3,}|-{3,}$', text, re.MULTILINE))
        }
        
        base_score = OCR_PERFORMANCE_METRICS["providers"][self.provider]["base_conf"]
        bonus = sum(1 for count in structure_indicators.values() if count > 0) * 0.05
        return min(base_score + bonus, 1.0)
    
    def _calculate_format_retention(self, text):
        """Calculate format retention score"""
        format_indicators = {
            "markdown": len(re.findall(r'[*_`].*[*_`]', text)),
            "whitespace": text.count('\n\n'),
            "indentation": len(re.findall(r'^\s+\S', text, re.MULTILINE))
        }
        
        base_score = OCR_PERFORMANCE_METRICS["providers"][self.provider]["base_conf"]
        bonus = sum(1 for count in format_indicators.values() if count > 0) * 0.05
        return min(base_score + bonus, 1.0)
    
    def _calculate_quality_score(self, metrics):
        """Calculate overall quality score"""
        weights = OCR_PERFORMANCE_METRICS["weights"]
        return (
            metrics["confidence_score"] * weights["confidence"] +
            metrics["structure_score"] * weights["structure"] +
            metrics["format_retention"] * weights["format"]
        )
