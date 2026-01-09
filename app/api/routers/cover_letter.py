"""Cover letter API router module for cover letter management operations.

This module implements the API endpoints for cover letter-related functionality including
cover letter creation, retrieval, generation, PDF generation and deletion. It handles
the interface between HTTP requests and the cover letter repository, and coordinates
AI-powered cover letter generation services.
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import FileResponse

from app.config import computed_settings as settings
from app.database.models.ai_cover_letter import (
    AICoverLetterRequest,
    AICoverLetterResponse,
)
from app.database.models.cover_letter import (
    CoverLetter,
    CoverLetterData,
    CoverLetterGenerationRequest,
    CoverLetterRequest,
    CoverLetterSummary,
)
from app.database.repositories.cover_letter_repository import CoverLetterRepository
from app.services.cover_letter import (
    AICoverLetterGenerator,
    CoverLetterTemplateGenerator,
)
from app.services.resume.typst_generator import TypstGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


cover_letter_router = APIRouter(
    prefix="/api/cover-letter", tags=["Cover Letter"])


def get_ai_generator() -> AICoverLetterGenerator:
    """Dependency for getting the AI cover letter generator.

    Returns:
        AICoverLetterGenerator: An instance of the AI cover letter generator
    """
    return AICoverLetterGenerator(
        model_name=settings.CEREBRAS_MODEL,
        api_key=settings.CEREBRAS_API_KEY,
        api_base=settings.CEREBRAS_API_BASE
    )


@cover_letter_router.post(
    "/generate-with-ai",
    response_model=AICoverLetterResponse,
    summary="Generate a cover letter using AI",
    response_description="AI-generated cover letter",
    status_code=status.HTTP_200_OK,
)
async def generate_cover_letter_with_ai(
    request: Request,
    ai_request: AICoverLetterRequest,
    background_tasks: BackgroundTasks,
    ai_generator: AICoverLetterGenerator = Depends(get_ai_generator),
):
    """Generate a cover letter using AI based on resume and job description.

    This endpoint uses AI to generate a tailored cover letter based on the provided
    resume and job description. The AI will analyze the job requirements and create
    a customized cover letter that highlights the most relevant qualifications.

    Args:
        request: The incoming request
        ai_request: The AI generation request containing resume and job details
        background_tasks: FastAPI background tasks
        ai_generator: The AI cover letter generator

    Returns:
        AICoverLetterResponse containing the generated cover letter

    Raises:
        HTTPException: If generation fails or required fields are missing
    """
    try:
        # Generate the cover letter using AI
        cover_letter_content = await ai_generator.generate_cover_letter(
            resume_text=ai_request.resume_text,
            job_description=ai_request.job_description,
            company_name=ai_request.company_name,
            job_title=ai_request.job_title,
            tone=ai_request.tone,
            length=ai_request.length,
            additional_instructions=ai_request.additional_instructions or ""
        )

        return AICoverLetterResponse(
            content=cover_letter_content,
            template_name=ai_request.template_name or "ai_generated",
            model=ai_generator.model_name
        )

    except Exception as e:
        logger.error(
            f"AI cover letter generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate cover letter: {str(e)}"
        )


async def get_cover_letter_repository(request: Request) -> CoverLetterRepository:
    """Dependency for getting the cover letter repository instance.

    Args:
        request: The incoming request

    Returns:
        CoverLetterRepository: An instance of the cover letter repository
    """
    return CoverLetterRepository()


@cover_letter_router.post(
    "/",
    response_model=Dict[str, str],
    summary="Create a cover letter",
    response_description="Cover letter created successfully",
)
async def create_cover_letter(
    request: Request,
    cover_letter_data: CoverLetterRequest,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Create a new cover letter.

    This endpoint creates a new cover letter entry in the database with the provided
    information. The cover letter can be generated later or filled in manually.

    Args:
        request: The incoming request
        cover_letter_data: Cover letter creation data
        repo: Cover letter repository instance

    Returns:
        Dict containing the ID of the created cover letter

    Raises:
        HTTPException: If the cover letter creation fails
    """
    try:
        # Create CoverLetterData from request
        content_data = CoverLetterData(
            recipient_name=cover_letter_data.recipient_name,
            recipient_title=cover_letter_data.recipient_title,
            company_name=cover_letter_data.target_company,
            company_address=cover_letter_data.company_address,
            sender_name=cover_letter_data.sender_name,
            sender_email=cover_letter_data.sender_email,
            sender_phone=cover_letter_data.sender_phone,
            sender_location=cover_letter_data.sender_location,
            job_title=cover_letter_data.target_role,
            job_reference=cover_letter_data.job_reference,
            introduction="",  # Empty initially
            body_paragraphs=[],  # Empty initially
            closing="",  # Empty initially
            # Default signature
            signature=f"Sincerely,\n{cover_letter_data.sender_name}"
        )

        # Get user ID from request context (fallback to session/temp ID for development)
        user_id = getattr(request.state, 'user_id', None) or 'temp-user-' + str(hash(str(request.client)))[:8]
        
        new_cover_letter = CoverLetter(
            user_id=user_id,
            title=cover_letter_data.title,
            resume_id=cover_letter_data.resume_id,
            target_company=cover_letter_data.target_company,
            target_role=cover_letter_data.target_role,
            job_description=cover_letter_data.job_description,
            content_data=content_data,
            template_name=cover_letter_data.template_name,
            is_generated=False,
        )

        cover_letter_id = await repo.create_cover_letter(new_cover_letter)
        if not cover_letter_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create cover letter",
            )
        return {"id": cover_letter_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating cover letter: {str(e)}",
        )


