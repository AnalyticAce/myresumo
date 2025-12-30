"""Main application entry point for PowerCV.

This module initializes the FastAPI application, configures routers, middleware,
and handles application startup and shutdown events. It serves as the central
coordination point for the entire application.
"""

from app.web.dashboard import web_router
from app.web.core import core_web_router
from app.database.connector import MongoConnectionManager
from app.api.routers.token_usage import router as token_usage_router
from app.api.routers.resume import resume_router
from app.api.routers.cover_letter import cover_letter_router
from app.api.routers.comprehensive_optimizer import comprehensive_router
from app.routes.n8n_integration import router as n8n_router
from app.services.workflow_orchestrator import CVWorkflowOrchestrator
from app.utils.shared_utils import ValidationHelper, ErrorHandler
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv(override=True)


# Initialize Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="app/templates")

# Initialize orchestrator for new Cerebras integration
orchestrator = CVWorkflowOrchestrator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Request models for new endpoints
class OptimizationRequest(BaseModel):
    cv_text: str = Field(..., min_length=100, max_length=10000,
                         description="CV text to optimize")
    jd_text: str = Field(..., min_length=50, max_length=5000,
                         description="Job description text")
    generate_cover_letter: bool = Field(
        default=True, description="Whether to generate cover letter")

    class Config:
        schema_extra = {
            "example": {
                "cv_text": "John Doe\nSenior Software Engineer...",
                "jd_text": "We are looking for a Senior Software Engineer...",
                "generate_cover_letter": True
            }
        }


class CoverLetterRequest(BaseModel):
    candidate_data: dict = Field(..., description="Candidate information")
    job_data: dict = Field(..., description="Job information")
    tone: str = Field(default="Professional", regex="^(Professional|Enthusiastic|Formal|Casual)$",
                      description="Tone for cover letter")

    class Config:
        schema_extra = {
            "example": {
                "candidate_data": {
                    "name": "John Doe",
                    "current_title": "Software Engineer",
                    "top_skills": ["Python", "JavaScript"]
                },
                "job_data": {
                    "company": "TechCorp",
                    "position": "Senior Developer"
                },
                "tone": "Professional"
            }
        }


async def startup_logic(app: FastAPI) -> None:
    """Execute startup logic for the FastAPI application.

    Initialize database connections and other resources needed by the application.

    Args:
        app: The FastAPI application instance

    Raises:
    ------
        Exception: If any startup operation fails
    """
    try:
        connection_manager = MongoConnectionManager.get_instance()
        app.state.mongo = connection_manager
    except Exception as e:
        print(f"Error during startup: {e}")
        raise


async def shutdown_logic(app: FastAPI) -> None:
    """Execute shutdown logic for the FastAPI application.

    Properly close database connections and clean up resources.

    Args:
        app: The FastAPI application instance
    """
    try:
        await app.state.mongo.close_all()
        print("Successfully closed all database connections")
    except Exception as e:
        print(f"Error during shutdown: {e}")
    finally:
        print("Shutting down background tasks.")


