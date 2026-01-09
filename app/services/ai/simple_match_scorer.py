"""Simple AI-powered resume-job matching scorer using Cerebras AI.

This module provides a simplified scoring system that uses Cerebras AI directly
to calculate how well a resume matches a job description.
"""

import json
import re
from typing import Dict, List, Optional

from openai import OpenAI

from app.config import computed_settings as settings


class SimpleMatchScorer:
    """Simplified resume-job matching scorer using Cerebras AI."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the scorer with Cerebras AI client.
        
        Args:
            model_name: Name of the model to use (defaults to API_MODEL_NAME from settings)
        """
        self.model_name = model_name or settings.API_MODEL_NAME
        self.client = OpenAI(
            base_url=settings.API_BASE,
            api_key=settings.CEREBRASAI_API_KEY
        )
    
    async def calculate_match_score(
        self, 
        resume_text: str, 
        job_description: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """Calculate a comprehensive match score between resume and job description.
        
        Args:
            resume_text: The candidate's resume text
            job_description: The job description text
            user_id: Optional user ID for tracking
            
        Returns:
            Dictionary containing match score and analysis
        """
        try:
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(resume_text, job_description)
            
            # Get AI analysis
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert ATS (Applicant Tracking System) analyzer and recruiter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            analysis = self._parse_analysis_response(result_text)
            
            # Ensure we have all required fields
            analysis.update({
                "user_id": user_id,
                "model_used": self.model_name,
                "success": True
            })
            
            return analysis
            
        except Exception as e:
            # Return error fallback
            return {
                "score": 50,
                "matching_skills": [],
                "missing_skills": [],
                "recommendation": "Unable to analyze due to an error. Please try again.",
                "rationale": f"Analysis failed: {str(e)}",
                "user_id": user_id,
                "model_used": self.model_name,
                "success": False,
                "error": str(e)
            }
    
    def _create_analysis_prompt(self, resume_text: str, job_description: str) -> str:
        """Create the analysis prompt for the AI.
        
        Args:
            resume_text: The resume text
            job_description: The job description
            
        Returns:
            The formatted prompt string
        """
        return f"""Analyze how well this candidate's resume matches the job requirements.

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
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the AI response into a structured dictionary.
        
        Args:
            response_text: The raw response from the AI
            
        Returns:
            Parsed analysis dictionary
        """
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                
                # Validate and fix the parsed data
                return {
                    "score": min(100, max(0, int(parsed.get("score", 50)))),
                    "matching_skills": self._ensure_list(parsed.get("matching_skills", [])),
                    "missing_skills": self._ensure_list(parsed.get("missing_skills", [])),
                    "recommendation": str(parsed.get("recommendation", "No recommendation provided."))[:500],
                    "rationale": str(parsed.get("rationale", "No rationale provided."))[:500]
                }
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response text: {response_text[:500]}...")
        
        # Fallback: try to extract score manually
        score_match = re.search(r'score["\']?\s*:\s*(\d+)', response_text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 50
        
        return {
            "score": min(100, max(0, score)),
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": "Analysis completed but response format was unclear.",
            "rationale": "Score extracted from response but detailed analysis could not be parsed."
        }
    
    def _ensure_list(self, value) -> List[str]:
        """Ensure the value is a list of strings.
        
        Args:
            value: Value to convert to list
            
        Returns:
            List of strings
        """
        if isinstance(value, list):
            return [str(item) for item in value if item]
        elif isinstance(value, str):
            # Try to parse if it looks like a JSON list string
            if value.startswith('[') and value.endswith(']'):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed if item]
                except:
                    pass
            return [value]
        else:
            return [str(value)] if value else []


# Convenience function for backward compatibility
async def compute_match_score(
    resume_text: str, 
    job_description: str, 
    weights: Optional[Dict] = None,
    user_id: Optional[str] = None
) -> Dict:
    """Compute match score between resume and job description.
    
    Args:
        resume_text: The candidate's resume text
        job_description: The job description text
        weights: Ignored, kept for backward compatibility
        user_id: Optional user ID for tracking
        
    Returns:
        Dictionary containing match score and analysis
    """
    scorer = SimpleMatchScorer()
    return await scorer.calculate_match_score(resume_text, job_description, user_id)


# Example usage
async def demo_simple_match_scorer():
    """Demo function to showcase the SimpleMatchScorer functionality."""
    scorer = SimpleMatchScorer()
    
    resume = """
    John Doe
    Software Engineer with 5 years of experience in Python, Django, and React.
    Experience building web applications, REST APIs, and working with databases.
    """
    
    job_desc = """
    Senior Software Engineer
    Requirements: 5+ years Python experience, Django framework, React frontend, 
    database design, REST APIs.
    """
    
    result = await scorer.calculate_match_score(resume, job_desc)
    
    print(f"Score: {result['score']}%")
    print(f"Matching Skills: {', '.join(result['matching_skills'])}")
    print(f"Missing Skills: {', '.join(result['missing_skills'])}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Rationale: {result['rationale']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_simple_match_scorer())
