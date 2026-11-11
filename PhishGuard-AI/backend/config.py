import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "PhishGuardAI")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
TRUSTED_HOSTS = [h.strip() for h in os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()


def validate_configuration() -> None:
    if ENVIRONMENT not in {"development", "testing", "production"}:
        raise RuntimeError("ENVIRONMENT must be development, testing, or production")
    if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise RuntimeError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    if not TRUSTED_HOSTS:
        raise RuntimeError("TRUSTED_HOSTS must contain at least one host")
    if ENVIRONMENT == "production":
        if FRONTEND_URL.startswith("http://"):
            raise RuntimeError("Production FRONTEND_URL must use HTTPS")
        if any(host in {"localhost", "127.0.0.1"} for host in TRUSTED_HOSTS):
            raise RuntimeError("Production TRUSTED_HOSTS must not use localhost defaults")
