"""Cerebras AI API client wrapper."""
import logging
import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class CerebrasClient:
    """Wrapper for Cerebras AI API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize Cerebras client.
        
        Args:
            api_key: Cerebras API key (defaults to env variable)
            api_base: API base URL (defaults to env variable)
            model: Model name (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        self.api_base = api_base or os.getenv("CEREBRAS_API_BASE", "https://api.cerebras.ai/v1")
        self.model = model or os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")
        
        if not self.api_key:
            raise ValueError(
                "CEREBRAS_API_KEY not found. "
                "Set it in .env file or pass as parameter."
            )
        
        logger.info(f"Initialized Cerebras client with model: {self.model}")
    
    def chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ) -> str:
        """Send chat completion request to Cerebras with comprehensive error handling.
        
        Args:
            system_prompt: System instructions for the model
            user_message: User's input message
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            str: Model's response text
            
        Raises:
            Exception: If API request fails with detailed error information
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
        
        # Validate inputs before making request
        self._validate_request_inputs(system_prompt, user_message, temperature, max_tokens, timeout)
        
        try:
            logger.debug(f"Sending request to Cerebras API: {url}")
            logger.debug(f"Request payload size: {len(str(payload))} chars")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                raise Exception("Cerebras API authentication failed. Check your API key.")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds.")
            elif response.status_code == 400:
                error_detail = self._extract_error_detail(response)
                raise Exception(f"Bad request: {error_detail}")
            elif response.status_code == 403:
                raise Exception("Access forbidden. Check your API permissions.")
            elif response.status_code == 404:
                raise Exception("API endpoint not found. Check your API base URL.")
            elif response.status_code >= 500:
                raise Exception(f"Cerebras API server error: {response.status_code}")
            
            response.raise_for_status()
            
            # Parse and validate response
            result = response.json()
            self._validate_response_structure(result)
            
            content = result['choices'][0]['message']['content']
            
            if not content:
                raise Exception("Empty response received from Cerebras API")
            
            logger.debug(f"Received response ({len(content)} chars)")
            return content
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after {timeout}s")
            raise Exception(f"Cerebras API request timed out after {timeout}s")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise Exception(f"Failed to connect to Cerebras API: {str(e)}")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            raise Exception(f"Cerebras API HTTP error: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Cerebras API request error: {str(e)}")
            raise Exception(f"Cerebras API request failed: {str(e)}")
            
        except ValueError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise Exception(f"Invalid JSON response from Cerebras API: {str(e)}")
            
        except KeyError as e:
            logger.error(f"Response structure error: {str(e)}")
            raise Exception(f"Invalid response structure from Cerebras API: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error in Cerebras API request: {str(e)}")
            raise Exception(f"Cerebras API error: {str(e)}")
    
    def _validate_request_inputs(self, system_prompt: str, user_message: str, temperature: float, max_tokens: int, timeout: int):
        """Validate request inputs before sending to API."""
        if not system_prompt or not system_prompt.strip():
            raise ValueError("System prompt cannot be empty")
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty")
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if max_tokens < 1 or max_tokens > 8000:
            raise ValueError("Max tokens must be between 1 and 8000")
        if timeout < 1 or timeout > 300:
            raise ValueError("Timeout must be between 1 and 300 seconds")
    
    def _validate_response_structure(self, result: Dict):
        """Validate response structure from Cerebras API."""
        if not isinstance(result, dict):
            raise ValueError("Response is not a valid JSON object")
        
        if 'choices' not in result:
            raise ValueError("Response missing 'choices' field")
        
        if not isinstance(result['choices'], list) or len(result['choices']) == 0:
            raise ValueError("Response 'choices' must be a non-empty list")
        
        choice = result['choices'][0]
        if 'message' not in choice:
            raise ValueError("Response choice missing 'message' field")
        
        if 'content' not in choice['message']:
            raise ValueError("Response message missing 'content' field")
    
    def _extract_error_detail(self, response) -> str:
        """Extract detailed error information from response."""
        try:
            error_data = response.json()
            if 'error' in error_data:
                error = error_data['error']
                if isinstance(error, dict):
                    return error.get('message', str(error))
                return str(error)
            return response.text
        except (ValueError, KeyError):
            return response.text
