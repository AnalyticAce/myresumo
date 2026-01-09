"""Base LLM provider abstraction.

This module defines the universal interface for all LLM providers,
making the application provider-agnostic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ProviderType(Enum):
    """Supported LLM provider types."""
    CEREBRAS = "cerebras"
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider_type: ProviderType
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 60
    retry_attempts: int = 3
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Standard response format from all LLM providers."""
    content: str
    model_used: str
    tokens_used: Optional[Dict[str, int]] = None
    cost_usd: Optional[float] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMMessage:
    """Standard message format for all LLM providers."""
    role: str  # system, user, assistant
    content: str


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the provider with configuration."""
        self.config = config
        self._client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the provider's client."""
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    async def completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text completion."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass
    
    def _convert_message(self, message: Union["LLMMessage", Dict[str, str]]) -> "LLMMessage":
        """Convert message to LLMMessage format."""
        if isinstance(message, LLMMessage):
            return message
        elif isinstance(message, dict):
            return LLMMessage(
                role=message.get('role', 'user'),
                content=message.get('content', '')
            )
        else:
            raise ValueError(f"Unsupported message format: {type(message)}")
    
    @property
    def provider_type(self) -> ProviderType:
        """Get the provider type."""
        return self.config.provider_type
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.config.model_name
    
    def _merge_kwargs(self, **kwargs) -> Dict[str, Any]:
        """Merge kwargs with default configuration."""
        merged = {
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
        }
        
        if self.config.extra_params:
            merged.update(self.config.extra_params)
        
        # Remove None values
        return {k: v for k, v in merged.items() if v is not None}
