import ipaddress
import re
from html import unescape
from urllib.parse import unquote, urlparse

try:
    from backend.services.header_analyzer import analyze_headers
    from backend.services.content_analyzer import analyze_content_signals
    from backend.services.attachment_analyzer import analyze_attachments
except ModuleNotFoundError:
    from .header_analyzer import analyze_headers
    from .content_analyzer import analyze_content_signals
    from .attachment_analyzer import analyze_attachments

SHORTENED_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "cutt.ly", "rb.gy", "shorturl.at",
}

# These are used only to recognize common email tracking/redirect wrappers.
# They are NOT treated as trusted domains. Their embedded destination is what
# gets security-scored.
TRACKING_HOST_HINTS = {
    "click.", "clk.", "track.", "tracking.", "links.", "link.",
    "clicks.", "email.", "emails.", "mail.", "sendgrid.net",
    "mailchimp.", "list-manage.com", "hubspot.", "braze.",
}

# Generic redirect/deep-link infrastructure. These are not trusted domains;
# they are simply recognized as link wrappers so the wrapper itself is not
# mistaken for the final destination.
REDIRECT_INFRASTRUCTURE_SUFFIXES = {
    "onelink.me", "app.link", "lnk.to",
}

SUSPICIOUS_URL_CHARS = re.compile(r"[<>\[\]\\\"']")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.I)
EMBEDDED_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.I)


def _finding(finding_id, category, title, severity, evidence, source):
    return {
        "id": finding_id,
        "category": category,
        "title": title,
        "severity": severity,
        "evidence": evidence,
        "source": source,
    }


def extract_email_address(sender):
    match = EMAIL_PATTERN.search(sender or "")
    return match.group(0).lower() if match else ""


def get_domain(email_address):
    return email_address.split("@", 1)[1].lower() if "@" in email_address else ""


def _extract_display_name(sender):
    if not sender:
        return ""
    match = re.match(r'\s*(.*?)\s*<[^>]+>\s*$', sender)
    return match.group(1).strip().strip('"') if match else ""


def analyze_sender(sender, reply_to):
    sender_email = extract_email_address(sender)
    reply_email = extract_email_address(reply_to)
    sender_domain = get_domain(sender_email)
    reply_domain = get_domain(reply_email)
    display_name = _extract_display_name(sender)

    mismatch = bool(sender_domain and reply_domain and sender_domain != reply_domain)
    relationship = "not_available"
    if sender_domain and reply_domain:
        relationship = "exact_match" if sender_domain == reply_domain else "different_domains"

    findings = []
    positive_signals = []

    if sender_email:
        positive_signals.append({
            "type": "sender",
            "title": "Sender address available",
            "evidence": sender_email,
            "source": "sender_analysis",
        })
    else:
        findings.append(_finding(
            "missing_sender_address", "sender", "Sender address unavailable",
            "low", "No valid sender email address could be extracted from the available header.",
            "sender_analysis",
        ))

    # A Reply-To difference is context, not proof of phishing. Keep it as
    # structured evidence for diagnostics/tests, while the decision engine and
    # UI explicitly treat it as non-warning context. Many legitimate marketing
    # systems use separate reply infrastructure.
    if mismatch:
        findings.append(_finding(
            "reply_to_mismatch", "reply_to", "Reply-To mismatch", "low",
            f"Sender domain is {sender_domain}, while Reply-To domain is {reply_domain}.",
            "sender_analysis",
        ))
    elif sender_domain and reply_domain and sender_domain == reply_domain:
        positive_signals.append({
            "type": "reply_to",
            "title": "Sender and Reply-To domains match",
            "evidence": f"Both use {sender_domain}.",
            "source": "sender_analysis",
        })

    return {
        "sender_email": sender_email,
        "sender_domain": sender_domain,
        "display_name": display_name,
        "reply_to_email": reply_email,
        "reply_to_domain": reply_domain,
        "reply_to_mismatch": mismatch,
        "domain_relationship": relationship,
        "has_reply_to": bool(reply_email),
        "status": "review_context" if mismatch else "no_mismatch_detected",
        "findings": findings,
        "positive_signals": positive_signals,
    }


