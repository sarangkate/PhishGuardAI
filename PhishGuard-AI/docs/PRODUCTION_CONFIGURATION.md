# PhishGuardAI Environment Configuration

PhishGuardAI separates configuration by environment:

- Development: local Vite/FastAPI services and localhost URLs.
- Testing: isolated test configuration and synthetic fixtures.
- Production: HTTPS URLs, strict trusted hosts, production OAuth redirect URIs, production logging/monitoring and deployment-specific settings.

## Configuration rules
- Secrets and environment-specific values come from environment variables.
- Never commit OAuth secrets, Gmail tokens, passwords or production credentials.
- The Google OAuth client ID used by a browser is configuration, not a client secret; production redirect/origin configuration must still be restricted to approved domains.
- Production must use a strict `TRUSTED_HOSTS` value and a production `FRONTEND_URL`.
- Production must not use development localhost defaults.
- Production must use HTTPS.
