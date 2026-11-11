import threading
import time

from backend.services import gmail_service


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200
    def raise_for_status(self):
        return None
    def json(self):
        return self.payload


def test_message_metadata_fetches_preserve_list_order_with_concurrency(monkeypatch):
    active = 0
    max_active = 0
    lock = threading.Lock()

    def fake_get(url, headers=None, params=None, timeout=None):
        nonlocal active, max_active
        if url.endswith("/messages"):
            return FakeResponse({"messages": [{"id": str(i), "threadId": f"t{i}"} for i in range(6)]})
        message_id = url.rsplit("/", 1)[-1]
        with lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.02)
        with lock:
            active -= 1
        return FakeResponse({
            "id": message_id,
            "threadId": f"t{message_id}",
            "snippet": f"preview {message_id}",
            "payload": {"headers": [
                {"name": "From", "value": f"sender{message_id}@example.com"},
                {"name": "Subject", "value": f"Subject {message_id}"},
            ]},
        })

    monkeypatch.setattr(gmail_service.requests, "get", fake_get)
    result = gmail_service.get_gmail_messages("token", max_results=6)
    assert [m["id"] for m in result["messages"]] == [str(i) for i in range(6)]
    assert max_active > 1


def test_modify_gmail_message_star_adds_star(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured.update(url=url, json=json)
        return FakeResponse({"id": "abc123", "labelIds": ["STARRED"]})

    monkeypatch.setattr(gmail_service.requests, "post", fake_post)
    result = gmail_service.modify_gmail_message_star("token", "abc123", True)
    assert result == {"id": "abc123", "starred": True}
    assert captured["json"] == {"addLabelIds": ["STARRED"], "removeLabelIds": []}


def test_modify_gmail_message_star_removes_star(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured.update(url=url, json=json)
        return FakeResponse({"id": "abc123", "labelIds": []})

    monkeypatch.setattr(gmail_service.requests, "post", fake_post)
    result = gmail_service.modify_gmail_message_star("token", "abc123", False)
    assert result == {"id": "abc123", "starred": False}
    assert captured["json"] == {"addLabelIds": [], "removeLabelIds": ["STARRED"]}
