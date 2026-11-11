from backend import config


def test_environment_values_are_supported():
    assert config.ENVIRONMENT in {"development", "testing", "production"}
    assert config.TRUSTED_HOSTS


def test_production_validation_rejects_http(monkeypatch):
    monkeypatch.setattr(config, "ENVIRONMENT", "production")
    monkeypatch.setattr(config, "FRONTEND_URL", "http://example.com")
    monkeypatch.setattr(config, "TRUSTED_HOSTS", ["example.com"])
    try:
        config.validate_configuration()
    except RuntimeError as exc:
        assert "HTTPS" in str(exc)
    else:
        raise AssertionError("Expected production HTTPS validation failure")
