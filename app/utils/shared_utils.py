"""Shared utilities for PowerCV services."""

import json
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONParser:
    """Utility class for parsing JSON responses from AI APIs."""

    @staticmethod
    def clean_json_response(response: str) -> str:
        """Remove markdown code fences and cleanup JSON with enhanced error handling.

        Args:
            response: Raw response from API

        Returns:
            str: Cleaned JSON string
        """
        if not response or not response.strip():
            raise ValueError("Empty response received from API")

        response = response.strip()

        # Remove ```json and ``` markers
        if '```' in response:
            match = re.search(
                r'```(?:json)?\s*([\s\S]*?)\s*```', response, re.DOTALL)
            if match:
                response = match.group(1)
            else:
                # Fallback: remove fences manually
                response = re.sub(r'```(?:json)?', '', response)
                response = response.replace('```', '')

        # Find JSON object or array boundaries
        json_start = response.find('{')
        array_start = response.find('[')

        # Determine if we are looking for an object or an array
        start_char = '{'
        end_char = '}'
        start_idx = json_start

        if (array_start != -1 and json_start == -1) or (array_start != -1 and array_start < json_start):
            start_char = '['
            end_char = ']'
            start_idx = array_start

        json_end = response.rfind(end_char)

        if start_idx == -1 or json_end == -1 or json_end <= start_idx:
            # If no structure found, return as is (might be raw string)
            return response.strip()

        response = response[start_idx:json_end+1]
        response = response.strip()

        # Fix common JSON issues safely
        # 1. Fix trailing commas before closing braces/brackets
        response = re.sub(r',\s*\}', '}', response)
        response = re.sub(r',\s*\]', ']', response)

        # 2. Fix missing commas between key-value pairs (handles string, number, bool, null values)
        response = re.sub(
            r'([0-9]|"|true|false|null)\s*\n\s*"', r'\1, "', response)

        # 3. Fix missing commas between closing brace and next key
        response = re.sub(r'\}\s*\n?\s*"([^"]+)"\s*:', r'}, "\1":', response)

        # 4. Remove potential single-line comments // or # (risky but common in AI output)
        response = re.sub(r'^\s*//.*$', '', response, flags=re.MULTILINE)
        response = re.sub(r'^\s*#.*$', '', response, flags=re.MULTILINE)

        return response

    @staticmethod
    def repair_json(json_str: str) -> str:
        """Attempt to repair truncated JSON by closing open braces/brackets.

        Args:
            json_str: The potentially truncated JSON string

        Returns:
            str: Repaired JSON string
        """
        # Count open braces/brackets
        open_braces = json_str.count('{') - json_str.count('}')
        open_brackets = json_str.count('[') - json_str.count(']')

        # Determine last open char to decide closing order (heuristic)
        # This is a simple stack-based approach
        stack = []
        in_string = False
        escape = False

        # Re-scan to build closing stack correctly
        for char in json_str:
            if char == '"' and not escape:
                in_string = not in_string
            elif char == '\\' and in_string:
                escape = not escape
                continue  # Skip next char check
            elif not in_string:
                if char == '{':
                    stack.append('}')
                elif char == '[':
                    stack.append(']')
                elif char == '}':
                    if stack and stack[-1] == '}':
                        stack.pop()
                elif char == ']':
                    if stack and stack[-1] == ']':
                        stack.pop()

            escape = False

        # Perform repair
        if in_string:
            # Close the open string first
            json_str += '"'

        # Append needed closing characters in reverse order
        while stack:
            json_str += stack.pop()

        return json_str

    @staticmethod
    def safe_json_parse(response: str, fallback_structure: Optional[Any] = None) -> Any:
        """Safely parse JSON response with fallback handling.

        Args:
            response: Raw JSON response
            fallback_structure: Default structure if parsing fails

        Returns:
            Parsed JSON or fallback structure
        """
        if not response:
            return fallback_structure.copy() if hasattr(fallback_structure, 'copy') else fallback_structure

        try:
            cleaned = JSONParser.clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(
                f"Raw response (first 2000 chars):\n{response[:2000]}")
            logger.debug(
                f"Cleaned response attempt (first 1000 chars):\n{cleaned[:1000] if 'cleaned' in locals() else 'N/A'}")

            if fallback_structure is not None:
                logger.warning(
                    "Using fallback structure due to JSON parse error")
                return fallback_structure.copy() if hasattr(fallback_structure, 'copy') else fallback_structure

            # Return minimal fallback
            return {"error": "JSON Parse Error", "raw_response": response[:500]}


