# PhishGuardAI Privacy

## Data minimization

PhishGuardAI processes Gmail message content in memory to perform phishing analysis. Email bodies, raw MIME content, OAuth access tokens, passwords, and raw authentication headers are not stored in the analysis-history database.

## Analysis history

When history is enabled, the server stores only metadata needed for the history/dashboard experience: Google account subject, Gmail message ID, sender, subject, message date, classification, risk/trust scores, timestamps, and structured finding metadata.

History is isolated by the authenticated Google account. Users can delete their stored analysis history from the application. Records older than 30 days are eligible for automatic purge.

## OAuth

Gmail access tokens remain in application memory on the frontend and are not written to localStorage. The backend uses the supplied token only to access Gmail and resolve the authenticated Google account; it does not persist the token.

## Important limitation

A high trust score means that the current analysis found few strong phishing indicators. It is not a guarantee that an email is safe.
