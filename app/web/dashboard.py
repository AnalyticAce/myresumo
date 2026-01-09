"""Dashboard web module for user-specific interfaces.

This module implements the dashboard interface routes, handling user-specific
views such as resume management, profile settings, and personalized features
that require user context.
"""

from fastapi import Path, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.web.base_router import WebRouter

web_router = WebRouter()
templates = Jinja2Templates(directory="app/templates")


@web_router.get(
    "/dashboard",
    summary="Dashboard",
    response_description="User dashboard showing resumes and statistics",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):
    """Render the user dashboard.

    This endpoint displays the user's resume collection, optimization statistics,
    and actions they can take to create or optimize resumes.

    Args:
        request: The incoming request object

    Returns:
    -------
        HTMLResponse: The dashboard HTML page
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@web_router.get(
    "/master-cv",
    summary="Master CV Management",
    response_description="Master CV management page for uploading and managing master CVs",
    response_class=HTMLResponse,
)
async def master_cv_management(
    request: Request,
):
    """Render the master CV management page.

    This endpoint displays the master CV management interface where users can
    upload, view, and manage their master CVs.

    Args:
        request: The incoming request object

    Returns:
    -------
        HTMLResponse: The master CV management HTML page
    """
    return templates.TemplateResponse("master_cv.html", {"request": request})


@web_router.get(
    "/templates",
    summary="Template Gallery",
    response_description="Template gallery page for browsing and selecting resume templates",
    response_class=HTMLResponse,
)
async def template_gallery(
    request: Request,
):
    """Render the template gallery page.

    This endpoint displays the template gallery where users can browse
    and select from different resume templates.

    Args:
        request: The incoming request object

    Returns:
    -------
        HTMLResponse: The template gallery HTML page
    """
    return templates.TemplateResponse("templates.html", {"request": request})


@web_router.get(
    "/create",
    summary="Create Resume",
    response_description="Create a new resume",
    response_class=HTMLResponse,
)
async def create_resume(
    request: Request,
    master_cv_id: str = Query(None, description="Master CV ID to create resume from"),
):
    """Render the resume creation page.

    This endpoint displays the form for creating a new resume, including
    file upload for the original resume and input for job descriptions.

    Args:
        request: The incoming HTTP request

    Returns:
    -------
        HTMLResponse: The rendered resume creation page
    """
    return templates.TemplateResponse("create.html", {"request": request})


@web_router.get(
    "/resume/{resume_id}",
    summary="View Resume",
    response_description="View a specific resume",
    response_class=HTMLResponse,
)
async def view_resume(
    request: Request,
    resume_id: str = Path(..., title="Resume ID"),
):
    """Render the detailed view of a specific resume.

    This endpoint displays the details of a specific resume, including
    optimization results, ATS score, and options to download or edit.

    Args:
        request: The incoming HTTP request
        resume_id: The ID of the resume to view

    Returns:
    -------
        HTMLResponse: The rendered resume view page
    """
    # In a complete implementation, we would fetch the resume data
    # from the API and pass it to the template
    return templates.TemplateResponse(
        "resume_view.html", {"request": request, "resume_id": resume_id}
    )


@web_router.get(
    "/resume/{resume_id}/optimize",
    summary="Optimize Resume",
    response_description="Optimize a specific resume",
    response_class=HTMLResponse,
)
async def optimize_resume_page(
    request: Request,
    resume_id: str = Path(..., title="Resume ID"),
):
    """Render the resume optimization page.

    This page allows users to optimize a specific resume with AI-powered tools
    after viewing its ATS score.

    Args:
        request: The incoming request
        resume_id: The unique identifier of the resume

    Returns:
    -------
        HTMLResponse: Rendered resume optimization page
    """
    return templates.TemplateResponse(
        "resume_optimize.html",
        {
            "request": request,
            "resume_id": resume_id,
            "page_title": "Optimize Resume",
        },
    )


@web_router.get(
    "/cover-letter",
    summary="Cover Letter Composer",
    response_description="Cover letter composition page",
    response_class=HTMLResponse,
)
async def cover_letter_composer(
    request: Request,
):
    """Render the cover letter composer page.

    This endpoint displays the cover letter composition interface where users can
    create, edit, and generate professional cover letters.

    Args:
        request: The incoming request object

    Returns:
    -------
        HTMLResponse: The cover letter composer HTML page
    """
    return templates.TemplateResponse("cover_letter.html", {"request": request})


@web_router.get(
    "/settings",
    summary="Settings",
    response_description="Manage your settings",
    response_class=HTMLResponse,
)
async def settings(
    request: Request,
):
    """Render the user settings page.

    This endpoint displays user profile settings, preferences,
    and account management options.

    Args:
        request: The incoming HTTP request

    Returns:
    -------
        HTMLResponse: The rendered settings page
    """
    return templates.TemplateResponse("settings.html", {"request": request})
