from pathlib import Path


def test_step_56_google_production_configuration_documented():
    text = Path("docs/GOOGLE_PRODUCTION_CONFIGURATION.md").read_text()
    assert "gmail.readonly" in text
    assert "authorization denial" in text.lower()
    assert "production" in text.lower()


def test_step_57_deployment_artifacts_exist():
    assert Path("Dockerfile.backend").exists()
    assert Path("Dockerfile.frontend").exists()
    compose = Path("docker-compose.production.yml").read_text()
    assert "backend:" in compose
    assert "frontend:" in compose
    assert "phishguard_data" in compose


def test_step_58_security_review_controls_documented():
    text = Path("docs/FINAL_SECURITY_REVIEW.md").read_text()
    for phrase in [
        "malicious email HTML",
        "authentication tokens",
        "suspicious URLs",
        "AI invent warnings",
        "sensitive email data",
    ]:
        assert phrase.lower() in text.lower()


def test_step_58_production_hsts_is_conditional():
    text = Path("backend/main.py").read_text()
    assert "Strict-Transport-Security" in text
    assert "ENVIRONMENT" in text


def test_step_59_ux_review_covers_required_scenarios():
    text = Path("docs/UX_REVIEW.md").read_text()
    for phrase in ["Login", "Gmail", "mobile", "desktop", "Errors", "Loading"]:
        assert phrase.lower() in text.lower()


def test_step_60_documentation_set_exists():
    required = [
        "README.md",
        "docs/INSTALLATION.md",
        "docs/ARCHITECTURE.md",
        "docs/API.md",
        "docs/DATABASE.md",
        "docs/AI_MODEL.md",
        "docs/SECURITY.md",
        "docs/PRIVACY.md",
        "docs/DEPLOYMENT.md",
        "docs/TROUBLESHOOTING.md",
        "docs/USER_GUIDE.md",
    ]
    for path in required:
        assert Path(path).exists(), path
