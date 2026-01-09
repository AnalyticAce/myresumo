"""Ollama (Local LLM) Provider."""

import time
from typing import Any, Dict, List, Optional

import aiohttp

from ..base import BaseLLMProvider, LLMMessage, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM models."""
    
    def _initialize_client(self) -> None:
        """Initialize the Ollama client (uses aiohttp for HTTP requests)."""
        self._session = None
        self.api_url = f"{self.config.api_base}/api"
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session
    
    def validate_config(self) -> bool:
        """Validate Ollama configuration."""
        if not self.config.api_base:
            raise ValueError("Ollama API base URL is required")
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
        """Generate chat completion using Ollama."""
        start_time = time.time()
        
        # Prepare the request
        payload = {
            "model": self.config.model_name,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "options": {
                "temperature": temperature or self.config.temperature,
            }
        }
        
        if max_tokens or self.config.max_tokens:
            payload["options"]["num_predict"] = max_tokens or self.config.max_tokens
        
        session = await self._get_session()
        
        try:
            async with session.post(
                f"{self.api_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama API error: {response.status} - {error_text}")
                
                data = await response.json()
                response_time = time.time() - start_time
                
                # Extract content
                content = data.get("message", {}).get("content", "")
                
                # Ollama doesn't provide token usage, but we can estimate
                tokens_used = None
                
                return LLMResponse(
                    content=content,
                    model_used=self.config.model_name,
                    tokens_used=tokens_used,
                    cost_usd=0.0,  # Local models are free
                    response_time=response_time,
                    metadata={
                        'provider': 'ollama',
                        'done': data.get('done', True),
                        'total_duration': data.get('total_duration'),
                        'load_duration': data.get('load_duration'),
                        'prompt_eval_count': data.get('prompt_eval_count'),
                        'eval_count': data.get('eval_count')
                    }
                )
                
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    async def completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text completion using Ollama."""
        start_time = time.time()
        
        # Prepare the request
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "options": {
                "temperature": temperature or self.config.temperature,
            }
        }
        
        if max_tokens or self.config.max_tokens:
            payload["options"]["num_predict"] = max_tokens or self.config.max_tokens
        
        session = await self._get_session()
        
        try:
            async with session.post(
                f"{self.api_url}/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama API error: {response.status} - {error_text}")
                
                data = await response.json()
                response_time = time.time() - start_time
                
                # Extract content
                content = data.get("response", "")
                
                return LLMResponse(
                    content=content,
                    model_used=self.config.model_name,
                    tokens_used={
                        'prompt_eval_count': data.get('prompt_eval_count'),
                        'eval_count': data.get('eval_count'),
                        'total_eval_count': data.get('prompt_eval_count', 0) + data.get('eval_count', 0)
                    },
                    cost_usd=0.0,  # Local models are free
                    response_time=response_time,
                    metadata={
                        'provider': 'ollama',
                        'done': data.get('done', True),
                        'total_duration': data.get('total_duration'),
                        'load_duration': data.get('load_duration')
                    }
                )
                
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Ollama model."""
        return {
            'provider': 'ollama',
            'model': self.config.model_name,
            'api_base': self.config.api_base,
            'supports_chat': True,
            'supports_completion': True,
            'supports_streaming': True,
            'max_tokens': self.config.max_tokens,
            'temperature_range': (0.0, 2.0),
            'local': True
        }
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
