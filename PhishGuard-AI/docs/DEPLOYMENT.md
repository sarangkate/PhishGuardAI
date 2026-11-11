# Step 57 — Deployment

PhishGuardAI is prepared for provider-neutral deployment. The exact hosting provider is intentionally not fixed by the roadmap.

## Components

- Frontend: React + Vite, served as static files.
- Backend: FastAPI + Uvicorn.
- Database: SQLite for the current prototype; production can move to a managed relational database without changing the analysis contract.
- AI: BERT inference runs with the backend using Hugging Face Transformers + PyTorch.

## Production requirements

- HTTPS for frontend and backend.
- A real production domain.
- Production Google OAuth configuration.
- Environment variables supplied by the hosting platform.
- Persistent storage for the database if SQLite is retained.
- Persistent model cache or a startup download strategy.
- Structured application logging without email bodies, raw MIME, OAuth tokens or passwords.
- Monitoring for availability and error rates.
- Error tracking that scrubs sensitive request data.

## Container option

`Dockerfile.backend` and `Dockerfile.frontend` provide a repeatable container-oriented deployment option. `docker-compose.production.yml` describes the component relationship without embedding credentials.

## Important limitation

A single-process SQLite deployment is appropriate for the current student prototype. For multiple backend replicas or high concurrency, use a server database and externalized rate limiting/cache.
