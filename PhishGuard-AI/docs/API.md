# PhishGuardAI API

## `GET /api/gmail/messages`

Retrieves the current user's Gmail message list using a bearer token.

## `GET /api/gmail/messages/{message_id}`

Retrieves and normalizes one Gmail message for safe display.

## `POST /api/emails/{message_id}/analyze`

Runs the security-analysis pipeline for a Gmail message.

### Result areas

- `features.sender`
- `features.urls`
- `features.headers`
- `risk_analysis.classification`
- `risk_analysis.risk_score`
- `risk_analysis.trust_score`
- `risk_analysis.model_confidence`
- `risk_analysis.evidence`
- `risk_analysis.warnings`
- `risk_analysis.recommendation`
- `risk_analysis.awareness`

## Authentication

Gmail endpoints require `Authorization: Bearer <token>`. Tokens are validated for presence/shape but are not persisted by the backend.
