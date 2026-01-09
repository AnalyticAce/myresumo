import json
import logging
import re
from typing import Dict, List, Optional

from ..prompts.prompt_loader import PromptLoader
from ..utils.shared_utils import JSONParser
from .ai_client import get_ai_client
from .cv_validator import CVValidator

# Compiled regex for email extraction to avoid recompilation on every call
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

logger = logging.getLogger(__name__)


class CVOptimizer:
    """Optimize CV sections based on job description using multi-provider AI."""

    _system_prompt = None
    _comprehensive_prompt = None

    def __init__(self):
        """Initialize optimizer."""
        self._client = None
        if CVOptimizer._system_prompt is None:
            loader = PromptLoader()
            CVOptimizer._system_prompt = loader.load_prompt('cv_optimizer')
            CVOptimizer._comprehensive_prompt = loader.load_prompt(
                'comprehensive_optimizer')
        logger.info("CVOptimizer initialized with comprehensive support")

    @property
    def client(self):
        """Lazy instantiation of AI client."""
        if self._client is None:
            self._client = get_ai_client()
        return self._client

    def optimize_comprehensive(
        self,
        cv_text: str,
        jd_text: str,
        analysis: Optional[Dict] = None,
        email: Optional[str] = None
    ) -> Dict:
        """Perform one-shot comprehensive CV optimization.

        Args:
            cv_text: Original CV text
            jd_text: Job description text
            analysis: Preliminary analysis from analyzer

        Returns:
            dict: Fully structured ResumeData JSON
        """
        logger.info("Starting comprehensive one-shot optimization")

        # Prepare email instruction
        email_instruction = ""
        if email:
            email_instruction = f"\n**EMAIL TO USE:** {email}\n"

        user_message = f"""
**JOB DESCRIPTION:**
{jd_text}

**CANDIDATE CV:**
{cv_text}
{email_instruction}
**PRELIMINARY ANALYSIS:**
{json.dumps(analysis, indent=2) if analysis else "Not provided"}
"""

        # Call AI API with low temp for structure
        response = self.client.chat_completion(
            system_prompt=CVOptimizer._comprehensive_prompt,
            user_message=user_message,
            temperature=0.2,
            max_tokens=8000
        )

        # Parse JSON response with fallback
        fallback_result = self._get_fallback_comprehensive_structure(cv_text, email)
        result = JSONParser.safe_json_parse(response, fallback_result)

        # Validate the optimization
        validation = CVValidator.validate_optimization(cv_text, result)

        # Log validation results
        if not validation['valid']:
            for error in validation['errors']:
                logger.error(f"CV Optimization Validation Error: {error}")

        if validation['warnings']:
            for warning in validation['warnings']:
                logger.warning(f"CV Optimization Warning: {warning}")

        # Add validation results to the output
        result['_validation'] = validation

        logger.info("Comprehensive optimization JSON parsed successfully")
        return result

    def optimize_section(
        self,
        original_section: str,
        jd_text: str,
        keywords: List[str],
        optimization_focus: str
    ) -> Dict:
        """Optimize a specific CV section.

        Args:
            original_section: Original CV section text
            jd_text: Job description text
            keywords: List of target keywords to include
            optimization_focus: Specific optimization instructions

        Returns:
            dict: Optimization results with optimized content and metadata
        """
        logger.info(f"Optimizing CV section with {len(keywords)} keywords")

        user_message = f"""
**ORIGINAL CV SECTION:**
{original_section}

**JOB DESCRIPTION:**
{jd_text}

**TARGET KEYWORDS:**
{', '.join(keywords)}

**OPTIMIZATION FOCUS:**
{optimization_focus}
"""

        # Call AI API
        response = self.client.chat_completion(
            system_prompt=CVOptimizer._system_prompt,
            user_message=user_message,
            temperature=0.6,  # Moderate temp for creative optimization
            max_tokens=2000
        )

        # Parse JSON response
        fallback_result = {
            "optimized_content": original_section,
            "keywords_used": [],
            "improvements_made": ["Optimization failed, returned original section"]
        }

        result = JSONParser.safe_json_parse(response, fallback_result)
        logger.info(
            f"Section optimization completed. Keywords used: {len(result.get('keywords_used', []))}")
        return result

    def optimize_professional_summary(
        self,
        cv_data: str,
        jd_text: str,
        keywords: List[str]
    ) -> Dict:
        """Optimize professional summary section.

        Args:
            cv_data: CV data (string or dict containing professional summary)
            jd_text: Job description text
            keywords: List of target keywords to include

        Returns:
            dict: Optimized professional summary
        """
        # Handle string input (current summary text)
        current_summary = ""
        if isinstance(cv_data, str):
            current_summary = cv_data
        elif isinstance(cv_data, dict):
            current_summary = cv_data.get('professional_summary', '')
            if not current_summary:
                current_summary = cv_data.get('summary', '')

        if not current_summary or current_summary.strip() == "":
            # Create a basic summary
            current_summary = "Experienced professional with technical expertise and proven track record."

        optimization_focus = (
            "Create a compelling 3-4 line professional summary that highlights "
            "key qualifications, emphasizes target keywords, and targets the "
            "specific role requirements. Focus on achievements and unique value proposition."
        )

        return self.optimize_section(
            original_section=f"PROFESSIONAL SUMMARY\n\n{current_summary}",
            jd_text=jd_text,
            keywords=keywords,
            optimization_focus=optimization_focus
        )

    def _get_fallback_comprehensive_structure(self, cv_text: str = "", email: Optional[str] = None) -> Dict:
        """Get fallback comprehensive structure with basic extraction from original CV.

        Args:
            cv_text: Original CV text to extract basic info from

        Returns:
            dict: Basic comprehensive structure for fallback cases
        """
        # Try to extract basic information from CV text
        name = "Candidate"

        # Use provided email, or extract from CV, or use better placeholder
        if not email and cv_text:
            # Extract email from CV text if not provided
            email_match = EMAIL_REGEX.search(cv_text)
            if email_match:
                email = email_match.group()

        # Use placeholder if no email found/provided
        if not email:
            email = "please-add-your-email@example.com"

        logger.warning(
            f"Using fallback structure with extracted name: {name[:30]}...")

        return {
            "user_information": {
                "name": name,
                "main_job_title": "Professional",
                "profile_description": "Experienced professional with technical expertise.",
                "email": email,
                "experiences": [],
                "education": [],
                "skills": {"hard_skills": [], "soft_skills": []}
            },
            "projects": []
        }

    def _extract_optimized_section(self, response: Dict) -> str:
        """Extract just the optimized content from response.

        Args:
            response: Full optimization response

        Returns:
            str: Optimized section content only
        """
        return response.get('optimized_content', '')