def _is_ip_host(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _is_tracking_wrapper(host: str, url: str) -> bool:
    host = (host or "").lower().rstrip(".")
    lower = (url or "").lower()
    return (
        any(hint in host for hint in TRACKING_HOST_HINTS)
        or any(host == suffix or host.endswith("." + suffix) for suffix in REDIRECT_INFRASTRUCTURE_SUFFIXES)
        or bool(re.search(r"/(?:cl0|click|redirect|track|r)/", lower))
    )


def _extract_embedded_destination(url: str):
    """Return an embedded final http(s) URL from a tracking/redirect URL."""
    decoded = unquote(unescape(url))
    first = re.search(r"https?://", decoded, re.I)
    if not first:
        return None
    remainder = decoded[first.end():]
    second = re.search(r"https?://", remainder, re.I)
    if not second:
        return None
    destination = remainder[second.start():]
    return destination.rstrip(".,;:!?)\\\"")




def _rough_base_domain(host: str) -> str:
    labels = [part for part in (host or "").lower().strip(".").split(".") if part]
    if len(labels) <= 2:
        return ".".join(labels)
    # Common country-code second-level domains; enough for display-vs-target comparison
    # without introducing a network dependency or an allowlist of trusted brands.
    if labels[-1] in {"uk", "au", "nz", "jp", "za", "in"} and labels[-2] in {"co", "com", "org", "net", "ac", "gov"}:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def analyze_visible_link_mismatches(links):
    findings = []
    for index, link in enumerate(links or [], start=1):
        visible = str(link.get("visible_text", "") or "").strip()
        actual = str(link.get("actual_url", "") or "").strip()
        if not actual.startswith(("http://", "https://")):
            continue
        actual_target = _extract_embedded_destination(actual) if _is_tracking_wrapper((urlparse(actual).hostname or ""), actual) else None
        actual_host = (urlparse(actual_target or actual).hostname or "").lower()
        visible_host = ""
        if visible.startswith(("http://", "https://")):
            visible_host = (urlparse(visible).hostname or "").lower()
        else:
            match = re.search(r"\b(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)\b", visible, re.I)
            if match:
                visible_host = match.group(1).lower().rstrip(".,;:!?)")
        if visible_host and actual_host and _rough_base_domain(visible_host) != _rough_base_domain(actual_host):
            findings.append(_finding(
                f"link_{index}_display_mismatch", "url", "Displayed link does not match destination", "high",
                f"The visible link suggests {visible_host}, but the destination resolves to {actual_host}.",
                "url_analysis",
            ))
    return findings


def analyze_urls(urls, links=None):
    links = links or []
    findings = []
    positive_signals = []
    analyzed = []
    seen_destinations = set()
    wrapper_count = 0

    findings.extend(analyze_visible_link_mismatches(links))
    unique_urls = list(dict.fromkeys(urls or []))

    for index, raw_url in enumerate(unique_urls, start=1):
        try:
            parsed_raw = urlparse(raw_url)
            raw_host = (parsed_raw.hostname or "").lower()
            if not parsed_raw.scheme or not raw_host:
                continue

            is_markup_reference = raw_host in {"www.w3.org", "w3.org"}
            tracking_wrapper = _is_tracking_wrapper(raw_host, raw_url)
            destination = _extract_embedded_destination(raw_url) if tracking_wrapper else None

            if destination:
                wrapper_count += 1
                target = destination
                parsed = urlparse(target)
                host = (parsed.hostname or "").lower()
                domain = host
                if domain in seen_destinations:
                    continue
                seen_destinations.add(domain)
                representation = "tracking_redirect"
            elif tracking_wrapper:
                # Wrapper/deep-link infrastructure without an embedded URL is
                # still useful metadata, but there is no final destination to
                # security-score. Do not manufacture a warning from the wrapper.
                wrapper_count += 1
                target = raw_url
                parsed = parsed_raw
                host = raw_host
                domain = host
                representation = "tracking_wrapper"
                if domain in seen_destinations:
                    continue
                seen_destinations.add(domain)
            else:
                target = raw_url
                parsed = parsed_raw
                host = raw_host
                domain = host
                representation = "direct"
                if domain in seen_destinations:
                    continue
                seen_destinations.add(domain)

            indicators = []

            # URL length is metadata only. It never creates a finding.
            if len(target) > 150:
                indicators.append("Long URL (metadata only)")

            if representation in {"direct", "tracking_redirect"} and parsed.scheme.lower() == "http" and not is_markup_reference:
                indicators.append("Uses HTTP instead of HTTPS")
                findings.append(_finding(
                    f"url_{index}_http", "url", "Insecure HTTP link", "medium",
                    f"The analyzed destination uses HTTP instead of HTTPS: {host}",
                    "url_analysis",
                ))

            if representation in {"direct", "tracking_redirect"} and domain in SHORTENED_DOMAINS:
                indicators.append("Known URL-shortening domain")
                findings.append(_finding(
                    f"url_{index}_shortened", "url", "Shortened URL", "medium",
                    f"The analyzed destination uses the URL shortener domain {domain}.",
                    "url_analysis",
                ))

            if representation in {"direct", "tracking_redirect"} and _is_ip_host(host):
                indicators.append("Uses an IP address as the host")
                findings.append(_finding(
                    f"url_{index}_ip", "url", "IP-address URL", "high",
                    f"The analyzed URL host is the IP address {host}.",
                    "url_analysis",
                ))

            if representation in {"direct", "tracking_redirect"} and "xn--" in host:
                indicators.append("Internationalized/punycode hostname")
                findings.append(_finding(
                    f"url_{index}_punycode", "url", "Punycode hostname", "medium",
                    f"The analyzed hostname contains the punycode marker xn--: {host}.",
                    "url_analysis",
                ))

            if representation in {"direct", "tracking_redirect"} and (parsed.username or parsed.password):
                indicators.append("Contains URL user information")
                findings.append(_finding(
                    f"url_{index}_userinfo", "url", "URL contains user information", "high",
                    "The analyzed URL contains credentials/user information before the host.",
                    "url_analysis",
                ))

            # Encoded tracking parameters are normal in redirect URLs and are
            # not treated as suspicious characters. For direct destinations,
            # only clearly unusual raw delimiters are retained at low severity.
            if representation == "direct" and SUSPICIOUS_URL_CHARS.search(target):
                indicators.append("Contains unusual URL characters")
                findings.append(_finding(
                    f"url_{index}_characters", "url", "Unusual URL characters", "low",
                    f"The direct destination contains unusual URL characters: {target}",
                    "url_analysis",
                ))

            labels = [part for part in host.split(".") if part]
            if len(labels) >= 4 and representation == "direct" and not _is_ip_host(host):
                indicators.append("Multiple subdomain levels")
                findings.append(_finding(
                    f"url_{index}_subdomains", "url", "Multiple subdomain levels", "low",
                    f"The destination hostname contains {len(labels) - 2} subdomain labels: {host}",
                    "url_analysis",
                ))

            analyzed.append({
                "url": target,
                "original_url": raw_url,
                "domain": domain,
                "scheme": parsed.scheme.lower(),
                "path": parsed.path,
                "query_present": bool(parsed.query),
                "representation": representation,
                "tracking_wrapper": bool(tracking_wrapper),
                "indicators": indicators,
            })
        except ValueError:
            findings.append(_finding(
                f"url_{index}_invalid", "url", "Invalid URL structure", "medium",
                f"The extracted value could not be parsed as a valid URL.",
                "url_analysis",
            ))

    if not findings and unique_urls:
        positive_signals.append({
            "type": "url",
            "title": "No validated URL indicators detected",
            "evidence": f"Analyzed {len(analyzed)} meaningful destination(s); tracking/redirect wrappers were normalized where possible.",
            "source": "url_analysis",
        })

    return {
        "url_count": len(unique_urls),
        "meaningful_destination_count": len(analyzed),
        "tracking_wrapper_count": wrapper_count,
        "links": links,
        "analyzed_urls": analyzed,
        "findings": findings,
        "positive_signals": positive_signals,
    }


def analyze_authentication(authentication_results, received_spf):
    authentication_results = (authentication_results or "").lower()
    received_spf = (received_spf or "").lower()
    return {
        "spf_pass": "spf=pass" in authentication_results or ("pass" in received_spf if received_spf else False),
        "spf_fail": bool(re.search(r"spf=(?:fail|softfail|neutral)", authentication_results)),
        "dkim_pass": "dkim=pass" in authentication_results,
        "dkim_fail": bool(re.search(r"dkim=(?:fail|neutral)", authentication_results)),
        "dmarc_pass": "dmarc=pass" in authentication_results,
        "dmarc_fail": bool(re.search(r"dmarc=(?:fail|neutral)", authentication_results)),
    }


def extract_features(parsed_email):
    subject = parsed_email.get("subject", "")
    body = parsed_email.get("body", "")
    combined_text = f"{subject}\n{body}".strip()
    sender_analysis = analyze_sender(parsed_email.get("sender", ""), parsed_email.get("reply_to", ""))
    url_analysis = analyze_urls(parsed_email.get("urls", []), parsed_email.get("links", []))
    header_analysis = analyze_headers(parsed_email)
    content_analysis = analyze_content_signals(subject, body)
    attachment_analysis = analyze_attachments(parsed_email.get("attachments", []))
    return {
        "message_id": parsed_email.get("message_id", parsed_email.get("id", "")),
        "subject": subject,
        "text": {"body_length": len(body), "combined_length": len(combined_text)},
        "sender": sender_analysis,
        "urls": url_analysis,
        "authentication": header_analysis["authentication"],
        "headers": header_analysis,
        "content": content_analysis,
        "attachments": attachment_analysis,
    }