@cover_letter_router.post(
    "/{cover_letter_id}/generate",
    response_model=Dict[str, str],
    summary="Generate cover letter content",
    response_description="Cover letter generated successfully",
)
async def generate_cover_letter(
    cover_letter_id: str,
    request: Request,
    generation_data: CoverLetterGenerationRequest,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Generate the final cover letter content from structured data.

    This endpoint takes the structured cover letter data and generates the final
    formatted cover letter text using the selected template.

    Args:
        cover_letter_id: ID of the cover letter to generate
        request: The incoming request
        generation_data: Structured content for generation
        repo: Cover letter repository instance

    Returns:
        Dict containing success message and generated content

    Raises:
        HTTPException: If generation fails or cover letter not found
    """
    try:
        # Get existing cover letter
        cover_letter = await repo.get_cover_letter_by_id(cover_letter_id)
        if not cover_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found"
            )

        # Create CoverLetterData from existing data and new content
        existing_content_data = CoverLetterData(
            **cover_letter.get("content_data", {}))

        # Update with new generation data
        existing_content_data.introduction = generation_data.introduction
        existing_content_data.body_paragraphs = generation_data.body_paragraphs
        existing_content_data.closing = generation_data.closing
        existing_content_data.signature = generation_data.signature

        # Validate content data
        template_generator = CoverLetterTemplateGenerator()
        validation_errors = template_generator.validate_content_data(
            existing_content_data)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation errors: {'; '.join(validation_errors)}"
            )

        # Generate formatted content using template generator
        template_name = cover_letter.get(
            "template_name", "professional_template")
        generated_content = template_generator.generate_cover_letter(
            existing_content_data, template_name)

        # Update cover letter with generated content
        update_data = {
            "content_data": existing_content_data.model_dump(),
            "generated_content": generated_content,
            "is_generated": True,
        }

        success = await repo.update_cover_letter(cover_letter_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update cover letter with generated content"
            )

        return {"message": "Cover letter generated successfully", "content": generated_content}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cover letter: {str(e)}",
        )


@cover_letter_router.get(
    "/{cover_letter_id}",
    response_model=Dict[str, Any],
    summary="Get a cover letter",
    response_description="Cover letter retrieved successfully",
)
async def get_cover_letter(
    cover_letter_id: str,
    request: Request,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Get a specific cover letter by ID.

    Args:
        cover_letter_id: ID of the cover letter to retrieve
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        Dict containing the cover letter data

    Raises:
        HTTPException: If the cover letter is not found
    """
    cover_letter_data = await repo.get_cover_letter_by_id(cover_letter_id)
    if not cover_letter_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter with ID {cover_letter_id} not found",
        )
    cover_letter_data["id"] = str(cover_letter_data.pop("_id"))
    return cover_letter_data