app = FastAPI(
    title="PowerCV API",
    summary="",
    description="""
    PowerCV is an AI-backed resume generator designed to tailor your resume and skills based on a given job description. This innovative tool leverages the latest advancements in AI technology to provide you with a customized resume that stands out.
    """,
    license_info={"name": "MIT License",
                  "url": "https://opensource.org/licenses/MIT"},
    version="2.0.0",
    docs_url=None,
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom exception handler for HTTP exceptions.

    Renders the 404.html template for 404 errors.
    For other HTTP errors, renders a basic error page or returns JSON for API routes.

    Args:
        request: The incoming request
        exc: The HTTP exception that was raised

    Returns:
    -------
        An appropriate response based on the request type and error
    """
    if exc.status_code == 404:
        # Check if this is an API request or a web page request
        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=404, content={"detail": "Resource not found"}
            )
        # For web requests, render our custom 404 page
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )

    # For API routes, return JSON error
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": str(exc.detail)}
        )

    # For other errors on web routes, show a simple error page
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "status_code": exc.status_code,
            "detail": str(exc.detail)},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom exception handler for request validation errors.

    Args:
        request: The incoming request
        exc: The validation error that was raised

    Returns:
    -------
        JSON response for API routes or template response for web routes
    """
    # For API routes, return JSON error
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    # For web routes, show an error page with validation details
    return templates.TemplateResponse(
        "404.html",
        {
            "request": request,
            "status_code": 422,
            "detail": "Validation Error: Please check your input data.",
        },
        status_code=422,
    )


@app.middleware("http")
async def add_response_headers(request: Request, call_next):
    """Middleware to add response headers and handle flashed messages.

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
    -------
        The response with added security headers
    """
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# Add middleware and static file mounts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080",
                   "http://127.0.0.1:3000", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.mount("/templates", StaticFiles(directory="app/templates"), name="templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve custom Swagger UI HTML for API documentation.

    Returns:
    -------
        HTMLResponse: Custom Swagger UI HTML

    Raises:
    ------
        FileNotFoundError: If the custom Swagger template is not found
    """
    try:
        with open("app/templates/custom_swagger.html") as f:
            template = f.read()

        return HTMLResponse(
            template.replace("{{ title }}", "PowerCV API Documentation").replace(
                "{{ openapi_url }}", "/openapi.json"
            )
        )
    except FileNotFoundError:
        return HTMLResponse(
            content="Custom Swagger template not found", status_code=500
        )
    except Exception as e:
        return HTMLResponse(
            content=f"Error loading documentation: {str(e)}", status_code=500
        )


@app.get("/health", tags=["Health"], summary="Health Check")
async def health_check():
    """Health check endpoint for monitoring and container orchestration.

    Returns:
    -------
        JSONResponse: Status information about the application.
    """
    return JSONResponse(
        content={"status": "healthy",
                 "version": app.version, "service": "myresumo"}
    )


# New Cerebras-powered endpoints
@app.post("/api/v2/optimize", tags=["CV Optimization v2"], summary="Complete CV optimization workflow")
async def optimize_cv_v2(request: OptimizationRequest):
    """
    New Cerebras-powered CV optimization endpoint.
    Uses modular prompts for better quality.
    """
    try:
        result = orchestrator.optimize_cv_for_job(
            cv_text=request.cv_text,
            jd_text=request.jd_text,
            generate_cover_letter=request.generate_cover_letter
        )
        return result

    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/analyze", tags=["CV Analysis v2"], summary="Analyze CV against job description")
async def analyze_cv_v2(request: OptimizationRequest):
    """
    Analyze CV without optimization.
    Returns ATS score, keyword analysis, and recommendations.
    """
    try:
        from app.services.cv_analyzer import CVAnalyzer
        analyzer = CVAnalyzer()
        analysis = analyzer.analyze(request.cv_text, request.jd_text)
        return analysis

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/cover-letter", tags=["Cover Letter v2"], summary="Generate cover letter")
async def generate_cover_letter_v2(request: CoverLetterRequest):
    """
    Generate cover letter based on candidate and job data.
    """
    try:
        from app.services.cover_letter_gen import CoverLetterGenerator
        generator = CoverLetterGenerator()
        result = generator.generate(
            request.candidate_data,
            request.job_data,
            request.tone
        )
        return result

    except Exception as e:
        logger.error(f"Cover letter generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scrape", tags=["Scraping"], summary="Scrape job description from URL")
async def scrape_job_description(url: str = Field(..., description="URL to job posting")):
    """
    Scrape job description from a LinkedIn, Indeed, or other job board URL.

    Returns extracted job title, company, location, and full description.
    """
    try:
        from app.utils.shared_utils import ValidationHelper
        # Validate URL
        validated_url = ValidationHelper.validate_url(url)

        from app.services.scraper import fetch_job_description
        result = await fetch_job_description(validated_url)
        return result

    except ValueError as e:
        logger.error(f"URL validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to scrape job description: {str(e)}")


@app.post("/api/v1/extract-keywords", tags=["Analysis"], summary="Extract keywords from job description")
async def extract_keywords(jd_text: str = Field(..., min_length=50, max_length=5000, description="Job description text")):
    """
    Extract skills and requirements from a job description.

    Useful for identifying what to highlight in your CV.
    """
    try:
        from app.utils.shared_utils import ValidationHelper
        # Validate input
        validated_text = ValidationHelper.validate_text_input(
            jd_text, 5000, "job description")

        from app.services.scraper import extract_keywords_from_jd
        result = await extract_keywords_from_jd(validated_text)
        return result

    except ValueError as e:
        logger.error(f"Input validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Keyword extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/optimize-structured", tags=["Optimization"], summary="Optimize using structured CV data")
async def optimize_structured_cv(
    master_cv_file: str,
    jd_text: str,
    generate_cover_letter: bool = True
):
    """
    Optimize CV using structured master CV format (JSON/YAML).

    This endpoint reads a structured CV file and generates a tailored version
    for the provided job description.
    """
    try:
        from app.services.master_cv import MasterCV
        from pathlib import Path

        # Load structured CV
        cv_path = Path(master_cv_file)
        if not cv_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")

        master_cv = MasterCV.from_file(str(cv_path))

        # Extract relevant sections for this job
        from app.services.scraper import extract_keywords_from_jd
        jd_analysis = await extract_keywords_from_jd(jd_text)
        keywords = jd_analysis.get("skills", [])

        extracted_data = master_cv.extract_for_job(keywords)

        # Run optimization
        from app.services.workflow_orchestrator import CVWorkflowOrchestrator
        orchestrator = CVWorkflowOrchestrator()

        # Convert extracted data to text for optimization
        cv_text = master_cv.to_markdown()

        result = orchestrator.optimize_cv_for_job(
            cv_text=cv_text,
            jd_text=jd_text,
            generate_cover_letter=generate_cover_letter
        )

        return {
            "extracted_cv": extracted_data,
            "optimization_result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Structured optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include routers - These must come BEFORE the catch-all route
app.include_router(resume_router)
app.include_router(cover_letter_router)
# Add token usage tracking API endpoints
app.include_router(token_usage_router)
# Add comprehensive optimizer API endpoints
app.include_router(comprehensive_router)
# Add n8n integration endpoints
app.include_router(n8n_router)
app.include_router(core_web_router)
app.include_router(web_router)


# Catch-all for not found pages - IMPORTANT: This must come AFTER including all routers
@app.get("/{path:path}", include_in_schema=False)
async def catch_all(request: Request, path: str):
    """Catch-all route handler for undefined paths.

    This must be defined AFTER all other routes to avoid intercepting valid routes.

    Args:
        request: The incoming request
        path: The path that was not matched by any other route

    Returns:
    -------
        Template response with 404 page
    """
    # Skip handling for paths that should be handled by other middleware/routers
    if path.startswith(("api/", "static/", "templates/", "docs")):
        # Let the normal routing handle these paths
        raise StarletteHTTPException(status_code=404)

    # For truly non-existent routes, render the 404 page
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
