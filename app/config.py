"""
Configuration settings for PowerCV application.

This module provides centralized configuration management using environment variables
and sensible defaults. It supports different deployment environments and provides
type-safe access to configuration values.
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="PowerCV", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
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
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080", 
            "http://localhost:8000",
            "https://localhost:3000",
            "https://localhost:8080",
            "https://localhost:8000"
        ],
        env="CORS_ORIGINS"
    )
    
    # MongoDB settings
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        env="MONGODB_URI"
    )
    mongodb_db: str = Field(default="powercv", env="MONGODB_DB")
    mongodb_user: Optional[str] = Field(default=None, env="MONGODB_USER")
    mongodb_password: Optional[str] = Field(default=None, env="MONGODB_PASSWORD")
    
    # Redis settings (for caching and rate limiting)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # AI Provider settings
    # Cerebras AI
    cerebras_api_key: Optional[str] = Field(default=None, env="CEREBRASAI_API_KEY")
    cerebras_api_base: str = Field(default="https://api.cerebras.ai/v1", env="CEREBRASAI_API_BASE")
    cerebras_model: str = Field(default="gpt-oss-120b", env="CEREBRAS_MODEL")
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Ollama (local models)
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    
    # API Configuration
    api_base: str = Field(default="https://api.cerebras.ai/v1", env="API_BASE")
    api_model_name: str = Field(default="gpt-oss-120b", env="API_MODEL_NAME")
    
    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
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
    
    # AI Model tiers configuration
    fast_model: str = Field(default="gpt-oss-120b", env="FAST_MODEL")
    balanced_model: str = Field(default="gpt-oss-120b", env="BALANCED_MODEL")
    quality_model: str = Field(default="gpt-4", env="QUALITY_MODEL")
    
    # Token tracking
    enable_token_tracking: bool = Field(default=True, env="ENABLE_TOKEN_TRACKING")
    token_usage_limit_per_user: int = Field(default=10000, env="TOKEN_USAGE_LIMIT_PER_USER")
    
    # Additional settings from .env file
    llm_provider: str = Field(default="cerebras", env="LLM_PROVIDER")
    ai_provider: str = Field(default="cerebras", env="AI_PROVIDER")
    n8n_api_key: Optional[str] = Field(default=None, env="N8N_API_KEY")
    n8n_user: Optional[str] = Field(default=None, env="N8N_USER")
    n8n_password: Optional[str] = Field(default=None, env="N8N_PASSWORD")
    skip_ats_scoring: bool = Field(default=False, env="SKIP_ATS_SCORING")
    use_fast_optimizer: bool = Field(default=False, env="USE_FAST_OPTIMIZER")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


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
