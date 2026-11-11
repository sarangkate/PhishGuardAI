from typing import Any, Dict

from ai.analysis.awareness import build_awareness
from ai.analysis.bert_analyzer import analyze_content
from ai.analysis.explanation import explain
from ai.analysis.recommendation import build_recommendation
from ai.decision.decision_engine import build_decision
from ai.preprocessing.email_cleaner import clean_email_text
from ai.schemas.analysis_result import analysis_result


def analyze_email(parsed_email: Dict[str, Any], feature_data: Dict[str, Any]) -> Dict[str, Any]:
    text = clean_email_text(parsed_email.get("subject", ""), parsed_email.get("body", ""))
    bert = analyze_content(text)
    decision = build_decision(bert, feature_data)
    explanation = explain(decision)
    recommendation = build_recommendation(decision["classification"], decision["evidence"])
    awareness = build_awareness(decision["evidence"])

    result = analysis_result(
        classification=decision["classification"],
        risk_score=decision["risk_score"],
        model_confidence=decision["model_confidence"],
        evidence=decision["evidence"],
        warnings=decision["warnings"],
        recommendation=recommendation,
        awareness=awareness,
    )
    result["recommended_action"] = " ".join(recommendation["actions"])
    result["positive_signals"] = (
        feature_data.get("sender", {}).get("positive_signals", [])
        + feature_data.get("urls", {}).get("positive_signals", [])
        + feature_data.get("headers", {}).get("positive_signals", [])
    )

    return result | {
        "bert": bert,
        "explanation": explanation,
        "preprocessed_text_length": len(text),
        "rule_score": decision["rule_score"],
        "trust_score": decision["trust_score"],
    }
