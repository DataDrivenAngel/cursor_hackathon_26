"""
Application configuration and settings.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    MEETUP_API_KEY: str = ""
    LUMA_API_KEY: str = ""
    MINIMAX_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_PATH: str = "data/meetup.db"
    
    # Application
    APP_TITLE: str = "Meetup Organizing Information Support System"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
