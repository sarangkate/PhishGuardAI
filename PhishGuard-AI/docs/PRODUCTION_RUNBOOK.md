# Production Runbook

## 1. Configure environment
Set `ENVIRONMENT=production`, an HTTPS `FRONTEND_URL`, strict `TRUSTED_HOSTS`, `VITE_API_BASE_URL`, and the approved `VITE_GOOGLE_CLIENT_ID`.

## 2. Build
Frontend: `cd frontend && npm ci && npm run build`
Backend: install `backend/requirements.txt` or build `Dockerfile.backend`.

## 3. Deploy
Run the frontend and backend behind HTTPS. If SQLite is retained, mount persistent storage for `/app/data`. Use a single backend replica unless a server database and shared rate limiter are introduced.

## 4. Verify
Check `/health` and `/ready`, Google authorization, Gmail inbox retrieval, analysis, history isolation, deletion, loading/error states and mobile/desktop layouts.

## 5. Rollback
Keep the previous application image/build available. If a release causes analysis, auth or data-integrity failures, restore the previous version and investigate before redeployment.
