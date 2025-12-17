"""Cover letter templates module.

This module defines various cover letter templates with different styles
and formats for professional applications.
"""

from typing import Dict, List


class CoverLetterTemplates:
    """Collection of cover letter templates with different styles."""
    
    @staticmethod
    def get_template(template_name: str) -> Dict[str, str]:
        """Get a specific template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Dictionary containing template information and structure
        """
        templates = CoverLetterTemplates.get_all_templates()
        return templates.get(template_name, templates["professional_template"])
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, str]]:
        """Get all available templates.
        
        Returns:
            Dictionary of all templates with their information
        """
        return {
            "professional_template": {
                "name": "professional_template",
                "display_name": "Professional",
                "description": "Classic professional template suitable for most applications",
                "template": """{sender_info}
{date}

{recipient_info}

Subject: Application for {job_title} position{job_ref}

Dear {recipient_salutation},

{introduction}

{body_paragraphs}

{closing}

{signature}"""
            },
            
            "modern_template": {
                "name": "modern_template",
                "display_name": "Modern",
                "description": "Contemporary design with clean layout and concise formatting",
                "template": """{sender_info}
{date}

{recipient_info}

Re: {job_title} Application{job_ref}

Dear {recipient_salutation},

{introduction}

{body_paragraphs}

{closing}

{signature}"""
            },
            
            "creative_template": {
                "name": "creative_template",
                "display_name": "Creative",
                "description": "More expressive template for creative industries",
                "template": """{sender_info}
{date}

{recipient_info}

Subject: Excited to Apply for {job_title} Position{job_ref}

Dear {recipient_salutation},

{introduction}

{body_paragraphs}

{closing}

{signature}"""
            },
            
            "executive_template": {
                "name": "executive_template",
                "display_name": "Executive",
                "description": "Formal template for senior-level positions",
                "template": """{sender_info}
{date}

{recipient_info}

Subject: Executive Application: {job_title}{job_ref}

Dear {recipient_salutation},

{introduction}

{body_paragraphs}

{closing}

Respectfully,

{signature}"""
            }
        }
    
    @staticmethod
    def format_sender_info(content_data: Dict[str, str]) -> str:
        """Format sender information block.
        
        Args:
            content_data: Cover letter content data
            
        Returns:
            Formatted sender information string
        """
        sender_parts = [
            content_data.get("sender_name", ""),
            content_data.get("sender_location", ""),
            content_data.get("sender_email", ""),
            content_data.get("sender_phone", "")
        ]
        return "\n".join(filter(None, sender_parts))
    
    @staticmethod
    def format_recipient_info(content_data: Dict[str, str]) -> str:
        """Format recipient information block.
        
        Args:
            content_data: Cover letter content data
            
        Returns:
            Formatted recipient information string
        """
        recipient_parts = []
        
        if content_data.get("recipient_name"):
            recipient_parts.append(content_data["recipient_name"])
        
        recipient_parts.append(content_data.get("company_name", ""))
        
        if content_data.get("company_address"):
            recipient_parts.append(content_data["company_address"])
        
        return "\n".join(filter(None, recipient_parts))
    
    @staticmethod
    def get_recipient_salutation(content_data: Dict[str, str]) -> str:
        """Get appropriate recipient salutation.
        
        Args:
            content_data: Cover letter content data
            
        Returns:
            Recipient salutation string
        """
        recipient_name = content_data.get("recipient_name", "")
        if recipient_name:
            # Split name and use last name with appropriate title
            name_parts = recipient_name.split()
            if len(name_parts) > 1:
                last_name = name_parts[-1]
                return f"Mr./Ms. {last_name}"
            else:
                return recipient_name
        return "Hiring Manager"
    
    @staticmethod
    def format_job_reference(job_reference: str) -> str:
        """Format job reference line.
        
        Args:
            job_reference: Job reference number
            
        Returns:
            Formatted job reference string
        """
        if job_reference and job_reference.strip():
            return f" (Ref: {job_reference.strip()})"
        return ""
    
    @staticmethod
    def format_body_paragraphs(body_paragraphs: List[str]) -> str:
        """Format body paragraphs with proper spacing.
        
        Args:
            body_paragraphs: List of body paragraph strings
            
        Returns:
            Formatted body paragraphs string
        """
        filtered_paragraphs = [p.strip() for p in body_paragraphs if p.strip()]
        return "\n\n".join(filtered_paragraphs)
