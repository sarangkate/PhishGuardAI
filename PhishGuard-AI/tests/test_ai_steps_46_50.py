from pathlib import Path


def test_step_46_database_schema_is_metadata_only():
    text = Path("backend/db/database.py").read_text()
    assert "CREATE TABLE IF NOT EXISTS users" in text
    assert "CREATE TABLE IF NOT EXISTS analyses" in text
    assert "email_body" not in text.lower()
    assert "access_token" not in text.lower()


def test_step_47_mobile_responsive_rules_exist():
    text = Path("frontend/src/App.css").read_text()
    assert "max-width: 640px" in text
    assert "min-height: 44px" in text


def test_step_48_desktop_layout_exists():
    text = Path("frontend/src/App.css").read_text()
    assert "min-width: 1200px" in text
    assert "gmail-container" in text


def test_step_49_responsive_states_cover_mobile_and_desktop():
    text = Path("frontend/src/App.css").read_text()
    assert "max-width: 420px" in text
    assert "max-width: 900px" in text
    assert "min-width: 1200px" in text


def test_step_50_token_not_persisted_in_frontend():
    text = Path("frontend/src/App.jsx").read_text()
    assert 'localStorage.setItem("gmailAccessToken"' not in text
    assert 'localStorage.getItem("gmailAccessToken")' not in text
    assert 'sessionStorage.setItem(AUTH_KEY' in Path("frontend/src/auth.js").read_text()


def test_step_50_security_controls_exist():
    main = Path("backend/main.py").read_text()
    security = Path("backend/security.py").read_text()
    assert "TrustedHostMiddleware" in main
    assert "X-Content-Type-Options" in main
    assert "X-Frame-Options" in main
    assert "validate_message_id" in security
    assert "429" in security
