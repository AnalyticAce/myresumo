"""Resume API router module for resume management operations.

This module implements the API endpoints for resume-related functionality including
resume creation, retrieval, optimization, PDF generation and deletion. It handles
the interface between HTTP requests and the resume repository, and coordinates
AI-powered resume optimization services.
"""

import json
import logging
import os
import secrets
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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

from app.database.models.resume import Resume, ResumeData
from app.database.repositories.resume_repository import ResumeRepository
from app.services.resume.universal_scorer import UniversalResumeScorer
from app.services.ai.model_ai import AtsResumeOptimizer
from app.services.resume.latex_generator import LaTeXGenerator
from app.utils.file_handling import create_temporary_pdf, extract_text_from_file

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        # Validate file format
        supported_formats = ['.pdf', '.docx', '.md', '.markdown', '.txt']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Reset file position for potential reuse
        await file.seek(0)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text based on file type
            resume_text = extract_text_from_file(temp_file_path, file_extension)
            
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
            master_filename=file.filename,
            master_file_type=file.content_type,
            master_updated_at=datetime.now(),
        )

        resume_id = await repo.create_resume(new_resume)
        if not resume_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create resume",
            )
        return {"id": resume_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resume: {str(e)}",
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
            new_master_content = extract_text_from_file(temp_file_path, file_extension)
            
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
            master_content = extract_text_from_file(temp_file_path, file_extension)
            
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
        import os
        template_dir = "data/sample_latex_templates"
        templates = []
        
        template_info = {
            "resume_template.tex": {
                "name": "Standard Template",
                "description": "Classic professional resume template with A4 format and standard 1-inch margins",
                "style": "Professional",
                "margins": "1 inch"
            },
            "compact_resume_template.tex": {
                "name": "Compact Template", 
                "description": "Space-efficient template with A4 format and 1-inch margins",
                "style": "Professional",
                "margins": "1 inch"
            },
            "modern_template.tex": {
                "name": "Modern Template",
                "description": "Contemporary design with color accents, A4 format and 1-inch margins",
                "style": "Modern",
                "margins": "1 inch"
            },
            "minimalist_template.tex": {
                "name": "Minimalist Template",
                "description": "Clean, simple design with A4 format and 1-inch margins",
                "style": "Minimalist", 
                "margins": "1 inch"
            },
            "creative_template.tex": {
                "name": "Creative Template",
                "description": "Visually striking design with colored header, A4 format and 1-inch margins",
                "style": "Creative",
                "margins": "1 inch"
            },
            "simple_resume_template.tex": {
                "name": "Simple Template",
                "description": "Basic template with straightforward formatting, A4 format and 1-inch margins",
                "style": "Simple",
                "margins": "1 inch"
            }
        }
        
        if os.path.exists(template_dir):
            for filename in os.listdir(template_dir):
                if filename.endswith('.tex') and filename in template_info:
                    templates.append({
                        "filename": filename,
                        **template_info[filename]
                    })
        
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {str(e)}",
        )


