"""Configuration settings for PowerCV application.

This module provides centralized configuration management using environment variables
and sensible defaults. It supports different deployment environments and provides
type-safe access to configuration values.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    app_name: str = "PowerCV"
    app_version: str = "2.0.0"
    debug: bool = False

    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parse debug field to handle various boolean representations."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on', 'enable', 'enabled')
        return bool(v)
    environment: str = "development"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:8080",
        "https://localhost:8000"
    ]

    # MongoDB settings
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "powercv"
    mongodb_user: Optional[str] = None
    mongodb_password: Optional[str] = None

    # Redis settings (for caching and rate limiting)
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # AI Provider settings
    # Cerebras AI
    cerebras_api_key: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("CEREBRAS_API_KEY", "CEREBRASAI_API_KEY"))
    cerebras_api_base: str = Field(default="https://api.cerebras.ai/v1",
                                   validation_alias=AliasChoices("CEREBRAS_API_BASE", "CEREBRASAI_API_BASE"))
    cerebras_model: str = "gpt-oss-120b"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"

    # Ollama (local models)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # API Configuration
    api_base: str = "https://api.cerebras.ai/v1"
    api_model_name: str = "gpt-oss-120b"

    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_requests_per_hour: int = 1000

    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "doc", "docx", "txt"]
    upload_dir: str = "uploads"

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # External services
    # SMTP settings for email notifications
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True

    # n8n webhook settings
    n8n_webhook_url: Optional[str] = None
    n8n_webhook_secret: Optional[str] = None

    # AI Model tiers configuration
    fast_model: str = "gpt-oss-120b"
    balanced_model: str = "gpt-oss-120b"
    quality_model: str = "gpt-4"

    # Token tracking
    enable_token_tracking: bool = True
    token_usage_limit_per_user: int = 10000

    # Additional settings from .env file
    llm_provider: str = "cerebras"
    ai_provider: str = "cerebras"
    n8n_api_key: Optional[str] = None
    n8n_user: Optional[str] = None
    n8n_password: Optional[str] = None
    skip_ats_scoring: bool = False
    use_fast_optimizer: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: The application settings instance
    """
    return Settings()


# Create global settings instance
settings = get_settings()


# Computed properties for backward compatibility
class ComputedSettings:
    """Computed properties that depend on other settings."""

    @property
    def MONGODB_URI(self) -> str:
        """Get MongoDB URI with authentication if provided."""
        uri = settings.mongodb_uri
        if settings.mongodb_user and settings.mongodb_password:
            # Insert credentials into URI
            if "://" in uri:
                protocol, rest = uri.split("://", 1)
                uri = f"{protocol}://{settings.mongodb_user}:{settings.mongodb_password}@{rest}"
        return uri

    @property
    def MONGODB_DB(self) -> str:
        """Get MongoDB database name."""
        return settings.mongodb_db

    @property
    def CEREBRAS_API_KEY(self) -> Optional[str]:
        """Get Cerebras API key."""
        return settings.cerebras_api_key

    @property
    def CEREBRAS_API_BASE(self) -> str:
        """Get Cerebras API base URL."""
        return settings.cerebras_api_base

    @property
    def CEREBRAS_MODEL(self) -> str:
        """Get Cerebras model name."""
        return settings.cerebras_model

    @property
    def API_BASE(self) -> str:
        """Get API base URL."""
        return settings.api_base

    @property
    def API_MODEL_NAME(self) -> str:
        """Get API model name."""
        return settings.api_model_name

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins list."""
        return settings.cors_origins

    @property
    def CEREBRASAI_API_KEY(self) -> Optional[str]:
        """Get Cerebras API key (alias for backward compatibility)."""
        return settings.cerebras_api_key

    @property
    def API_BASE(self) -> str:
        """Get API base URL (alias for backward compatibility)."""
        return settings.api_base

    @property
    def API_MODEL_NAME(self) -> str:
        """Get API model name (alias for backward compatibility)."""
        return settings.api_model_name


# Create computed settings instance for backward compatibility
computed_settings = ComputedSettings()
