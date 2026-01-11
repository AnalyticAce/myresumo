"""Centralized template configuration for PowerCV.

This module defines all available templates, their validation patterns,
and alias mappings for consistent template selection across the application.
"""

from typing import Dict, List


class TemplateConfig:
    """Centralized configuration for CV templates."""

    # Canonical template paths
    TEMPLATES = {
        "resume.typ": {
            "description": "Clean, traditional layout",
            "type": "typst",
            "status": "active"
        },
        "modern.typ": {
            "description": "Contemporary two-column design",
            "type": "typst",
            "status": "active"
        },
        "brilliant-cv/cv.typ": {
            "description": "Professional template with icons",
            "type": "typst",
            "status": "active"
        },
        "awesome-cv/cv.tex": {
            "description": "LaTeX-based elegant design",
            "type": "latex",
            "status": "template_ready"
        },
        "simple-xd-resume/cv.typ": {
            "description": "Minimal ATS-friendly design",
            "type": "typst",
            "status": "active"
        },
        "rendercv-classic/cv.typ": {
            "description": "Highly customizable classic design",
            "type": "typst",
            "status": "active"
        },
        "rendercv-modern/cv.typ": {
            "description": "Modern minimalist design",
            "type": "typst",
            "status": "active"
        },
    }

    # Alias mappings for template selection
    ALIASES = {
        # Legacy aliases
        "classic": "resume.typ",
        "simple": "resume.typ",

        # Template-specific aliases
        "modern": "modern.typ",
        "brilliant-cv": "brilliant-cv/cv.typ",
        "brilliant": "brilliant-cv/cv.typ",
        "awesome-cv": "awesome-cv/cv.tex",
        "awesome": "awesome-cv/cv.tex",
        "simple-xd-resume": "simple-xd-resume/cv.typ",
        "simple-xd": "simple-xd-resume/cv.typ",
        "xd": "simple-xd-resume/cv.typ",
        "rendercv-classic": "rendercv-classic/cv.typ",
        "rendercv": "rendercv-classic/cv.typ",
        "rendercv-modern": "rendercv-modern/cv.typ",
    }

    @classmethod
    def get_valid_templates(cls) -> List[str]:
        """Get list of all valid template paths."""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template_pattern(cls) -> str:
        """Get regex pattern for template validation."""
        escaped_templates = [template.replace(".", r"\.").replace("/", r"\/")
                           for template in cls.get_valid_templates()]
        return f"^({'|'.join(escaped_templates)})$"

    @classmethod
    def resolve_template(cls, template: str) -> str:
        """Resolve template alias to canonical path."""
        return cls.ALIASES.get(template, template)

    @classmethod
    def is_valid_template(cls, template: str) -> bool:
        """Check if a template (including aliases) is valid."""
        canonical = cls.resolve_template(template)
        return canonical in cls.TEMPLATES

    @classmethod
    def get_template_description(cls, template: str) -> str:
        """Get description for a template."""
        canonical = cls.resolve_template(template)
        return cls.TEMPLATES.get(canonical, {}).get("description", "Unknown template")

    @classmethod
    def get_active_templates(cls) -> Dict[str, dict]:
        """Get all active templates."""
        return {k: v for k, v in cls.TEMPLATES.items() if v["status"] == "active"}

    @classmethod
    def get_template_table_data(cls) -> List[Dict[str, str]]:
        """Get data for template table in README."""
        data = []
        for template_path, info in cls.TEMPLATES.items():
            status_emoji = "" if info["status"] == "active" else ""
            data.append({
                "template": template_path,
                "description": info["description"],
                "status": f"{status_emoji} {info['status'].replace('_', ' ').title()}"
            })
        return data