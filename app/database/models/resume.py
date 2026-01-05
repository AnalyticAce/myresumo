"""Resume data models module.

This module defines the Pydantic data models for resumes, including their structure,
validation rules, and relationships. These models define the core domain entities
for the resume optimization system and are used for data validation, serialization,
and API documentation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, Field, field_validator

from app.database.models.base import BaseSchema


class Experience(BaseSchema):
    """Model representing a work experience entry in a resume.

    Attributes:
    ----------
        job_title (str): The job title/position held
        company (str): The company or organization name
        location (Optional[str]): The location/city of the job
        start_date (str): When the job started (stored as string for flexibility)
        end_date (str): When the job ended (or "Present" for current positions)
        four_tasks (List[str]): List of four key responsibilities or achievements
    """

    job_title: str
    company: str
    location: Optional[str] = None
    start_date: str
    end_date: str
    four_tasks: List[str] = Field(..., min_length=1, max_length=6)


class Education(BaseSchema):
    """Model representing an education entry in a resume.

    Attributes:
    ----------
        institution (str): Name of the educational institution
        degree (str): The degree or qualification obtained
        description (Optional[str]): Additional details about the education
        start_date (str): When education began
        end_date (str): When education completed (or "Present")
    """

    institution: str
    degree: str
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: str
    end_date: str


class Skills(BaseSchema):
    """Model representing skills in a resume.

    Attributes:
    ----------
        hard_skills (List[str]): List of technical/professional skills
        soft_skills (List[str]): List of interpersonal/soft skills
    """

    hard_skills: List[str]
    soft_skills: List[str]


class UserInformation(BaseSchema):
    """Model representing basic user information in a resume.

    Attributes:
    ----------
        name (str): The full name of the resume owner
        main_job_title (str): Primary professional title
        profile_description (str): Professional summary or objective
        email (EmailStr): Contact email address
        linkedin (Optional[str]): LinkedIn profile URL or username
        github (Optional[str]): GitHub profile URL or username
        experiences (List[Experience]): List of work experiences
        education (List[Education]): List of education entries
        skills (Skills): Technical and soft skills
        hobbies (Optional[List[str]]): List of hobbies/interests
    """

    name: str
    main_job_title: str
    profile_description: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    languages: Optional[List[str]] = None
    experiences: List[Experience]
    education: List[Education]
    skills: Skills
    hobbies: Optional[List[str]] = None


class Project(BaseSchema):
    """Model representing a project in a resume.

    Attributes:
    ----------
        project_name (str): Name of the project
        two_goals_of_the_project (List[str]): Two main goals or objectives
        project_end_result (str): The outcome or result of the project
        tech_stack (Optional[List[str]]): Technologies used in the project
    """

    project_name: str
    two_goals_of_the_project: List[str] = Field(
        ..., min_length=1, max_length=4)
    project_end_result: str
    tech_stack: Optional[List[str]] = None


class Certificate(BaseSchema):
    """Model representing a professional certificate in a resume.

    Attributes:
    ----------
        name (str): Name of the certification
        institution (str): Organization that issued the certificate
        description (Optional[str]): Details about the certification
        date (str): When the certification was obtained
    """

    name: str
    institution: str
    description: Optional[str] = None
    date: str


class ExtraCurricularActivity(BaseSchema):
    """Model representing an extracurricular activity in a resume.

    Attributes:
    ----------
        name (str): Name of the activity
        description (str): Details about the activity
        start_date (Optional[str]): When the activity began
        end_date (Optional[str]): When the activity ended (or "Present")
    """

    name: str
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ResumeData(BaseSchema):
    """Complete model for resume data that will be used for AI optimization and PDF generation.

    Attributes:
    ----------
        user_information (UserInformation): Basic personal and professional info
        projects (Optional[List[Project]]): List of projects
        certificate (Optional[List[Certificate]]): List of certificates
        extra_curricular_activities (Optional[List[ExtraCurricularActivity]]): List of activities
    """

    user_information: UserInformation
    projects: Optional[List[Project]] = None
    certificate: Optional[List[Certificate]] = None
    extra_curricular_activities: Optional[List[ExtraCurricularActivity]] = None


class Resume(BaseSchema):
    """Model representing a resume in the database.

    Attributes:
    ----------
        user_id (str): ID of the user who owns this resume
        title (str): Title/name of this resume version
        original_content (str): The original uploaded resume content as text
        job_description (str): The job description used for optimization
        optimized_data (Optional[ResumeData]): AI-optimized resume data
        ats_score (Optional[int]): ATS compatibility score (0-100)
        original_ats_score (Optional[int]): Score of the original resume before optimization
        matching_skills (Optional[List[str]]): Skills that match the job description
        missing_skills (Optional[List[str]]): Skills missing from resume but in job description
        score_improvement (Optional[int]): Difference between optimized and original scores
        recommendation (Optional[str]): AI recommendation for improving the resume
        created_at (datetime): When the resume was created
        updated_at (datetime): When the resume was last updated

    """

    user_id: str
    title: str
    original_content: str
    job_description: str
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    # Master CV fields
    master_content: Optional[str] = None  # Original master CV content
    master_filename: Optional[str] = None  # Safe master CV filename
    original_filename: Optional[str] = None  # Original uploaded filename
    master_file_type: Optional[str] = None  # Original master CV file type
    master_file_path: Optional[str] = None  # Secure file storage path
    master_file_hash: Optional[str] = None  # File hash for deduplication
    # When master CV was last updated
    master_updated_at: Optional[datetime] = None
    # Status fields for application tracking
    application_status: str = Field(
        default="not_applied", description="Application status: not_applied, applied, answered, rejected, interview")
    is_applied: bool = False  # Whether the resume has been sent/applied
    applied_date: Optional[datetime] = None  # When the resume was applied
    is_answered: bool = False  # Whether there's been a response
    answered_date: Optional[datetime] = None  # When there was a response
    optimized_data: Optional[ResumeData] = None
    matching_score: Optional[int] = None
    # Score of the original resume before optimization
    original_matching_score: Optional[int] = None
    # Skills that match the job description
    matching_skills: Optional[List[str]] = None
    # Skills missing from resume but in job description
    missing_skills: Optional[List[str]] = None
    # Difference between optimized and original scores
    score_improvement: Optional[int] = None
    # AI recommendation for improving the resume
    recommendation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("matching_score", "original_matching_score")
    @classmethod
    def validate_matching_score(cls, v):
        """Validate that matching score is between 0 and 100."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Matching score must be between 0 and 100")
        return v
