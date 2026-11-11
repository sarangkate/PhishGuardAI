# Installation

## Backend

From the project root:

```powershell
py -m pip install -r backend/requirements.txt
```

Configure backend environment variables from `.env.example`.

Start the backend with:

```powershell
py -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Configure `VITE_GOOGLE_CLIENT_ID` and `VITE_API_BASE_URL` in the frontend environment.

## Testing

From the project root:

```powershell
py -m pytest -q
```