@cover_letter_router.get(
    "/user/{user_id}",
    response_model=List[CoverLetterSummary],
    summary="Get all cover letters for a user",
    response_description="Cover letters retrieved successfully",
)
async def get_user_cover_letters(
    user_id: str,
    request: Request,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Get all cover letters for a specific user.

    Args:
        user_id: ID of the user whose cover letters to retrieve
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        List of cover letter summaries for the specified user
    """
    cover_letters = await repo.get_cover_letters_by_user_id(user_id)
    formatted_cover_letters = []

    for cover_letter in cover_letters:
        formatted_cover_letters.append({
            "id": str(cover_letter.get("_id")),
            "title": cover_letter.get("title"),
            "target_company": cover_letter.get("target_company"),
            "target_role": cover_letter.get("target_role"),
            "is_generated": cover_letter.get("is_generated", False),
            "created_at": cover_letter.get("created_at"),
            "updated_at": cover_letter.get("updated_at"),
        })

    return formatted_cover_letters


@cover_letter_router.put(
    "/{cover_letter_id}",
    response_model=Dict[str, bool],
    summary="Update a cover letter",
    response_description="Cover letter updated successfully",
)
async def update_cover_letter(
    cover_letter_id: str,
    update_data: Dict[str, Any] = Body(...),
    request: Request = None,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Update a specific cover letter by ID.

    Args:
        cover_letter_id: ID of the cover letter to update
        update_data: Data to update in the cover letter
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        Dict indicating success status

    Raises:
        HTTPException: If the cover letter is not found or update fails
    """
    cover_letter = await repo.get_cover_letter_by_id(cover_letter_id)
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter with ID {cover_letter_id} not found",
        )
    success = await repo.update_cover_letter(cover_letter_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cover letter",
        )
    return {"success": True}


@cover_letter_router.delete(
    "/{cover_letter_id}",
    response_model=Dict[str, bool],
    summary="Delete a cover letter",
    response_description="Cover letter deleted successfully",
)
async def delete_cover_letter(
    cover_letter_id: str,
    request: Request = None,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Delete a specific cover letter by ID.

    Args:
        cover_letter_id: ID of the cover letter to delete
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        Dict indicating success status

    Raises:
        HTTPException: If the cover letter is not found or deletion fails
    """
    cover_letter = await repo.get_cover_letter_by_id(cover_letter_id)
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter with ID {cover_letter_id} not found",
        )
    success = await repo.delete_cover_letter(cover_letter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete cover letter",
        )
    return {"success": True}


@cover_letter_router.get(
    "/{cover_letter_id}/download",
    response_class=FileResponse,
    summary="Download cover letter as PDF",
    response_description="PDF file generated and downloaded successfully",
)
async def download_cover_letter_pdf(
    cover_letter_id: str,
    request: Request,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Generate and download a cover letter as PDF.

    Args:
        cover_letter_id: ID of the cover letter to generate PDF for
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        FileResponse containing the generated PDF

    Raises:
        HTTPException: If cover letter not found or PDF generation fails
    """
    cover_letter = await repo.get_cover_letter_by_id(cover_letter_id)
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )

    # Check if cover letter is generated
    if not cover_letter.get("is_generated"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cover letter content not generated yet"
        )

    # Get content data
    content_data = CoverLetterData(**cover_letter.get("content_data", {}))

    # Prepare data for Typst
    typst_data = {
        "user_information": {
            "name": content_data.sender_name,
            "email": content_data.sender_email,
            "phone": content_data.sender_phone,
            "address": content_data.sender_location
        },
        # Join paragraphs for body
        "cover_letter_content": "\n\n".join([
            content_data.introduction,
            *content_data.body_paragraphs,
            content_data.closing,
            content_data.signature
        ])
    }

    # Initialize Typst Generator
    templates_dir = Path("data/templates")
    generator = TypstGenerator(str(templates_dir))
    generator.json_data = {"data": typst_data}

    # Generate PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        output_path = tmp_pdf.name

    success = generator.generate_pdf("cover_letter.typ", output_path)

    if not success or not Path(output_path).exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF. Check Typst installation."
        )

    pdf_path = output_path

    # Return PDF file
    filename = f"cover_letter_{cover_letter.get('title', 'untitled').replace(' ', '_')}.pdf"
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type="application/pdf"
    )


