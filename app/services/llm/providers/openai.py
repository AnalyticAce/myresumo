"""OpenAI LLM Provider."""

import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

from ..base import BaseLLMProvider, LLMMessage, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation."""
    
    def _initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        self._client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base
        )
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
        if not self.config.model_name:
            raise ValueError("Model name is required")
        return True
    
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion using OpenAI."""
        start_time = time.time()
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = self._client.chat.completions.create(
                model=self.config.model_name,
                messages=openai_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
            
            response_time = time.time() - start_time
            
            # Extract token usage
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            # Calculate cost (OpenAI pricing)
            cost_usd = None
            if tokens_used:
                # OpenAI pricing (example rates - update with actual rates)
                pricing = {
                    'gpt-4': {'input': 0.03, 'output': 0.06},
                    'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
                    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
                }
                model_pricing = pricing.get(self.config.model_name, pricing['gpt-4'])
                cost_usd = (
                    (tokens_used['prompt_tokens'] / 1000) * model_pricing['input'] +
                    (tokens_used['completion_tokens'] / 1000) * model_pricing['output']
                )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model_used=response.model,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time=response_time,
                metadata={
                    'finish_reason': response.choices[0].finish_reason,
                    'provider': 'openai'
                }
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text completion using OpenAI."""
        # Convert to chat completion format
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat_completion(messages, temperature, max_tokens, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI model."""
        return {
            'provider': 'openai',
            'model': self.config.model_name,
            'api_base': self.config.api_base,
            'supports_chat': True,
            'supports_completion': True,
            'supports_streaming': True,
            'max_tokens': self.config.max_tokens,
            'temperature_range': (0.0, 2.0)
        }
