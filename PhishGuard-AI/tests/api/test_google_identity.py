import requests


def test_google_identity_requires_subject(monkeypatch):
    from backend.services import google_identity

    class Response:
        status_code = 200
        def json(self):
            return {"email": "test@example.com"}

    monkeypatch.setattr(requests, "get", lambda *a, **k: Response())
    try:
        google_identity.get_google_subject("token")
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
    else:
        raise AssertionError("Missing Google subject must be rejected")
