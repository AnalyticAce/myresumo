"""LLM Provider Factory.

This module provides a factory pattern for creating LLM providers
based on configuration, making it easy to switch between providers.
"""

import os
from typing import Dict, Any, Optional, Type, List
from .base import BaseLLMProvider, LLMConfig, ProviderType
from .providers import CerebrasProvider, OpenAIProvider, OllamaProvider


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers: Dict[ProviderType, Type[BaseLLMProvider]] = {
        ProviderType.CEREBRAS: CerebrasProvider,
        ProviderType.OPENAI: OpenAIProvider,
        ProviderType.OLLAMA: OllamaProvider,
    }
    
    @classmethod
    def register_provider(
        cls,
        provider_type: ProviderType,
        provider_class: Type[BaseLLMProvider]
    ) -> None:
        """Register a new provider type."""
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create_from_env(cls, **overrides) -> BaseLLMProvider:
        """Create provider from environment variables."""
        # Determine provider type
        provider_str = (
            overrides.get('provider_type') or
            os.getenv('LLM_PROVIDER') or
            os.getenv('PROVIDER_TYPE') or
            'cerebras'
        ).lower()
        
        # Map string to ProviderType
        provider_mapping = {
            'cerebras': ProviderType.CEREBRAS,
            'openai': ProviderType.OPENAI,
            'ollama': ProviderType.OLLAMA,
            'anthropic': ProviderType.ANTHROPIC,
            'huggingface': ProviderType.HUGGINGFACE,
        }
        
        provider_type = provider_mapping.get(provider_str, ProviderType.CEREBRAS)
        
        # Get configuration
        config = cls._get_config_from_env(provider_type, **overrides)
        
        return cls.create(config)
    
    @classmethod
    def create(cls, config: LLMConfig) -> BaseLLMProvider:
        """Create a provider instance from configuration."""
        if config.provider_type not in cls._providers:
            raise ValueError(f"Unsupported provider type: {config.provider_type}")
        
        provider_class = cls._providers[config.provider_type]
        return provider_class(config)
    
    @staticmethod
    def _get_config_from_env(provider_type: ProviderType, **overrides) -> LLMConfig:
        """Get configuration from environment variables."""
        # Base configuration
        config = LLMConfig(
            provider_type=provider_type,
            model_name=(
                overrides.get('model_name') or
                os.getenv('MODEL_NAME') or
                os.getenv('LLM_MODEL') or
                'gpt-oss-120b'
            ),
            api_key=(
                overrides.get('api_key') or
                os.getenv('API_KEY') or
                os.getenv('LLM_API_KEY')
            ),
            api_base=(
                overrides.get('api_base') or
                os.getenv('API_BASE') or
                os.getenv('LLM_API_BASE')
            ),
            temperature=(
                overrides.get('temperature') or
                float(os.getenv('LLM_TEMPERATURE', '0.7'))
            ),
            max_tokens=(
                overrides.get('max_tokens') or
                (int(os.getenv('LLM_MAX_TOKENS')) if os.getenv('LLM_MAX_TOKENS') else None)
            ),
            timeout=(
                overrides.get('timeout') or
                int(os.getenv('LLM_TIMEOUT', '60'))
            ),
            retry_attempts=(
                overrides.get('retry_attempts') or
                int(os.getenv('LLM_RETRY_ATTEMPTS', '3'))
            )
        )
        
        # Provider-specific defaults
        if provider_type == ProviderType.CEREBRAS:
            if not config.api_key:
                config.api_key = os.getenv('CEREBRASAI_API_KEY')
            if not config.api_base:
                config.api_base = os.getenv('CEREBRAS_API_BASE', 'https://api.cerebras.ai/v1')
            if not config.model_name:
                config.model_name = os.getenv('CEREBRAS_MODEL_NAME', 'gpt-oss-120b')
        
        elif provider_type == ProviderType.OPENAI:
            if not config.api_key:
                config.api_key = os.getenv('OPENAI_API_KEY')
            if not config.api_base:
                config.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
            if not config.model_name:
                config.model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')
        
        elif provider_type == ProviderType.OLLAMA:
            if not config.api_base:
                config.api_base = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            if not config.model_name:
                config.model_name = os.getenv('OLLAMA_MODEL', 'llama2')
            # Ollama doesn't need API key
            config.api_key = None
        
        # Apply any overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    @staticmethod
    def get_available_providers() -> List[ProviderType]:
        """Get list of available provider types."""
        return list(LLMProviderFactory._providers.keys())
    
    @staticmethod
    def detect_provider_from_config() -> Optional[ProviderType]:
        """Auto-detect provider type from available environment variables."""
        # Check for Cerebras
        if os.getenv('CEREBRASAI_API_KEY'):
            return ProviderType.CEREBRAS
        
        # Check for OpenAI
        if os.getenv('OPENAI_API_KEY'):
            return ProviderType.OPENAI
        
        # Check for Ollama (local)
        if os.getenv('OLLAMA_BASE_URL') or 'localhost' in os.getenv('API_BASE', ''):
            return ProviderType.OLLAMA
        
        # Default to Cerebras
        return ProviderType.CEREBRAS


# Convenience function for easy usage
def get_llm_provider(**overrides) -> BaseLLMProvider:
    """Get an LLM provider instance with automatic configuration."""
    return LLMProviderFactory.create_from_env(**overrides)
