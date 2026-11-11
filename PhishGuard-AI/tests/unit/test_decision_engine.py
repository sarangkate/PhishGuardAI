from ai.decision.decision_engine import build_decision


def test_content_only_cannot_be_phishing_without_concrete_evidence():
    result = build_decision(
        {"phishing_probability": 1.0, "confidence": 1.0},
        {"sender": {}, "urls": {}, "headers": {}},
    )
    assert result["classification"] == "Suspicious"
    assert result["risk_score"] <= 59


def test_concrete_critical_evidence_can_drive_phishing():
    result = build_decision(
        {"phishing_probability": 0.9, "confidence": 0.9},
        {
            "sender": {},
            "urls": {"findings": [
                {"id": "credential_theft", "category": "url", "severity": "critical", "title": "Credential theft URL"},
                {"id": "malicious_login", "category": "url", "severity": "critical", "title": "Malicious login URL"}
            ]},
            "headers": {},
        },
    )
    assert result["classification"] == "Phishing"
    assert result["trust_score"] < 30
