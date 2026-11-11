# Database and Retention Policy

## Purpose

PhishGuardAI has a SQLite persistence foundation for application metadata. The database is designed to support users, Gmail account connections, analysis metadata, findings and feedback.

## Data that may be stored

- Provider subject identifier for the authenticated application user
- Gmail account connection metadata (provider and connection timestamps)
- Analysis metadata: message ID, sender, subject, message date, classification, risk score, trust score and analysis timestamp
- Structured finding metadata (code, category, severity and title)
- Optional user feedback associated with an analysis

## Data deliberately not stored

- Gmail OAuth access tokens
- Google passwords
- Email body/raw MIME content
- Raw Gmail headers
- Credentials, verification codes or attachment contents

## Retention

Persisted analysis history is designed for a **30-day default retention period**. Expired analysis records are purged by the database maintenance function. Users must also have a clear delete-history operation in the application.

The current browser history feature remains metadata-only. Server-side persistence should only be enabled after authenticated API ownership is established, so one user's history can never be exposed to another user.
