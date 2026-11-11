from typing import Any, Dict, List

SEVERITY_WEIGHTS = {"low": 5, "medium": 12, "high": 22, "critical": 30}


def _severity_weight(severity: str) -> int:
    return SEVERITY_WEIGHTS.get(str(severity).lower(), 0)


def _positive_credit(feature_data: Dict[str, Any]) -> int:
    credit = 0
    positives: List[Dict[str, Any]] = []
    for section in ("sender", "urls", "headers", "content", "attachments"):
        positives.extend(feature_data.get(section, {}).get("positive_signals", []))
    for item in positives:
        title = str(item.get("title", "")).lower()
        if "authentication passed" in title:
            credit += 6
        elif "sender and reply-to domains match" in title:
            credit += 8
        elif "no validated url indicators" in title:
            credit += 4
        elif "sender address available" in title:
            credit += 2
    return min(25, credit)


def build_decision(bert: Dict[str, Any], feature_data: Dict[str, Any]) -> Dict[str, Any]:
    evidence: List[Dict[str, Any]] = []
    ignored_context_ids = {
        "reply_to_mismatch",
        "header_reply_to_mismatch",
        "return_path_mismatch",
    }
    for section in ("sender", "urls", "headers", "content", "attachments"):
        evidence.extend(
            item for item in feature_data.get(section, {}).get("findings", [])
            if item.get("id") not in ignored_context_ids
        )

    rule_score = min(100, sum(_severity_weight(item.get("severity", "low")) for item in evidence))
    bert_probability = bert.get("phishing_probability")
    model_confidence = bert.get("confidence")
    positive_credit = _positive_credit(feature_data)

    # Concrete security evidence has the majority share. BERT is content
    # evidence only, which prevents newsletter/marketing language from being
    # treated as a standalone phishing verdict.
    if bert_probability is not None:
        raw_score = (0.45 * float(bert_probability) * 100) + (0.55 * rule_score) - positive_credit
        combined_score = round(raw_score)
    else:
        combined_score = rule_score - positive_credit

    # If there is no concrete security evidence, cap a content-only result at
    # Suspicious. This avoids labeling ordinary marketing mail as phishing.
    if not evidence and bert_probability is not None:
        combined_score = min(combined_score, 59)

    # Strong authentication passes should further dampen content-only false
    # positives, but never erase concrete high/critical findings.
    auth_passes = sum(
        1 for item in feature_data.get("headers", {}).get("positive_signals", [])
        if "authentication passed" in str(item.get("title", "")).lower()
    )
    if auth_passes >= 2 and not any(str(e.get("severity", "")).lower() in {"high", "critical"} for e in evidence):
        combined_score = max(0, combined_score - 10)

    combined_score = max(0, min(100, int(combined_score)))
    trust_score = 100 - combined_score

    if combined_score >= 70:
        classification = "Phishing"
    elif combined_score >= 35:
        classification = "Suspicious"
    else:
        classification = "Legitimate"

    warnings = [item.get("title", "") for item in evidence if item.get("title")]
    return {
        "classification": classification,
        "risk_score": combined_score,
        "trust_score": trust_score,
        "model_confidence": model_confidence,
        "bert_probability": bert_probability,
        "rule_score": rule_score,
        "positive_credit": positive_credit,
        "evidence": evidence,
        "warnings": warnings,
    }
