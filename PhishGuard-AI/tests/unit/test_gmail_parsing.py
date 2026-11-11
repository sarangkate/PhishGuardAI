import base64
from backend.services.gmail_service import extract_email_information


def enc(value):
    return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")


def test_html_href_is_analyzed_even_when_plain_text_is_preferred_for_display():
    message = {
        "id": "m1",
        "threadId": "t1",
        "payload": {
            "mimeType": "multipart/alternative",
            "headers": [{"name": "From", "value": "sender@example.com"}],
            "parts": [
                {"mimeType": "text/plain", "body": {"data": enc("Hello, review your account")}},
                {"mimeType": "text/html", "body": {"data": enc('<p>Hello <a href="http://192.0.2.10/login">https://accounts.example.com</a></p>')}},
            ],
        },
    }
    parsed = extract_email_information(message)
    assert parsed["body"] == "Hello, review your account"
    assert "http://192.0.2.10/login" in parsed["urls"]
    assert parsed["links"][0]["visible_text"] == "https://accounts.example.com"


def test_attachment_metadata_is_collected_without_bytes():
    message = {
        "id": "m2",
        "threadId": "t2",
        "payload": {
            "mimeType": "multipart/mixed",
            "headers": [],
            "parts": [
                {"mimeType": "text/plain", "body": {"data": enc("See attachment")}},
                {"mimeType": "application/pdf", "filename": "invoice.pdf", "body": {"attachmentId": "a1", "size": 1234}},
            ],
        },
    }
    parsed = extract_email_information(message)
    assert parsed["attachments"] == [{"filename": "invoice.pdf", "mime_type": "application/pdf", "size": 1234, "attachment_id": "a1"}]
