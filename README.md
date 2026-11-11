# PhishGuardAI v0.4.0 — Forensic Email Security

PhishGuardAI combines Gmail access, phishing detection, forensic header analysis, approximate email-origin tracing, security evidence, recommendations, awareness guidance, and PDF reporting.

## Main flow
Google Login → Gmail authorization → Inbox → Open email → AI + security analysis → Origin trace → Export forensic PDF

## Features
- Google OAuth + Gmail API
- BERT-assisted phishing classification
- Sender / Reply-To / header / URL / attachment analysis
- SPF/DKIM/DMARC evidence when present in message headers
- Received-header chain extraction
- Earliest public IP observed in the available chain
- Optional approximate IP geolocation
- Evidence-based risk/trust scoring
- Security awareness recommendations
- Forensic PDF export
- Per-Google-account analysis history metadata
- Safe HTML rendering and no automatic opening of suspicious links

## Local setup
1. Copy `frontend/.env.example` to `frontend/.env` and set your Google OAuth Web Client ID.
2. Copy `backend/.env.example` to `backend/.env`.
3. Install backend requirements: `pip install -r backend/requirements.txt`
4. Start backend: `uvicorn backend.main:app --reload --port 8000`
5. In `frontend`, run `npm ci` then `npm run dev`.
6. Add `http://localhost:5173` to Authorized JavaScript origins in Google Cloud.
7. Add team Gmail accounts as OAuth Test Users while the app is in Testing mode.

## Important forensic limitation
An email's `Received` headers can expose public mail-server IP addresses, but an observed IP is not proof of the attacker's physical identity or location. Geolocation is approximate and should be treated as contextual evidence.

## Sharing
Do not commit `.env` files, OAuth secrets, tokens, or database files. Each teammate should create their own local `.env` from the examples. The Google OAuth client ID can be shared as configuration; the OAuth client secret must never be placed in frontend code.
