from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Urban Infrastructure Intelligence Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./urban_infrastructure.db"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    SECRET_KEY: str = "urban-infra-secret-key-2024"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
