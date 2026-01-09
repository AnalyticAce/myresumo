"""Advanced Resume Optimization Service.

Uses comprehensive prompt engineering for professional resume optimization.
"""

import logging
from typing import Any, Dict

from ..llm.universal import get_llm

logger = logging.getLogger(__name__)


class AdvancedResumeOptimizer:
    """Advanced optimizer using comprehensive prompt engineering."""
    
    def __init__(self, **llm_config):
        """Initialize the optimizer with LLM configuration."""
        self.llm = get_llm(**llm_config)
    
    async def optimize_resume_comprehensive(
        self,
        resume_text: str,
        job_description: str,
        job_title: str = "",
        company: str = "",
        focus_area: str = "backend/data",
        seniority: str = "mid-senior"
    ) -> Dict[str, Any]:
        """Run comprehensive resume optimization using the master prompt."""
        master_prompt = f"""You are optimizing a resume for a job application.

TARGET JOB: {job_title} at {company}

JOB DESCRIPTION:
{job_description}

CURRENT RESUME:
{resume_text}

TASK: Create an optimized resume that:
1. Keeps ALL real experiences, education, and skills from the original
2. Adds relevant keywords from the job description
3. Formats professionally

IMPORTANT: Extract and use the ACTUAL work experience from the current resume. Do not invent or omit any real positions.

OUTPUT FORMAT:
John Doe
john.doe@example.com | +31 6 12345678 | 123 Main St, Amsterdam, The Netherlands

PROFESSIONAL SUMMARY
[3-4 lines highlighting relevant experience]

SKILLS
Hard Skills: [extract from resume + add relevant from JD]
Soft Skills: [extract from resume]

EXPERIENCE
[Extract ALL real experiences from current resume with dates and achievements]

EDUCATION
[Extract from current resume]

READY FOR INTERVIEW"""

        try:
            result = await self.llm.complete(
                prompt=master_prompt,
                temperature=0.3  # Lower temperature for consistency
            )
            
            return {
                "success": True,
                "optimized_resume": result,  # result is already a string
                "method": "comprehensive_master_prompt"
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive optimization: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "comprehensive_master_prompt"
            }
    
    async def ats_keyword_analysis(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """ATS keyword and gap analysis."""
        prompt = f"""Analyze JD vs resume for ATS gaps:

JD: {job_description}
Resume: {resume_text}

1) Extract 20 keywords from JD, categorize, prioritize
2) Table: Keyword | Priority | Coverage | Fix
3) Bullet-level rewrite suggestions for top 5 gaps"""

        try:
            result = await self.llm.complete(prompt=prompt, temperature=0.2)
            
            return {
                "success": True,
                "analysis": result,  # result is already a string
                "method": "ats_keyword_analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in ATS analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "ats_keyword_analysis"
            }
    
    async def create_three_versions(
        self,
        resume_text: str,
        job_description: str,
        job_title: str = ""
    ) -> Dict[str, Any]:
        """Create 3 resume positioning variants."""
        prompt = f"""Create 3 resume positioning variants for this JD:

JD: {job_description}
Resume: {resume_text}
Role: {job_title}

1) Results-focused ($$/ROI/business impact)
2) Leadership-focused (teams/mentoring/collaboration)  
3) Technical-depth (architecture/scale/innovation)

Each: summary + 4 bullets + when to use."""

        try:
            result = await self.llm.complete(prompt=prompt, temperature=0.3)
            
            return {
                "success": True,
                "variants": result,  # result is already a string
                "method": "three_version_positioning"
            }
            
        except Exception as e:
            logger.error(f"Error creating variants: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "three_version_positioning"
            }
    
    async def quick_ats_pass(
        self,
        resume_text: str,
        job_description: str,
        job_title: str = ""
    ) -> Dict[str, Any]:
        """5-minute ATS pass for emergency applications."""
        prompt = f"""Quick ATS optimization for emergency application:

Role: {job_title}
JD: {job_description}
Resume: {resume_text}

Tasks:
1. Step-back analysis: key skills/requirements (5-10)
2. Keyword extraction: 15-20 critical ATS keywords
3. Skills optimization: match JD keywords exactly
4. Conservative professional summary

Focus on ATS keywords and basic relevance. Output optimized resume."""

        try:
            result = await self.llm.complete(prompt=prompt, temperature=0.1)
            
            return {
                "success": True,
                "optimized_resume": result,  # result is already a string
                "method": "quick_ats_pass"
            }
            
        except Exception as e:
            logger.error(f"Error in quick ATS pass: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "quick_ats_pass"
            }


# Convenience function for easy usage
async def optimize_resume_advanced(
    resume_text: str,
    job_description: str,
    method: str = "comprehensive",
    **kwargs
) -> Dict[str, Any]:
    """Optimize resume using advanced prompts."""
    optimizer = AdvancedResumeOptimizer()
    
    if method == "comprehensive":
        return await optimizer.optimize_resume_comprehensive(
            resume_text=resume_text,
            job_description=job_description,
            **kwargs
        )
    elif method == "ats_analysis":
        return await optimizer.ats_keyword_analysis(
            resume_text=resume_text,
            job_description=job_description
        )
    elif method == "three_versions":
        return await optimizer.create_three_versions(
            resume_text=resume_text,
            job_description=job_description,
            **kwargs
        )
    elif method == "quick_ats":
        return await optimizer.quick_ats_pass(
            resume_text=resume_text,
            job_description=job_description,
            **kwargs
        )
    else:
        raise ValueError(f"Unknown optimization method: {method}")
