from typing import Any, Dict, List, Optional


def finding(finding_id: str, category: str, title: str, severity: str, evidence: str, source: str) -> Dict[str, Any]:
    return {
        "id": finding_id,
        "category": category,
        "title": title,
        "severity": severity,
        "evidence": evidence,
        "source": source,
    }


def analysis_result(
    classification: str,
    risk_score: int,
    model_confidence: Optional[float],
    evidence: List[Dict[str, Any]],
    warnings: List[str],
    recommendation: Dict[str, Any],
    awareness: List[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "classification": classification,
        "risk_score": risk_score,
        "model_confidence": model_confidence,
        "evidence": evidence,
        "warnings": warnings,
        "recommendation": recommendation,
        "awareness": awareness,
    }
