"""Application configuration using pydantic settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # App Configuration
    app_name: str = Field(default="Nutrition Coach", description="Application name")
    debug: bool = Field(default=True, description="Enable debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Groq API Configuration
    groq_api_key: str = Field(default="", description="Groq API key for LLM inference")
    groq_model: str = Field(
        default="llama-3.1-70b-versatile",
        description="Groq model to use for LLM inference",
    )

    # Google Sheets Configuration (via Composio)
    google_sheets_spreadsheet_id: str = Field(
        default="",
        description="Google Sheets spreadsheet ID for meal logging",
    )
    google_sheets_sheet_name: str = Field(
        default="MealLog",
        description="Sheet name for logging meals",
    )

    # Project paths
    project_root: Path = Field(
        default=Path(__file__).parent.parent,
        description="Project root directory",
    )
    log_file: str = Field(
        default="logs/app.log",
        description="Log file path (relative to project root)",
    )

    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq API is properly configured."""
        return bool(self.groq_api_key)

    @property
    def is_google_sheets_configured(self) -> bool:
        """Check if Google Sheets is properly configured."""
        return bool(self.google_sheets_spreadsheet_id)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging() -> None:
    """Configure application logging with file output."""
    import logging
    import os

    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = settings.project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Full log file path
    log_path = settings.project_root / settings.log_file
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not settings.debug else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),  # Also output to console
        ],
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)