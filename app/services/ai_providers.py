"""Multi-provider AI client."""
import os
import requests
from typing import Optional
from dotenv import load_dotenv
import logging

from app.config.settings import get_settings
from app.core.exceptions import MissingApiKeyError

load_dotenv()
logger = logging.getLogger(__name__)


class AIClient:
    """Supports Cerebras (primary), OpenAI, and Deepseek (legacy fallback)."""

    CONFIGS = {
        'deepseek': {
            'base': 'https://api.deepseek.com/v1',
            'model': 'deepseek-chat',
            'key': 'API_KEY'
        },
        'cerebras': {
            'base': 'https://api.cerebras.ai/v1',
            'model': 'gpt-oss-120b',
            'key': 'CEREBRAS_API_KEY'
        },
        'openai': {
            'base': 'https://api.openai.com/v1',
            'model': 'gpt-4',
            'key': 'OPENAI_API_KEY'
        }
    }

    def __init__(self, provider: str = None):
        """Initialize AI client with specified provider.

        Args:
            provider: AI provider name ('deepseek', 'cerebras', 'openai')
                     If None, uses AI_PROVIDER env variable, defaults to 'cerebras'
        """
        self.provider = provider or os.getenv('AI_PROVIDER', 'cerebras')

        if self.provider not in self.CONFIGS:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Supported: {list(self.CONFIGS.keys())}"
            )

        settings = get_settings()
        config = self.CONFIGS[self.provider]
        self.api_base = config['base']
        self.model = config['model']
        self.api_key = getattr(settings, config['key'].lower(), None)

        if not self.api_key:
            raise MissingApiKeyError(config['key'], self.provider)

        logger.info(f"Initialized AI client: {self.provider} ({self.model})")

    def chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ) -> str:
        """Send chat completion request.

        Args:
            system_prompt: System instructions
            user_message: User's input
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds

        Returns:
            str: Model's response

        Raises:
            Exception: If API request fails
        """
        url = f"{self.api_base}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            logger.debug(f"Calling {self.provider} API")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            logger.debug(f"Response received: {len(content)} chars")
            return content

        except requests.exceptions.Timeout:
            logger.error(f"{self.provider} API timeout after {timeout}s")
            raise Exception(f"{self.provider} API timeout after {timeout}s")

        except requests.exceptions.RequestException as e:
            logger.error(f"{self.provider} API error: {type(e).__name__}")
            raise Exception(f"{self.provider} API error: {type(e).__name__}")

    def get_provider_info(self) -> dict:
        """Get current provider information."""
        return {
            "provider": self.provider,
            "model": self.model,
            "api_base": self.api_base
        }


# Convenience function for backward compatibility
def get_ai_client(provider: Optional[str] = None) -> AIClient:
    """Get AI client instance.

    Args:
        provider: Optional provider override

    Returns:
        AIClient: Configured client instance
    """
    return AIClient(provider=provider)
