"""
Application settings using Pydantic BaseSettings.
Loads configuration from environment variables and .env file.
"""

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # API Configuration
    app_name: str = "Invoice Analyzer API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Google Gemini API
    google_api_key: str = Field(..., description="Google Gemini API Key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins"
    )
    
    # Storage Configuration
    storage_dir: Path = Field(default=Path("storage"), description="Base storage directory")
    upload_dir: Path = Field(default=Path("storage/uploads"), description="Upload directory")
    
    # Session Configuration
    session_ttl_hours: int = Field(default=1, description="Session time-to-live in hours")
    max_upload_size_mb: int = Field(default=10, description="Maximum upload size per file in MB")
    allowed_extensions: list[str] = Field(
        default=["jpg", "jpeg", "png"],
        description="Allowed file extensions for upload"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
