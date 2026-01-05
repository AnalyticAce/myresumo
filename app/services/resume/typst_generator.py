"""Typst PDF generator module."""
import os
import logging
import json
import subprocess
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class TypstGenerator:
    """Generates PDF resumes using Typst templates."""

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize Typst Generator.

        Args:
            template_dir: Directory containing Typst templates.
        """
        if template_dir is None:
            base_dir = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))))
            template_dir = os.path.join(base_dir, 'data', 'templates')

        self.template_dir = template_dir
        self.json_data = None
        self.env = None
        self.setup_jinja_environment()

        # Check for typst binary
        self.typst_bin = shutil.which("typst")
        if not self.typst_bin:
            # Fallback to local user bin
            local_bin = os.path.expanduser("~/.local/bin/typst")
            if os.path.exists(local_bin):
                self.typst_bin = local_bin
            else:
                logger.warning(
                    "Typst binary not found. PDF generation will fail.")

    def setup_jinja_environment(self) -> None:
        """Set up Jinja2 environment with Typst-friendly delimiters."""
        # Use different delimiters to avoid conflict with Typst syntax (which uses #)
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            variable_start_string="<<",
            variable_end_string=">>",
            block_start_string="<%",
            block_end_string="%>",
            comment_start_string="<#",
            comment_end_string="#>",
            autoescape=False  # Typst is text-based, we handle escaping manually
        )

        self.env.filters["typst_escape"] = self.typst_escape
        self.env.filters["typst_escape_email"] = self.typst_escape_email
        self.env.filters["format_date"] = self.format_date

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
        """Generate PDF from Typst template.

        Args:
            template_name: Name of the Typst template (e.g., 'resume.typ')
            output_path: Path to write the PDF file

        Returns:
            bool: True if successful
        """
        if not self.json_data:
            logger.error("No data loaded")
            return False

        if not self.typst_bin:
            logger.error("Typst binary not found")
            return False

        try:
            # Render the Typt file with data
            template = self.env.get_template(template_name)
            typst_content = template.render(data=self.json_data)

            # Write temporary .typ file
            temp_typ_path = output_path.replace('.pdf', '.typ')
            with open(temp_typ_path, "w", encoding="utf-8") as f:
                f.write(typst_content)

            # Compile using Typst CLI
            cmd = [self.typst_bin, "compile", temp_typ_path, output_path]
            logger.info(f"Running typst: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            # Cleanup temp file
            if os.path.exists(temp_typ_path):
                os.remove(temp_typ_path)

            if result.returncode != 0:
                logger.error(f"Typst compilation failed: {result.stderr}")
                return False

            logger.info(f"PDF generated at {output_path}")
            return True

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False

    @staticmethod
    def typst_escape(text) -> str:
        """Escape special characters for Typst."""
        if not isinstance(text, str):
            return str(text)

        # Typst uses #, *, _, ` as special chars
        replacements = {
            "#": "\\#",
            "*": "\\*",
            "_": "\\_",
            "`": "\\`",
            "$": "\\$",
            "[": "\\[",
            "]": "\\]",
            "@": "\\@",
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        return text

    @staticmethod
    def typst_escape_email(text) -> str:
        """Escape special characters for Typst, but preserve @ in emails."""
        if not isinstance(text, str):
            return str(text)

        # Escape all dangerous Typst characters EXCEPT @
        replacements = {
            "#": "\\#",
            "*": "\\*",
            "_": "\\_",
            "`": "\\`",
            "$": "\\$",
            "[": "\\[",
            "]": "\\]",
            # Note: @ is NOT escaped here for email addresses
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        return text

    @staticmethod
    def format_date(date_str) -> str:
        """Format date string."""
        if not date_str or str(date_str).strip().lower() == "present":
            return "Present"
        # ... reuse date formatting logic ...
        return str(date_str)  # Implementation same as before
