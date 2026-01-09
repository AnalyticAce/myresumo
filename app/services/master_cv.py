"""Structured Master CV Module.

This module provides functionality to work with structured CV data in JSON/YAML format,
enabling better LLM processing and easier customization for different job applications.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


# Master CV Schema Definition
MASTER_CV_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Master CV",
    "description": "Structured master CV format for PowerCV",
    "type": "object",
    "required": ["profile", "experience", "skills", "education"],
    "properties": {
        "meta": {
            "type": "object",
            "description": "Metadata about the CV",
            "properties": {
                "version": {"type": "string"},
                "last_updated": {"type": "string"},
                "author": {"type": "string"},
            },
        },
        "profile": {
            "type": "object",
            "description": "Personal and contact information",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "title": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "location": {"type": "string"},
                "linkedin": {"type": "string"},
                "github": {"type": "string"},
                "website": {"type": "string"},
                "summary": {"type": "string"},
            },
        },
        "experience": {
            "type": "array",
            "description": "Work experience entries",
            "items": {
                "type": "object",
                "required": ["company", "role", "period"],
                "properties": {
                    "company": {"type": "string"},
                    "role": {"type": "string"},
                    "period": {"type": "string"},
                    "location": {"type": "string"},
                    "current": {"type": "boolean"},
                    "achievements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "technologies": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "highlights": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "skills": {
            "type": "object",
            "description": "Skills organized by category",
            "properties": {
                "technical": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "programming": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "frameworks": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "databases": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "devops": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "soft": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "languages": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "certifications": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "education": {
            "type": "array",
            "description": "Education entries",
            "items": {
                "type": "object",
                "required": ["institution", "degree", "period"],
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": "string"},
                    "period": {"type": "string"},
                    "location": {"type": "string"},
                    "thesis": {"type": "string"},
                    "relevant_courses": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "projects": {
            "type": "array",
            "description": "Notable projects",
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "technologies": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "url": {"type": "string"},
                    "achievements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "awards": {
            "type": "array",
            "description": "Awards and recognitions",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "issuer": {"type": "string"},
                    "year": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
        },
        "interests": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}


class MasterCV:
    """Class for managing structured master CV data."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize MasterCV with data.

        Args:
            data: CV data dictionary
        """
        self.data = data or self._create_empty_cv()

    def _create_empty_cv(self) -> Dict[str, Any]:
        """Create empty CV structure.

        Returns:
            Empty CV data dictionary
        """
        return {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "author": "",
            },
            "profile": {
                "name": "",
                "title": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": "",
                "website": "",
                "summary": "",
            },
            "experience": [],
            "skills": {
                "technical": [],
                "programming": [],
                "frameworks": [],
                "databases": [],
                "devops": [],
                "soft": [],
                "languages": [],
                "certifications": [],
            },
            "education": [],
            "projects": [],
            "awards": [],
            "interests": [],
        }

    @classmethod
    def from_file(cls, file_path: str) -> "MasterCV":
        """Load CV from JSON or YAML file.

        Args:
            file_path: Path to the CV file

        Returns:
            MasterCV instance
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CV file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix.lower() in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif path.suffix.lower() == ".json":
                data = json.load(f)
            else:
                # Try to detect format
                content = f.read()
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = yaml.safe_load(content)

        return cls(data)

    def to_file(self, file_path: str, format: str = "yaml") -> None:
        """Save CV to JSON or YAML file.

        Args:
            file_path: Output file path
            format: Output format ('json' or 'yaml')
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            if format.lower() == "yaml":
                yaml.dump(
                    self.data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            else:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Convert CV to Markdown format.

        Returns:
            CV in Markdown format
        """
        lines = []

        # Header
        profile = self.data.get("profile", {})
        lines.append(f"# {profile.get('name', 'Name')}")
        lines.append(f"**{profile.get('title', 'Professional')}")
        lines.append("")
        lines.append("## Contact Information")
        lines.append(f"- Email: {profile.get('email', 'N/A')}")
        lines.append(f"- Phone: {profile.get('phone', 'N/A')}")
        lines.append(f"- Location: {profile.get('location', 'N/A')}")
        if profile.get("linkedin"):
            lines.append(f"- LinkedIn: {profile.get('linkedin')}")
        if profile.get("github"):
            lines.append(f"- GitHub: {profile.get('github')}")
        if profile.get("website"):
            lines.append(f"- Website: {profile.get('website')}")
        lines.append("")
        lines.append("## Professional Summary")
        lines.append(profile.get("summary", ""))

        # Experience
        experience = self.data.get("experience", [])
        if experience:
            lines.append("")
            lines.append("## Work Experience")
            for job in experience:
                lines.append("")
                lines.append(f"### {job.get('role', 'Role')} - {job.get('company', 'Company')}")
                lines.append(f"*{job.get('period', 'Period')} | {job.get('location', 'Location')}*")
                if job.get("achievements"):
                    for achievement in job.get("achievements", []):
                        lines.append(f"- {achievement}")

        # Skills
        skills = self.data.get("skills", {})
        if skills:
            lines.append("")
            lines.append("## Skills")
            for category, skill_list in skills.items():
                if skill_list:
                    category_name = category.title()
                    lines.append(f"**{category_name}:** {', '.join(skill_list)}")

        # Education
        education = self.data.get("education", [])
        if education:
            lines.append("")
            lines.append("## Education")
            for edu in education:
                lines.append("")
                lines.append(f"### {edu.get('degree', 'Degree')} in {edu.get('field', 'Field')}")
                lines.append(f"**{edu.get('institution', 'Institution')}**")
                lines.append(f"*{edu.get('period', 'Period')}*")

        # Projects
        projects = self.data.get("projects", [])
        if projects:
            lines.append("")
            lines.append("## Projects")
            for project in projects:
                lines.append("")
                lines.append(f"### {project.get('name', 'Project')}")
                lines.append(project.get("description", ""))
                if project.get("technologies"):
                    lines.append(f"**Technologies:** {', '.join(project.get('technologies', []))}")
                if project.get("url"):
                    lines.append(f"**Link:** {project.get('url')}")
                if project.get("achievements"):
                    for achievement in project.get("achievements", []):
                        lines.append(f"- {achievement}")

        # Awards
        awards = self.data.get("awards", [])
        if awards:
            lines.append("")
            lines.append("## Awards & Recognition")
            for award in awards:
                lines.append(f"- **{award.get('title', 'Award')}** ({award.get('year', 'Year')}): {award.get('description', '')}")

        return "\n".join(lines)

    def get_skills(self, category: Optional[str] = None) -> List[str]:
        """Get skills from a specific category or all skills.

        Args:
            category: Skill category (technical, programming, frameworks, etc.)

        Returns:
            List of skills
        """
        skills = self.data.get("skills", {})
        if category:
            return skills.get(category, [])
        else:
            all_skills = []
            for skill_list in skills.values():
                all_skills.extend(skill_list)
            return all_skills

    def get_experience_by_role(self, role_keywords: List[str]) -> List[Dict[str, Any]]:
        """Get experience entries matching role keywords.

        Args:
            role_keywords: Keywords to match against role titles

        Returns:
            List of matching experience entries
        """
        matching = []
        for job in self.data.get("experience", []):
            role = job.get("role", "").lower()
            if any(keyword.lower() in role for keyword in role_keywords):
                matching.append(job)
        return matching

    def get_experience_by_company(self, company_keywords: List[str]) -> List[Dict[str, Any]]:
        """Get experience entries matching company keywords.

        Args:
            company_keywords: Keywords to match against company names

        Returns:
            List of matching experience entries
        """
        matching = []
        for job in self.data.get("experience", [], []):
            company = job.get("company", "").lower()
            if any(keyword.lower() in company for keyword in company_keywords):
                matching.append(job)
        return matching

    def get_relevant_experience(self, job_requirements: List[str]) -> List[Dict[str, Any]]:
        """Get experience entries relevant to job requirements.

        Args:
            job_requirements: List of requirement keywords

        Returns:
            List of relevant experience entries sorted by relevance
        """
        experience = self.data.get("experience", [])
        scored = []

        for job in experience:
            score = 0
            role = job.get("role", "").lower()
            achievements = " ".join(job.get("achievements", [])).lower()
            technologies = " ".join(job.get("technologies", [])).lower()

            for req in job_requirements:
                req_lower = req.lower()
                if req_lower in role:
                    score += 3
                if req_lower in achievements:
                    score += 2
                if req_lower in technologies:
                    score += 1

            if score > 0:
                scored.append((score, job))

        # Sort by score descending
        scored.sort(key=lambda x: -x[0])
        return [job for _, job in scored]

    def extract_for_job(self, job_keywords: List[str], max_years: int = 10) -> Dict[str, Any]:
        """Extract relevant CV sections for a specific job.

        Args:
            job_keywords: Keywords to prioritize
            max_years: Maximum years of experience to include

        Returns:
            Extracted CV data for the job
        """
        relevant_experience = self.get_relevant_experience(job_keywords)

        # Filter to recent experience only
        recent_experience = []
        for job in relevant_experience:
            # Simple check - keep if first entry or has "current" flag
            if job.get("current", False) or len(recent_experience) < 3:
                recent_experience.append(job)

        # Prioritize matching skills
        skills = self.data.get("skills", {})
        relevant_skills = {}
        for category, skill_list in skills.items():
            matching = [s for s in skill_list if any(kw.lower() in s.lower() for kw in job_keywords)]
            if matching:
                relevant_skills[category] = matching

        return {
            "profile": self.data.get("profile", {}),
            "experience": recent_experience,
            "skills": relevant_skills,
            "education": self.data.get("education", [])[:2],  # Top 2 education entries
            "projects": [
                p
                for p in self.data.get("projects", [])
                if any(kw.lower() in p.get("description", "").lower() for kw in job_keywords)
            ][:3],
        }

    def validate(self) -> tuple[bool, List[str]]:
        """Validate CV data against schema.

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check required fields
        profile = self.data.get("profile", {})
        if not profile.get("name"):
            errors.append("Profile name is required")
        if not profile.get("email"):
            errors.append("Profile email is required")

        experience = self.data.get("experience", [])
        if not experience:
            errors.append("At least one work experience entry is required")

        skills = self.data.get("skills", {})
        if not any(skills.get(cat) for cat in skills):
            errors.append("At least one skill category must have entries")

        education = self.data.get("education", [])
        if not education:
            errors.append("At least one education entry is required")

        return len(errors) == 0, errors


class CVTemplate:
    """Templates for creating Master CV files."""

    @staticmethod
    def software_engineer() -> Dict[str, Any]:
        """Get template for software engineer.

        Returns:
            Software engineer CV template
        """
        return {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "author": "Your Name",
            },
            "profile": {
                "name": "Your Name",
                "title": "Software Engineer",
                "email": "your.email@example.com",
                "phone": "+31 6 12345678",
                "location": "Amsterdam, Netherlands",
                "linkedin": "https://linkedin.com/in/yourname",
                "github": "https://github.com/yourname",
                "website": "https://yourname.dev",
                "summary": "Experienced software engineer with a passion for building scalable, user-friendly applications. Skilled in full-stack development with a focus on clean code and best practices.",
            },
            "experience": [
                {
                    "company": "Tech Company",
                    "role": "Senior Software Engineer",
                    "period": "2022 - Present",
                    "location": "Amsterdam",
                    "current": True,
                    "achievements": [
                        "Led development of microservices architecture reducing system latency by 40%",
                        "Mentored 5 junior developers and established code review practices",
                        "Implemented CI/CD pipelines reducing deployment time by 60%",
                    ],
                    "technologies": ["Python", "Docker", "Kubernetes", "AWS"],
                    "highlights": [],
                },
                {
                    "company": "Startup Inc",
                    "role": "Software Engineer",
                    "period": "2020 - 2022",
                    "location": "Rotterdam",
                    "current": False,
                    "achievements": [
                        "Developed full-stack web applications using React and Node.js",
                        "Built RESTful APIs serving 100k+ daily requests",
                        "Integrated payment processing systems (Stripe, PayPal)",
                    ],
                    "technologies": ["React", "Node.js", "PostgreSQL", "Redis"],
                    "highlights": [],
                },
            ],
            "skills": {
                "technical": ["System Design", "API Development", "Database Design"],
                "programming": ["Python", "JavaScript", "TypeScript", "SQL"],
                "frameworks": ["React", "Django", "FastAPI", "Flask"],
                "databases": ["PostgreSQL", "MongoDB", "Redis"],
                "devops": ["Docker", "Kubernetes", "AWS", "CI/CD", "Git"],
                "soft": ["Team Leadership", "Problem Solving", "Communication"],
                "languages": ["English (Native)", "Dutch (Intermediate)", "German (Basic)"],
                "certifications": ["AWS Solutions Architect", "Docker Certified Associate"],
            },
            "education": [
                {
                    "institution": "University of Amsterdam",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "period": "2016 - 2020",
                    "location": "Amsterdam",
                    "thesis": "Distributed Systems Optimization",
                },
            ],
            "projects": [
                {
                    "name": "Open Source Project",
                    "description": "Contributed to popular open source library for data processing",
                    "technologies": ["Python", "PyPI"],
                    "url": "https://github.com/yourname/project",
                    "achievements": ["500+ GitHub stars", "10k+ monthly downloads"],
                },
            ],
            "awards": [
                {
                    "title": "Best Hackathon Project",
                    "issuer": "TechConf 2021",
                    "year": "2021",
                    "description": "Won first place for AI-powered task management app",
                },
            ],
            "interests": ["Open Source", "Machine Learning", "Cloud Architecture"],
        }

    @staticmethod
    def data_scientist() -> Dict[str, Any]:
        """Get template for data scientist.

        Returns:
            Data scientist CV template
        """
        return {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "author": "Your Name",
            },
            "profile": {
                "name": "Your Name",
                "title": "Data Scientist",
                "email": "your.email@example.com",
                "phone": "+31 6 12345678",
                "location": "Utrecht, Netherlands",
                "linkedin": "https://linkedin.com/in/yourname",
                "github": "https://github.com/yourname",
                "summary": "Data scientist with expertise in machine learning, statistical analysis, and data visualization. Passionate about turning data into actionable insights.",
            },
            "experience": [
                {
                    "company": "Data Corp",
                    "role": "Senior Data Scientist",
                    "period": "2021 - Present",
                    "location": "Utrecht",
                    "current": True,
                    "achievements": [
                        "Developed ML models improving prediction accuracy by 25%",
                        "Built real-time analytics dashboard processing 1M+ events/day",
                        "Led team of 4 data scientists on customer segmentation project",
                    ],
                    "technologies": ["Python", "TensorFlow", "Spark", "AWS"],
                },
            ],
            "skills": {
                "technical": ["Machine Learning", "Statistical Analysis", "A/B Testing"],
                "programming": ["Python", "R", "SQL", "Scala"],
                "frameworks": ["TensorFlow", "PyTorch", "Scikit-learn", "Pandas"],
                "databases": ["PostgreSQL", "MongoDB", "BigQuery"],
                "devops": ["Docker", "AWS", "MLflow", "Git"],
                "soft": ["Data Storytelling", "Cross-functional Collaboration"],
                "certifications": ["AWS Machine Learning Specialty", "TensorFlow Developer"],
            },
            "education": [
                {
                    "institution": "Delft University of Technology",
                    "degree": "Master of Science",
                    "field": "Data Science",
                    "period": "2019 - 2021",
                },
            ],
            "projects": [],
            "awards": [],
            "interests": ["Kaggle", "AI Research", "Data Visualization"],
        }


def create_template_cv(role: str = "software_engineer") -> MasterCV:
    """Create a template CV for a specific role.

    Args:
        role: Role type (software_engineer, data_scientist, etc.)

    Returns:
        MasterCV instance with template data
    """
    templates = {
        "software_engineer": CVTemplate.software_engineer(),
        "data_scientist": CVTemplate.data_scientist(),
    }

    template_data = templates.get(role, templates["software_engineer"])
    return MasterCV(template_data)
