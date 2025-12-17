"""Cover letter data models module.

This module defines the Pydantic data models for cover letters, including their structure,
validation rules, and relationships. These models define the core domain entities
for the cover letter composition system and are used for data validation, serialization,
and API documentation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, Field, field_validator

from app.database.models.base import BaseSchema


class CoverLetterData(BaseSchema):
    """Model representing the structured data of a cover letter.

    Attributes:
    ----------
        recipient_name (Optional[str]): Name of the hiring manager or recipient
        recipient_title (Optional[str]): Title of the recipient
        company_name (str): Name of the target company
        company_address (Optional[str]): Address of the company
        sender_name (str): Name of the sender (applicant)
        sender_email (EmailStr): Email address of the sender
        sender_phone (Optional[str]): Phone number of the sender
        sender_location (Optional[str]): Location/address of the sender
        job_title (str): Position being applied for
        job_reference (Optional[str]): Job reference number or ID
        introduction (str): Opening paragraph of the cover letter
        body_paragraphs (List[str]): Main content paragraphs
        closing (str): Closing paragraph
        signature (str): Professional closing and signature
    """

    recipient_name: Optional[str] = None
    recipient_title: Optional[str] = None
    company_name: str
    company_address: Optional[str] = None
    sender_name: str
    sender_email: EmailStr
    sender_phone: Optional[str] = None
    sender_location: Optional[str] = None
    job_title: str
    job_reference: Optional[str] = None
    introduction: str
    body_paragraphs: List[str] = Field(..., min_items=1, max_items=4)
    closing: str
    signature: str


class CoverLetter(BaseSchema):
    """Model representing a cover letter in the database.

    Attributes:
    ----------
        user_id (str): ID of the user who owns this cover letter
        title (str): Title/name of this cover letter
        resume_id (Optional[str]): ID of the associated resume (if any)
        target_company (str): Company this cover letter is for
        target_role (str): Position this cover letter is for
        job_description (str): Job description used for tailoring
        content_data (CoverLetterData): Structured cover letter data
        generated_content (Optional[str]): Final generated cover letter text
        template_name (str): Name of the template used
        is_generated (bool): Whether the cover letter has been generated
        created_at (datetime): When the cover letter was created
        updated_at (datetime): When the cover letter was last updated
    """

    user_id: str
    title: str
    resume_id: Optional[str] = None
    target_company: str
    target_role: str
    job_description: str
    content_data: CoverLetterData
    generated_content: Optional[str] = None
    template_name: str = "professional_template"
    is_generated: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CoverLetterTemplate(BaseSchema):
    """Model representing a cover letter template.

    Attributes:
    ----------
        name (str): Unique name identifier for the template
        display_name (str): Human-readable name for the template
        description (str): Description of the template style and use case
        template_content (str): The template structure with placeholders
        style (str): Style category (professional, modern, creative, etc.)
    """

    name: str
    display_name: str
    description: str
    template_content: str
    style: str


class CoverLetterRequest(BaseSchema):
    """Schema for creating a new cover letter request."""

    title: str = Field(..., description="Title of the cover letter")
    resume_id: Optional[str] = Field(None, description="Associated resume ID")
    target_company: str = Field(..., description="Target company")
    target_role: str = Field(..., description="Target position/role")
    job_description: str = Field(..., description="Job description")
    sender_name: str = Field(..., description="Applicant name")
    sender_email: EmailStr = Field(..., description="Applicant email")
    sender_phone: Optional[str] = Field(None, description="Applicant phone")
    sender_location: Optional[str] = Field(None, description="Applicant location")
    recipient_name: Optional[str] = Field(None, description="Hiring manager name")
    recipient_title: Optional[str] = Field(None, description="Hiring manager title")
    company_address: Optional[str] = Field(None, description="Company address")
    job_reference: Optional[str] = Field(None, description="Job reference number")
    template_name: str = Field("professional_template", description="Template to use")


class CoverLetterGenerationRequest(BaseSchema):
    """Schema for generating cover letter content."""

    introduction: str = Field(..., description="Introduction paragraph")
    body_paragraphs: List[str] = Field(..., min_items=1, max_items=4, description="Main body paragraphs")
    closing: str = Field(..., description="Closing paragraph")
    signature: str = Field(..., description="Professional closing")


class CoverLetterSummary(BaseSchema):
    """Schema for cover letter summary information."""

    id: str = Field(..., description="Unique identifier for the cover letter")
    title: str = Field(..., description="Title of the cover letter")
    target_company: str = Field(..., description="Target company")
    target_role: str = Field(..., description="Target position/role")
    is_generated: bool = Field(..., description="Whether the cover letter is generated")
    created_at: datetime = Field(..., description="When the cover letter was created")
    updated_at: datetime = Field(..., description="When the cover letter was last updated")
