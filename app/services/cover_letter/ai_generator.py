"""AI-powered cover letter generator using CerebrasAI."""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from app.config import computed_settings as settings
from app.services.llm.prompts.cover_letter_prompts import (
    COVER_LETTER_PROMPT,
    COVER_LETTER_SYSTEM_PROMPT
)

class AICoverLetterGenerator:
    """Service for generating cover letters using AI."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the AI cover letter generator.
        
        Args:
            model_name: Name of the CerebrasAI model to use (defaults to API_MODEL_NAME from env)
        """
        self.model_name = model_name or settings.API_MODEL_NAME
        self.client = OpenAI(
            base_url=settings.API_BASE,
            api_key=settings.CEREBRASAI_API_KEY
        )
    
    async def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        company_name: str,
        job_title: str,
        tone: str = "professional",
        length: str = "medium",
        additional_instructions: str = ""
    ) -> str:
        """Generate a tailored cover letter using AI.
        
        Args:
            resume_text: The user's resume/CV text
            job_description: The job description to tailor the cover letter to
            company_name: Name of the target company
            job_title: Job title being applied for
            tone: Desired tone (e.g., professional, enthusiastic, formal)
            length: Desired length (short, medium, long)
            additional_instructions: Any specific instructions for the AI
            
        Returns:
            Generated cover letter text
        """
        # Format the prompt with the provided information
        prompt = COVER_LETTER_PROMPT.format(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            resume=resume_text,
            tone=tone,
            length=length,
            additional_instructions=additional_instructions
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": COVER_LETTER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate cover letter: {str(e)}")

# Example usage:
# generator = AICoverLetterGenerator()
# cover_letter = await generator.generate_cover_letter(
#     resume_text="...",
#     job_description="...",
#     company_name="Acme Inc.",
#     job_title="Software Engineer"
# )