@resume_router.get(
    "/{resume_id}",
    response_model=Dict[str, Any],
    summary="Get a resume",
    response_description="Resume retrieved successfully",
)
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
    resume_data = await repo.get_resume_by_id(resume_id)
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
    sort_by: Optional[str] = Query(None, description="Sort by: date, company, title"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    filter_company: Optional[str] = Query(None, description="Filter by company"),
    filter_position: Optional[str] = Query(None, description="Filter by position/role"),
    filter_date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    filter_date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
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
               (r.get("main_job_title") and filter_position.lower() in r["main_job_title"].lower())
        ]
    
    if filter_date_from or filter_date_to:
        filtered_resumes = []
        for r in formatted_resumes:
            date_field = r.get("updated_at") or r.get("created_at")
            if date_field:
                try:
                    if isinstance(date_field, str):
                        date_obj = datetime.fromisoformat(date_field.replace("Z", "+00:00"))
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
                key=lambda x: (x.get("updated_at") or x.get("created_at") or datetime.min),
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
        valid_statuses = ["not_applied", "applied", "answered", "rejected", "interview"]
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
    resume = await repo.get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    success = await repo.delete_resume(resume_id)
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
    logger.info(f"Starting resume optimization for resume_id: {resume_id}")

    # 1. Retrieve resume
    logger.info(f"Retrieving resume with ID: {resume_id}")
    resume = await repo.get_resume_by_id(resume_id)
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
    logger.info("Initializing UniversalResumeScorer for pre-optimization scoring")
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

        if skip_scoring:
            logger.info("Skipping initial ATS scoring as per configuration")
            original_ats_score = 0
            original_score_result = {"missing_skills": [
            ], "matching_skills": [], "recommendation": "Scoring skipped"}
        else:
            logger.info("Scoring original resume against job description")
            try:
                original_score_result = await scorer.calculate_match_score(
                    resume["original_content"], job_description, user_id="local-user"
                )
            except Exception as e:
                if (not is_local_llm) and _should_fallback_to_local(e):
                    local_cfg = _get_local_llm_config()
                    logger.warning(
                        f"Primary LLM scoring failed, retrying with local Ollama. Error: {e}"
                    )
                    scorer = SimpleMatchScorer()
                    original_score_result = await scorer.calculate_match_score(
                        resume["original_content"], job_description, user_id="local-user"
                    )
                    is_local_llm = True
                else:
                    raise
            original_ats_score = int(original_score_result["score"])
            logger.info(f"Original resume ATS score: {original_ats_score}")

        # Extract missing skills to be addressed in optimization
        missing_skills = original_score_result.get("missing_skills", [])
        logger.info(f"Identified missing skills: {missing_skills}")

        # 6. Initialize optimizer and generate optimized resume
        # 6. Initialize and run optimizer
        logger.info("Initializing Resume Optimizer")

        # Check if fast optimization is enabled (defaulting to True for now given user complaints)
        use_fast_optimizer = os.getenv(
            "USE_FAST_OPTIMIZER", "true").lower() == "true"

        if use_fast_optimizer:
            from app.services.ai.multi_model_optimizer import MultiModelResumeOptimizer
            logger.info(
                "Using MultiModelResumeOptimizer (Tiered Architecture)")

            # Initialize with default max_workers=5
            multi_optimizer = MultiModelResumeOptimizer()

            # Prepare input data
            try:
                import json
                resume_content_source = resume.get("master_content") or resume.get("original_content", "")
                if isinstance(resume_content_source, str) and resume_content_source.strip().startswith('{'):
                    resume_data_dict = json.loads(resume_content_source)
                elif isinstance(resume_content_source, dict):
                    resume_data_dict = resume_content_source
                else:
                    # Fallback for other types
                    raise ValueError(
                        f"Unexpected type for resume content: {type(resume_content_source)}")
            except Exception as e:
                logger.warning(
                    f"Failed to load resume content as JSON/Dict: {e}. Using robust fallback with extraction.")
                content_str = str(resume.get("master_content") or resume.get("original_content", ""))

                # Heuristic Extraction
                import re

                # 1. Email Extraction
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content_str)
                email = email_match.group(
                    0) if email_match else "placeholder@example.com"

                # 2. Phone Extraction (simple pattern)
                phone_match = re.search(
                    r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', content_str)
                phone = phone_match.group(0) if phone_match else ""

                # 3. Name Extraction (Heuristic: First non-empty line, max 3 words)
                name = "Candidate"
                lines = [line.strip()
                         for line in content_str.split('\n') if line.strip()]
                if lines:
                    first_line = lines[0]
                    # Check if first line looks like a name (e.g. 2-3 words, no numbers)
                    if 0 < len(first_line.split()) <= 4 and not any(char.isdigit() for char in first_line):
                        name = first_line

                resume_data_dict = {
                    "user_information": {
                        "name": name,
                        "main_job_title": "Professional",  # Could try to extract this too, but harder
                        "email": email,
                        "phone": phone,
                        "location": "",
                        "profile_description": content_str,
                        "experiences": [],
                        "education": [],
                        "skills": []
                    },
                    "projects": []
                }

            optimized_data_dict = None
            try:
                optimized_data_dict = await multi_optimizer.optimize_resume(
                    resume_data_dict,
                    job_description,
                    job_title="AI Software Engineer",
                    company="BCG X"
                )
            except Exception as e:
                if _should_fallback_to_local(e):
                    logger.warning(
                        f"Multi-model optimizer failed, falling back to legacy optimizer. Error: {e}"
                    )
                    use_fast_optimizer = False
                else:
                    raise

            if use_fast_optimizer:
                result = optimized_data_dict

        if not use_fast_optimizer:
            logger.info(
                "Using Legacy AtsResumeOptimizer (Sequential Processing)")
            try:
                optimizer = AtsResumeOptimizer(
                    model_name=model_name,
                    resume=resume["original_content"],
                    api_key=api_key,
                    api_base=api_base_url,
                )
                result = optimizer.generate_ats_optimized_resume_json(
                    job_description)
            except Exception as e:
                if (not is_local_llm) and _should_fallback_to_local(e):
                    local_cfg = _get_local_llm_config()
                    logger.warning(
                        f"Primary LLM optimization failed, retrying with local Ollama. Error: {e}"
                    )
                    optimizer = AtsResumeOptimizer(
                        model_name=local_cfg["model_name"],
                        resume=resume["original_content"],
                        api_key=local_cfg["api_key"],
                        api_base=local_cfg["api_base"],
                    )
                    result = optimizer.generate_ats_optimized_resume_json(
                        job_description)
                    is_local_llm = True
                else:
                    raise

        # 7. Check for errors in result (Unified)
        if "error" in result:
            # Standard legacy error handling
            logger.error(f"AI service returned error: {result['error']}")
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
                    # Remove markdown link formatting [text](url) -> text
                    # Also handles [email] -> email
                    import re
                    # Pattern for [text](url) -> text
                    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', data)
                    # Pattern for [text] -> text
                    cleaned = re.sub(r'\[([^\]]+)\]', r'\1', cleaned)
                    return cleaned
                return data

            cleaned_result = clean_markdown_formatting(result)
            optimized_data = ResumeData.parse_obj(cleaned_result)
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

        # 10. Score the optimized resume
        logger.info(
            "Generating JSON text representation of the optimized resume")
        optimized_resume_text = json.dumps(result)

        logger.info("Scoring optimized resume against job description")
        try:
            optimized_score_result = await scorer.calculate_match_score(
                optimized_resume_text, job_description, user_id="local-user"
            )
        except Exception as e:
            if (not is_local_llm) and _should_fallback_to_local(e):
                local_cfg = _get_local_llm_config()
                logger.warning(
                    f"Primary LLM optimized scoring failed, retrying with local Ollama. Error: {e}"
                )
                scorer = SimpleMatchScorer()
                optimized_score_result = await scorer.calculate_match_score(
                    optimized_resume_text, job_description, user_id="local-user"
                )
                is_local_llm = True
            else:
                raise
        optimized_ats_score = int(optimized_score_result["score"])
        logger.info(f"Optimized resume ATS score: {optimized_ats_score}")

        def _norm(s: str) -> str:
            import re
            s = (s or "").strip().lower()
            return re.sub(r"\s+", " ", s)

        def _is_soft_skill(s: str) -> bool:
            t = _norm(s)
            # Strict whitelist only. Everything else is considered a hard skill/tool/method.
            soft = {
                "communication",
                "teamwork",
                "collaboration",
                "cross-functional collaboration",
                "adaptability",
                "problem solving",
                "problem-solving",
                "time management",
                "attention to detail",
                "detail oriented",
            }
            if t in soft:
                return True
            if t.startswith("communication"):
                return True
            if t.startswith("teamwork"):
                return True
            if "attention to detail" in t:
                return True
            return False

        def _dedupe_keep_order(items: list) -> list:
            seen = set()
            out = []
            for it in items if isinstance(items, list) else []:
                if not isinstance(it, str):
                    continue
                v = it.strip()
                if not v:
                    continue
                key = _norm(v)
                if key in seen:
                    continue
                seen.add(key)
                out.append(v)
            return out

        def _extract_skills_from_text(text: str) -> dict:
            import re
            if not isinstance(text, str) or not text.strip():
                return {"hard_skills": [], "soft_skills": []}

            t = text
            # Try to isolate the Skills block
            m = re.search(
                r"\n\s*Skills\s*\n(?P<body>.*?)(\n\s*(Hobbies|Education|Work Experience|Projects|Certifications)\s*\n|\Z)", t, re.IGNORECASE | re.DOTALL)
            body = m.group("body") if m else ""
            if not body:
                body = t

            # Extract labeled lines when present
            hard = []
            soft = []

            # soft skills line
            for mm in re.finditer(r"Soft\s*Skills\s*:\s*(.+)", body, re.IGNORECASE):
                soft.extend([x.strip() for x in re.split(
                    r"[,;]", mm.group(1)) if x.strip()])

            # tools / programming / technical skills
            for mm in re.finditer(r"(Tools|Programming|Technical\s*Skills|Hard\s*Skills)\s*:\s*(.+)", body, re.IGNORECASE):
                hard.extend([x.strip() for x in re.split(
                    r"[,;]", mm.group(2)) if x.strip()])

            # If nothing labeled, fallback to comma-separated chunk
            if not hard and not soft and body:
                candidates = [x.strip()
                              for x in re.split(r"[,;\n]", body) if x.strip()]
                for c in candidates:
                    (soft if _is_soft_skill(c) else hard).append(c)

            # Final strict re-split to prevent mixing
            fixed_hard, fixed_soft = [], []
            for x in hard:
                (fixed_soft if _is_soft_skill(x) else fixed_hard).append(x)
            for x in soft:
                (fixed_soft if _is_soft_skill(x) else fixed_hard).append(x)

            return {
                "hard_skills": _dedupe_keep_order(fixed_hard),
                "soft_skills": _dedupe_keep_order(fixed_soft),
            }

        # Conservative skills handling: preserve optimized structure, only append missing skills
        try:
            # Get the optimized skills from AI processing
            optimized_skills = optimized_data.user_information.skills
            optimized_hard = list(optimized_skills.hard_skills or [])
            optimized_soft = list(optimized_skills.soft_skills or [])
            
            # Get missing skills from job description
            missing_skills = optimized_score_result.get("missing_skills", []) or []
            missing_skills = [m for m in missing_skills if isinstance(m, str) and m.strip()]
            
            # Create normalized sets for comparison
            optimized_hard_norm = {_norm(s) for s in optimized_hard if isinstance(s, str)}
            optimized_soft_norm = {_norm(s) for s in optimized_soft if isinstance(s, str)}
            
            # Only add missing skills that aren't already present
            for missing in missing_skills:
                missing_norm = _norm(missing)
                if missing_norm in optimized_hard_norm or missing_norm in optimized_soft_norm:
                    continue  # Skip if already present
                    
                if _is_soft_skill(missing):
                    optimized_soft.append(missing)
                    optimized_soft_norm.add(missing_norm)
                else:
                    optimized_hard.append(missing)
                    optimized_hard_norm.add(missing_norm)
            
            # Update with final lists (preserve AI-optimized structure)
            optimized_data.user_information.skills.hard_skills = _dedupe_keep_order(optimized_hard)
            optimized_data.user_information.skills.soft_skills = _dedupe_keep_order(optimized_soft)
            
            # Update result dict if it exists
            if isinstance(result, dict):
                ui = result.get("user_information") if isinstance(result.get("user_information"), dict) else None
                if ui is not None:
                    skills = ui.get("skills") if isinstance(ui.get("skills"), dict) else None
                    if skills is not None:
                        skills["hard_skills"] = optimized_data.user_information.skills.hard_skills
                        skills["soft_skills"] = optimized_data.user_information.skills.soft_skills
                        
        except Exception as e:
            logger.warning(f"Failed to preserve skills structure: {e}")

        # Education location fallback (conservative): infer Moscow-based education when institution includes Moscow.
        try:
            edu_list = optimized_data.user_information.education or []
            for edu in edu_list:
                if getattr(edu, "location", None):
                    continue
                inst = getattr(edu, "institution", "") or ""
                if "moscow" in inst.lower():
                    edu.location = "Moscow, RU"

            if isinstance(result, dict):
                ui = result.get("user_information") if isinstance(
                    result.get("user_information"), dict) else None
                if ui is not None and isinstance(ui.get("education"), list):
                    for edu in ui.get("education"):
                        if not isinstance(edu, dict):
                            continue
                        if edu.get("location"):
                            continue
                        inst = (edu.get("institution") or "")
                        if "moscow" in inst.lower():
                            edu["location"] = "Moscow, RU"
        except Exception as e:
            logger.warning(f"Failed to apply education location fallback: {e}")

        score_improvement = optimized_ats_score - original_ats_score
        logger.info(f"Score improvement: {score_improvement}")

        # 11. Update database
        logger.info(f"Updating resume {resume_id} with optimized data")
        try:
            await repo.update_optimized_data(
                resume_id, optimized_data, optimized_ats_score,
                original_ats_score=original_ats_score,
                matching_skills=optimized_score_result.get(
                    "matching_skills", []),
                missing_skills=optimized_score_result.get(
                    "missing_skills", []),
                score_improvement=score_improvement,
                recommendation=optimized_score_result.get("recommendation", "")
            )
            logger.info("Successfully updated resume with optimized data")
        except Exception as db_error:
            logger.error(f"Database error during update: {str(db_error)}")
            logger.error(f"Database error details: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error during update: {str(db_error)}",
            )

        # 12. Return success response with both scores and skill analysis
        logger.info(
            f"Resume optimization completed successfully for resume_id: {resume_id}"
        )
        return {
            "resume_id": resume_id,
            "original_matching_score": original_ats_score,
            "optimized_matching_score": optimized_ats_score,
            "score_improvement": score_improvement,
            "matching_skills": optimized_score_result.get("matching_skills", []),
            "missing_skills": optimized_score_result.get("missing_skills", []),
            "recommendation": optimized_score_result.get("recommendation", ""),
            "optimized_data": result,
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
    logger.info(f"Starting resume scoring for resume_id: {resume_id}")

    # Retrieve resume
    logger.info(f"Retrieving resume with ID: {resume_id}")
    resume = await repo.get_resume_by_id(resume_id)
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

    # Initialize universal scorer
    try:
        scorer = UniversalResumeScorer()

        # Get job description
        job_description = scoring_request.job_description
        if not job_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is required for scoring",
            )

        # Get resume content - first check if optimized data exists, use that for comparison
        resume_content = resume["original_content"]

        # Optionally also score the optimized version if it exists
        optimized_data = resume.get("optimized_data")
        optimized_score = None

        # Score the original resume
        logger.info("Scoring original resume against job description")
        score_result = await scorer.calculate_match_score(
            resume_content, job_description, user_id="local-user"
        )
        ats_score = int(score_result["score"])

        # If optimized data exists, score it too for comparison
        if optimized_data:
            logger.info("Scoring optimized resume for comparison")
            if isinstance(optimized_data, str):
                optimized_content = optimized_data
            else:
                optimized_content = json.dumps(optimized_data)

            optimized_score_result = await scorer.calculate_match_score(
                optimized_content, job_description, user_id="local-user"
            )
            optimized_score = int(optimized_score_result["score"])
            logger.info(
                f"Original score: {ats_score}, Optimized score: {optimized_score}")

        # Prepare enhanced recommendation if we have both scores
        recommendation = score_result.get("recommendation", "")
        if optimized_score:
            improvement = optimized_score - ats_score
            if improvement > 0:
                recommendation += f"\n\nYour optimized resume scores {improvement} points higher ({optimized_score}%). Consider using the optimized version for better results."

        return {
            "resume_id": resume_id,
            "ats_score": ats_score,
            "matching_skills": score_result.get("matching_skills", []),
            "missing_skills": score_result.get("missing_skills", []),
            "recommendation": recommendation,
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
    resume = await repo.get_resume_by_id(resume_id)
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
        latex_dir = Path("data/sample_latex_templates")
        if not latex_dir.exists():
            latex_dir = Path("app/services/resume/latex_templates")
            if not latex_dir.exists():
                latex_dir.mkdir(parents=True, exist_ok=True)
        generator = LaTeXGenerator(str(latex_dir))
        if use_optimized:
            json_data = resume["optimized_data"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Downloading original resume as PDF is not supported. Please optimize first.",
            )
        if isinstance(json_data, str):
            generator.parse_json_from_string(json_data)
        else:
            generator.json_data = json_data
        latex_content = generator.generate_from_template(template)
        if not latex_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate LaTeX content",
            )
        pdf_path = create_temporary_pdf(latex_content)
        if not pdf_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create PDF",
            )

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

        # For now, we'll just return a success response
        # TODO: Implement actual email sending functionality

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
