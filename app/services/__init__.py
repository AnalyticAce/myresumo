"""Services package for business logic components.

This package contains various service modules that implement the core business
logic of the application, including AI processing, resume generation, and other
key functionality.
"""

from app.services.scraper import (
    fetch_job_description,
    extract_keywords_from_jd,
    JobDescriptionScraperFactory,
)
from app.services.master_cv import MasterCV, CVTemplate, create_template_cv
from app.services.cv_optimizer import CVOptimizer
from app.services.cv_analyzer import CVAnalyzer
from app.services.cover_letter_gen import CoverLetterGenerator
from app.services.workflow_orchestrator import CVWorkflowOrchestrator
from app.services.cerebras_client import CerebrasClient
from app.services.ai_providers import AIProviders
from app.services.ai_client import get_ai_client

__all__ = [
    # AI Clients
    "get_ai_client",
    "AIProviders",
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
