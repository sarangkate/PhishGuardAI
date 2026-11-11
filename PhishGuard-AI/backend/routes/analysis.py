from fastapi import APIRouter, Header, HTTPException, Query
import requests

from backend.services.gmail_service import (
    get_gmail_messages,
    get_gmail_message,
    extract_email_information,
    modify_gmail_message_star,
)

from backend.services.feature_extractor import extract_features
from backend.models.email_model import EmailModel
from ai.analysis.pipeline import analyze_email
from backend.security import rate_limiter, validate_bearer, validate_message_id
from backend.services.google_identity import get_google_subject
from backend.services.origin_tracer import trace_origin
from backend.services.report_generator import build_forensic_pdf
from backend.services.investigation_case import build_investigation_case
from fastapi.responses import Response
from backend.db.repository import ensure_user, mark_connection, save_analysis, list_history, clear_history


router = APIRouter()


@router.get("/test")
def test_analysis():
    return {
        "message": "Analysis API is working"
    }


def _gmail_http_error(error: requests.HTTPError) -> HTTPException:
    response = getattr(error, "response", None)
    status = getattr(response, "status_code", None)
    if status == 401:
        return HTTPException(status_code=401, detail="Your Google/Gmail session expired. Reconnect Gmail and try again.")
    if status == 403:
        return HTTPException(status_code=403, detail="Gmail access was denied. Reconnect Google and grant Gmail read permission.")
    if status == 429:
        return HTTPException(status_code=429, detail="Gmail is temporarily rate-limiting requests. Try again shortly.")
    if status == 400:
        return HTTPException(status_code=400, detail="Gmail rejected this mailbox request. Reconnect Gmail and retry.")
    return HTTPException(status_code=502, detail="Google Gmail API is temporarily unavailable.")


@router.get("/gmail/messages")
def gmail_messages(
    authorization: str = Header(None),
    label: str = Query("inbox"),
    max_results: int = Query(25, ge=1, le=100),
    page_token: str | None = Query(None),
):
    access_token = _get_authorized_token(authorization)
    allowed_labels = {"inbox", "starred", "snoozed", "sent", "drafts", "all", "spam", "trash"}
    if label not in allowed_labels:
        raise HTTPException(status_code=400, detail="Unsupported Gmail mailbox.")
    try:
        return get_gmail_messages(
            access_token=access_token,
            max_results=max_results,
            page_token=page_token,
            label=label,
        )
    except requests.HTTPError as error:
        raise _gmail_http_error(error)
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Gmail took too long to respond. Please retry.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to retrieve Gmail messages right now.")


@router.get("/gmail/messages/{message_id}")
def gmail_message(
    message_id: str,
    authorization: str = Header(None),
):
    access_token = _get_authorized_token(authorization)
    message_id = validate_message_id(message_id)
    try:
        data = get_gmail_message(access_token=access_token, message_id=message_id)
        return extract_email_information(data)
    except requests.HTTPError as error:
        raise _gmail_http_error(error)
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Gmail took too long to load this message. Please retry.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to retrieve this Gmail message right now.")


@router.post("/gmail/messages/{message_id}/star")
def star_gmail_message(
    message_id: str,
    authorization: str = Header(None),
    action: str = Query("star"),
):
    """Star or unstar a Gmail message using the user's OAuth token."""
    message_id = validate_message_id(message_id)
    access_token = _get_authorized_token(authorization)
    if action not in {"star", "unstar"}:
        raise HTTPException(status_code=400, detail="Unsupported star action.")
    try:
        return modify_gmail_message_star(access_token, message_id, action == "star")
    except requests.HTTPError as error:
        raise _gmail_http_error(error)
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Gmail took too long to update the star. Please retry.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to update the Gmail star right now.")


def _get_authorized_token(authorization: str):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    return validate_bearer(authorization)


def _get_current_user_id(authorization: str) -> tuple[str, int]:
    access_token = _get_authorized_token(authorization)
    provider_subject = get_google_subject(access_token)
    user_id = ensure_user(provider_subject)
    mark_connection(user_id, "google")
    return access_token, user_id


def _analyze_gmail_message(access_token: str, message_id: str):
    message = get_gmail_message(
        access_token=access_token,
        message_id=message_id,
    )
    parsed_email = extract_email_information(message)
    features = extract_features(parsed_email)
    combined_analysis = analyze_email(
        parsed_email=parsed_email,
        feature_data=features,
    )
    origin = trace_origin(parsed_email)
    investigation_case = build_investigation_case(parsed_email, combined_analysis, origin)

    return {
        "email": parsed_email,
        "features": features,
        "risk_analysis": combined_analysis,
        "origin_trace": origin,
        "investigation_case": investigation_case,
        "pipeline": {
            "bert": combined_analysis.get("bert"),
            "evidence_count": len(combined_analysis.get("evidence", [])),
            "decision_engine": "weighted_bert_plus_security_evidence",
        },
    }


