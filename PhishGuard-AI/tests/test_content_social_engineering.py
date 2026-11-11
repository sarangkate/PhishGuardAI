from backend.services.content_analyzer import analyze_content_signals
from backend.services.feature_extractor import extract_features
from ai.decision.decision_engine import build_decision


def _decision(subject, body, bert_probability=None):
    features = extract_features({
        "id": "case",
        "subject": subject,
        "body": body,
        "sender": "Example <alerts@example.com>",
        "reply_to": "alerts@example.com",
        "urls": [],
        "links": [],
        "authentication_results": "",
        "received_spf": "",
        "return_path": "",
    })
    bert = {"phishing_probability": bert_probability, "confidence": bert_probability} if bert_probability is not None else {}
    return features, build_decision(bert, features)


def test_neutral_account_review_does_not_create_content_warning():
    result = analyze_content_signals(
        "Account review",
        "Your account requires attention. Please review your account when convenient. Thank you.",
    )
    assert result["findings"] == []


def test_urgency_password_suspension_is_detected_without_exact_sentence_hardcoding():
    features, decision = _decision(
        "Action required",
        "Access may be suspended within 24 hours. Confirm your password immediately to keep the account active.",
        0.70,
    )
    ids = {item["id"] for item in features["content"]["findings"]}
    assert "content_urgency_pressure" in ids
    assert "content_threat_consequence" in ids
    assert "content_credential_request" in ids
    assert "content_social_engineering_cluster" in ids
    assert decision["classification"] in {"Suspicious", "Phishing"}
    assert decision["risk_score"] >= 35


def test_sensitive_information_request_is_high_risk_even_without_url():
    features, decision = _decision(
        "Identity check",
        "Please provide your social security number and credit card number to validate your identity.",
        0.55,
    )
    ids = {item["id"] for item in features["content"]["findings"]}
    assert "content_sensitive_information_request" in ids
    assert decision["classification"] in {"Suspicious", "Phishing"}


def test_legitimate_password_reset_notice_without_credential_submission_is_not_credential_request():
    result = analyze_content_signals(
        "Password changed",
        "Your password was changed successfully. If you did not make this change, visit the official account settings page.",
    )
    ids = {item["id"] for item in result["findings"]}
    assert "content_credential_request" not in ids
