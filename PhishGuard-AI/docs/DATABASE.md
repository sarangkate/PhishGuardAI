# PhishGuardAI Database

The current prototype uses SQLite.

## Tables

- `users` — provider subject and creation metadata.
- `account_connections` — connection lifecycle metadata.
- `analyses` — classification/risk/trust metadata for an analyzed message.
- `findings` — structured finding metadata attached to an analysis.
- `feedback` — user feedback metadata.

## Deliberately excluded

- Gmail OAuth access tokens
- passwords
- email body content
- raw MIME content
- raw email headers

Analysis metadata is subject to the documented 30-day retention policy.

## Scaling note

SQLite is suitable for the current prototype. A production multi-instance deployment should use a server database with transactional concurrency and per-user authorization.
