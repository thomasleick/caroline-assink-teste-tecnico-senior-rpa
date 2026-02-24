import os
from core.config import Settings


def test_settings_empty_db_url_fallback():
    # Set DATABASE_URL to empty in environment
    os.environ["DATABASE_URL"] = ""
    settings = Settings()
    # Should fall back to default cloud URL
    assert (
        settings.DATABASE_URL
        == "postgresql+asyncpg://postgres:3%40%7CDh%7DL3%228%5Ey%3B%25Rc@34.95.152.162:5432/rpa"
    )
    # Clean up
    del os.environ["DATABASE_URL"]


def test_settings_empty_rabbitmq_url_fallback():
    # Set RABBITMQ_URL to empty in environment
    os.environ["RABBITMQ_URL"] = ""
    settings = Settings()
    # Should fall back to default cloud URL
    assert (
        settings.RABBITMQ_URL
        == "amqps://wnhsexac:wa-neOo-CGZv4VLBLc6eNOwza4uN55cB@porpoise.rmq.cloudamqp.com/wnhsexac"
    )
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
