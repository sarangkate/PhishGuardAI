# Security Documentation

PhishGuardAI applies defense-in-depth controls:

- read-only Gmail scope
- in-memory Gmail access tokens
- validated bearer tokens and message IDs
- strict CORS/trusted hosts
- security response headers
- rate limiting
- DOMPurify email HTML sanitization
- blocked email-link navigation
- evidence-driven warnings
- separation of trust, risk and model confidence
- metadata-only analysis history
- privacy-conscious logging

See `docs/FINAL_SECURITY_REVIEW.md` for the release checklist and residual production risks.
