def test_history_endpoint_uses_authenticated_user(monkeypatch):
    from backend.routes import analysis

    monkeypatch.setattr(analysis, "_get_current_user_id", lambda _: ("token", 42))
    monkeypatch.setattr(analysis, "list_history", lambda user_id: [{"user_id": user_id, "classification": "Suspicious"}])

    result = analysis.analysis_history("Bearer test")
    assert result == {"items": [{"user_id": 42, "classification": "Suspicious"}]}


def test_delete_history_is_scoped_to_authenticated_user(monkeypatch):
    from backend.routes import analysis

    monkeypatch.setattr(analysis, "_get_current_user_id", lambda _: ("token", 99))
    monkeypatch.setattr(analysis, "clear_history", lambda user_id: 3 if user_id == 99 else 0)

    assert analysis.delete_analysis_history("Bearer test") == {"deleted": 3}
