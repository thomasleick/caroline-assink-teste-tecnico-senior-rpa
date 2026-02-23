from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    PROJECT_NAME: str = "RPA Challenge"

    # DB Configuration
    DATABASE_URL: str = "postgresql+asyncpg://rpa_user:rpa_pass@localhost:5432/rpa_db"

    # RabbitMQ Configuration
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Target URLs
    HOCKEY_URL: str = "https://www.scrapethissite.com/pages/forms/"
    OSCAR_URL: str = "https://www.scrapethissite.com/pages/ajax-javascript/"


settings = Settings()
