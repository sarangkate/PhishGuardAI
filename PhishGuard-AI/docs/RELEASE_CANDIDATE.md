# PhishGuardAI Release Candidate

This document defines the release gate for the 74-step roadmap. Code-side preparation is complete; external deployment and Google production verification must be completed before calling the application market-ready.

## Code-side gate
- Automated Python tests pass.
- Backend import and configuration validation pass.
- BERT inference is available.
- Frontend production build passes locally.
- No OAuth tokens, passwords, email bodies or raw MIME are persisted in analysis history.
- Suspicious links are never opened automatically.
- Trust score, model confidence and risk score remain distinct.

## External gate
- [ ] Production hosting account selected and configured
- [ ] Production HTTPS/domain active
- [ ] Production Google OAuth client configured
- [ ] Authorized origins/redirect URIs restricted
- [ ] Google verification completed if required
- [ ] Live Gmail authorization tested
- [ ] Live end-to-end flow tested
- [ ] Monitoring/error tracking configured
- [ ] Backup/restore plan for persistent database if SQLite is retained

## Market-ready decision
Do not label the release market-ready until every external gate is checked and the final live security/UX review is complete.
