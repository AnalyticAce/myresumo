"""Consolidated configuration settings for PowerCV application.

This module provides a single, unified configuration management system
that replaces the duplicate config.py and config/settings.py files.
"""

import re
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Unified application settings loaded from environment variables."""

    # Application settings
    app_name: str = "PowerCV"
    app_version: str = "3.0.0-beta"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parse debug field to handle various boolean representations."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on', 'enable', 'enabled')
        return bool(v)

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS settings
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://localhost:8000",
            "https://localhost:3000",
            "https://localhost:5173",
            "https://localhost:8080",
            "https://localhost:8000"
        ],
        env="CORS_ORIGINS"
    )

    # Database settings
    mongodb_uri: str = Field(default="mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db: str = Field(default="powercv", env="MONGODB_DB")
    mongodb_user: Optional[str] = Field(default=None, env="MONGODB_USER")
    mongodb_password: Optional[str] = Field(default=None, env="MONGODB_PASSWORD")

    # Redis settings (for caching and rate limiting)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # AI Provider settings
    # Cerebras AI
    cerebras_api_key: Optional[str] = Field(
        default=None, 
        env=["CEREBRAS_API_KEY", "CEREBRASAI_API_KEY"]
    )
    cerebras_api_base: str = Field(
        default="https://api.cerebras.ai/v1",
        env=["CEREBRAS_API_BASE", "CEREBRASAI_API_BASE"]
    )
    cerebras_model: str = Field(default="gpt-oss-120b", env="CEREBRAS_MODEL")

    # OpenAI
    openai_api_key: Optional[str] = Field(
        default=None,
        env=["OPENAI_API_KEY", "OPENAI_API_KEY_UPPER"]
    )
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")

    # Deepseek
    deepseek_api_key: Optional[str] = Field(
        default=None,
        env=["API_KEY", "API_KEY_UPPER", "DEEPSEEK_API_KEY"]
    )

    # Ollama (local models)
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")

    # Security settings
    secret_key: str = Field(
        default="development-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(default=100, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_requests_per_hour: int = Field(default=1000, env="RATE_LIMIT_REQUESTS_PER_HOUR")

    # File upload settings
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx", "txt"],
        env="ALLOWED_FILE_TYPES"
    )
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")

    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # External services
    # SMTP settings for email notifications
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")

    # n8n webhook settings
    n8n_webhook_url: Optional[str] = Field(default=None, env="N8N_WEBHOOK_URL")
    n8n_webhook_secret: Optional[str] = Field(default=None, env="N8N_WEBHOOK_SECRET")
    n8n_api_key: Optional[str] = Field(default=None, env="N8N_API_KEY")
    n8n_user: Optional[str] = Field(default=None, env="N8N_USER")
    n8n_password: Optional[str] = Field(default=None, env="N8N_PASSWORD")

    # Sentry for error tracking
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # AI Model tiers configuration
    fast_model: str = Field(default="gpt-oss-120b", env="FAST_MODEL")
    balanced_model: str = Field(default="gpt-oss-120b", env="BALANCED_MODEL")
    quality_model: str = Field(default="gpt-4", env="QUALITY_MODEL")

    # Token tracking
    enable_token_tracking: bool = Field(default=True, env="ENABLE_TOKEN_TRACKING")
    token_usage_limit_per_user: int = Field(default=10000, env="TOKEN_USAGE_LIMIT_PER_USER")

    # Additional AI settings
    llm_provider: str = Field(default="cerebras", env="LLM_PROVIDER")
    ai_provider: str = Field(default="cerebras", env="AI_PROVIDER")
    skip_ats_scoring: bool = Field(default=False, env="SKIP_ATS_SCORING")
    use_fast_optimizer: bool = Field(default=False, env="USE_FAST_OPTIMIZER")

    # Sensitive fields (never log these)
    _sensitive_fields = {
        "secret_key",
        "cerebras_api_key",
        "openai_api_key",
        "deepseek_api_key",
        "mongodb_password",
        "redis_password",
        "smtp_password",
        "n8n_webhook_secret",
        "n8n_password",
        "sentry_dsn"
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def __repr__(self):
        """Secure repr that doesn't expose sensitive data."""
        safe_attrs = {}
        for field_name, field_info in self.__fields__.items():
            if field_name not in self._sensitive_fields:
                safe_attrs[field_name] = getattr(self, field_name)

        attrs_str = ", ".join(f"{k}={v!r}" for k, v in safe_attrs.items())
        return f"Settings({attrs_str})"

    def get_database_config(self) -> dict:
        """Get database configuration (without exposing credentials in logs)."""
        return {
            "uri": self._mask_mongodb_uri(self.mongodb_uri),
            "database": self.mongodb_db
        }

    @staticmethod
    def _mask_mongodb_uri(uri: str) -> str:
        """Mask credentials in MongoDB URI for safe logging."""
        return re.sub(r'://([^:]+):([^@]+)@', '://***:***@', uri)

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment.lower() == "staging"

    @property
    def mongodb_uri_with_auth(self) -> str:
        """Get MongoDB URI with authentication if provided."""
        uri = self.mongodb_uri
        if self.mongodb_user and self.mongodb_password:
            if "://" in uri:
                protocol, rest = uri.split("://", 1)
                uri = f"{protocol}://{self.mongodb_user}:{self.mongodb_password}@{rest}"
        return uri

    @property
    def active_ai_provider(self) -> str:
        """Get the active AI provider based on available API keys."""
        if self.cerebras_api_key:
            return "cerebras"
        elif self.openai_api_key:
            return "openai"
        elif self.deepseek_api_key:
            return "deepseek"
        else:
            return "none"

    @property
    def active_api_key(self) -> Optional[str]:
        """Get the active API key based on provider."""
        if self.cerebras_api_key:
            return self.cerebras_api_key
        elif self.openai_api_key:
            return self.openai_api_key
        elif self.deepseek_api_key:
            return self.deepseek_api_key
        return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: The application settings instance
    """
    return Settings()


# Create global settings instance
settings = get_settings()
