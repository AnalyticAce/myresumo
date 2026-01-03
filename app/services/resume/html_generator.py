"""HTML/CSS to PDF generator module."""
import os
import logging
from typing import Dict, Optional, Union
import json
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
try:
    from weasyprint import HTML, CSS
except ImportError:
    HTML = None
    CSS = None

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generates PDF resumes using HTML/CSS templates and WeasyPrint."""

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize HTML Generator.

        Args:
            template_dir: Directory containing HTML templates. If None, uses default.
        """
        if template_dir is None:
            # Default to parallel directory structure as latex templates
            base_dir = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))))
            template_dir = os.path.join(base_dir, 'data', 'templates')

        self.template_dir = template_dir
        self.json_data = None
        self.env = None
        self.setup_jinja_environment()

        if HTML is None:
            logger.warning(
                "WeasyPrint not installed. PDF generation will fail.")

    def setup_jinja_environment(self) -> None:
        """Set up Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )

        # Register standard filters
        self.env.filters["format_date"] = self.format_date
        self.env.filters["nl2br"] = self.nl2br

    def load_json(self, json_path: str) -> bool:
        """Load JSON data from file."""
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                self.json_data = json.load(file)
            return True
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            return False

    def parse_json_from_string(self, json_string: str) -> bool:
        """Parse JSON data from string."""
        try:
            self.json_data = json.loads(json_string)
            return True
        except Exception as e:
            logger.error(f"Error parsing JSON string: {e}")
            return False

    def generate_pdf(self, template_name: str, output_path: str) -> bool:
        """Generate PDF from HTML template.

        Args:
            template_name: Name of the HTML template (e.g., 'modern_resume.html')
            output_path: Path to write the PDF file

        Returns:
            bool: True if successful
        """
        if not self.json_data:
            logger.error("No data loaded")
            return False

        if not HTML:
            logger.error("WeasyPrint not installed")
            return False

        try:
            template = self.env.get_template(template_name)
            html_content = template.render(data=self.json_data)

            # Base URL for assets (css, images)
            base_url = self.template_dir

            HTML(string=html_content, base_url=base_url).write_pdf(output_path)
            logger.info(f"PDF generated at {output_path}")
            return True

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False

    @staticmethod
    def format_date(date_str) -> str:
        """Format date string (MM/YYYY -> Month YYYY)."""
        if not date_str or str(date_str).strip().lower() == "present":
            return "Present"

        try:
            date_str = str(date_str).strip()
            # Handle MM/YYYY
            if len(date_str.split('/')) == 2:
                dt = datetime.strptime(date_str, "%m/%Y")
                return dt.strftime("%b %Y")
            # Handle YYYY-MM-DD
            if len(date_str.split('-')) == 3:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime("%b %Y")
            # Handle YYYY
            if len(date_str) == 4 and date_str.isdigit():
                return date_str

            return date_str
        except Exception:
            return date_str

    @staticmethod
    def nl2br(value):
        """Convert newlines to <br> tags."""
        if not value:
            return ""
        return value.replace('\n', '<br>\n')
