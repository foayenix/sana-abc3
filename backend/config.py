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

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password hashing
    PASSWORD_MIN_LENGTH: int = 8

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@sana.health"

    # SMS (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PLATFORM_FEE_PERCENT: float = 10.0

    # Wearable APIs
    FITBIT_CLIENT_ID: Optional[str] = None
    FITBIT_CLIENT_SECRET: Optional[str] = None
    OURA_CLIENT_ID: Optional[str] = None
    OURA_CLIENT_SECRET: Optional[str] = None
    WHOOP_CLIENT_ID: Optional[str] = None
    WHOOP_CLIENT_SECRET: Optional[str] = None
    GARMIN_CONSUMER_KEY: Optional[str] = None
    GARMIN_CONSUMER_SECRET: Optional[str] = None

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
