import re


def get_header(headers, name):
    """
    Get a specific email header value.
    """

    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")

    return ""


def extract_urls(text):
    """
    Extract URLs from email body text.
    """

    if not text:
        return []

    url_pattern = r"https?://[^\s<>\"]+"

    urls = re.findall(url_pattern, text)

    return list(dict.fromkeys(urls))


def parse_gmail_message(message):
    """
    Convert a raw Gmail API message into
    a clean structure for phishing analysis.
    """

    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    sender = get_header(headers, "From")
    reply_to = get_header(headers, "Reply-To")
    recipient = get_header(headers, "To")
    subject = get_header(headers, "Subject")
    date = get_header(headers, "Date")

    authentication_results = get_header(
        headers,
        "Authentication-Results"
    )

    received_spf = get_header(
        headers,
        "Received-SPF"
    )

    dkim_signature = get_header(
        headers,
        "DKIM-Signature"
    )

    body = message.get("body", "")

    urls = extract_urls(body)

    return {
        "message_id": message.get("id", ""),
        "thread_id": message.get("thread_id", ""),
        "sender": sender,
        "reply_to": reply_to,
        "recipient": recipient,
        "subject": subject,
        "date": date,
        "authentication_results": authentication_results,
        "received_spf": received_spf,
        "dkim_signature": dkim_signature,
        "body": body,
        "urls": urls,
    }