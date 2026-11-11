# PhishGuardAI v0.4.0 — Forensic Analysis

## Three jobs
1. Detect phishing using BERT plus structured security evidence.
2. Trace the observable email path using Received headers and identify the earliest public IP available.
3. Export a forensic PDF containing classification, scores, evidence, authentication results, origin context and recommendations.

## Important limitation
A public IP found in a Received header identifies an observed mail-server/network endpoint, not necessarily the attacker. IP geolocation is approximate and may identify infrastructure rather than a person's physical location.

## Privacy
The report is generated on demand. Analysis history continues to store metadata only; raw email bodies are not written to the history database.
