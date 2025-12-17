"""Universal LLM Service.

This module provides a high-level service interface for all LLM operations
throughout the application, making it completely provider-agnostic.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from .base import BaseLLMProvider, LLMMessage, LLMResponse
from .factory import get_llm_provider

logger = logging.getLogger(__name__)


class UniversalLLMService:
    """Universal LLM service that works with any provider."""
    
    def __init__(self, provider: Optional[BaseLLMProvider] = None, **config_overrides):
        """Initialize the LLM service.
        
        Args:
            provider: Optional pre-configured provider
            config_overrides: Configuration overrides for auto-detection
        """
        self.provider = provider or get_llm_provider(**config_overrides)
        logger.info(f"Initialized LLM service with {self.provider.provider_type.value} provider")
    
    async def chat(
        self,
        messages: Union[List[LLMMessage], List[Dict[str, str]], List[str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat messages and get response.
        
        Args:
            messages: Messages in various formats
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
        """
        # Normalize messages
        normalized_messages = self._normalize_messages(messages)
        
        return await self.provider.chat_completion(
            messages=normalized_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def complete(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Complete text prompt.
        
        Args:
            prompt: The prompt to complete
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
        """
        return await self.provider.completion(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def extract_json(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        temperature: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """Extract JSON from LLM response.
        
        Args:
            prompt: The prompt for JSON extraction
            schema: Optional JSON schema for validation
            temperature: Low temperature for consistent output
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        import re
        
        # Add JSON extraction instruction to prompt
        if schema:
            json_instruction = f"\n\nReturn a valid JSON object that matches this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_instruction = "\n\nReturn a valid JSON object."
        
        full_prompt = prompt + json_instruction
        
        response = await self.complete(
            prompt=full_prompt,
            temperature=temperature,
            **kwargs
        )
        
        # Parse JSON from response
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                # Try parsing the entire response
                return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Response content: {response.content[:500]}...")
            raise ValueError("Failed to extract valid JSON from LLM response")
    
    async def analyze_resume_match(
        self,
        resume_text: str,
        job_description: str,
        temperature: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description.
        
        Args:
            resume_text: The resume text
            job_description: The job description
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with match analysis
        """
        prompt = f"""Analyze how well this candidate's resume matches the job requirements.

RESUME:
{resume_text[:3000]}...

JOB DESCRIPTION:
{job_description[:3000]}...

Provide a detailed analysis in JSON format with these exact fields:
{{
    "score": number (0-100),
    "matching_skills": ["list of matching skills"],
    "missing_skills": ["list of important missing skills"],
    "recommendation": "brief recommendation about the candidate's fit",
    "rationale": "explanation of the score and key factors"
}}

Scoring guidelines:
- 95-100: Excellent match, candidate meets nearly all requirements
- 80-94: Strong match, candidate meets most requirements
- 70-79: Good match, candidate meets core requirements
- 50-69: Moderate match, candidate meets some requirements
- 30-49: Weak match, candidate has significant gaps
- 0-29: Poor match, candidate lacks most requirements

Be optimistic - consider transferable skills and relevant experience. Return ONLY valid JSON."""
        
        return await self.extract_json(prompt, temperature=temperature, **kwargs)
    
    async def optimize_resume_section(
        self,
        section_text: str,
        job_description: str,
        section_type: str = "general",
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Optimize a specific section of a resume.
        
        Args:
            section_text: The section text to optimize
            job_description: The job description
            section_type: Type of section (summary, experience, skills, etc.)
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Optimized section text
        """
        section_prompts = {
            "summary": "Write a compelling professional summary that highlights relevant experience and skills for this position.",
            "experience": "Rewrite these bullet points to be more impactful and results-oriented, using action verbs and quantifiable achievements.",
            "skills": "Optimize this skills section to align with the job requirements and include relevant keywords.",
            "general": "Optimize this section to better match the job requirements and stand out to recruiters."
        }
        
        instruction = section_prompts.get(section_type, section_prompts["general"])
        
        prompt = f"""{instruction}

ORIGINAL TEXT:
{section_text}

JOB DESCRIPTION:
{job_description[:2000]}...

Provide the optimized version of this section. Make it more impactful while maintaining accuracy."""
        
        response = await self.complete(prompt=prompt, temperature=temperature, **kwargs)
        return response.content
    
    def _normalize_messages(
        self,
        messages: Union[List[LLMMessage], List[Dict[str, str]], List[str]]
    ) -> List[LLMMessage]:
        """Normalize messages to LLMMessage format."""
        normalized = []
        
        for msg in messages:
            if isinstance(msg, LLMMessage):
                normalized.append(msg)
            elif isinstance(msg, dict):
                normalized.append(LLMMessage(
                    role=msg.get('role', 'user'),
                    content=msg.get('content', '')
                ))
            elif isinstance(msg, str):
                normalized.append(LLMMessage(role='user', content=msg))
            else:
                raise ValueError(f"Unsupported message format: {type(msg)}")
        
        return normalized
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return self.provider.get_model_info()
    
    async def switch_provider(self, **config_overrides) -> None:
        """Switch to a different provider."""
        self.provider = get_llm_provider(**config_overrides)
        logger.info(f"Switched to {self.provider.provider_type.value} provider")


# Singleton instance for easy access
_default_service = None

def get_llm_service(**config_overrides) -> UniversalLLMService:
    """Get a universal LLM service instance."""
    global _default_service
    if _default_service is None:
        _default_service = UniversalLLMService(**config_overrides)
    return _default_service


# Convenience functions for common operations
async def chat_with_llm(messages, **kwargs) -> LLMResponse:
    """Chat with the default LLM."""
    service = get_llm_service()
    return await service.chat(messages, **kwargs)


async def complete_with_llm(prompt: str, **kwargs) -> LLMResponse:
    """Complete text with the default LLM."""
    service = get_llm_service()
    return await service.complete(prompt, **kwargs)


async def analyze_resume_match(resume_text: str, job_description: str, **kwargs) -> Dict[str, Any]:
    """Analyze resume-job match with the default LLM."""
    service = get_llm_service()
    return await service.analyze_resume_match(resume_text, job_description, **kwargs)
