"""Enhanced validation utilities for PowerCV."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Union
from urllib.parse import urlparse

from fastapi import HTTPException, status
from pydantic import BaseModel
import pydantic

logger = logging.getLogger(__name__)


class ValidationHelper:
    """Enhanced validation helper with detailed error messages."""

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL with detailed error messages.

        Args:
            url: URL to validate

        Returns:
            str: Validated URL

        Raises:
            ValueError: If URL is invalid
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        url = url.strip()

        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                raise ValueError(
                    f"URL must use HTTP or HTTPS protocol. Got: {parsed.scheme}")

            # Check netloc (domain)
            if not parsed.netloc:
                raise ValueError("URL must contain a valid domain name")

            # Check for common job board domains
            job_board_domains = [
                'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
                'careerbuilder.com', 'ziprecruiter.com', 'dice.com', 'angel.co'
            ]

            domain = parsed.netloc.lower()
            is_job_board = any(board in domain for board in job_board_domains)

            if not is_job_board:
                logger.warning(
                    f"URL may not be from a known job board: {domain}")

            # Validate URL length
            if len(url) > 2048:
                raise ValueError("URL is too long (max 2048 characters)")

            return url

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid URL format: {str(e)}")

    @staticmethod
    def validate_text_input(
        text: str,
        max_length: int,
        field_name: str,
        min_length: int = 10
    ) -> str:
        """Validate text input with comprehensive checks.

        Args:
            text: Text to validate
            max_length: Maximum allowed length
            field_name: Name of the field for error messages
            min_length: Minimum allowed length

        Returns:
            str: Validated text

        Raises:
            ValueError: If text is invalid
        """
        if not text or not text.strip():
            raise ValueError(f"{field_name} cannot be empty")

        text = text.strip()

        if len(text) < min_length:
            raise ValueError(
                f"{field_name} must be at least {min_length} characters long")

        if len(text) > max_length:
            raise ValueError(
                f"{field_name} is too long (max {max_length} characters)")

        # Check for potentially malicious content
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'vbscript:',
            r'data:text/html',
            r'<?php',
            r'<%.*%>',
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                raise ValueError(
                    f"{field_name} contains potentially unsafe content")

        # Check for excessive repetition (possible spam/filler)
        words = text.split()
        if len(words) > 50:
            unique_words = set(word.lower() for word in words)
            if len(unique_words) / len(words) < 0.3:
                logger.warning(
                    f"{field_name} may contain excessive repetition")
                raise ValueError(f"{field_name} contains excessive repetition")

        return text

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address with detailed checks.

        Args:
            email: Email to validate

        Returns:
            str: Validated email

        Raises:
            ValueError: If email is invalid
        """
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")

        email = email.strip().lower()

        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        # Additional checks
        if len(email) > 254:
            raise ValueError("Email is too long")

        if email.startswith('.') or email.endswith('.'):
            raise ValueError("Email cannot start or end with a dot")

        if '..' in email:
            raise ValueError("Email cannot contain consecutive dots")

        return email

    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """Validate phone number with international format support.

        Args:
            phone: Phone number to validate

        Returns:
            str: Normalized phone number

        Raises:
            ValueError: If phone number is invalid
        """
        if not phone or not phone.strip():
            raise ValueError("Phone number cannot be empty")

        phone = phone.strip()

        # Remove common formatting characters
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Check minimum length (at least 10 digits for most countries)
        if len(cleaned) < 10:
            raise ValueError("Phone number is too short")

        if len(cleaned) > 15:
            raise ValueError("Phone number is too long")

        # Must start with + for international numbers or be a valid local format
        if not (cleaned.startswith('+') or re.match(r'^\d{10,15}$', cleaned)):
            raise ValueError(
                "Phone number must start with + (international) or be 10-15 digits")

        return cleaned

    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: List[str]) -> str:
        """Validate file path and extension.

        Args:
            file_path: File path to validate
            allowed_extensions: List of allowed extensions

        Returns:
            str: Validated file path

        Raises:
            ValueError: If file path is invalid
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")

        file_path = file_path.strip()

        try:
            path = Path(file_path)

            # Check for path traversal attempts
            if '..' in path.parts:
                raise ValueError("Path traversal not allowed")

            # Check extension
            if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                raise ValueError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")

            # Check filename length
            if len(path.name) > 255:
                raise ValueError("Filename too long")

            return file_path

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid file path: {str(e)}")

    @staticmethod
    def validate_template_name(template: str, available_templates: List[str]) -> str:
        """Validate template name against available options.

        Args:
            template: Template name to validate
            available_templates: List of available template names

        Returns:
            str: Validated template name

        Raises:
            ValueError: If template is not available
        """
        if not template or not template.strip():
            raise ValueError("Template name cannot be empty")

        template = template.strip()

        if template not in available_templates:
            raise ValueError(
                f"Template '{template}' not available. "
                f"Available templates: {', '.join(available_templates)}"
            )

        return template

    @staticmethod
    def validate_json_structure(data: Any, required_fields: List[str]) -> Dict[str, Any]:
        """Validate JSON structure and required fields.

        Args:
            data: Data to validate (dict or JSON string)
            required_fields: List of required field names

        Returns:
            Dict[str, Any]: Validated data

        Raises:
            ValueError: If structure is invalid
        """
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {str(e)}")

        if not isinstance(data, dict):
            raise ValueError("Data must be a JSON object")

        missing_fields = [
            field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}")

        return data

    @staticmethod
    def validate_skill_list(skills: Union[str, List[str]]) -> List[str]:
        """Validate and normalize skill list.

        Args:
            skills: Skills to validate (string or list)

        Returns:
            List[str]: Normalized skill list

        Raises:
            ValueError: If skills are invalid
        """
        if isinstance(skills, str):
            # Split by common delimiters
            skills_list = re.split(r'[,;]\s*', skills.strip())
        elif isinstance(skills, list):
            skills_list = skills
        else:
            raise ValueError("Skills must be a string or list")

        if len(skills_list) > 50:
            raise ValueError("Too many skills provided (max 50)")

        # Clean and validate each skill
        validated_skills = []
        for skill in skills_list:
            skill = skill.strip()
            if skill and len(skill) >= 2 and len(skill) <= 50:
                validated_skills.append(skill)

        if not validated_skills:
            raise ValueError("At least one valid skill is required")

        return validated_skills

    @staticmethod
    def validate_date_range(start_date: str, end_date: str = None) -> tuple:
        """Validate date range.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: Optional end date

        Returns:
            tuple: (start_date, end_date) as datetime objects

        Raises:
            ValueError: If dates are invalid
        """
        from datetime import datetime

        try:
            start_dt = datetime.strptime(start_date.strip(), '%Y-%m-%d')
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date.strip(), '%Y-%m-%d')
            except ValueError:
                raise ValueError("End date must be in YYYY-MM-DD format")

            if end_dt < start_dt:
                raise ValueError("End date cannot be before start date")

            return start_dt, end_dt

        return start_dt, None

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Remove or replace unsafe characters
        safe_chars = []
        for char in filename:
            if char.isalnum() or char in "-_ .":
                safe_chars.append(char)
            else:
                safe_chars.append("_")

        # Remove multiple consecutive underscores/spaces
        sanitized = "".join(safe_chars)
        sanitized = re.sub(r'[_\s]+', '_', sanitized)

        # Limit length
        return sanitized[:100].strip('_')


class EnhancedValidationError(Exception):
    """Enhanced validation error with field details."""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation error for {field}: {message}")


def validate_pydantic_model(model: BaseModel, data: Dict[str, Any]) -> BaseModel:
    """Validate data against a Pydantic model with detailed errors.

    Args:
        model: Pydantic model class
        data: Data to validate

    Returns:
        BaseModel: Validated model instance

    Raises:
        HTTPException: If validation fails
    """
    try:
        return model(**data)
    except pydantic.ValidationError as e:
        errors = []
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            message = error['msg']
            errors.append(f"{field}: {message}")

        error_detail = "Validation failed: " + "; ".join(errors)
        logger.warning(f"Pydantic validation error: {error_detail}")

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail
        )