@router.get("/gmail/messages/{message_id}/features")
def gmail_message_features(
    message_id: str,
    authorization: str = Header(None),
):
    """Compatibility endpoint; new clients should use POST /emails/{id}/analyze."""
    message_id = validate_message_id(message_id)
    access_token = _get_authorized_token(authorization)
    rate_limiter.check(access_token[:32])

    try:
        return _analyze_gmail_message(access_token, message_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to complete the security analysis right now.")


@router.post("/emails/{message_id}/analyze")
def analyze_gmail_message(
    message_id: str,
    authorization: str = Header(None),
):
    """Analyze one Gmail message without storing its content."""
    message_id = validate_message_id(message_id)
    access_token, user_id = _get_current_user_id(authorization)
    rate_limiter.check(access_token[:32])

    try:
        result = _analyze_gmail_message(access_token, message_id)
        risk = result.get("risk_analysis", {})
        email = result.get("email", {})
        save_analysis(
            user_id=user_id,
            message_id=message_id,
            sender=email.get("sender", ""),
            subject=email.get("subject", ""),
            message_date=email.get("date", ""),
            classification=str(risk.get("classification", "Unknown")),
            risk_score=risk.get("risk_score"),
            trust_score=risk.get("trust_score"),
            evidence=risk.get("evidence", []),
        )
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to complete the security analysis right now.")


@router.get("/emails/{message_id}/report/metadata")
def forensic_report_metadata(
    message_id: str,
    authorization: str = Header(None),
):
    """Return integrity metadata for the currently generated forensic report."""
    import hashlib
    message_id = validate_message_id(message_id)
    access_token = _get_authorized_token(authorization)
    rate_limiter.check(access_token[:32])
    try:
        result = _analyze_gmail_message(access_token, message_id)
        pdf = build_forensic_pdf(result.get("email", {}), result, result.get("origin_trace", {}))
        case = result.get("investigation_case", {}) or {}
        return {
            "case_id": case.get("case_id"),
            "evidence_manifest_sha256": case.get("evidence_manifest_sha256"),
            "report_sha256": hashlib.sha256(pdf).hexdigest(),
            "algorithm": "SHA-256",
            "verification": "Re-download the report and hash the exact PDF bytes; the resulting SHA-256 should match report_sha256.",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to calculate report integrity metadata right now.")


@router.post("/emails/{message_id}/report")
def forensic_report(
    message_id: str,
    authorization: str = Header(None),
):
    """Generate a forensic PDF for one Gmail message without storing its body."""
    message_id = validate_message_id(message_id)
    access_token = _get_authorized_token(authorization)
    rate_limiter.check(access_token[:32])
    try:
        result = _analyze_gmail_message(access_token, message_id)
        pdf = build_forensic_pdf(result.get("email", {}), result, result.get("origin_trace", {}))
        import hashlib
        report_sha256 = hashlib.sha256(pdf).hexdigest()
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="PhishGuardAI-{message_id}.pdf"',
                "X-PhishGuard-Report-SHA256": report_sha256,
                "X-PhishGuard-Evidence-SHA256": str((result.get("investigation_case") or {}).get("evidence_manifest_sha256") or ""),
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to generate the forensic report right now.")


@router.get("/google/profile")
def google_profile(authorization: str = Header(None)):
    access_token = _get_authorized_token(authorization)
    try:
        import requests
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=8,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Google account information is unavailable.")
        payload = response.json()
        return {
            "name": str(payload.get("name", "")),
            "email": str(payload.get("email", "")),
            "picture": str(payload.get("picture", "")),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to retrieve Google account information right now.")


@router.get("/history")
def analysis_history(authorization: str = Header(None)):
    _, user_id = _get_current_user_id(authorization)
    return {"items": list_history(user_id)}


@router.delete("/history")
def delete_analysis_history(authorization: str = Header(None)):
    _, user_id = _get_current_user_id(authorization)
    return {"deleted": clear_history(user_id)}


@router.get("/ai/status")
def ai_status():
    from ai.models.bert_model import MODEL_NAME, _model, _load_error
    return {
        "model": MODEL_NAME,
        "loaded": _model is not None,
        "error": _load_error,
    }
