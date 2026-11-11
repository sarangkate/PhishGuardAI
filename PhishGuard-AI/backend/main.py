from pathlib import Path
import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.routes.analysis import router as analysis_router
from backend.db.database import initialize_database
from backend.config import validate_configuration, ENVIRONMENT

validate_configuration()

app = FastAPI(
    docs_url=None if ENVIRONMENT == "production" else "/docs",
    redoc_url=None if ENVIRONMENT == "production" else "/redoc",
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [frontend_url]
if frontend_url == "http://localhost:5173":
    allowed_origins.append("http://127.0.0.1:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=(r"https?://(localhost|127\.0\.0\.1):\d+" if ENVIRONMENT != "production" else None),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

# Local development hosts only. Production must set a strict trusted host list.
trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[h.strip() for h in trusted_hosts if h.strip()])

@app.on_event("startup")
def startup():
    initialize_database()

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    if os.getenv("ENVIRONMENT", "development").strip().lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.include_router(analysis_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "PhishGuardAI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "phishguardai-backend"}


@app.get("/ready")
def readiness():
    # Database initialization is intentionally lightweight and local.
    initialize_database()
    return {"status": "ready", "service": "phishguardai-backend"}
