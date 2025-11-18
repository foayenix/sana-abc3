"""
Configuration management for SANA Algorithms Suite.

Uses pydantic-settings for environment variable loading and validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "SANA Algorithms Suite"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://sana_user:sana_pass_dev@localhost:5432/sana_algorithms"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Algorithm Parameters
    SISM_DOMAIN_WEIGHTS: dict = {
        "physical": 0.25,
        "emotional": 0.25,
        "social": 0.15,
        "cognitive": 0.20,
        "spiritual": 0.15
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
