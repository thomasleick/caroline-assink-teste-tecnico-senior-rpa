from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "RPA Challenge"

    # DB Configuration
    DATABASE_URL: str = "postgresql+asyncpg://rpa_user:rpa_pass@localhost:5432/rpa_db"

    # RabbitMQ Configuration
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Target URLs
    HOCKEY_URL: str = "https://www.scrapethissite.com/pages/forms/"
    OSCAR_URL: str = "https://www.scrapethissite.com/pages/ajax-javascript/"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            logger.warning("DATABASE_URL is empty. Falling back to default local URL.")
            return "postgresql+asyncpg://rpa_user:rpa_pass@localhost:5432/rpa_db"
        if "postgresql+asyncpg://" not in v:
            logger.error(f"Invalid DATABASE_URL format: {v}")
            # We don't raise here to allow the app to boot, but it will fail later with SQLAlchemy error if not fixed.
            # However, for Cloud Run, we might want to be stricter or fallback.
        return v

    @field_validator("RABBITMQ_URL", mode="before")
    @classmethod
    def validate_rabbitmq_url(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.strip() == "":
            logger.warning("RABBITMQ_URL is empty. Falling back to default local URL.")
            return "amqp://guest:guest@localhost:5672/"
        return v


settings = Settings()
