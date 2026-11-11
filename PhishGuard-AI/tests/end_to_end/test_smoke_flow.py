def test_email_to_result_smoke_flow(monkeypatch):
    import ai.analysis.pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_content",
        lambda text: {
            "available": True,
            "phishing_probability": 0.05,
            "confidence": 0.95,
            "classification": "Legitimate",
        },
    )

    email = {
        "sender": "alerts@example.test",
        "reply_to": "alerts@example.test",
        "subject": "Please review this message",
        "body": "This is a controlled security test message.",
        "urls": [],
    }
    features = {
        "sender": {"findings": [], "positive_signals": []},
        "urls": {"findings": [], "positive_signals": []},
        "headers": {"findings": [], "positive_signals": []},
    }

    result = pipeline.analyze_email(email, features)
    assert result["classification"] == "Legitimate"
    assert "recommendation" in result
    assert "awareness" in result
    assert "trust_score" in result
