from ai.analysis.awareness import build_awareness
from ai.analysis.explanation import explain
from ai.analysis.recommendation import build_recommendation
from ai.decision.decision_engine import build_decision


def test_decision_engine_combines_bert_and_evidence():
    evidence = [{
        "id": "url_ip",
        "category": "url",
        "title": "IP-address URL",
        "severity": "high",
        "evidence": "The URL host is 192.0.2.10.",
        "source": "url_analysis",
    }]
    result = build_decision(
        {"phishing_probability": 0.92, "confidence": 0.92},
        {"sender": {"findings": []}, "urls": {"findings": evidence}, "headers": {"findings": []}},
    )
    assert result["risk_score"] > 0
    assert result["evidence"] == evidence
    assert result["classification"] in {"Suspicious", "Phishing"}


def test_explanation_recommendation_and_awareness_are_evidence_based():
    evidence = [{
        "id": "reply_to_mismatch",
        "category": "reply_to",
        "title": "Reply-To mismatch",
        "severity": "medium",
        "evidence": "Sender domain differs from Reply-To domain.",
        "source": "sender_analysis",
    }]
    decision = {"classification": "Suspicious", "evidence": evidence}
    assert explain(decision)["items"][0]["source"] == "sender_analysis"
    assert build_recommendation("Suspicious", evidence)["actions"]
    assert build_awareness(evidence)[0]["trigger"] == "Reply-To mismatch"


def test_decision_engine_bert_only_is_not_automatic_phishing():
    result = build_decision(
        {"phishing_probability": 1.0, "confidence": 1.0},
        {"sender": {"findings": [], "positive_signals": []}, "urls": {"findings": [], "positive_signals": []}, "headers": {"findings": [], "positive_signals": []}},
    )
    assert result["risk_score"] == 45
    assert result["trust_score"] == 55
    assert result["classification"] == "Suspicious"


def test_decision_engine_positive_evidence_reduces_false_positive_risk():
    positives = [
        {"title": "Sender and Reply-To domains match"},
        {"title": "SPF authentication passed"},
        {"title": "DKIM authentication passed"},
        {"title": "DMARC authentication passed"},
        {"title": "No validated URL indicators detected"},
    ]
    result = build_decision(
        {"phishing_probability": 0.85, "confidence": 0.85},
        {
            "sender": {"findings": [], "positive_signals": positives[:1]},
            "urls": {"findings": [], "positive_signals": positives[4:]},
            "headers": {"findings": [], "positive_signals": positives[1:4]},
        },
    )
    assert result["risk_score"] <= 15
    assert result["trust_score"] >= 85
    assert result["classification"] == "Legitimate"


def test_decision_engine_keeps_model_confidence_separate_from_risk():
    result = build_decision(
        {"phishing_probability": 0.80, "confidence": 0.80},
        {"sender": {"findings": [], "positive_signals": []}, "urls": {"findings": [], "positive_signals": []}, "headers": {"findings": [], "positive_signals": []}},
    )
    assert result["risk_score"] == 36
    assert result["trust_score"] == 64
    assert result["model_confidence"] == 0.80
