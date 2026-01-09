"""Resume API router module for resume management operations.

This module implements the API endpoints for resume-related functionality including
resume creation, retrieval, optimization, PDF generation and deletion. It handles
the interface between HTTP requests and the resume repository, and coordinates
AI-powered resume optimization services.
"""

import json
import logging
import os
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

from app.config.templates import TemplateConfig
from app.database.models.resume import Resume, ResumeData
from app.database.repositories.resume_repository import ResumeRepository
from app.middleware.rate_limit import heavy_limit, light_limit
from app.services.file_validator import SecureFileValidator, store_file_securely
from app.services.resume.typst_generator import TypstGenerator
from app.services.resume.universal_scorer import UniversalResumeScorer
from app.utils.file_handling import extract_text_from_file

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Supported file extensions for resume uploads
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.md', '.markdown']


def validate_object_id(object_id: str) -> ObjectId:
    """Validate and convert string to ObjectId.

    Args:
        object_id: String representation of ObjectId

    Returns:
        ObjectId: Validated ObjectId instance

    Raises:
        HTTPException: If the object_id is invalid
    """
    try:
        return ObjectId(object_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )


# Request and response models
class CreateResumeRequest(BaseModel):
    """Schema for creating a new resume."""

    user_id: str = Field(..., description="Unique identifier for the user")
    title: str = Field(..., description="Title of the resume")
    original_content: str = Field(...,
                                  description="Original content of the resume")
    job_description: str = Field(
        ..., description="Job description to tailor the resume for"
    )


class OptimizeResumeRequest(BaseModel):
    """Schema for optimizing an existing resume."""

    job_description: str = Field(
        ..., description="Job description to tailor the resume for"
    )

    target_company: Optional[str] = Field(
        None, description="Target company for which this resume is optimized"
    )
    target_role: Optional[str] = Field(
        None, description="Target position/role for which this resume is optimized"
    )
    email: Optional[str] = Field(
        None, description="Email address to include in the optimized resume"
    )


class ResumeSummary(BaseModel):
    """Schema for resume summary information."""

    id: str = Field(..., description="Unique identifier for the resume")
    title: str = Field(..., description="Title of the resume")
    matching_score: Optional[int] = Field(
        None, description="Matching score of the resume if optimized"
    )
    application_status: Optional[str] = Field(
        "not_applied", description="Application status: not_applied, applied, answered, rejected, interview"
    )
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    main_job_title: Optional[str] = None
    skills_preview: List[str] = Field(default_factory=list)
    created_at: datetime = Field(...,
                                 description="When the resume was created")
    updated_at: datetime = Field(...,
                                 description="When the resume was last updated")


class OptimizationResponse(BaseModel):
    """Schema for resume optimization response."""

    resume_id: str = Field(
        ..., description="Unique identifier for the optimized resume"
    )
    original_matching_score: int = Field(...,
                                         description="Matching score before optimization")
    optimized_matching_score: int = Field(...,
                                          description="Matching score after optimization")
    score_improvement: int = Field(
        ..., description="Score improvement after optimization"
    )
    matching_skills: List[str] = Field(
        [], description="Skills that match the job description"
    )
    missing_skills: List[str] = Field(
        [], description="Skills missing from the resume")
    recommendation: str = Field(
        "", description="AI recommendation for improvement")
    optimized_data: Dict[str,
                         Any] = Field(..., description="Optimized resume data")


class ContactFormRequest(BaseModel):
    """Schema for contact form submission."""

    name: str = Field(..., description="Full name of the person reaching out")
    email: EmailStr = Field(...,
                            description="Email address for return communication")
    subject: str = Field(..., description="Subject of the contact message")
    message: str = Field(..., description="Detailed message content")


class ContactFormResponse(BaseModel):
    """Schema for contact form response."""

    success: bool = Field(...,
                          description="Whether the message was sent successfully")
    message: str = Field(..., description="Status message")


class ScoreResumeRequest(BaseModel):
    """Schema for scoring an existing resume."""

    job_description: str = Field(
        ..., description="Job description to score the resume against"
    )


class ResumeScoreResponse(BaseModel):
    """Schema for resume score response."""

    resume_id: str = Field(..., description="Unique identifier for the resume")
    ats_score: int = Field(..., description="ATS compatibility score (0-100)")
    matching_skills: List[str] = Field(
        [], description="Skills that match the job description"
    )
    missing_skills: List[str] = Field(
        [], description="Skills missing from the resume")
    recommendation: str = Field(
        "", description="AI recommendation for improvement")
    resume_skills: List[str] = Field(
        [], description="Skills extracted from the resume")
    job_requirements: List[str] = Field(
        [], description="Requirements extracted from the job description"
    )


resume_router = APIRouter(prefix="/api/resume", tags=["Resume"])


async def get_resume_repository(request: Request) -> ResumeRepository:
    """Dependency for getting the resume repository instance.

    Args:
        request: The incoming request

    Returns:
    -------
        ResumeRepository: An instance of the resume repository
    """
    return ResumeRepository()


