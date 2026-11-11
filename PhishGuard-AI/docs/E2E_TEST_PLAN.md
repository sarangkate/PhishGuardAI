# PhishGuardAI End-to-End Test Plan

The complete flow to verify is:

OPEN PHISHGUARDAI → LOGIN → GOOGLE AUTHENTICATION → GMAIL AUTHORIZATION → INBOX → OPEN EMAIL → RETRIEVE EMAIL → PARSE EMAIL → ANALYZE EMAIL → BERT → SENDER ANALYSIS → HEADER ANALYSIS → URL ANALYSIS → DECISION ENGINE → SECURITY RESULT → WARNING SIGNS → RECOMMENDATION → AWARENESS

## Acceptance checks
1. Login is visible and understandable.
2. Gmail authorization requests read-only access.
3. Inbox loads authorized messages.
4. Opening a message retrieves only the selected message.
5. Email HTML is rendered safely.
6. Analysis produces structured evidence.
7. BERT inference is available or reports a clear model error.
8. Sender/header/URL analysis completes without opening suspicious URLs.
9. Decision engine produces classification, risk/trust score and evidence.
10. UI displays only actual findings.
11. Recommendation and awareness match the classification/evidence.
12. Authentication, Gmail, backend and timeout failures show user-friendly errors.
