# Troubleshooting

## `No module named pytest`

Install the test dependency:

```powershell
py -m pip install pytest
```

## Gmail authorization fails

Check the production/development Google OAuth client ID, allowed origin, Gmail read-only scope and user consent. Reconnect Gmail after correcting configuration.

## BERT is unavailable

The model must be downloaded or available in the configured Hugging Face cache. Run the project's AI setup/download process and retry.

## Frontend build says `vite: not found`

From `frontend` run:

```powershell
npm install
npm run build
```

## Backend cannot start

Verify Python dependencies:

```powershell
py -m pip install -r backend/requirements.txt
```

Then start FastAPI with Uvicorn from the project root.

## A suspicious email link does not open

This is intentional. PhishGuardAI analyzes suspicious destinations without automatically navigating to them.
