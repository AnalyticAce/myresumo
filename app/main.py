"""Main application entry point for PowerCV.

This module initializes the FastAPI application, configures routers, middleware,
and handles application startup and shutdown events. It serves as the central
coordination point for the entire application.
"""

import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, HTTPException, Body, Query, status
from app.utils.shared_utils import ValidationHelper, ErrorHandler
from app.services.master_cv import MasterCV
from app.services.scraper import fetch_job_description, extract_keywords_from_jd
from app.services.cover_letter_gen import CoverLetterGenerator
from app.services.cv_analyzer import CVAnalyzer
from app.services.workflow_orchestrator import CVWorkflowOrchestrator
from app.routes.n8n_integration import router as n8n_router
from app.api.routers.comprehensive_optimizer import comprehensive_router
from app.api.routers.cover_letter import cover_letter_router
from app.api.routers.resume import resume_router
from app.api.routers.token_usage import router as token_usage_router
from app.database.connector import MongoConnectionManager
from app.web.core import core_web_router
from app.web.dashboard import web_router
# Load environment variables from .env file
load_dotenv(override=True)


# Initialize Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="app/templates")

# Initialize orchestrator
orchestrator = CVWorkflowOrchestrator()

# Configure secure logging and settings
from app.config.logging_config import logger
from app.config.settings import get_settings
from app.middleware.rate_limit import init_rate_limiting
from app.core.exceptions import ConfigurationError, MissingApiKeyError


# Request models
class OptimizationRequest(BaseModel):
    cv_text: str = Field(..., min_length=100, max_length=25000,
                         description="CV text to optimize")
    jd_text: str = Field(..., min_length=50, max_length=15000,
                         description="Job description text")
    generate_cover_letter: bool = Field(
        default=True, description="Whether to generate cover letter")
    template: str = Field(
        default="resume.typ",
        pattern="^(resume\.typ|modern\.typ|brilliant-cv/cv\.typ|awesome-cv/cv\.tex)$",
        description="Template to use for CV generation (resume.typ, modern.typ, brilliant-cv/cv.typ, awesome-cv/cv.tex)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cv_text": "John Doe\nSenior Software Engineer...",
                "jd_text": "We are looking for a Senior Software Engineer...",
                "generate_cover_letter": True,
                "template": "resume.typ"
            }
        }
    )


class CoverLetterRequest(BaseModel):
    candidate_data: dict = Field(..., description="Candidate information")
    job_data: dict = Field(..., description="Job information")

    tone: str = Field(default="Professional", pattern="^(Professional|Enthusiastic|Formal|Casual)$",
                      description="Tone for cover letter")

    model_config = ConfigDict(
        json_schema_extra={
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
    )

    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v):
        valid_tones = ["Professional", "Enthusiastic", "Formal", "Casual"]
        if v not in valid_tones:
            raise ValueError(f'tone must be one of: {valid_tones}')
        return v


class OptimizationResponse(BaseModel):
    """Response model for resume optimization."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {
                    "analysis": {},
                    "optimized_cv": {},
                    "ats_score": 85
                },
                "message": "Resume optimization completed successfully"
            }
        }
    )


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

    Closes database connections and cleans up resources.

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
    PowerCV is a resume generation system that adapts resumes to specific job descriptions.
    It leverages AI to provide customized resume content based on user input.
    """,
    license_info={"name": "MIT License",
                  "url": "https://opensource.org/licenses/MIT"},
    version="2.0.0",
    docs_url=None,
)

# Initialize rate limiting
init_rate_limiting(app)


@app.on_event("startup")
async def startup_event():
    """Handle application startup and configuration validation."""
    try:
        # Test database connection (always required)
        from app.database.connector import MongoConnectionManager
        manager = MongoConnectionManager.get_instance()

        # Check if AI provider is configured (optional for development)
        from app.config import get_settings
        settings = get_settings()
        ai_provider_configured = bool(settings.cerebras_api_key or settings.api_key or settings.openai_api_key)

        if ai_provider_configured:
            # Test AI client configuration only if API keys are present
            from app.services.ai_providers import AIClient
            AIClient()
            logger.info("Application startup completed successfully with AI providers")
        else:
            logger.warning("No AI provider API keys configured - AI features will be unavailable")
            logger.info("Application startup completed (development mode)")

    except (ConfigurationError, MissingApiKeyError) as e:
        logger.error(f"Configuration error during startup: {e}")
        error_msg = f"""
{"="*60}
❌ CONFIGURATION ERROR
{"="*60}
Error: {e}

Please check your environment configuration:
"""
        if hasattr(e, 'config_key'):
            error_msg += f"  - Missing or invalid: {e.config_key}\n"
        if hasattr(e, 'provider'):
            error_msg += f"  - For AI provider: {e.provider}\n"
        error_msg += "\nUpdate your .env file or environment variables.\n"
        error_msg += "="*60

        print(error_msg, flush=True)
        # Re-raise as RuntimeError to cause startup failure
        raise RuntimeError(f"Application configuration error: {e}") from e

    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        print("\n" + "="*60)
        print("❌ STARTUP ERROR")
        print("="*60)
        print(f"Unexpected error: {e}")
        print("\nCheck application logs for details.")
        print("="*60 + "\n")
        import sys
        sys.exit(1)


