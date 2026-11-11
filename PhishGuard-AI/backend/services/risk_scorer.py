def calculate_risk_score(features):
    """
    Calculate a phishing risk score from extracted email features.

    Score range: 0 - 100
    """

    score = 0
    warning_signs = []
    positive_signals = []

    # --------------------------------------------------
    # Sender analysis
    # --------------------------------------------------

    sender = features.get("sender", {})

    if sender.get("reply_to_mismatch"):
        score += 25

        warning_signs.append(
            "Sender and Reply-To domains do not match"
        )

    else:
        positive_signals.append(
            "No Sender and Reply-To mismatch detected"
        )

    # --------------------------------------------------
    # URL analysis
    # --------------------------------------------------

    urls = features.get("urls", {})

    if urls.get("shortened_url_count", 0) > 0:
        score += 20

        warning_signs.append(
            "Shortened URL detected"
        )

    if urls.get("insecure_url_count", 0) > 0:
        score += 20

        warning_signs.append(
            "Insecure HTTP URL detected"
        )

    if urls.get("excessive_subdomain_count", 0) > 0:
        score += 15

        warning_signs.append(
            "Excessive subdomains detected"
        )

    if urls.get("long_url_count", 0) > 0:
        score += 5

        warning_signs.append(
            "Long URL detected"
        )

    if urls.get("url_count", 0) == 0:
        positive_signals.append(
            "No URLs detected in the email"
        )

    # --------------------------------------------------
    # Language analysis
    # --------------------------------------------------

    language = features.get("language", {})

    urgency_count = language.get(
        "urgency_count",
        0
    )

    financial_count = language.get(
        "financial_count",
        0
    )

    credential_count = language.get(
        "credential_count",
        0
    )

    if urgency_count > 0:
        score += min(
            urgency_count * 5,
            15
        )

        warning_signs.append(
            "Urgency or pressure-related language detected"
        )

    if financial_count > 0:
        score += min(
            financial_count * 5,
            15
        )

        warning_signs.append(
            "Financial-related language detected"
        )

    if credential_count > 0:
        score += min(
            credential_count * 7,
            20
        )

        warning_signs.append(
            "Credential-related language detected"
        )

    # --------------------------------------------------
    # Authentication analysis
    # --------------------------------------------------

    authentication = features.get(
        "authentication",
        {}
    )

    spf_pass = authentication.get(
        "spf_pass",
        False
    )

    dkim_pass = authentication.get(
        "dkim_pass",
        False
    )

    dmarc_pass = authentication.get(
        "dmarc_pass",
        False
    )

    spf_fail = authentication.get(
        "spf_fail",
        False
    )

    dkim_fail = authentication.get(
        "dkim_fail",
        False
    )

    dmarc_fail = authentication.get(
        "dmarc_fail",
        False
    )

    if spf_fail:
        score += 15

        warning_signs.append(
            "SPF authentication failed"
        )

    elif spf_pass:
        positive_signals.append(
            "SPF authentication passed"
        )

    if dkim_fail:
        score += 15

        warning_signs.append(
            "DKIM authentication failed"
        )

    elif dkim_pass:
        positive_signals.append(
            "DKIM authentication passed"
        )

    if dmarc_fail:
        score += 20

        warning_signs.append(
            "DMARC authentication failed"
        )

    elif dmarc_pass:
        positive_signals.append(
            "DMARC authentication passed"
        )

    # --------------------------------------------------
    # Keep score between 0 and 100
    # --------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------
    # Classification
    # --------------------------------------------------

    if score >= 60:
        classification = "Phishing"

        recommended_action = (
            "Do not click links or provide sensitive "
            "information. Verify the sender through "
            "an official source."
        )

    elif score >= 30:
        classification = "Suspicious"

        recommended_action = (
            "Be cautious. Avoid clicking links or "
            "sharing sensitive information until "
            "the email is verified."
        )

    else:
        classification = "Legitimate"

        recommended_action = (
            "No major phishing indicators were detected. "
            "Still verify unexpected requests before "
            "taking action."
        )

    return {
        "risk_score": score,
        "classification": classification,
        "warning_signs": warning_signs,
        "positive_signals": positive_signals,
        "recommended_action": recommended_action,
    }