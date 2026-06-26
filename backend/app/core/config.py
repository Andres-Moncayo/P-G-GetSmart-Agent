from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/getsmart"
    
    # Debug
    debug: bool = False

    # JWT
    jwt_secret: str = "your-super-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "getsmart-api"
    jwt_audience: str = "getsmart-frontend"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    okta_client_id: str = ""
    okta_client_secret: str = ""
    okta_domain: str = ""

    # AI
    gemini_api_key: str = ""

    # Game data APIs (pre-scraper Phase 0)
    rawg_api_key: str = ""
    
    # Scraper API keys (Phase 1)
    steam_api_key: str = ""
    tavily_api_key: str = ""

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "https://getsmart.dev"]

    # Redis
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

GEMINI_API_KEY = settings.gemini_api_key
SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm

PIPELINE_VERSION = "3.0.0"
SYNTHESIS_MODEL = "gemini-1.5-flash"

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = BASE_DIR / "templates"
OPENSPEC_SYNTHESIS_YAML = Path(__file__).resolve().parents[2] / "openspec" / "config.yaml"