@cover_letter_router.get(
    "/search/{user_id}",
    response_model=List[CoverLetterSummary],
    summary="Search cover letters",
    response_description="Cover letters search results",
)
async def search_cover_letters(
    user_id: str,
    query: str = Query(..., description="Search query"),
    request: Request = None,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Search cover letters by text content.

    Args:
        user_id: ID of the user whose cover letters to search
        query: Search query string
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        List of matching cover letter summaries
    """
    cover_letters = await repo.search_cover_letters(user_id, query)
    formatted_cover_letters = []

    for cover_letter in cover_letters:
        formatted_cover_letters.append({
            "id": str(cover_letter.get("_id")),
            "title": cover_letter.get("title"),
            "target_company": cover_letter.get("target_company"),
            "target_role": cover_letter.get("target_role"),
            "is_generated": cover_letter.get("is_generated", False),
            "created_at": cover_letter.get("created_at"),
            "updated_at": cover_letter.get("updated_at"),
        })

    return formatted_cover_letters


@cover_letter_router.get(
    "/statistics/{user_id}",
    response_model=Dict[str, Any],
    summary="Get cover letter statistics",
    response_description="Cover letter statistics retrieved successfully",
)
async def get_cover_letter_statistics(
    user_id: str,
    request: Request = None,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Get statistics about a user's cover letters.

    Args:
        user_id: ID of the user
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        Dictionary containing cover letter statistics
    """
    return await repo.get_cover_letter_statistics(user_id)


@cover_letter_router.get(
    "/templates",
    response_model=List[Dict[str, str]],
    summary="Get available cover letter templates",
    response_description="Available cover letter templates retrieved successfully",
)
async def get_cover_letter_templates(
    request: Request = None,
):
    """Get all available cover letter templates.

    Args:
        request: The incoming request

    Returns:
        List of available template dictionaries
    """
    try:
        from app.services.cover_letter.templates import CoverLetterTemplates
        templates_service = CoverLetterTemplates()
        all_templates = templates_service.get_all_templates()

        # Convert to response format
        template_list = []
        for template_name, template_data in all_templates.items():
            template_list.append({
                "name": template_data["name"],
                "display_name": template_data["display_name"],
                "description": template_data["description"]
            })

        return template_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {str(e)}",
        )


@cover_letter_router.post(
    "/{cover_letter_id}/preview",
    response_model=Dict[str, Any],
    summary="Preview cover letter",
    response_description="Cover letter preview generated successfully",
)
async def preview_cover_letter(
    cover_letter_id: str,
    request: Request,
    repo: CoverLetterRepository = Depends(get_cover_letter_repository),
):
    """Generate a preview of the cover letter without generating final content.

    Args:
        cover_letter_id: ID of the cover letter to preview
        request: The incoming request
        repo: Cover letter repository instance

    Returns:
        Dictionary containing preview information

    Raises:
        HTTPException: If cover letter not found or preview fails
    """
    try:
        cover_letter = await repo.get_cover_letter_by_id(cover_letter_id)
        if not cover_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found"
            )

        content_data = CoverLetterData(**cover_letter.get("content_data", {}))
        template_name = cover_letter.get(
            "template_name", "professional_template")

        template_generator = CoverLetterTemplateGenerator()
        preview_info = template_generator.preview_cover_letter(
            content_data, template_name)

        return preview_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating preview: {str(e)}",
        )
