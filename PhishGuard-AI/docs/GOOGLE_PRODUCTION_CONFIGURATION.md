# Step 56 — Google Production Configuration

This document is a provider-neutral production checklist. It does not claim that Google Cloud Console verification has been completed; those actions must be completed in the project's Google account before release.

## Production OAuth checklist

1. Create/select the production Google OAuth client.
2. Register only the final production web origin(s).
3. Register the exact production redirect URI(s) required by the selected OAuth flow.
4. Confirm the OAuth consent screen contains accurate application name, support contact, authorized domain(s), privacy policy and terms information where applicable.
5. Review the Gmail scope. PhishGuardAI currently requests `https://www.googleapis.com/auth/gmail.readonly` because it only reads messages for analysis.
6. Complete any Google verification/review requirements applicable to the chosen Gmail scope and publishing status.
7. Confirm the privacy documentation accurately describes Gmail access and metadata-only history.
8. Test successful account connection with a dedicated test account.
9. Test authorization denial and confirm the application gives a clear error without exposing tokens.
10. Test logout/disconnection and confirm the in-memory Gmail access token is discarded.

## Production values

Set production values through the deployment platform's secret/environment configuration. Never commit them to Git.

- `ENVIRONMENT=production`
- `FRONTEND_URL=https://<production-domain>`
- `TRUSTED_HOSTS=<production-backend-host>`
- `VITE_API_BASE_URL=https://<production-backend-domain>`
- `VITE_GOOGLE_CLIENT_ID=<production-web-client-id>`

## Scope principle

Request the minimum Google scope required by the feature. Do not request Gmail send, modify, compose or full-mailbox scopes when read-only analysis is sufficient.
