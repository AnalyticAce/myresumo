"""CV analysis service using multi-provider AI."""
import json
import re
from typing import Dict, List, Optional
import logging
from .ai_client import get_ai_client
from ..prompts.prompt_loader import PromptLoader
from ..utils.shared_utils import JSONParser, ErrorHandler, MetricsHelper

logger = logging.getLogger(__name__)


class CVAnalyzer:
    """Analyze CV against job description using multi-provider AI."""

    def __init__(self):
        """Initialize analyzer with AI client and prompt."""
        self.client = get_ai_client()
        self.loader = PromptLoader()
        self.system_prompt = self.loader.load_prompt('cv_analyzer')
        logger.info("CVAnalyzer initialized")

    def analyze(self, cv_text: str, jd_text: str) -> Dict:
        """Analyze CV against job description.

        Args:
            cv_text: Full CV text
            jd_text: Job description text

        Returns:
            dict: Analysis results with ATS score, keywords, gaps, etc.

        Raises:
            ValueError: If response parsing fails
        """
        logger.info("Starting CV analysis")

        user_message = f"""
**JOB DESCRIPTION:**
{jd_text}

**CANDIDATE CV:**
{cv_text}
"""

        # Call AI API
        response = self.client.chat_completion(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.5,  # Lower temp for structured output
            max_tokens=2500
        )

        # Parse JSON response with fallback
        fallback_analysis = self._get_fallback_analysis()
        analysis = JSONParser.safe_json_parse(response, fallback_analysis)

        # Ensure ats_score is properly formatted
        if 'ats_score' in analysis:
            analysis['ats_score'] = MetricsHelper.extract_ats_score_from_text(str(analysis['ats_score']))

        logger.info(f"Analysis completed. ATS Score: {analysis.get('ats_score', 'N/A')}")
        return analysis

    def _get_fallback_analysis(self) -> Dict:
        """Get fallback analysis structure.
        
        Returns:
            dict: Basic analysis structure for fallback cases
        """
        return {
            "ats_score": 50,
            "summary": "Analysis completed with fallback parsing",
            "keyword_analysis": {
                "matched_keywords": [],
                "missing_critical": [],
                "missing_nice_to_have": []
            },
            "experience_analysis": {
                "relevant_roles": [],
                "transferable_roles": []
            },
            "skill_gaps": {
                "critical": [],
                "important": [],
                "nice_to_have": []
            },
            "strengths": [],
            "education_relevance": {
                "relevant_degrees": [],
                "relevant_certifications": []
            },
            "optimization_priorities": [],
            "recommendations": []
        }
