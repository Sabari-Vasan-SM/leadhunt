import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LeadHunt"
    API_V1_STR: str = "/api/v1"
    
    # Database: Defaults to PostgreSQL, falls back to SQLite for local development without Docker
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/leadhunt"
    )
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./leadhunt.db"

    # Scraping Configuration
    MAX_CONCURRENCY: int = 5
    REQUEST_TIMEOUT_SECONDS: int = 15
    MAX_RESULTS_PER_SEARCH: int = 50
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 LeadHuntBot/1.0"
    )
    
    # Optional Google Places API Key (if provided by user in .env)
    GOOGLE_PLACES_API_KEY: Optional[str] = os.getenv("GOOGLE_PLACES_API_KEY", None)

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
