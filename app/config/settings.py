"""Secure application settings configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with secure handling of sensitive data."""

    # Application
    app_name: str = "PowerCV"
    version: str = "2.0.0"
    environment: str = "development"
    debug: bool = False

    # Security
    secret_key: str = "development-secret-key-change-in-production"  # Must be set in environment for production
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # API Keys (sensitive - never log these)
    api_key: Optional[str] = None  # Deepseek
    cerebras_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Case-insensitive aliases for common environment variable variations
    CEREBRAS_API_KEY: Optional[str] = None  # Uppercase variant
    API_KEY: Optional[str] = None  # Uppercase Deepseek variant
    OPENAI_API_KEY: Optional[str] = None  # Uppercase OpenAI variant

    # Database
    mongodb_uri: str = "mongodb://localhost:27017/powercv"
    database_name: str = "powercv"

    # Redis (for caching and rate limiting)
    redis_url: Optional[str] = None

    # External services
    sentry_dsn: Optional[str] = None

    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "/tmp/uploads"

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Case-insensitive aliases for common environment variable variations
    CEREBRAS_API_KEY: Optional[str] = None  # Uppercase variant
    API_KEY_UPPER: Optional[str] = None  # Uppercase Deepseek variant
    OPENAI_API_KEY_UPPER: Optional[str] = None  # Uppercase OpenAI variant

    def model_post_init(self, __context):
        """Normalize API key variants after initialization."""
        # Merge uppercase variants into lowercase ones for backward compatibility
        if self.CEREBRAS_API_KEY and not self.cerebras_api_key:
            self.cerebras_api_key = self.CEREBRAS_API_KEY
        if self.API_KEY_UPPER and not self.api_key:
            self.api_key = self.API_KEY_UPPER
        if self.OPENAI_API_KEY_UPPER and not self.openai_api_key:
            self.openai_api_key = self.OPENAI_API_KEY_UPPER

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True  # Strict case-sensitive environment variables
        extra = "ignore"  # Allow extra environment variables

        # Fields that contain sensitive information
        sensitive_fields = {
            "secret_key",
            "api_key",
            "cerebras_api_key",
            "openai_api_key",
            "CEREBRAS_API_KEY",
            "API_KEY_UPPER",
            "OPENAI_API_KEY_UPPER",
            "mongodb_uri",
            "redis_url",
            "sentry_dsn"
        }

    def __repr__(self):
        """Secure repr that doesn't expose sensitive data."""
        # Only show non-sensitive fields
        safe_attrs = {}
        for field_name, field_info in self.__fields__.items():
            if field_name not in self.Config.sensitive_fields:
                safe_attrs[field_name] = getattr(self, field_name)

        attrs_str = ", ".join(f"{k}={v!r}" for k, v in safe_attrs.items())
        return f"Settings({attrs_str})"

    def get_database_config(self) -> dict:
        """Get database configuration (without exposing credentials in logs)."""
        return {
            "uri": self._mask_mongodb_uri(self.mongodb_uri),
            "database": self.database_name
        }

    @staticmethod
    def _mask_mongodb_uri(uri: str) -> str:
        """Mask credentials in MongoDB URI for safe logging."""
        import re
        return re.sub(r'://([^:]+):([^@]+)@', '://***:***@', uri)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()