import re
from typing import Dict, List


def _finding(finding_id: str, title: str, severity: str, evidence: str, source: str = "header_analysis", category: str = "header") -> Dict:
    return {"id": finding_id, "category": category, "title": title, "severity": severity, "evidence": evidence, "source": source}


def _auth_status(authentication_results: str, method: str):
    if not authentication_results:
        return "none"
    match = re.search(rf"\b{re.escape(method)}\s*=\s*(pass|fail|softfail|neutral|none|temperror|permerror)\b", authentication_results, flags=re.IGNORECASE)
    return match.group(1).lower() if match else "none"


def analyze_headers(parsed_email: dict) -> Dict:
    findings: List[Dict] = []
    positive_signals: List[Dict] = []
    authentication_results = parsed_email.get("authentication_results", "")
    received_spf = parsed_email.get("received_spf", "")
    sender = parsed_email.get("sender", "")
    reply_to = parsed_email.get("reply_to", "")

    spf = _auth_status(authentication_results, "spf")
    dkim = _auth_status(authentication_results, "dkim")
    dmarc = _auth_status(authentication_results, "dmarc")
    if spf == "none" and received_spf:
        if re.search(r"\bpass\b", received_spf, re.I):
            spf = "pass"
        elif re.search(r"\b(?:fail|softfail|neutral)\b", received_spf, re.I):
            spf = "fail"

    for method, status in (("SPF", spf), ("DKIM", dkim), ("DMARC", dmarc)):
        if status in {"fail", "softfail", "permerror", "temperror"}:
            findings.append(_finding(
                f"{method.lower()}_{status}",
                f"{method} authentication {status}",
                "high" if method == "DMARC" else "medium",
                f"{method} reported {status} by the available email authentication headers.",
            ))
        elif status == "pass":
            positive_signals.append({
                "type": "authentication",
                "title": f"{method} authentication passed",
                "evidence": f"{method} reported pass by the available email authentication headers.",
                "source": "header_analysis",
            })

    # Return-Path and Reply-To relationships are retained as metadata only.
    # They are common in legitimate mailing infrastructure and are not
    # sufficient on their own to create a phishing warning.
    return {
        "available": bool(authentication_results or received_spf or sender or reply_to),
        "authentication": {"spf": spf, "dkim": dkim, "dmarc": dmarc},
        "findings": findings,
        "positive_signals": positive_signals,
    }
