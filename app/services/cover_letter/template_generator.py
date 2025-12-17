"""Cover letter template generator module.

This module provides the main service for generating cover letters
using various templates and formatting options.
"""

from datetime import datetime
from typing import Dict, List, Optional

from app.database.models.cover_letter import CoverLetterData
from app.services.cover_letter.templates import CoverLetterTemplates


class CoverLetterTemplateGenerator:
    """Service for generating cover letters from templates and content data."""
    
    def __init__(self):
        """Initialize the cover letter template generator."""
        self.templates = CoverLetterTemplates()
    
    def generate_cover_letter(
        self,
        content_data: CoverLetterData,
        template_name: str = "professional_template"
    ) -> str:
        """Generate a formatted cover letter from content data and template.
        
        Args:
            content_data: Structured cover letter data
            template_name: Name of the template to use
            
        Returns:
            Formatted cover letter text
        """
        template = self.templates.get_template(template_name)
        template_string = template["template"]
        
        # Format all components
        sender_info = self.templates.format_sender_info(content_data.model_dump())
        recipient_info = self.templates.format_recipient_info(content_data.model_dump())
        recipient_salutation = self.templates.get_recipient_salutation(content_data.model_dump())
        job_ref = self.templates.format_job_reference(content_data.job_reference or "")
        body_paragraphs = self.templates.format_body_paragraphs(content_data.body_paragraphs)
        
        # Current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Substitute placeholders in template
        formatted_letter = template_string.format(
            sender_info=sender_info,
            date=current_date,
            recipient_info=recipient_info,
            recipient_salutation=recipient_salutation,
            job_title=content_data.job_title,
            job_ref=job_ref,
            introduction=content_data.introduction.strip(),
            body_paragraphs=body_paragraphs,
            closing=content_data.closing.strip(),
            signature=content_data.signature.strip()
        )
        
        return formatted_letter
    
    def generate_latex_cover_letter(
        self,
        content_data: CoverLetterData,
        template_name: str = "professional_template"
    ) -> str:
        """Generate LaTeX code for cover letter PDF.
        
        Args:
            content_data: Structured cover letter data
            template_name: Name of the template to use
            
        Returns:
            LaTeX code string
        """
        # Generate the formatted content first
        formatted_content = self.generate_cover_letter(content_data, template_name)
        
        # Convert to LaTeX format
        latex_content = formatted_content.replace('\n', '\\\\')
        
        # Create LaTeX document
        latex_template = f"""\\documentclass[11pt,a4paper]{{letter}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{parskip}}

\\address{{{latex_content}}}

\\begin{{document}}

\\begin{{letter}}{{{content_data.company_name}}}

\\opening{{Dear {self.templates.get_recipient_salutation(content_data.model_dump())},}}

{latex_content}

\\closing{{Sincerely,}}

\\end{{letter}}

\\end{{document}}"""
        
        return latex_template
    
    def preview_cover_letter(
        self,
        content_data: CoverLetterData,
        template_name: str = "professional_template"
    ) -> Dict[str, str]:
        """Generate a preview of the cover letter with metadata.
        
        Args:
            content_data: Structured cover letter data
            template_name: Name of the template to use
            
        Returns:
            Dictionary containing preview information
        """
        formatted_content = self.generate_cover_letter(content_data, template_name)
        
        return {
            "content": formatted_content,
            "word_count": len(formatted_content.split()),
            "character_count": len(formatted_content),
            "template_used": template_name,
            "preview_lines": formatted_content.split('\n')[:10],  # First 10 lines
        }
    
    def validate_content_data(self, content_data: CoverLetterData) -> List[str]:
        """Validate cover letter content data.
        
        Args:
            content_data: Cover letter data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not content_data.sender_name or not content_data.sender_name.strip():
            errors.append("Sender name is required")
        
        if not content_data.sender_email or not content_data.sender_email.strip():
            errors.append("Sender email is required")
        
        if not content_data.company_name or not content_data.company_name.strip():
            errors.append("Company name is required")
        
        if not content_data.job_title or not content_data.job_title.strip():
            errors.append("Job title is required")
        
        if not content_data.introduction or not content_data.introduction.strip():
            errors.append("Introduction is required")
        
        if not content_data.body_paragraphs or not any(p.strip() for p in content_data.body_paragraphs):
            errors.append("At least one body paragraph is required")
        
        if not content_data.closing or not content_data.closing.strip():
            errors.append("Closing paragraph is required")
        
        if not content_data.signature or not content_data.signature.strip():
            errors.append("Signature is required")
        
        return errors
    
    def get_template_suggestions(self, job_title: str, industry: Optional[str] = None) -> List[str]:
        """Get template suggestions based on job title and industry.
        
        Args:
            job_title: The job title being applied for
            industry: The industry (optional)
            
        Returns:
            List of recommended template names
        """
        job_title_lower = job_title.lower()
        industry_lower = (industry or "").lower()
        
        # Executive positions
        if any(title in job_title_lower for title in ["ceo", "cto", "cfo", "director", "vice president", "vp", "executive", "manager", "lead"]):
            return ["executive_template", "professional_template"]
        
        # Creative positions
        if any(title in job_title_lower for title in ["designer", "artist", "creative", "writer", "content", "marketing", "brand"]):
            return ["creative_template", "modern_template"]
        
        # Tech positions
        if any(title in job_title_lower for title in ["developer", "engineer", "programmer", "software", "data", "analyst"]):
            return ["modern_template", "professional_template"]
        
        # Default
        return ["professional_template"]
    
    def auto_populate_signature(self, content_data: CoverLetterData) -> CoverLetterData:
        """Auto-populate signature if missing.
        
        Args:
            content_data: Cover letter data to update
            
        Returns:
            Updated cover letter data
        """
        if not content_data.signature or not content_data.signature.strip():
            content_data.signature = f"Sincerely,\n{content_data.sender_name}"
        
        return content_data
