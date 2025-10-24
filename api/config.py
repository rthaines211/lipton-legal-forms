"""
Configuration settings for the Legal Forms ETL API
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "postgresql://ryanhaines@localhost:5432/legal_forms"
    database_pool_min_size: int = 2
    database_pool_max_size: int = 10

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Application
    app_name: str = "Legal Forms ETL API"
    app_version: str = "1.0.0"

    # Pydantic v2 config
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # ignore unrelated env vars provided by Node/.env
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