@resume_router.post(
    "/",
    response_model=Dict[str, str],
    summary="Create a resume",
    response_description="Resume created successfully",
)
async def create_resume(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(default="Untitled Resume"),
    job_description: str = Form(default=""),
    user_id: str = Form(default="local-user"),
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Create a new resume from uploaded file.

    This endpoint accepts PDF, DOCX, MD, and TXT file uploads, extracts the text content,
    and creates a new resume entry in the database.

    Args:
        request: The incoming request
        file: Uploaded resume file (PDF, DOCX, MD, or TXT)
        title: Title for the resume
        job_description: Job description to tailor the resume for
        user_id: ID of the user creating the resume
        repo: Resume repository instance

    Returns:
    -------
        Dict containing the ID of the created resume

    Raises:
    ------
        HTTPException: If the resume creation fails
    """
    try:
        logger.info("Resume upload started", extra={"user_id": user_id, "operation": "resume_upload"})

        # Secure file validation
        file_content, safe_filename, file_hash = await SecureFileValidator.validate_upload(file)
        logger.debug("File validation completed", extra={
            "content_length": len(file_content),
            "file_extension": Path(safe_filename).suffix.lower(),
            "operation": "resume_upload"
        })

        # Ensure file_content is bytes
        if not isinstance(file_content, bytes):
            logger.error("File content validation failed", extra={
                "error": "invalid_content_type",
                "content_type": str(type(file_content)),
                "operation": "resume_upload"
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file content format"
            )

        # Validate file size
        if len(file_content) == 0:
            logger.error("File content validation failed", extra={
                "error": "empty_file",
                "operation": "resume_upload"
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        file_extension = Path(safe_filename).suffix.lower()

        # Validate file extension
        if file_extension not in SUPPORTED_EXTENSIONS:
            logger.error("File extension validation failed", extra={
                "error": "unsupported_extension",
                "file_extension": file_extension,
                "supported_extensions": SUPPORTED_EXTENSIONS,
                "operation": "resume_upload"
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension: {file_extension}"
            )

        # Store file securely
        logger.info("Storing uploaded file", extra={"operation": "resume_upload", "step": "file_storage"})
        stored_file_path = store_file_securely(file_content, safe_filename, user_id)
        logger.debug("File stored successfully", extra={"operation": "resume_upload", "step": "file_storage"})

        # Create temporary file for text extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Extract text based on file type (avoid logging full temp path for security)
            logger.info("Extracting text from uploaded file", extra={
                "file_extension": file_extension,
                "operation": "resume_upload",
                "step": "text_extraction"
            })
            logger.info(f"Extracting text from uploaded {file_extension} file")
            resume_text = extract_text_from_file(
                temp_file_path, file_extension)
            logger.info("Text extraction successful", extra={
                "characters_extracted": len(resume_text),
                "operation": "resume_upload",
                "step": "text_extraction"
            })

            # Check if extraction failed
            if resume_text.startswith("Error:") or resume_text.startswith("Unsupported file format:"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=resume_text
                )

        finally:
            os.unlink(temp_file_path)

        new_resume = Resume(
            user_id=user_id,
            title=title,
            original_content=resume_text,
            job_description=job_description,
            master_content=resume_text,  # Store as master CV initially
            master_filename=safe_filename,  # Use safe filename
            original_filename=file.filename,  # Store original filename
            master_file_type=file.content_type,
            master_file_path=stored_file_path,  # Store secure file path
            master_file_hash=file_hash,  # Store file hash for deduplication
            master_updated_at=datetime.now(),
        )

        logger.info("Creating resume in database", extra={"operation": "resume_upload", "step": "database_save"})
        resume_id = await repo.create_resume(new_resume)
        if not resume_id:
            logger.error("Database create_resume returned empty ID", extra={
                "operation": "resume_upload",
                "step": "database_save",
                "error": "empty_resume_id"
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create resume",
            )
        logger.info("Resume created successfully", extra={
            "resume_id": resume_id,
            "operation": "resume_upload",
            "step": "database_save"
        })
        return {"id": resume_id}
    except HTTPException:
        # Re-raise HTTPExceptions as-is (they're already properly handled)
        raise
    except Exception:
        # Log unexpected errors before converting to HTTPException
        logger.error("Unexpected error creating resume", exc_info=True, extra={
            "operation": "resume_upload",
            "error_type": "unexpected_exception"
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating resume",
        )


@resume_router.put(
    "/{resume_id}/master",
    response_model=Dict[str, str],
    summary="Replace master CV",
    response_description="Master CV replaced successfully",
)
async def replace_master_cv(
    resume_id: str,
    request: Request,
    file: UploadFile = File(...),
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Replace the master CV for an existing resume.

    This endpoint accepts a new file upload to replace the master CV content.
    The existing optimized data will be preserved but can be re-optimized.

    Args:
        resume_id: ID of the resume to update
        request: The incoming request
        file: New master CV file (PDF, DOCX, MD, or TXT)
        repo: Resume repository instance

    Returns:
    -------
        Dict containing success message

    Raises:
    ------
        HTTPException: If the resume doesn't exist or file replacement fails
    """
    try:
        # Validate file format
        supported_formats = ['.pdf', '.docx', '.md', '.markdown', '.txt']
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}"
            )

        # Get existing resume
        resume = await repo.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        # Extract text from new file
        file_content = await file.read()

        # Reset file position for potential reuse
        await file.seek(0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            new_master_content = extract_text_from_file(
                temp_file_path, file_extension)

            # Check if extraction failed
            if new_master_content.startswith("Error:") or new_master_content.startswith("Unsupported file format:"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=new_master_content
                )

        finally:
            os.unlink(temp_file_path)

        # Update resume with new master CV
        update_data = {
            "master_content": new_master_content,
            "master_filename": file.filename,
            "master_file_type": file.content_type,
            "master_updated_at": datetime.now(),
            "original_content": new_master_content,  # Also update current content
        }

        success = await repo.update_resume(resume_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update master CV"
            )

        return {"message": "Master CV replaced successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error replacing master CV: {str(e)}",
        )


@resume_router.post(
    "/master-cv",
    response_model=Dict[str, str],
    summary="Upload master CV",
    response_description="Master CV uploaded successfully",
)
async def upload_master_cv(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    user_id: str = Form(default="local-user"),
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Upload a new master CV.

    This endpoint creates a new master CV that can be used as a base for creating optimized resumes.

    Args:
        request: The incoming request
        file: Master CV file (PDF, DOCX, MD, or TXT)
        title: Title for the master CV
        user_id: ID of the user uploading the master CV
        repo: Resume repository instance

    Returns:
    -------
        Dict containing success message and master CV ID

    Raises:
    ------
        HTTPException: If file upload fails or format is unsupported
    """
    try:
        # Validate file format
        supported_formats = ['.pdf', '.docx', '.md', '.markdown', '.txt']
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}"
            )

        # Extract text from file
        file_content = await file.read()

        # Reset file position for potential reuse
        await file.seek(0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            master_content = extract_text_from_file(
                temp_file_path, file_extension)

            # Check if extraction failed
            if master_content.startswith("Error:") or master_content.startswith("Unsupported file format:"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=master_content
                )

        finally:
            os.unlink(temp_file_path)

        # Create master CV entry
        master_cv = Resume(
            user_id=user_id,
            title=title,
            original_content=master_content,
            job_description="",  # Empty for master CV
            master_content=master_content,
            master_filename=file.filename,
            master_file_type=file.content_type,
            master_updated_at=datetime.now(),
        )

        master_cv_id = await repo.create_resume(master_cv)
        if not master_cv_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create master CV",
            )

        return {"message": "Master CV uploaded successfully", "id": master_cv_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading master CV: {str(e)}",
        )


@resume_router.get(
    "/master-cvs",
    response_model=List[Dict[str, Any]],
    summary="Get all master CVs",
    response_description="Master CVs retrieved successfully",
)
async def get_master_cvs(
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Get all master CVs for the user.

    This endpoint retrieves all master CVs that have master_content set.

    Args:
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        List of master CV dictionaries

    Raises:
    ------
        HTTPException: If retrieval fails
    """
    try:
        # Get all resumes and filter for master CVs
        all_resumes = await repo.get_resumes_by_user_id("local-user")
        master_cvs = [
            {
                "id": str(resume.get("_id")),
                "title": resume.get("title"),
                "master_filename": resume.get("master_filename"),
                "master_file_type": resume.get("master_file_type"),
                "master_updated_at": resume.get("master_updated_at"),
            }
            for resume in all_resumes
            if resume.get("master_content")
        ]

        return master_cvs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving master CVs: {str(e)}",
        )


@resume_router.get(
    "/master-cv/{master_cv_id}",
    response_model=Dict[str, Any],
    summary="Get master CV by ID",
    response_description="Master CV retrieved successfully",
)
async def get_master_cv_by_id(
    master_cv_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Get a specific master CV by ID.

    This endpoint retrieves a single master CV with all its details.

    Args:
        master_cv_id: ID of the master CV to retrieve
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
    Dict containing master CV details

    Raises:
    ------
    HTTPException: If master CV is not found or retrieval fails
    """
    try:
        # Get master CV by ID
        master_cv = await repo.get_resume_by_id(master_cv_id)
        if not master_cv or not master_cv.get("master_content"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Master CV not found"
            )

        return {
            "id": str(master_cv.get("_id")),
            "title": master_cv.get("title"),
            "master_filename": master_cv.get("master_filename"),
            "master_file_type": master_cv.get("master_file_type"),
            "master_file_path": master_cv.get("master_file_path"),
            "master_content": master_cv.get("master_content"),
            "master_updated_at": master_cv.get("master_updated_at"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving master CV: {str(e)}",
        )


@resume_router.get(
    "/test-master-cv",
    response_model=Dict[str, str],
    summary="Test master CV endpoint",
    response_description="Test endpoint working",
)
async def test_master_cv_endpoint(
    request: Request,
):
    """Test endpoint to verify master CV functionality."""
    return {"message": "Master CV endpoints are working"}


@resume_router.delete(
    "/master-cv/{master_cv_id}",
    response_model=Dict[str, str],
    summary="Delete master CV",
    response_description="Master CV deleted successfully",
)
async def delete_master_cv(
    master_cv_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Delete a master CV.

    This endpoint removes a master CV from the database.

    Args:
        master_cv_id: ID of the master CV to delete
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict containing success message

    Raises:
    ------
        HTTPException: If master CV is not found or deletion fails
    """
    try:
        # Check if master CV exists
        master_cv = await repo.get_resume_by_id(master_cv_id)
        if not master_cv or not master_cv.get("master_content"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Master CV not found"
            )

        # Delete the master CV
        success = await repo.delete_resume(master_cv_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete master CV"
            )

        return {"message": "Master CV deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting master CV: {str(e)}",
        )


@resume_router.get(
    "/templates",
    response_model=List[Dict[str, Any]],
    summary="Get available LaTeX templates",
    response_description="Available LaTeX templates retrieved successfully",
)
async def get_templates(
    request: Request,
):
    """Get all available LaTeX templates.

    This endpoint returns a list of available LaTeX templates with their
    descriptions and metadata.

    Args:
        request: The incoming request

    Returns:
    -------
        List of template dictionaries

    Raises:
    ------
        HTTPException: If template retrieval fails
    """
    try:
        template_dir = "data/sample_latex_templates"
        templates = []

        available_templates = [
            {
                "filename": "resume.typ",
                "name": "Classic Template",
                "description": "Clean, single-column layout suitable for all industries. Features a centered header and optimized spacing.",
                "style": "Professional",
                "margins": "Standard"
            },
            {
                "filename": "modern.typ",
                "name": "Modern Side-Column",
                "description": "Distinctive two-column layout with a sidebar for skills and contact info. Great for tech and creative roles.",
                "style": "Modern",
                "margins": "Full Bleed Sidebar"
            }
        ]

        return available_templates
        # No-op for now as we return static list above
        return available_templates

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {str(e)}",
        )


@resume_router.post(
    "/{resume_id}/cover-letter",
    response_model=Dict[str, Any],
    summary="Generate a cover letter",
    response_description="Cover letter generated successfully",
)
async def generate_cover_letter(
    resume_id: str,
    cover_letter_request: Dict[str, str] = Body(..., description="Cover letter generation parameters"),
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Generate a professional cover letter based on the resume and job details.

    Args:
        resume_id: ID of the resume to retrieve
        cover_letter_request: Dictionary containing company, position, and optional job description
        repo: Resume repository instance

    Returns:
    -------
        Dict containing the generated cover letter
    """
    try:
        # Validate resume_id format to prevent NoSQL injection
        validated_resume_id = validate_object_id(resume_id)

        # Retrieve the resume
        resume = await repo.get_resume_by_id(str(validated_resume_id))
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found",
            )

        # Extract job details
        company = cover_letter_request.get("company", "")
        position = cover_letter_request.get("position", "")
        job_description = cover_letter_request.get("job_description", "")

        if not company or not position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company and position are required",
            )

        # Get resume content
        resume_content = resume.get("master_content") or resume.get("original_content", "")

        # Initialize AI service for cover letter generation
        from app.services.cover_letter_gen import get_cover_letter_generator
        cover_letter_gen = await get_cover_letter_generator()

        # Generate the cover letter
        generated_letter = await cover_letter_gen.generate_cover_letter(
            resume_content=resume_content,
            company=company,
            position=position,
            job_description=job_description
        )

        return {
            "cover_letter": generated_letter,
            "company": company,
            "position": position
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cover letter: {str(e)}",
        )


@resume_router.get(
    "/{resume_id}",
    response_model=Dict[str, Any],
    summary="Get a resume",
    response_description="Resume retrieved successfully",
)
@light_limit()  # Light rate limiting for read operations
async def get_resume(
    resume_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Get a specific resume by ID.

    Args:
        resume_id: ID of the resume to retrieve
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict containing the resume data

    Raises:
    ------
        HTTPException: If the resume is not found
    """
    # Validate resume_id format to prevent NoSQL injection
    validated_resume_id = validate_object_id(resume_id)

    resume_data = await repo.get_resume_by_id(str(validated_resume_id))
    if not resume_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    resume_data["id"] = str(resume_data.pop("_id"))
    return resume_data


@resume_router.get(
    "/user/{user_id}",
    response_model=List[ResumeSummary],
    summary="Get all resumes for a user",
    response_description="Resumes retrieved successfully",
)
async def get_user_resumes(
    user_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
    sort_by: Optional[str] = Query(
        None, description="Sort by: date, company, title"),
    sort_order: Optional[str] = Query(
        "desc", description="Sort order: asc, desc"),
    filter_company: Optional[str] = Query(
        None, description="Filter by company"),
    filter_position: Optional[str] = Query(
        None, description="Filter by position/role"),
    filter_date_from: Optional[str] = Query(
        None, description="Filter by date from (YYYY-MM-DD)"),
    filter_date_to: Optional[str] = Query(
        None, description="Filter by date to (YYYY-MM-DD)"),
):
    """Get all resumes for a specific user with sorting and filtering.

    Args:
        user_id: ID of the user whose resumes to retrieve
        request: The incoming request
        repo: Resume repository instance
        sort_by: Sort field (date, company, title)
        sort_order: Sort order (asc, desc)
        filter_company: Filter by company name
        filter_position: Filter by position/role
        filter_date_from: Filter by date from (YYYY-MM-DD)
        filter_date_to: Filter by date to (YYYY-MM-DD)

    Returns:
    -------
        List of resume summaries for the specified user
    """
    resumes = await repo.get_resumes_by_user_id(user_id)
    formatted_resumes = []

    for resume in resumes:
        optimized_data = resume.get(
            "optimized_data") if isinstance(resume, dict) else None
        main_job_title = None
        skills_preview = []
        try:
            if isinstance(optimized_data, dict):
                ui = optimized_data.get("user_information")
                if isinstance(ui, dict):
                    main_job_title = ui.get("main_job_title")
                    skills = ui.get("skills")
                    if isinstance(skills, dict):
                        hs = skills.get("hard_skills")
                        ss = skills.get("soft_skills")
                        if isinstance(hs, list) and hs:
                            skills_preview = [
                                s for s in hs if isinstance(s, str)][:3]
                        elif isinstance(ss, list) and ss:
                            skills_preview = [
                                s for s in ss if isinstance(s, str)][:3]
        except Exception:
            pass

        if not skills_preview:
            ms = resume.get("matching_skills") if isinstance(
                resume, dict) else None
            if isinstance(ms, list) and ms:
                skills_preview = [s for s in ms if isinstance(s, str)][:3]

        formatted_resumes.append(
            {
                "id": str(resume.get("_id")),
                "title": resume.get("title"),
                "application_status": resume.get("application_status", "not_applied"),
                "matching_score": resume.get("matching_score"),
                "target_company": resume.get("target_company"),
                "target_role": resume.get("target_role"),
                "main_job_title": main_job_title,
                "skills_preview": skills_preview,
                "created_at": resume.get("created_at"),
                "updated_at": resume.get("updated_at"),
            }
        )

    # Apply filters
    if filter_company:
        formatted_resumes = [
            r for r in formatted_resumes
            if r.get("target_company") and filter_company.lower() in r["target_company"].lower()
        ]

    if filter_position:
        formatted_resumes = [
            r for r in formatted_resumes
            if (r.get("target_role") and filter_position.lower() in r["target_role"].lower()) or
               (r.get("main_job_title") and filter_position.lower()
                in r["main_job_title"].lower())
        ]

    if filter_date_from or filter_date_to:
        filtered_resumes = []
        for r in formatted_resumes:
            date_field = r.get("updated_at") or r.get("created_at")
            if date_field:
                try:
                    if isinstance(date_field, str):
                        date_obj = datetime.fromisoformat(
                            date_field.replace("Z", "+00:00"))
                    else:
                        date_obj = date_field

                    date_str = date_obj.date().isoformat()

                    if filter_date_from and date_str < filter_date_from:
                        continue
                    if filter_date_to and date_str > filter_date_to:
                        continue

                    filtered_resumes.append(r)
                except:
                    pass
        formatted_resumes = filtered_resumes

    # Apply sorting
    if sort_by:
        reverse_order = sort_order.lower() == "desc"

        if sort_by == "date":
            formatted_resumes.sort(
                key=lambda x: (x.get("updated_at") or x.get(
                    "created_at") or datetime.min),
                reverse=reverse_order
            )
        elif sort_by == "company":
            formatted_resumes.sort(
                key=lambda x: x.get("target_company", "").lower(),
                reverse=reverse_order
            )
        elif sort_by == "title":
            formatted_resumes.sort(
                key=lambda x: x.get("title", "").lower(),
                reverse=reverse_order
            )

    return formatted_resumes


@resume_router.patch(
    "/{resume_id}/status",
    response_model=Dict[str, bool],
    summary="Update resume application status",
    response_description="Resume status updated successfully",
)
async def update_resume_status(
    resume_id: str,
    status_data: Dict[str, str] = Body(...),
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Update the application status of a resume.

    Args:
        resume_id: ID of the resume to update
        status_data: Dictionary containing the new application_status
        repo: Resume repository instance

    Returns:
    -------
        Dict indicating success of the update

    Raises:
    ------
        HTTPException: If the resume is not found or update fails
    """
    try:
        # Validate status value
        valid_statuses = ["not_applied", "applied",
                          "answered", "rejected", "interview"]
        new_status = status_data.get("application_status")

        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Update the resume status
        update_data = {
            "application_status": new_status,
            # Update legacy boolean fields for backward compatibility
            "is_applied": new_status in ["applied", "answered", "rejected", "interview"],
            "is_answered": new_status in ["answered", "rejected", "interview"]
        }

        # Add timestamp for applied date
        if new_status == "applied":
            update_data["applied_date"] = datetime.now()
        elif new_status == "answered":
            update_data["answered_date"] = datetime.now()

        success = await repo.update_resume(resume_id, update_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found"
            )

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating resume status: {str(e)}",
        )


@resume_router.put(
    "/{resume_id}",
    response_model=Dict[str, bool],
    summary="Update a resume",
    response_description="Resume updated successfully",
)
async def update_resume(
    resume_id: str,
    update_data: Dict[str, Any] = Body(...),
    request: Request = None,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Update a specific resume by ID.

    Args:
        resume_id: ID of the resume to update
        update_data: Data to update in the resume
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict indicating success status

    Raises:
    ------
        HTTPException: If the resume is not found or update fails
    """
    resume = await repo.get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    success = await repo.update_resume(resume_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resume",
        )
    return {"success": True}


@resume_router.delete(
    "/{resume_id}",
    response_model=Dict[str, bool],
    summary="Delete a resume",
    response_description="Resume deleted successfully",
)
async def delete_resume(
    resume_id: str,
    request: Request = None,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Delete a specific resume by ID.

    Args:
        resume_id: ID of the resume to delete
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict indicating success status

    Raises:
    ------
        HTTPException: If the resume is not found or deletion fails
    """
    # Validate resume_id format to prevent NoSQL injection
    validated_resume_id = validate_object_id(resume_id)

    resume = await repo.get_resume_by_id(str(validated_resume_id))
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {validated_resume_id} not found",
        )
    success = await repo.delete_resume(str(validated_resume_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume",
        )
    return {"success": True}


@resume_router.post(
    "/{resume_id}/optimize",
    response_model=OptimizationResponse,
    summary="Optimize a resume with AI",
    response_description="Resume optimized successfully",
)
@heavy_limit()  # Rate limit expensive AI operations
async def optimize_resume(
    resume_id: str,
    optimization_request: OptimizeResumeRequest,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Optimize a resume using AI based on a job description.

    This endpoint uses AI to analyze the original resume and job description,
    then generates an optimized version that's tailored to the job requirements.
    It also compares the ATS scores before and after optimization.

    Args:
        resume_id: ID of the resume to optimize
        optimization_request: Contains the job description for optimization
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        OptimizationResponse: Contains the optimized data, before/after ATS scores, and skill analysis

    Raises:
    ------
        HTTPException: If the resume is not found or optimization fails
    """
    # Validate resume_id format to prevent NoSQL injection
    validated_resume_id = validate_object_id(resume_id)

    logger.info(f"Starting resume optimization for resume_id: {validated_resume_id}")

    # 1. Retrieve resume
    logger.info(f"Retrieving resume with ID: {validated_resume_id}")
    resume = await repo.get_resume_by_id(str(validated_resume_id))
    if not resume:
        logger.warning(f"Resume not found with ID: {resume_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    logger.info(
        f"Successfully retrieved resume: {resume.get('title', 'Untitled')}")

    # 2. Get API configuration
    logger.info("Retrieving API configuration")

    provider = (os.getenv("API_TYPE") or os.getenv(
        "LLM_PROVIDER") or "").lower()
    enable_local_fallback = os.getenv(
        "ENABLE_LOCAL_LLM_FALLBACK", "false").lower() == "true"

    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    api_key = os.getenv("API_KEY") or os.getenv(
        "OPENAI_API_KEY") or cerebras_key

    api_base_url = (
        os.getenv("API_BASE")
        or os.getenv("OLLAMA_BASE_URL")
        or os.getenv("OLLAMA_HOST")
    )
    model_name = os.getenv(
        "MODEL_NAME",
        "mistral:7b-instruct-v0.3-q4_K_M",
    )

    if cerebras_key:
        api_key = cerebras_key
        api_base_url = "https://api.cerebras.ai/v1"
        model_name = os.getenv("CEREBRAS_MODEL_NAME", "llama3.3-70b")
        logger.info(f"Using Cerebras API for Optimization: {model_name}")
    elif provider == "ollama" and not api_base_url:
        api_base_url = "http://localhost:11434"

    is_local_llm = bool(api_base_url) and (
        "localhost" in api_base_url
        or "127.0.0.1" in api_base_url
        or "11434" in api_base_url
    )

    if not api_base_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM API base URL not configured. Set API_BASE (OpenAI-compatible) or OLLAMA_BASE_URL for local Ollama.",
        )

    if is_local_llm and not api_key:
        api_key = "ollama"

    def _get_local_llm_config() -> Dict[str, str]:
        local_base = (
            os.getenv("OLLAMA_BASE_URL")
            or os.getenv("OLLAMA_HOST")
            or "http://localhost:11434"
        )
        local_model = (
            os.getenv("OLLAMA_MODEL_NAME")
            or os.getenv("LOCAL_MODEL_NAME")
            or "mistral:7b-instruct-v0.3-q4_K_M"
        )
        return {
            "api_key": "ollama",
            "api_base": local_base,
            "model_name": local_model,
        }

    def _should_fallback_to_local(err: Exception) -> bool:
        if not enable_local_fallback:
            return False
        msg = str(err).lower()
        return (
            "insufficient" in msg
            or "payment required" in msg
            or "402" in msg
            or "api status" in msg
            or "apistatuserror" in msg
            or "rate limit" in msg
            or "timeout" in msg
            or "connection" in msg
        )

    logger.info(f"API configuration - model_name: {model_name}")
    logger.info(f"API configuration - api_base_url: {api_base_url}")
    logger.info(f"API Key present: {bool(api_key)}")

    # 3. Initialize universal scorer
    logger.info(
        "Initializing UniversalResumeScorer for pre-optimization scoring")
    scorer = UniversalResumeScorer()

    # 4. Get job description
    job_description = optimization_request.job_description or resume.get(
        "job_description", ""
    )
    logger.info(f"Job description length: {len(job_description)} characters")

    if not job_description:
        logger.warning("Job description is empty")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required for optimization",
        )

    try:
        meta_update = {"job_description": job_description}
        if optimization_request.target_company:
            meta_update["target_company"] = optimization_request.target_company
        if optimization_request.target_role:
            meta_update["target_role"] = optimization_request.target_role
        if len(meta_update) > 1:
            await repo.update_resume(resume_id, meta_update)
    except Exception as e:
        logger.warning(f"Failed to update resume metadata (company/role): {e}")

    try:
        # 5. Score original resume against job description (Optional)
        skip_scoring = os.getenv("SKIP_ATS_SCORING", "false").lower() == "true"

        # We always want one analysis for the original CV
        from app.services.cv_analyzer import CVAnalyzer
        analyzer = CVAnalyzer()

        logger.info("Analyzing original resume against job description")
        original_analysis = analyzer.analyze(
            resume["original_content"], job_description)
        original_ats_score = original_analysis.get("ats_score", 0)
        missing_skills = original_analysis.get("missing_skills", [])

        # 6. Initialize and run new Cerebras Orchestrator
        logger.info(
            "Using CVWorkflowOrchestrator for high-quality optimization")
        from app.services.workflow_orchestrator import CVWorkflowOrchestrator
        orchestrator = CVWorkflowOrchestrator()

        # Run optimization
        optimization_result = orchestrator.optimize_cv_for_job(
            cv_text=resume.get("master_content") or resume.get(
                "original_content", ""),
            jd_text=job_description,
            generate_cover_letter=False,  # Dashboard has separate cover letter generation
            email=optimization_request.email
        )

        if "error" in optimization_result:
            logger.error(
                f"Orchestrator returned error: {optimization_result['error']}")
            raise HTTPException(
                status_code=500, detail=optimization_result["error"])

        result = optimization_result.get("optimized_cv", {})
        optimized_analysis = optimization_result.get("analysis", {})
        optimized_ats_score = optimization_result.get(
            "ats_score", original_ats_score + 10)
        matching_skills = optimization_result.get("matching_skills", [])
        missing_skills = optimization_result.get("missing_skills", [])
        recommendation = optimization_result.get("recommendation", "")

        # Log success
        logger.info("Optimization completed successfully via Orchestrator")

        # 7. Check for errors in result (Unified)
        if "error" in result:
            if result.get("error") == "JSON Parse Error" or "JSON" in result.get("error", ""):
                logger.warning(
                    f"AI optimization had parsing issues: {result['error']}. Attempting recovery.")
                # We will let it proceed to sanitize_for_pydantic which can handle it
            else:
                logger.error(
                    f"AI service returned critical error: {result['error']}")
                raise HTTPException(status_code=500, detail=result["error"])

        # 8. Log success
        logger.info("Optimization completed successfully")

        # 9. validation follows below...
        logger.info(
            f"Result keys: {list(result.keys() if isinstance(result, dict) else [])}"
        )

        # 9. Parse and validate result
        logger.info("Parsing result into ResumeData model")
        try:
            # Clean data to remove markdown formatting possibly added by local LLMs
            def clean_markdown_formatting(data):
                if isinstance(data, dict):
                    return {k: clean_markdown_formatting(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_markdown_formatting(item) for item in data]
                elif isinstance(data, str):
                    import re
                    # Remove markdown link formatting [text](url) -> text
                    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', data)
                    # Pattern for [text] -> text
                    cleaned = re.sub(r'\[([^\]]+)\]', r'\1', cleaned)
                    return cleaned
                return data

            def sanitize_for_pydantic(data):
                """Ensure data matches ResumeData model requirements."""
                if not isinstance(data, dict):
                    return {}

                # 1. Ensure user_information exists
                if "user_information" not in data or not isinstance(data["user_information"], dict):
                    data["user_information"] = {
                        "name": "Candidate",
                        "main_job_title": "Professional",
                        "profile_description": "Experienced professional.",
                        "email": "candidate@example.com",
                        "experiences": [],
                        "education": [],
                        "skills": {"hard_skills": [], "soft_skills": []}
                    }

                ui = data["user_information"]

                # 2. Fix mandatory strings in user_information
                for field in ["name", "main_job_title", "profile_description", "email"]:
                    if field not in ui or not ui[field]:
                        ui[field] = "None Provided" if field != "email" else "none@example.com"

                # 3. Ensure experiences is a list and items have required fields
                if "experiences" not in ui or not isinstance(ui["experiences"], list):
                    ui["experiences"] = []

                for exp in ui["experiences"]:
                    if not isinstance(exp, dict):
                        continue
                    for f in ["job_title", "company", "start_date", "end_date"]:
                        if f not in exp:
                            exp[f] = "Unknown"
                    if "four_tasks" not in exp or not isinstance(exp["four_tasks"], list):
                        exp["four_tasks"] = ["Responsible for core duties."]
                    elif not exp["four_tasks"]:
                        exp["four_tasks"] = ["Responsible for core duties."]

                # 4. Ensure education is a list
                if "education" not in ui or not isinstance(ui["education"], list):
                    ui["education"] = []
                for edu in ui["education"]:
                    if not isinstance(edu, dict):
                        continue
                    for f in ["institution", "degree", "start_date", "end_date"]:
                        if f not in edu:
                            edu[f] = "Unknown"

                # 5. Ensure skills object
                if "skills" not in ui or not isinstance(ui["skills"], dict):
                    ui["skills"] = {"hard_skills": [], "soft_skills": []}
                for s_field in ["hard_skills", "soft_skills"]:
                    if s_field not in ui["skills"] or not isinstance(ui["skills"][s_field], list):
                        ui["skills"][s_field] = []

                # 6. Optional top level fields
                for list_field in ["projects", "certificate", "extra_curricular_activities"]:
                    if list_field in data and not isinstance(data[list_field], list):
                        data[list_field] = []

                return data

            cleaned_result = clean_markdown_formatting(result)
            sanitized_result = sanitize_for_pydantic(cleaned_result)
            optimized_data = ResumeData.parse_obj(sanitized_result)
            logger.info("Successfully validated result through Pydantic model")
        except Exception as validation_error:
            logger.error(
                f"Failed to parse result into ResumeData model: {str(validation_error)}"
            )
            logger.error(f"Validation error details: {traceback.format_exc()}")
            logger.debug(f"Problematic data: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsing AI response: {str(validation_error)}",
            )

        # 10. Update database
        logger.info(f"Updating resume {resume_id} with optimized data")
        try:
            await repo.update_optimized_data(
                resume_id, optimized_data, optimized_ats_score,
                original_ats_score=original_ats_score,
                matching_skills=matching_skills,
                missing_skills=missing_skills,
                score_improvement=optimized_ats_score - original_ats_score,
                recommendation=recommendation
            )
            logger.info("Successfully updated resume with optimized data")
        except Exception as db_error:
            logger.error(f"Database error during update: {str(db_error)}")
            logger.error(f"Database error details: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error during update: {str(db_error)}",
            )

        # 11. Return success response with both scores and skill analysis
        logger.info(
            f"Resume optimization completed successfully for resume_id: {resume_id}"
        )
        return {
            "resume_id": resume_id,
            "original_matching_score": original_ats_score,
            "optimized_matching_score": optimized_ats_score,
            "score_improvement": optimized_ats_score - original_ats_score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "recommendation": recommendation,
            "optimized_data": sanitized_result,
        }

    except HTTPException:
        # Re-raise HTTP exceptions as they're already properly formatted
        raise
    except Exception as e:
        # Log the full stack trace for any other exception
        logger.error(f"Unexpected error during resume optimization: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")

        # Check for specific error types to provide better error messages
        if "API key" in str(e).lower() or "authentication" in str(e).lower():
            logger.error("AI service authentication error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error authenticating with AI service. Please check API configuration.",
            )
        elif "timeout" in str(e).lower() or "time" in str(e).lower():
            logger.error("AI service timeout error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service request timed out. Please try again later.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during resume optimization: {str(e)}",
            )


@resume_router.post(
    "/{resume_id}/score",
    response_model=ResumeScoreResponse,
    summary="Score a resume against a job description",
    response_description="Resume scored successfully",
)
@heavy_limit()  # Rate limit AI scoring operations
async def score_resume(
    resume_id: str,
    scoring_request: ScoreResumeRequest,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Score a resume against a job description using ATS algorithms.

    This endpoint analyzes the resume against the provided job description and
    returns an ATS compatibility score along with matching skills and recommendations.

    Args:
        resume_id: ID of the resume to score
        scoring_request: Contains the job description to score against
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        ResumeScoreResponse: Contains the ATS score and skill analysis

    Raises:
    ------
        HTTPException: If the resume is not found or scoring fails
    """
    # Validate resume_id format to prevent NoSQL injection
    validated_resume_id = validate_object_id(resume_id)

    logger.info(f"Starting resume scoring for resume_id: {validated_resume_id}")

    # Retrieve resume
    logger.info(f"Retrieving resume with ID: {validated_resume_id}")
    resume = await repo.get_resume_by_id(str(validated_resume_id))
    if not resume:
        logger.warning(f"Resume not found with ID: {resume_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )

    # Get API configuration
    api_key = os.getenv("CEREBRASAI_API_KEY")
    model_name = os.getenv("API_MODEL_NAME", "gpt-oss-120b")
    api_base_url = os.getenv("API_BASE", "https://api.cerebras.ai/v1")

    logger.info("Retrieving API configuration")
    logger.info(f"Using Cerebras API: {model_name}")
    logger.info(f"API configuration - model_name: {model_name}")
    logger.info(f"API configuration - api_base_url: {api_base_url}")
    logger.info(f"API Key present: {bool(api_key)}")

    # Logic to handle local LLM without API Key
    if not api_key:
        if api_base_url and ("localhost" in api_base_url or "127.0.0.1" in api_base_url):
            logger.info(
                "Using local LLM (Ollama), skipping API key requirement")
            api_key = "ollama"  # Dummy key for local
        else:
            logger.warning("API key not found in environment variables")
            api_key = "dummy"  # Fallback to prevent crash, rely on error handling downstream

    # Initialize CV Analyzer
    try:
        from app.services.cv_analyzer import CVAnalyzer
        analyzer = CVAnalyzer()

        # Get job description
        job_description = scoring_request.job_description
        if not job_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is required for scoring",
            )

        # Get resume content
        resume_content = resume["original_content"]

        # Score the original resume
        logger.info("Scoring resume against job description using CVAnalyzer")
        score_result = analyzer.analyze(resume_content, job_description)
        ats_score = score_result.get("ats_score", 0)

        # Handle optimized version comparison if it exists
        optimized_data = resume.get("optimized_data")
        recommendation = score_result.get("recommendation", "")

        if optimized_data:
            logger.info("Scoring optimized resume for comparison")
            optimized_content = json.dumps(optimized_data) if isinstance(
                optimized_data, dict) else str(optimized_data)
            optimized_score_result = analyzer.analyze(
                optimized_content, job_description)
            optimized_score = optimized_score_result.get("ats_score", 0)

            improvement = optimized_score - ats_score
            if improvement > 0:
                recommendation += f"\n\nYour optimized resume scores {improvement} points higher ({optimized_score}%). Use the optimized version for better ATS results."

        return {
            "resume_id": resume_id,
            "ats_score": ats_score,
            "matching_skills": score_result.get("matching_skills", []),
            "missing_skills": score_result.get("missing_skills", []),
            "recommendation": recommendation,
            # Note: CVAnalyzer might name these differently
            "resume_skills": score_result.get("resume_skills", []),
            "job_requirements": score_result.get("job_requirements", []),
        }

    except Exception as e:
        logger.error(f"Error during resume scoring: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")

        # Check for specific error types
        if "API key" in str(e).lower() or "authentication" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error authenticating with AI service. Please check API configuration.",
            )
        elif "timeout" in str(e).lower() or "time" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service request timed out. Please try again later.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during resume scoring: {str(e)}",
            )


@resume_router.get(
    "/{resume_id}/download",
    summary="Download a resume as PDF",
    response_description="Resume downloaded successfully",
)
async def download_resume(
    resume_id: str,
    use_optimized: bool = True,
    template: str = "resume_template.tex",
    request: Request = None,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Download a resume as a PDF file.

    This endpoint generates a PDF version of the resume using LaTeX templates.
    By default, it uses the optimized version of the resume.

    Args:
        resume_id: ID of the resume to download
        use_optimized: Whether to use the optimized version of the resume
        template: LaTeX template to use for generating the PDF
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        FileResponse: PDF file download

    Raises:
    ------
        HTTPException: If the resume is not found or PDF generation fails
    """
    # Validate resume_id format to prevent NoSQL injection
    validated_resume_id = validate_object_id(resume_id)

    resume = await repo.get_resume_by_id(str(validated_resume_id))
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    if use_optimized and not resume.get("optimized_data"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Optimized resume data not available. Please optimize the resume first.",
        )
    try:
        # Prepare paths
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        templates_dir = base_dir / "data" / "templates"

        output_dir = tempfile.gettempdir()
        output_filename = f"resume_{resume_id}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # Resolve template using centralized configuration
        target_template = TemplateConfig.resolve_template(template)

        # Validate the resolved template
        if not TemplateConfig.is_valid_template(target_template):
            target_template = "resume.typ"  # fallback to default

        # Convert old template extensions to .typ
        if target_template.endswith('.tex') or target_template.endswith('.html'):
            target_template = "resume.typ"

        # Initialize Typst Generator
        generator = TypstGenerator(str(templates_dir))

        if use_optimized:
            json_data = resume["optimized_data"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Downloading original resume as PDF is not supported. Please optimize first.",
            )

        # Parse data
        if isinstance(json_data, str):
            generator.parse_json_from_string(json_data)
        else:
            generator.json_data = json_data

        # Generate PDF
        success = generator.generate_pdf(target_template, output_path)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Check Typst installation."
            )

        # We need to return the file path for FileResponse
        pdf_path = output_path

        # Generate filename in format: name_cv_company_position_date
        import re

        # Extract name from optimized data
        name = "resume"
        if json_data and isinstance(json_data, dict):
            user_info = json_data.get("user_information", {})
            if isinstance(user_info, dict):
                name_str = user_info.get("name", "")
                if name_str:
                    # Sanitize name for filename (remove special chars, spaces -> underscores)
                    name = re.sub(r'[^\w\s-]', '', name_str).strip()
                    name = re.sub(r'[-\s]+', '_', name)
                    name = name.lower()[:50]  # Limit length

        # Get company and position from resume metadata
        company = resume.get("target_company", "")
        if company:
            company = re.sub(r'[^\w\s-]', '', company).strip()
            company = re.sub(r'[-\s]+', '_', company).lower()[:30]
        else:
            company = "company"

        position = resume.get("target_role", "")
        if position:
            position = re.sub(r'[^\w\s-]', '', position).strip()
            position = re.sub(r'[-\s]+', '_', position).lower()[:30]
        else:
            position = "position"

        # Get date (use updated_at or current date)
        date_str = ""
        if resume.get("updated_at"):
            if isinstance(resume["updated_at"], datetime):
                date_str = resume["updated_at"].strftime("%Y%m%d")
            elif isinstance(resume["updated_at"], str):
                try:
                    date_obj = datetime.fromisoformat(
                        resume["updated_at"].replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%Y%m%d")
                except:
                    date_str = datetime.now().strftime("%Y%m%d")
        else:
            date_str = datetime.now().strftime("%Y%m%d")

        filename = f"{name}_cv_{company}_{position}_{date_str}.pdf"
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            background=None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}",
        )


@resume_router.get(
    "/{resume_id}/preview",
    summary="Preview a resume",
    response_description="Resume previewed successfully",
)
async def preview_resume(
    resume_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Preview a resume (not implemented).

    This endpoint is intended for previewing a resume, but it's not yet implemented.

    Args:
        resume_id: ID of the resume to preview
        request: The incoming request
        repo: Resume repository instance

    Raises:
    ------
        HTTPException: Always raises a 501 Not Implemented error
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Resume preview not implemented. Use the download endpoint to generate a PDF.",
    )


@resume_router.put(
    "/{resume_id}/status/applied",
    response_model=Dict[str, Any],
    summary="Mark resume as applied",
    response_description="Resume marked as applied successfully",
)
async def mark_resume_as_applied(
    resume_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Mark a resume as applied.

    Args:
        resume_id: ID of the resume to mark as applied
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict indicating success status and applied date

    Raises:
    ------
        HTTPException: If the resume is not found or update fails
    """
    try:
        resume = await repo.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found",
            )

        # Update the resume status - create update dict without _id
        update_data = {
            "is_applied": True,
            "applied_date": datetime.now()
        }

        success = await repo.update_resume(resume_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update resume status",
            )

        return {
            "success": True,
            "message": "Resume marked as applied",
            "applied_date": update_data["applied_date"].isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating resume status: {str(e)}",
        )


@resume_router.put(
    "/{resume_id}/status/answered",
    response_model=Dict[str, Any],
    summary="Mark resume as answered",
    response_description="Resume marked as answered successfully",
)
async def mark_resume_as_answered(
    resume_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Mark a resume as answered (received response).

    Args:
        resume_id: ID of the resume to mark as answered
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict indicating success status and answered date

    Raises:
    ------
        HTTPException: If the resume is not found or update fails
    """
    try:
        resume = await repo.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found",
            )

        # Update the resume status - create update dict without _id
        update_data = {
            "is_answered": True,
            "answered_date": datetime.now()
        }

        success = await repo.update_resume(resume_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update resume status",
            )

        return {
            "success": True,
            "message": "Resume marked as answered",
            "answered_date": update_data["answered_date"].isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating resume status: {str(e)}",
        )


@resume_router.put(
    "/{resume_id}/status/reset",
    response_model=Dict[str, Any],
    summary="Reset resume status",
    response_description="Resume status reset successfully",
)
async def reset_resume_status(
    resume_id: str,
    request: Request,
    repo: ResumeRepository = Depends(get_resume_repository),
):
    """Reset the applied and answered status of a resume.

    Args:
        resume_id: ID of the resume to reset status
        request: The incoming request
        repo: Resume repository instance

    Returns:
    -------
        Dict indicating success status

    Raises:
    ------
        HTTPException: If the resume is not found or update fails
    """
    try:
        resume = await repo.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID {resume_id} not found",
            )

        # Reset the resume status - create update dict without _id
        update_data = {
            "is_applied": False,
            "applied_date": None,
            "is_answered": False,
            "answered_date": None
        }

        success = await repo.update_resume(resume_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset resume status",
            )

        return {
            "success": True,
            "message": "Resume status reset successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting resume status: {str(e)}",
        )


@resume_router.post(
    "/contact",
    response_model=ContactFormResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit contact form",
    response_description="Contact form submission status",
)
async def submit_contact_form(
    request: ContactFormRequest = Body(...),
) -> ContactFormResponse:
    """Submit a contact form.

    This endpoint processes contact form submissions from users wanting to reach out
    to the project maintainers, report issues, or ask questions.

    Args:
        request: The contact form data including name, email, subject, and message

    Returns:
    -------
        ContactFormResponse: Success status and confirmation message

    Raises:
    ------
        HTTPException: If there's an issue processing the form
    """
    try:
        # In a production environment, this would typically:
        # 1. Store the message in a database
        # 2. Send an email notification to administrators
        # 3. Potentially send an auto-response to the user

        # Store contact message (implementation pending)
        # TODO: Implement proper email notification system with templates
        # Current implementation: Log the message for manual follow-up
        logger.info(f"Contact form submission from {contact_data.email}: {contact_data.message[:100]}...")

        return ContactFormResponse(
            success=True,
            message="Thank you for your message! We'll get back to you soon.",
        )
    except Exception as e:
        # Log the error in a production environment
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process your message: {str(e)}",
        )
