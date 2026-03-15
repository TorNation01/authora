"""Environment variable validation tests."""

import os

import pytest

# Import after setting env
from authora.config import Settings, get_settings


def test_settings_load_defaults():
    """Settings load with defaults when env is minimal."""
    # Clear cache to pick up test env
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.app_name == "AUTHORA"
        assert settings.database_url
        assert settings.redis_url
        assert settings.secret_key
    finally:
        get_settings.cache_clear()


def test_settings_deployment_mode():
    """Deployment mode validates to standalone or anakatech."""
    get_settings.cache_clear()
    try:
        os.environ["DEPLOYMENT_MODE"] = "standalone"
        settings = get_settings()
        assert settings.is_standalone() is True
        assert settings.is_anakatech() is False

        os.environ["DEPLOYMENT_MODE"] = "anakatech"
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.is_standalone() is False
        assert settings.is_anakatech() is True
    finally:
        os.environ.pop("DEPLOYMENT_MODE", None)
        get_settings.cache_clear()


def test_settings_get_feature_flags():
    """Feature flags return dict."""
    settings = get_settings()
    flags = settings.get_feature_flags()
    assert isinstance(flags, dict)
    assert "standalone_auth" in flags
    assert "sso_ready" in flags


def test_settings_get_branding():
    """Branding returns dict."""
    settings = get_settings()
    branding = settings.get_branding()
    assert isinstance(branding, dict)
    assert "product_name" in branding
    assert "tagline" in branding


def test_settings_database_url_format():
    """Database URL accepts postgresql format."""
    get_settings.cache_clear()
    try:
        os.environ["DATABASE_URL"] = "postgresql://user:pass@host:5432/dbname"
        settings = get_settings()
        assert "postgresql" in settings.database_url
    finally:
        get_settings.cache_clear()
