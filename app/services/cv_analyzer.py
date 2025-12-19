"""CV analysis service using Cerebras AI."""
import json
import re
from typing import Dict, List, Optional
import logging
from .cerebras_client import CerebrasClient
from ..prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class CVAnalyzer:
    """Analyze CV against job description using Cerebras AI."""

    def __init__(self):
        """Initialize analyzer with Cerebras client and prompt."""
        self.client = CerebrasClient()
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

        # Call Cerebras API
        response = self.client.chat_completion(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.5,  # Lower temp for structured output
            max_tokens=2500
        )

        # Parse JSON response
        try:
            cleaned = self._clean_json_response(response)
            analysis = json.loads(cleaned)

            # Ensure ats_score is an integer
            if 'ats_score' in analysis:
                try:
                    if isinstance(analysis['ats_score'], str):
                        # Extract first number found (e.g. "85/100" -> 85)
                        match = re.search(r'(\d+)', analysis['ats_score'])
                        if match:
                            analysis['ats_score'] = int(match.group(1))
                        else:
                            analysis['ats_score'] = 0
                    else:
                        analysis['ats_score'] = int(analysis['ats_score'])
                except (ValueError, TypeError):
                    analysis['ats_score'] = 0

            logger.info(
                f"Analysis completed. ATS Score: {analysis.get('ats_score', 'N/A')}")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analyzer response: {str(e)}")
            logger.debug(f"Raw response (first 500 chars): {response[:500]}")

            # Try to extract basic info with regex fallback
            try:
                fallback_analysis = self._fallback_parse(response)
                logger.info("Using fallback parsing method")
                return fallback_analysis
            except Exception as fallback_error:
                logger.error(
                    f"Fallback parsing also failed: {str(fallback_error)}")
                raise ValueError(
                    f"Failed to parse analyzer response: {str(e)}")

    def _clean_json_response(self, response: str) -> str:
        """Remove markdown code fences and cleanup JSON with enhanced error handling.
        """
        if not response or not response.strip():
            raise ValueError("Empty response received from API")

        response = response.strip()

        # Remove ```json and ``` markers
        if '```' in response:
            import re
            match = re.search(
                r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                response = match.group(1)
            else:
                # Fallback: remove fences manually
                response = re.sub(r'```(?:json)?', '', response)
                response = response.replace('```', '')

        # Find JSON object boundaries
        json_start = response.find('{')
        json_end = response.rfind('}')

        if json_start == -1 or json_end == -1 or json_end <= json_start:
            return response

        response = response[json_start:json_end+1]
        response = response.strip()

        # Fix common JSON issues safely
        # 1. Fix trailing commas before closing braces/brackets
        response = re.sub(r',\s*\}', '}', response)
        response = re.sub(r',\s*\]', ']', response)

        # 2. Fix missing commas between key-value pairs
        response = re.sub(r'"\s*\n?\s*"([^"]+)"\s*:', r'", "\1":', response)

        # 3. Fix missing commas between closing brace and next key
        response = re.sub(r'\}\s*\n?\s*"([^"]+)"\s*:', r'}, "\1":', response)

        return response

    def _fallback_parse(self, response: str) -> Dict:
        """Fallback parsing method for malformed JSON responses.

        Args:
            response: Raw response from API

        Returns:
            dict: Basic analysis structure
        """
        import re

        # Initialize basic structure
        analysis = {
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

        # Try to extract ATS score
        ats_match = re.search(r'"?ats_score"?\s*:\s*(\d+)',
                              response, re.IGNORECASE)
        if ats_match:
            analysis["ats_score"] = int(ats_match.group(1))

        # Try to extract keywords
        keyword_matches = re.findall(
            r'"?keyword"?\s*:\s*"([^"]+)"', response, re.IGNORECASE)
        if keyword_matches:
            analysis["keyword_analysis"]["matched_keywords"] = [
                {"keyword": kw, "jd_mentions": 1, "cv_mentions": 1}
                for kw in keyword_matches[:10]
            ]

        # Try to extract summary
        summary_match = re.search(
            r'"?summary"?\s*:\s*"([^"]+)"', response, re.IGNORECASE)
        if summary_match:
            analysis["summary"] = summary_match.group(1)

        return analysis
