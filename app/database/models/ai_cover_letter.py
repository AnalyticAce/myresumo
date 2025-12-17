"""AI cover letter generation models."""

from pydantic import BaseModel, Field
from typing import Optional

class AICoverLetterRequest(BaseModel):
    """Request model for generating a cover letter with AI."""
    
    resume_text: str = Field(..., description="The full text of the user's resume/CV")
    job_description: str = Field(..., description="The job description to tailor the cover letter to")
    company_name: str = Field(..., description="Name of the target company")
    job_title: str = Field(..., description="Job title being applied for")
    tone: str = Field(
        "professional",
        description="Tone of the cover letter (e.g., professional, enthusiastic, formal)",
        pattern="^(professional|enthusiastic|formal|conversational|executive)$"
    )
    length: str = Field(
        "medium",
        description="Desired length of the cover letter",
        pattern="^(short|medium|long)$"
    )
    additional_instructions: Optional[str] = Field(
        None,
        description="Any specific instructions for the AI"
    )
    template_name: Optional[str] = Field(
        "professional_template",
        description="Name of the template to use for formatting"
    )


class AICoverLetterResponse(BaseModel):
    """Response model for AI-generated cover letters."""
    
    content: str = Field(..., description="The generated cover letter content")
    template_name: str = Field(..., description="Name of the template used")
    model: str = Field(..., description="The AI model used for generation")
