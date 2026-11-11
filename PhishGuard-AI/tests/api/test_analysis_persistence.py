def test_analysis_route_persists_metadata_only(monkeypatch):
    from backend.routes import analysis

    monkeypatch.setattr(analysis, "_get_current_user_id", lambda _: ("token", 7))
    monkeypatch.setattr(
        analysis,
        "_analyze_gmail_message",
        lambda token, message_id: {
            "email": {
                "sender": "sender@example.com",
                "subject": "Security test",
                "date": "2026-09-05",
                "body": "secret body must not be persisted",
            },
            "features": {},
            "risk_analysis": {
                "classification": "Suspicious",
                "risk_score": 50,
                "trust_score": 50,
                "evidence": [
                    {"id": "http_url", "category": "url", "severity": "medium", "title": "Insecure HTTP link"}
                ],
            },
            "pipeline": {},
        },
    )
    monkeypatch.setattr(analysis, "save_analysis", lambda **kwargs: captured.update(kwargs))
    captured = {}

    result = analysis.analyze_gmail_message("abc123", "Bearer token")
    assert result["risk_analysis"]["classification"] == "Suspicious"
    assert captured["user_id"] == 7
    assert captured["message_id"] == "abc123"
    assert "body" not in captured
    assert "secret body" not in str(captured)
