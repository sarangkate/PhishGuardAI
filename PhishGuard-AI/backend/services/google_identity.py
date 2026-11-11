"""Resolve the authenticated Google identity without storing OAuth tokens."""
from __future__ import annotations

import requests
from fastapi import HTTPException

USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_subject(access_token: str) -> str:
    try:
        response = requests.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=8,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Unable to verify Google identity right now.") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Google authorization is invalid or expired.")

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Google identity response was invalid.") from exc

    subject = str(payload.get("sub", "")).strip()
    if not subject:
        raise HTTPException(status_code=401, detail="Google account identity could not be verified.")
    return subject
