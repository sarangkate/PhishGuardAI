# PhishGuardAI v0.4.0 — Evidence-Linked Investigation Cases

PhishGuardAI 0.4.0 adds an evidence-linked investigation case to the existing Gmail phishing analysis pipeline.

## Core workflow

Email → Evidence Extraction → Evidence Correlation → Investigation Case → Forensic Report → Integrity Verification

## Case contents

- Case ID
- Classification, risk and trust
- Evidence IDs linked to existing security findings
- Evidence category, severity, observed value and source
- Entities such as email, sender, domains, URLs, authentication results and earliest observed public IP
- Derived relationships between entities
- Evidence manifest SHA-256

## Forensic boundary

The case describes evidence available from the message and enrichment services. An observed IP can represent a mail server, relay, VPN, proxy, compromised host, cloud service or other infrastructure. The application does not claim that an IP identifies the attacker's physical identity.

## Report integrity

The forensic report endpoint returns the exact PDF bytes. The response exposes `X-PhishGuard-Report-SHA256`. `GET /api/emails/{message_id}/report/metadata` exposes the report fingerprint and evidence-manifest fingerprint. Re-hashing the downloaded PDF allows byte-level integrity comparison later.

A hash supports integrity comparison; it does not by itself establish authenticity or chain of custody.