class TextProcessor:
    """Utility class for text processing operations."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text by normalizing whitespace.

        Args:
            text: Raw text to clean

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        return " ".join(text.split())

    @staticmethod
    def extract_keywords(text: str, patterns: List[str]) -> List[str]:
        """Extract keywords from text using regex patterns.

        Args:
            text: Text to search
            patterns: List of regex patterns

        Returns:
            List of unique keywords found
        """
        keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend([m.title() if m.isupper() else m for m in matches])

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(keyword)

        return unique_keywords

    @staticmethod
    def extract_section(cv_text: str, section_headers: List[str]) -> Optional[str]:
        """Extract a CV section by its header with improved boundary detection.

        Args:
            cv_text: Full CV text
            section_headers: List of possible section headers

        Returns:
            str: Section content or None if not found
        """
        if not cv_text:
            return None

        lines = cv_text.split('\n')
        section_start = None
        section_lines = []

        # Convert headers to uppercase for comparison
        upper_headers = [h.upper() for h in section_headers]

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check if this line matches any of our section headers
            is_header = any(header in line_stripped.upper()
                            for header in upper_headers)

            # Additional check: header should be reasonably short and likely a standalone line or bold
            if is_header and len(line_stripped) < 50:
                if section_start is not None and section_lines:
                    # Found new section, return the previous one
                    return '\n'.join(section_lines).strip()
                section_start = i
                section_lines = []
            elif section_start is not None:
                # Stop if we encounter a line that looks like a new section header
                if (line_stripped and
                    len(line_stripped) < 40 and
                    line_stripped.isupper() and
                    not line_stripped.startswith(('•', '-', '*', '>')) and
                        not any(char.isdigit() for char in line_stripped)):
                    # This looks like a new section header
                    break

                # Add the line
                section_lines.append(line)

        if section_start is not None and section_lines:
            return '\n'.join(section_lines).strip()

        return None

    @staticmethod
    def extract_contact_info(cv_text: str) -> Optional[str]:
        """Extract contact information from CV text.

        Args:
            cv_text: Full CV text

        Returns:
            str: Contact information or None if not found
        """
        if not cv_text:
            return None

        lines = cv_text.split('\n')
        contact_lines = []
        found_contact = False

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Look for contact information patterns
            if any(pattern in line_stripped.lower() for pattern in ['@', '.com', 'phone:', 'tel:', 'location:', 'linkedin:', 'github:']):
                found_contact = True
                contact_lines.append(line_stripped)
            elif found_contact and line_stripped:
                # Continue collecting related lines
                if any(char in line_stripped for char in ['@', '+', 'www.', 'http']):
                    contact_lines.append(line_stripped)
                elif len(contact_lines) < 5:  # Limit initial contact block
                    contact_lines.append(line_stripped)
                else:
                    break
            elif found_contact and not line_stripped:
                # Empty line might end contact section, but allow one empty line if short
                if len(contact_lines) > 0 and i < len(lines) - 1 and lines[i+1].strip():
                    continue
                break

        if contact_lines:
            return '\n'.join(contact_lines).strip()

        return None


class ValidationHelper:
    """Utility class for input validation."""

    @staticmethod
    def validate_text_input(text: str, max_length: int = 10000, field_name: str = "input") -> str:
        """Validate text input.

        Args:
            text: Text to validate
            max_length: Maximum allowed length
            field_name: Name of the field for error messages

        Returns:
            str: Validated text

        Raises:
            ValueError: If validation fails
        """
        if not text or not text.strip():
            raise ValueError(f"{field_name} cannot be empty")

        if len(text) > max_length:
            raise ValueError(
                f"{field_name} exceeds maximum length of {max_length} characters")

        return text.strip()

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format.

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
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")

        return url

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


class ErrorHandler:
    """Utility class for consistent error handling."""

    @staticmethod
    def log_and_raise_error(logger: logging.Logger, message: str, exception_class: type = Exception):
        """Log error and raise exception.

        Args:
            logger: Logger instance
            message: Error message
            exception_class: Exception class to raise
        """
        logger.error(message)
        raise exception_class(message)

    @staticmethod
    def create_error_response(error_message: str, error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
        """Create standardized error response.

        Args:
            error_message: Human-readable error message
            error_code: Machine-readable error code

        Returns:
            Standardized error response dict
        """
        return {
            "error": True,
            "error_code": error_code,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }


class MetricsHelper:
    """Utility class for metrics and scoring."""

    @staticmethod
    def calculate_ats_score(matched_keywords: List[Dict], total_keywords: List[str]) -> int:
        """Calculate ATS score based on keyword matching.

        Args:
            matched_keywords: List of matched keyword dictionaries
            total_keywords: List of all expected keywords

        Returns:
            int: ATS score (0-100)
        """
        if not total_keywords:
            return 0

        matched_count = len(matched_keywords)
        total_count = len(total_keywords)

        score = int((matched_count / total_count) * 100)
        return min(100, max(0, score))

    @staticmethod
    def extract_ats_score_from_text(score_text: str) -> int:
        """Extract numeric ATS score from text with improved accuracy.

        Args:
            score_text: Text containing score (e.g., "85/100", "85%")

        Returns:
            int: Extracted score
        """
        if isinstance(score_text, (int, float)):
            return min(100, max(0, int(score_text)))

        if isinstance(score_text, str):
            # Try to find "X/100" first
            match_base = re.search(r'(\d+)\s*/\s*100', score_text)
            if match_base:
                return min(100, max(0, int(match_base.group(1))))

            # Try to find "X%"
            match_percent = re.search(r'(\d+)\s*%', score_text)
            if match_percent:
                return min(100, max(0, int(match_percent.group(1))))

            # Extract first number found
            match = re.search(r'(\d+)', score_text)
            if match:
                score = int(match.group(1))
                return min(100, max(0, score))

        return 0
