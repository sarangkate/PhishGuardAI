import html
import re
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data and data.strip():
            self.parts.append(data)

    def get_text(self):
        return " ".join(self.parts)


def html_to_text(value: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(value or "")
        parser.close()
        return parser.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", value or "")


def clean_email_text(subject: str = "", body: str = "") -> str:
    subject = html.unescape(subject or "")
    body = html.unescape(body or "")
    if re.search(r"<\s*(html|body|div|p|br|table|a)\b", body, re.I):
        body = html_to_text(body)

    text = f"Subject: {subject}\n\n{body}".strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:20000].strip()
