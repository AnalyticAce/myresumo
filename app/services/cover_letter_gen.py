"""Cover letter generation service using multi-provider AI."""
import json
import re
from typing import Dict, List
import logging
from .ai_client import get_ai_client
from ..prompts.prompt_loader import PromptLoader
from ..utils.shared_utils import JSONParser, ErrorHandler

logger = logging.getLogger(__name__)


class CoverLetterGenerator:
    """Generate cover letters using multi-provider AI."""

    _system_prompt = None

    def __init__(self):
        """Initialize generator with AI client."""
        self.client = get_ai_client()
        if CoverLetterGenerator._system_prompt is None:
            loader = PromptLoader()
            CoverLetterGenerator._system_prompt = loader.load_prompt(
                'cover_letter')
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

        # Call AI API
        response = self.client.chat_completion(
            system_prompt=CoverLetterGenerator._system_prompt,
            user_message=user_message,
            temperature=0.7,  # Higher temp for creative writing
            max_tokens=1500
        )

        # Parse JSON response with fallback
        fallback_result = self._get_fallback_result(tone)
        result = JSONParser.safe_json_parse(response, fallback_result)

        logger.info(
            f"Cover letter generated successfully ({len(result.get('cover_letter', ''))} chars)")
        return result

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

    def _get_fallback_result(self, tone: str) -> Dict:
        """Get fallback result structure.

        Args:
            tone: Requested tone for the cover letter

        Returns:
            dict: Fallback result structure
        """
        return {
            "cover_letter": f"Unable to generate cover letter due to parsing error.",
            "word_count": 0,
            "tone": tone
        }
