import sqlite3


def test_analysis_metadata_is_owned_and_body_is_not_persisted(tmp_path, monkeypatch):
    import backend.db.database as database
    import backend.db.repository as repository

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(repository, "DB_PATH", db_path)

    user_id = repository.ensure_user("google-sub-123")
    repository.save_analysis(
        user_id=user_id,
        message_id="abc123",
        sender="sender@example.com",
        subject="Test message",
        message_date="2026-09-05",
        classification="Suspicious",
        risk_score=55,
        trust_score=45,
        evidence=[{"id": "http_url", "category": "url", "severity": "medium", "title": "Insecure HTTP link", "evidence": "http://example.test"}],
    )

    assert repository.list_history(user_id)[0]["message_id"] == "abc123"
    with sqlite3.connect(db_path) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(analyses)")}
        assert "body" not in columns
        assert "access_token" not in columns


def test_users_cannot_read_each_others_history(tmp_path, monkeypatch):
    import backend.db.database as database
    import backend.db.repository as repository

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(repository, "DB_PATH", db_path)

    first = repository.ensure_user("google-one")
    second = repository.ensure_user("google-two")
    repository.save_analysis(first, "message-one", "a@example.com", "One", "", "Legitimate", 10, 90, [])

    assert len(repository.list_history(first)) == 1
    assert repository.list_history(second) == []
