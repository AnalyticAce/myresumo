"""Services package for business logic components.

This package contains various service modules that implement the core business
logic of the application, including AI processing, resume generation, and other
key functionality.
"""

from app.services.ai_client import get_ai_client
from app.services.ai_providers import AIClient
from app.services.cerebras_client import CerebrasClient
from app.services.cover_letter_gen import CoverLetterGenerator
from app.services.cv_analyzer import CVAnalyzer
from app.services.cv_optimizer import CVOptimizer
from app.services.master_cv import CVTemplate, MasterCV, create_template_cv
from app.services.scraper import (
    JobDescriptionScraperFactory,
    extract_keywords_from_jd,
    fetch_job_description,
)
from app.services.workflow_orchestrator import CVWorkflowOrchestrator

__all__ = [
    # AI Clients
    "get_ai_client",
    "AIClient",
    "CerebrasClient",
    # Workflow
    "CVWorkflowOrchestrator",
    # Generators
    "CoverLetterGenerator",
    "CVAnalyzer",
    "CVOptimizer",
    # Master CV
    "MasterCV",
    "CVTemplate",
    "create_template_cv",
    # Scraping
    "fetch_job_description",
    "extract_keywords_from_jd",
    "JobDescriptionScraperFactory",
]
