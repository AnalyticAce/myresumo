"""Cover letter generation service using multi-provider AI."""
import json
import re
from typing import Dict, List
import logging
from .ai_client import get_ai_client
from ..prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class CoverLetterGenerator:
    """Generate cover letters using multi-provider AI."""
    
    def __init__(self):
        """Initialize generator with AI client and prompt."""
        self.client = get_ai_client()
        self.loader = PromptLoader()
        self.system_prompt = self.loader.load_prompt('cover_letter')
        logger.info("CoverLetterGenerator initialized")
    
    def generate(
        self,
        candidate_data: Dict,
        job_data: Dict,
        tone: str = "Professional"
    ) -> Dict:
        """Generate a cover letter.
        
        Args:
            candidate_data: Dictionary containing candidate information
            job_data: Dictionary containing job information
            tone: Tone for the cover letter (Professional, Enthusiastic, Formal)
            
        Returns:
            dict: Generated cover letter and metadata
            
        Raises:
            ValueError: If response parsing fails
        """
        logger.info(f"Generating cover letter with {tone} tone")
        
        user_message = f"""
**CANDIDATE INFORMATION:**
Name: {candidate_data.get('name', 'N/A')}
Current Title: {candidate_data.get('current_title', 'N/A')}
Location: {candidate_data.get('location', 'N/A')}
Years of Experience: {candidate_data.get('years_exp', 'N/A')}
Top Skills: {', '.join(candidate_data.get('top_skills', []))}
Key Achievements: {self._format_achievements(candidate_data.get('achievements', []))}

**JOB INFORMATION:**
Company: {job_data.get('company', 'N/A')}
Position: {job_data.get('position', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Requirements: {', '.join(job_data.get('requirements', []))}

**TONE:**
{tone}
"""
        
        # Call Cerebras API
        response = self.client.chat_completion(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.7,  # Higher temp for creative writing
            max_tokens=1500
        )
        
        # Parse JSON response
        try:
            if not response or not response.strip():
                logger.warning("Empty response received from AI")
                return {
                    "cover_letter": "Unable to generate cover letter due to empty AI response.",
                    "word_count": 0,
                    "tone": tone
                }
            
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            
            logger.info(f"Cover letter generated successfully ({len(result.get('cover_letter', ''))} chars)")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cover letter response: {str(e)}")
            logger.debug(f"Raw response: {response[:500]}")
            # Return a fallback response instead of raising an error
            return {
                "cover_letter": f"Unable to generate cover letter due to parsing error. Raw response: {response[:200]}...",
                "word_count": 0,
                "tone": tone
            }
    
    def _format_achievements(self, achievements: List[str]) -> str:
        """Format achievements list for the prompt.
        
        Args:
            achievements: List of achievement strings
            
        Returns:
            str: Formatted achievements text
        """
        if not achievements:
            return "No specific achievements provided"
        
        return "\n".join(f"- {achievement}" for achievement in achievements)
    
    def _clean_json_response(self, response: str) -> str:
        """Remove markdown code fences and cleanup JSON.
        
        Args:
            response: Raw response from API
            
        Returns:
            str: Cleaned JSON string
        """
        response = response.strip()
        
        # Remove ```json and ``` markers
        if response.startswith('```'):
            lines = response.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response = '\n'.join(lines)
        
        # Find JSON object boundaries
        json_start = response.find('{')
        json_end = response.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            response = response[json_start:json_end+1]
        
        return response.strip()
    
    def _parse_cover_letter_response(self, response: str) -> Dict:
        """Parse and validate cover letter response.
        
        Args:
            response: Raw response from API
            
        Returns:
            dict: Parsed and validated response
        """
        try:
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            
            # Validate required fields
            if 'cover_letter' not in result:
                logger.warning("Missing 'cover_letter' field in response")
                result['cover_letter'] = ''
            
            # Add metadata if not present
            if 'word_count' not in result:
                result['word_count'] = len(result.get('cover_letter', '').split())
            
            if 'tone_matched' not in result:
                result['tone_matched'] = True
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cover letter response: {str(e)}")
            raise ValueError(f"Failed to parse cover letter response: {str(e)}")
