from typing import Dict, Any

from ai.models.bert_model import MODEL_NAME, predict_text


def analyze_content(text: str) -> Dict[str, Any]:
    try:
        result = predict_text(text)
        result["source"] = "bert_content_analysis"
        return result
    except Exception as exc:
        return {
            "available": False,
            "model": MODEL_NAME,
            "source": "bert_content_analysis",
            "error": str(exc),
            "classification": None,
            "phishing_probability": None,
            "confidence": None,
        }
