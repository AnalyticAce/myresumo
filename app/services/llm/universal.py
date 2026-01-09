"""Simple Universal LLM Service.

A minimal, provider-agnostic LLM service that works with any provider.
"""

import json
import logging
import re
from typing import Any, Dict, List, Union

from .factory import get_llm_provider

logger = logging.getLogger(__name__)


class UniversalLLM:
    """Universal LLM interface that works with any provider."""
    
    def __init__(self, **config_overrides):
        """Initialize with automatic provider detection."""
        self.provider = get_llm_provider(**config_overrides)
        logger.info(f"Universal LLM initialized with {self.provider.provider_type.value}")
    
    async def chat(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """Chat with the LLM and return text response."""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        response = await self.provider.chat_completion(
            messages=[self.provider._convert_message(msg) for msg in messages],
            **kwargs
        )
        return response.content
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Complete a prompt and return text response."""
        response = await self.provider.completion(prompt, **kwargs)
        return response.content
    
    async def extract_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        response = await self.complete(
            prompt=prompt + "\n\nReturn ONLY valid JSON.",
            temperature=kwargs.get('temperature', 0.1),
            **{k: v for k, v in kwargs.items() if k != 'temperature'}
        )
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response[:200]}...")
            raise ValueError("Could not extract valid JSON from response")
    
    async def analyze_match(self, resume_text: str, job_description: str, **kwargs) -> Dict[str, Any]:
        """Analyze resume-job match."""
        prompt = f"""Analyze how well this resume matches the job description.

RESUME:
{resume_text[:3000]}...

JOB DESCRIPTION:
{job_description[:3000]}...

Return JSON with:
- score: number (0-100)
- matching_skills: list of strings
- missing_skills: list of strings  
- recommendation: string
- rationale: string

Be optimistic but realistic. Return ONLY valid JSON."""
        
        return await self.extract_json(prompt, **kwargs)
    
    async def optimize_text(self, text: str, instruction: str, **kwargs) -> str:
        """Optimize text based on instruction."""
        prompt = f"""{instruction}

ORIGINAL TEXT:
{text}

Provide the optimized version."""
        
        return await self.complete(prompt, **kwargs)


# Global instance
_llm_instance = None


def get_llm(**config_overrides) -> UniversalLLM:
    """Get or create the global LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = UniversalLLM(**config_overrides)
    return _llm_instance
