from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "RPA Challenge"

    # DB Configuration
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:3%40%7CDh%7DL3%228%5Ey%3B%25Rc@34.95.152.162:5432/rpa"
    )

    # RabbitMQ Configuration
    RABBITMQ_URL: str = (
        "amqps://wnhsexac:wa-neOo-CGZv4VLBLc6eNOwza4uN55cB@porpoise.rmq.cloudamqp.com/wnhsexac"
    )

    # Target URLs
    HOCKEY_URL: str = "https://www.scrapethissite.com/pages/forms/"
    OSCAR_URL: str = "https://www.scrapethissite.com/pages/ajax-javascript/"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            logger.warning("DATABASE_URL is empty. Falling back to default cloud URL.")
            return "postgresql+asyncpg://postgres:3%40%7CDh%7DL3%228%5Ey%3B%25Rc@34.95.152.162:5432/rpa"
        if "postgresql+asyncpg://" not in v:
            logger.error(f"Invalid DATABASE_URL format: {v}")
            # We don't raise here to allow the app to boot, but it will fail later with SQLAlchemy error if not fixed.
            # However, for Cloud Run, we might want to be stricter or fallback.
        return v

    @field_validator("RABBITMQ_URL", mode="before")
    @classmethod
    def validate_rabbitmq_url(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            logger.warning("RABBITMQ_URL is empty. Falling back to default cloud URL.")
            return "amqps://wnhsexac:wa-neOo-CGZv4VLBLc6eNOwza4uN55cB@porpoise.rmq.cloudamqp.com/wnhsexac"
        return v


settings = Settings()
