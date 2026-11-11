import requests
from fastapi import HTTPException

from backend.routes.analysis import _gmail_http_error


def _error(status):
    response = requests.Response()
    response.status_code = status
    error = requests.HTTPError(response=response)
    return error


def test_gmail_401_maps_to_reconnect_message():
    result = _gmail_http_error(_error(401))
    assert isinstance(result, HTTPException)
    assert result.status_code == 401
    assert "Reconnect" in result.detail


def test_gmail_403_maps_to_permission_message():
    result = _gmail_http_error(_error(403))
    assert result.status_code == 403
    assert "permission" in result.detail.lower()


def test_gmail_429_is_preserved():
    result = _gmail_http_error(_error(429))
    assert result.status_code == 429
