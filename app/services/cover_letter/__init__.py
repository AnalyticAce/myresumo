"""Cover letter service module.

This module provides cover letter generation and template services
for creating professional cover letters tailored to job applications.
"""

from .template_generator import CoverLetterTemplateGenerator
from .templates import CoverLetterTemplates
from .ai_generator import AICoverLetterGenerator

__all__ = [
    "CoverLetterTemplateGenerator", 
    "CoverLetterTemplates",
    "AICoverLetterGenerator"
]
