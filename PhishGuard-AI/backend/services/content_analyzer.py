import re
from typing import Any, Dict, List


def _finding(finding_id: str, title: str, severity: str, evidence: str) -> Dict[str, str]:
    return {
        "id": finding_id,
        "category": "content",
        "title": title,
        "severity": severity,
        "evidence": evidence,
        "source": "content_analysis",
    }


def _contains(patterns: List[str], text: str) -> bool:
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def analyze_content_signals(subject: str, body: str) -> Dict[str, Any]:
    """Detect general social-engineering patterns without sender/domain allowlists.

    The analyzer deliberately looks for *combinations and request patterns*, not a
    single hard-coded phishing sentence. Mild wording such as "review when
    convenient" should not create a warning by itself.
    """
    text = " ".join(f"{subject or ''}\n{body or ''}".split())
    lower = text.lower()
    findings: List[Dict[str, str]] = []
    positives: List[Dict[str, str]] = []

    urgency_patterns = [
        r"\burgent(?:ly)?\b", r"\bimmediately\b", r"\bact now\b",
        r"\bwithin\s+\d+\s*(?:minute|minutes|hour|hours|day|days)\b",
        r"\b(?:before|by)\s+(?:today|tonight|midnight)\b",
        r"\bfinal notice\b", r"\bexpires?\s+(?:today|soon|in)\b",
        r"\btime[- ]sensitive\b", r"\bwithout delay\b",
    ]
    threat_patterns = [
        r"\b(?:account|access|service|profile)\s+(?:will\s+be\s+|may\s+be\s+)?(?:suspend(?:ed)?|lock(?:ed)?|disable(?:d)?|terminate(?:d)?|close(?:d)?)\b",
        r"\b(?:suspend(?:ed)?|lock(?:ed)?|disable(?:d)?|terminate(?:d)?|close(?:d)?)\s+(?:your\s+)?(?:account|access|service|profile)\b",
        r"\bavoid\s+(?:suspension|closure|termination|penalty)\b",
        r"\blegal action\b", r"\bpenalt(?:y|ies)\b",
    ]
    credential_request_patterns = [
        r"\b(?:verify|confirm|provide|enter|submit|send|share|re-enter)\s+(?:your\s+)?(?:password|passcode|pin|otp|one[- ]time\s+(?:password|code)|verification\s+code|login\s+credentials?)\b",
        r"\b(?:password|passcode|pin|otp|verification\s+code|login\s+credentials?)\s+(?:is\s+)?(?:required|needed)\b",
    ]
    verification_patterns = [
        r"\b(?:verify|confirm|validate|authenticate)\s+(?:your\s+)?(?:account|identity|profile|login|payment|billing|email)\b",
        r"\b(?:account|identity|profile|login|payment|billing|email)\s+(?:verification|validation)\s+(?:is\s+)?required\b",
    ]
    sensitive_patterns = [
        r"\b(?:provide|enter|submit|send|share|confirm)\s+(?:your\s+)?(?:social security number|ssn|card number|credit card number|debit card number|cvv|cvc|bank account number|routing number|recovery code|backup code)\b",
    ]
    financial_patterns = [
        r"\b(?:wire|bank)\s+transfer\b", r"\bgift cards?\b", r"\bcrypto(?:currency)?\b",
        r"\b(?:send|transfer|pay|remit)\s+(?:the\s+)?(?:money|funds|payment)\b",
        r"\bchange\s+(?:the\s+)?(?:bank|payment)\s+(?:details|account)\b",
    ]
    action_link_patterns = [
        r"\bclick\s+(?:the\s+)?(?:link|button|below|here)\b",
        r"\bfollow\s+(?:the\s+)?link\b",
        r"\bopen\s+(?:the\s+)?link\b",
    ]

    urgency = _contains(urgency_patterns, lower)
    threat = _contains(threat_patterns, lower)
    credential_request = _contains(credential_request_patterns, lower)
    verification = _contains(verification_patterns, lower)
    sensitive_request = _contains(sensitive_patterns, lower)
    financial_request = _contains(financial_patterns, lower)
    action_link = _contains(action_link_patterns, lower)

    if urgency:
        findings.append(_finding(
            "content_urgency_pressure", "Urgency or deadline pressure", "medium",
            "The message uses language that pressures the recipient to act quickly.",
        ))
    if threat:
        findings.append(_finding(
            "content_threat_consequence", "Threat or account-consequence language", "medium",
            "The message threatens suspension, lockout, closure, a penalty, or a similar consequence.",
        ))
    if credential_request:
        findings.append(_finding(
            "content_credential_request", "Credential or verification-code request", "high",
            "The message asks the recipient to provide or verify a password, code, PIN, or login credential.",
        ))
    if verification:
        findings.append(_finding(
            "content_verification_request", "Account or identity verification request", "medium",
            "The message asks the recipient to verify or validate an account, identity, login, or payment detail.",
        ))
    if sensitive_request:
        findings.append(_finding(
            "content_sensitive_information_request", "Sensitive-information request", "critical",
            "The message asks for highly sensitive financial or identity information.",
        ))
    if financial_request:
        findings.append(_finding(
            "content_financial_request", "Unusual financial-action language", "high",
            "The message contains language associated with transfers, gift cards, payments, or financial-detail changes.",
        ))
    if action_link and (urgency or threat or credential_request or verification or sensitive_request or financial_request):
        findings.append(_finding(
            "content_pressured_link_action", "Pressured link action", "medium",
            "The message combines a request to follow a link with another social-engineering signal.",
        ))

    # A cluster is materially stronger than any isolated phrase and catches
    # cases such as urgency + account suspension + password verification.
    strong_signals = sum(bool(x) for x in (urgency, threat, credential_request, verification, sensitive_request, financial_request))
    if strong_signals >= 3 and (credential_request or sensitive_request or financial_request):
        findings.append(_finding(
            "content_social_engineering_cluster", "Multiple social-engineering signals", "high",
            "Several independent pressure/request patterns occur together in the same message.",
        ))

    if not findings:
        positives.append({
            "type": "content",
            "title": "No strong social-engineering language detected",
            "evidence": "No strong urgency, threat, credential, sensitive-data, or financial-request pattern was detected.",
            "source": "content_analysis",
        })

    return {
        "findings": findings,
        "positive_signals": positives,
        "signals": {
            "urgency": urgency,
            "threat": threat,
            "credential_request": credential_request,
            "verification_request": verification,
            "sensitive_information_request": sensitive_request,
            "financial_request": financial_request,
            "pressured_link_action": action_link,
        },
        "finding_count": len(findings),
    }
