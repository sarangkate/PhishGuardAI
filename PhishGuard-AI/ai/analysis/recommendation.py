from typing import Dict, List


def build_recommendation(classification: str, evidence: List[Dict]) -> Dict[str, object]:
    if classification == "Phishing":
        actions = [
            "Do not click suspicious links.",
            "Do not provide passwords, OTPs, or financial information.",
            "Verify the request using an independent official channel.",
            "Report the message as phishing if appropriate.",
        ]
    elif classification == "Suspicious":
        actions = [
            "Pause before interacting with the email.",
            "Verify the sender and destination independently.",
            "Avoid sharing sensitive information until verified.",
        ]
    else:
        actions = [
            "No major phishing indicators were detected by the current analysis.",
            "Continue normal security awareness for unexpected requests.",
        ]

    return {
        "classification": classification,
        "actions": actions,
        "basis": [item.get("title") for item in evidence],
    }
