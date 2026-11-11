# PhishGuardAI Architecture

## High-level flow

```text
React + Vite
    |
    | Google OAuth / Gmail read-only token
    v
FastAPI backend
    |
    +--> Gmail API retrieval
    +--> Email parser
    +--> Sender analysis
    +--> Header/authentication analysis
    +--> URL extraction and destination analysis
    |
    v
AI analysis pipeline
    |
    +--> Email cleaning/tokenization
    +--> BERT phishing-vs-legitimate evidence
    +--> Structured evidence
    +--> Decision engine
    |
    v
Security analysis result
    |
    +--> TrustScore
    +--> SenderAnalysis
    +--> LinkAnalysis
    +--> WarningList
    +--> RecommendationCard
    +--> AwarenessCard
```

## Security boundary

Email HTML is sanitized before rendering. Suspicious URLs are analyzed as data and are not automatically opened. Gmail access is performed using the user's authorization token and the application does not store passwords or Gmail access tokens.

## Scoring

The current project state defines risk as a weighted combination of BERT evidence and structured security evidence. Trust is the inverse display value (`100 - risk`). Model confidence remains separate from application trust.
