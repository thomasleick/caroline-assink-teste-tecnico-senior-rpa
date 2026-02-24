import os
import pytest
from core.config import Settings

def test_settings_empty_db_url_fallback():
    # Set DATABASE_URL to empty in environment
    os.environ["DATABASE_URL"] = ""
    settings = Settings()
    # Should fall back to default
    assert settings.DATABASE_URL == "postgresql+asyncpg://rpa_user:rpa_pass@localhost:5432/rpa_db"
    # Clean up
    del os.environ["DATABASE_URL"]

def test_settings_empty_rabbitmq_url_fallback():
    # Set RABBITMQ_URL to empty in environment
    os.environ["RABBITMQ_URL"] = ""
    settings = Settings()
    # Should fall back to default
    assert settings.RABBITMQ_URL == "amqp://guest:guest@localhost:5672/"
    # Clean up
    del os.environ["RABBITMQ_URL"]

def test_settings_valid_urls():
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@host:port/db"
    os.environ["RABBITMQ_URL"] = "amqp://user:pass@host:port/"
    settings = Settings()
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@host:port/db"
    assert settings.RABBITMQ_URL == "amqp://user:pass@host:port/"
    # Clean up
    del os.environ["DATABASE_URL"]
    del os.environ["RABBITMQ_URL"]