# Global exception handler for security
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that doesn't expose sensitive information.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSON response with sanitized error
    """
    # Log the full error securely (sensitive data is filtered by SensitiveDataFilter)
    logger.error(f"Unhandled exception on {request.url.path}: {type(exc).__name__}")

    # NEVER expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please contact support if this persists."
        }
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
    # Log validation errors securely (don't expose sensitive input data)
    logger.warning(f"Validation error on {request.url.path}: {len(exc.errors())} errors")

    # For API routes, return sanitized error
    if request.url.path.startswith("/api"):
        # Don't expose detailed validation errors that might contain sensitive data
        return JSONResponse(
            status_code=422,
            content={"detail": "Invalid input data. Please check your request."}
        )

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
                 "version": app.version, "service": "PowerCV"}
    )


# Cerebras v2 endpoints
_orchestrator = None


def get_orchestrator():
    """Get or create a singleton instance of the workflow orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        logger.info("Initializing CVWorkflowOrchestrator singleton")
        _orchestrator = CVWorkflowOrchestrator()
    return _orchestrator


@app.post("/api/v2/optimize", tags=["CV Optimization v2"], summary="Complete CV optimization workflow")
async def optimize_cv_v2(request: OptimizationRequest):
    """
    CV optimization endpoint utilizing modular prompts.
    """
    try:
        orchestrator = get_orchestrator()
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
        orchestrator = get_orchestrator()
        analysis = orchestrator.analyzer.analyze(
            request.cv_text, request.jd_text)
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
        orchestrator = get_orchestrator()
        result = orchestrator.cover_letter_gen.generate(
            request.candidate_data,
            request.job_data,
            request.tone
        )
        return result
    except Exception as e:
        logger.error(f"Cover letter generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy/General endpoints


@app.post("/api/optimize-resume", response_model=OptimizationResponse)
async def optimize_resume(request: OptimizationRequest):
    """
    Main endpoint for comprehensive resume optimization.
    """
    try:
        # Log request context for debugging without exposing sensitive data
        cv_length = len(request.cv_text) if request.cv_text else 0
        jd_length = len(request.jd_text) if request.jd_text else 0
        logger.info(
            f"Received resume optimization request (template: {request.template})",
            extra={
                "cv_length": cv_length,
                "jd_length": jd_length,
                "generate_cover_letter": request.generate_cover_letter,
                "template": request.template
            }
        )
        orchestrator = get_orchestrator()
        result = orchestrator.optimize_cv_for_job(
            cv_text=request.cv_text,
            jd_text=request.jd_text,
            generate_cover_letter=request.generate_cover_letter
        )
        return OptimizationResponse(
            success=True,
            data=result,
            message="Resume optimization completed successfully"
        )
    except Exception as e:
        logger.error(f"Error in optimize_resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-cv")
async def analyze_cv(request: OptimizationRequest):
    """
    Standalone endpoint for CV analysis only.
    """
    try:
        orchestrator = get_orchestrator()
        analysis = orchestrator.analyzer.analyze(
            request.cv_text, request.jd_text)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"Error in analyze_cv: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-cover-letter")
async def generate_cover_letter(request: OptimizationRequest):
    """
    Standalone endpoint for cover letter generation.
    """
    try:
        orchestrator = get_orchestrator()
        # Minimal data for generator
        candidate_data = {"name": "Candidate", "top_skills": []}
        job_data = {"position": "Professional", "requirements": []}

        result = orchestrator.cover_letter_gen.generate(
            candidate_data, job_data)
        return {"success": True, "cover_letter": result}
    except Exception as e:
        logger.error(f"Error in generate_cover_letter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Automation endpoints


@app.post("/api/v1/scrape", tags=["Scraping"], summary="Scrape job description from URL")
async def scrape_job_description(url: str = Body(..., description="URL to job posting")):
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
        logger.error(f"Scraping error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to scrape job description: {str(e)}")


@app.post("/api/v1/extract-keywords", tags=["Analysis"], summary="Extract keywords from job description")
async def extract_keywords(jd_text: str = Body(..., min_length=50, max_length=5000, description="Job description text")):
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
        logger.error(f"Keyword extraction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/optimize-structured", tags=["Optimization"], summary="Optimize using structured CV data")
async def optimize_structured_cv(
    master_cv_file: str = Body(..., description="Path to structured CV file"),
    jd_text: str = Body(..., description="Job description text"),
    generate_cover_letter: bool = Query(
        default=True, description="Whether to generate cover letter")
):
    """
    Optimize CV using structured master CV format(JSON/YAML).

    This endpoint reads a structured CV file and generates a tailored version
    for the provided job description.
    """
    try:
        from pathlib import Path

        # Load structured CV
        cv_path = Path(master_cv_file)
        if not cv_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")

        master_cv = MasterCV.from_file(str(cv_path))

        # Extract relevant sections for this job
        jd_analysis = await extract_keywords_from_jd(jd_text)
        keywords = jd_analysis.get("skills", [])

        extracted_data = master_cv.extract_for_job(keywords)

        # Run optimization
        local_orchestrator = CVWorkflowOrchestrator()

        # Convert extracted data to text for optimization
        cv_text = master_cv.to_markdown()

        result = local_orchestrator.optimize_cv_for_job(
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
        logger.error(f"Structured optimization error: {str(e)}", exc_info=True)
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
