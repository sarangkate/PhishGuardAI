import requests
import base64
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser


GMAIL_API_BASE_URL = (
    "https://gmail.googleapis.com/gmail/v1/users/me"
)




class _LinkParser(HTMLParser):
    """Extract visible anchor text and actual href values without opening links."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._current_href = None
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        attributes = dict(attrs)
        self._current_href = attributes.get("href")
        self._text_parts = []

    def handle_data(self, data):
        if self._current_href is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() != "a" or self._current_href is None:
            return
        visible_text = " ".join(" ".join(self._text_parts).split())
        href = self._current_href.strip()
        if href:
            self.links.append({
                "visible_text": visible_text,
                "actual_url": href,
            })
        self._current_href = None
        self._text_parts = []


def extract_link_details(content: str):
    """Extract anchor metadata from HTML without making network requests."""
    if not content or not re.search(r"<a\b", content, re.I):
        return []

    parser = _LinkParser()
    try:
        parser.feed(content)
        return parser.links
    except Exception:
        return []


def _message_metadata(access_token: str, message: dict):
    """Fetch one message metadata record. Returns a resilient row on timeout."""
    message_id = message.get("id")
    if not message_id:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            f"{GMAIL_API_BASE_URL}/messages/{message_id}",
            headers=headers,
            params={
                "format": "metadata",
                "metadataHeaders": ["From", "To", "Subject", "Date"],
            },
            timeout=6,
        )
        response.raise_for_status()
        message_data = response.json()
        header_map = {
            str(item.get("name", "")).lower(): str(item.get("value", ""))
            for item in message_data.get("payload", {}).get("headers", [])
        }
        label_ids = set(message_data.get("labelIds", []) or [])
        return {
            "id": message_data.get("id", message_id),
            "threadId": message_data.get("threadId", message.get("threadId")),
            "sender": header_map.get("from", "Unknown sender"),
            "subject": header_map.get("subject", "(No subject)"),
            "date": header_map.get("date", ""),
            "snippet": message_data.get("snippet", ""),
            "unread": "UNREAD" in label_ids,
            "starred": "STARRED" in label_ids,
        }
    except requests.exceptions.Timeout:
        return {
            "id": message_id,
            "threadId": message.get("threadId"),
            "sender": "Unknown sender",
            "subject": "(Preview temporarily unavailable)",
            "date": "",
            "snippet": "",
            "unread": False,
            "starred": False,
        }


def get_gmail_messages(
    access_token: str,
    max_results: int = 25,
    page_token: str = None,
    label: str = "inbox",
):
    """Retrieve one Gmail mailbox page with bounded concurrent metadata loading.

    Gmail's list endpoint returns IDs only. The previous implementation fetched
    every metadata record sequentially, which could exceed the browser timeout
    when 25 messages were requested. This version preserves ordering while
    fetching a small bounded set concurrently.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    label_map = {
        "inbox": "INBOX",
        "starred": "STARRED",
        "snoozed": "SNOOZED",
        "sent": "SENT",
        "drafts": "DRAFT",
        "spam": "SPAM",
        "trash": "TRASH",
    }
    params = {"maxResults": max_results}
    if label in label_map:
        params["labelIds"] = label_map[label]
    if page_token:
        params["pageToken"] = page_token

    response = requests.get(
        f"{GMAIL_API_BASE_URL}/messages",
        headers=headers,
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    source_messages = data.get("messages", [])

    # Keep concurrency modest: enough to remove the N x latency bottleneck
    # without hammering Gmail or creating an unbounded number of threads.
    results_by_id = {}
    max_workers = min(8, max(1, len(source_messages)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(_message_metadata, access_token, message): message
            for message in source_messages
        }
        for future in as_completed(future_map):
            message = future_map[future]
            message_id = message.get("id")
            try:
                row = future.result()
            except requests.HTTPError:
                # Authentication/permission failures must reach the route so the
                # frontend can ask the user to reconnect rather than showing a
                # fake placeholder for every message.
                raise
            except Exception:
                row = {
                    "id": message_id,
                    "threadId": message.get("threadId"),
                    "sender": "Unknown sender",
                    "subject": "(Preview unavailable)",
                    "date": "",
                    "snippet": "",
                    "unread": False,
                    "starred": False,
                }
            if row and message_id:
                results_by_id[message_id] = row

    messages = [results_by_id[m.get("id")] for m in source_messages if m.get("id") in results_by_id]
    return {
        "messages": messages,
        "nextPageToken": data.get("nextPageToken"),
        "resultSizeEstimate": data.get("resultSizeEstimate", len(messages)),
    }


def get_all_gmail_messages(
    access_token: str,
    page_size: int = 100
):
    """
    Retrieve all Gmail inbox messages.

    Kept for compatibility, but DO NOT use this
    for the initial inbox loading because it can
    retrieve hundreds of messages.
    """

    all_messages = []

    page_token = None

    while True:

        data = get_gmail_messages(
            access_token=access_token,
            max_results=page_size,
            page_token=page_token
        )

        page_messages = data.get(
            "messages",
            []
        )

        all_messages.extend(
            page_messages
        )

        page_token = data.get(
            "nextPageToken"
        )

        if not page_token:
            break

    return {
        "messages": all_messages,

        "resultSizeEstimate": len(
            all_messages
        )
    }


def get_gmail_message(
    access_token: str,
    message_id: str
):
    """
    Retrieve one complete Gmail message.

    This is used only when the user opens
    an individual email.
    """

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        f"{GMAIL_API_BASE_URL}/messages/{message_id}",
        headers=headers,
        params={
            "format": "full"
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def extract_html_parts(payload: dict):
    """Collect HTML body parts for link extraction while keeping display text separate."""
    html_parts = []
    if payload.get("mimeType") == "text/html":
        data = payload.get("body", {}).get("data")
        if data:
            decoded = decode_gmail_body(data)
            if decoded:
                html_parts.append(decoded)
    for part in payload.get("parts", []) or []:
        html_parts.extend(extract_html_parts(part))
    return html_parts


def extract_attachment_metadata(payload: dict):
    """Collect attachment filenames/types/IDs only; attachment bytes are never downloaded."""
    attachments = []
    filename = str(payload.get("filename", "") or "").strip()
    body = payload.get("body", {}) or {}
    attachment_id = body.get("attachmentId")
    if filename or attachment_id:
        attachments.append({
            "filename": filename,
            "mime_type": str(payload.get("mimeType", "") or ""),
            "size": body.get("size"),
            "attachment_id": attachment_id,
        })
    for part in payload.get("parts", []) or []:
        attachments.extend(extract_attachment_metadata(part))
    return attachments


def extract_email_information(
    message_data: dict
):
    """
    Extract useful information from a complete
    Gmail message.
    """

    payload = message_data.get(
        "payload",
        {}
    )

    headers = payload.get(
        "headers",
        []
    )

    header_map = {}

    for header in headers:

        name = header.get(
            "name",
            ""
        ).lower()

        value = header.get(
            "value",
            ""
        )

        header_map[name] = value

    body = extract_email_body(
        payload
    )

    html_parts = extract_html_parts(payload)
    links = []
    for html_part in html_parts:
        links.extend(extract_link_details(html_part))
    # De-duplicate links while preserving order.
    unique_links = []
    seen_links = set()
    for link in links:
        key = (link.get("visible_text", ""), link.get("actual_url", ""))
        if key not in seen_links:
            seen_links.add(key)
            unique_links.append(link)
    links = unique_links

    urls = extract_urls(body)
    for html_part in html_parts:
        for html_url in extract_urls(html_part):
            if html_url not in urls:
                urls.append(html_url)
    for link in links:
        actual_url = link.get("actual_url", "")
        if actual_url.startswith(("http://", "https://")) and actual_url not in urls:
            urls.append(actual_url)
    attachments = extract_attachment_metadata(payload)

    return {
        "id": message_data.get(
            "id"
        ),

        "thread_id": message_data.get(
            "threadId"
        ),

        # Keep header values available to the server-side forensic pipeline.
        # Raw headers are not rendered directly as trusted HTML.
        "headers": [
            {"name": str(h.get("name", "")), "value": str(h.get("value", ""))}
            for h in headers
            if h.get("name")
        ],

        "authentication_results": header_map.get("authentication-results", ""),
        "received_spf": header_map.get("received-spf", ""),

        "snippet": message_data.get(
            "snippet",
            ""
        ),

        "sender": header_map.get(
            "from",
            ""
        ),

        "reply_to": header_map.get(
            "reply-to",
            ""
        ),

        "recipient": header_map.get(
            "to",
            ""
        ),

        "subject": header_map.get(
            "subject",
            ""
        ),

        "date": header_map.get(
            "date",
            ""
        ),

        "return_path": header_map.get(
            "return-path",
            ""
        ),

        "authentication_results": header_map.get(
            "authentication-results",
            ""
        ),

        "received_spf": header_map.get(
            "received-spf",
            ""
        ),

        "dkim_signature": header_map.get(
            "dkim-signature",
            ""
        ),

        "arc_authentication_results": header_map.get(
            "arc-authentication-results",
            ""
        ),

        "body": body,

        "urls": urls,

        "links": links,

        "attachments": attachments,
    }


def decode_gmail_body(
    data: str
):
    """
    Decode Gmail URL-safe Base64 encoded body.
    """

    if not data:
        return ""

    try:

        decoded = base64.urlsafe_b64decode(
            data + "=" * (
                -len(data) % 4
            )
        )

        return decoded.decode(
            "utf-8",
            errors="replace"
        )

    except Exception:

        return ""


def extract_email_body(
    payload: dict
):
    """
    Recursively extract text/plain or text/html
    content from a Gmail message payload.
    """

    mime_type = payload.get(
        "mimeType",
        ""
    )

    body_data = payload.get(
        "body",
        {}
    ).get(
        "data"
    )

    if body_data:

        if mime_type == "text/plain":

            return decode_gmail_body(
                body_data
            )

        if mime_type == "text/html":

            return decode_gmail_body(
                body_data
            )

    parts = payload.get(
        "parts",
        []
    )

    # Prefer plain text when available.
    for part in parts:

        if part.get(
            "mimeType"
        ) == "text/plain":

            body = extract_email_body(
                part
            )

            if body:
                return body

    # Otherwise use HTML.
    for part in parts:

        if part.get(
            "mimeType"
        ) == "text/html":

            body = extract_email_body(
                part
            )

            if body:
                return body

    # Finally recursively check remaining parts.
    for part in parts:

        body = extract_email_body(
            part
        )

        if body:
            return body

    return ""


def extract_urls(
    text: str
):
    """
    Extract HTTP and HTTPS URLs from email text.
    """

    if not text:
        return []

    url_pattern = r"""https?://[^\s<>"']+"""

    urls = re.findall(
        url_pattern,
        text
    )

    cleaned_urls = []

    for url in urls:

        url = url.rstrip(
            ".,);]}>"
        )

        if url not in cleaned_urls:

            cleaned_urls.append(
                url
            )

    return cleaned_urls

def modify_gmail_message_star(access_token: str, message_id: str, starred: bool):
    """Add or remove the Gmail STARRED label without touching message content."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {"addLabelIds": ["STARRED"] if starred else [], "removeLabelIds": [] if starred else ["STARRED"]}
    response = requests.post(
        f"{GMAIL_API_BASE_URL}/messages/{message_id}/modify",
        headers=headers,
        json=body,
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()
    return {"id": data.get("id", message_id), "starred": starred}
