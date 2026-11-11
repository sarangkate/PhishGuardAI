from typing import Dict, List

AWARENESS = {
    "Urgent language": "Phishing messages often create urgency to encourage quick action.",
    "Reply-To mismatch": "Check the actual sender and Reply-To addresses instead of relying only on the display name.",
    "Insecure HTTP link": "Prefer secure destinations and verify the domain before opening a link.",
    "Shortened URL": "Shortened links hide the final destination, so verify them before clicking.",
    "IP-address URL": "A raw IP address as a destination deserves extra scrutiny in an email.",
    "Punycode hostname": "Internationalized domains can visually resemble trusted domains; inspect the actual hostname carefully.",
    "SPF authentication failed": "Email authentication failures can indicate that the message was not authorized by the sender's domain.",
    "DKIM authentication failed": "DKIM failures mean the message signature did not validate successfully.",
    "DMARC authentication failed": "DMARC failures can indicate an authentication or domain-alignment problem.",
}


def build_awareness(evidence: List[Dict]) -> List[Dict[str, str]]:
    cards = []
    for item in evidence:
        title = item.get("title", "")
        message = AWARENESS.get(title)
        if message:
            cards.append({"trigger": title, "message": message})
    return cards
