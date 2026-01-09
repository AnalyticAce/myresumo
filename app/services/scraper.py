"""Job Description Scraper Module.

This module provides functionality to scrape job descriptions from various job boards
including LinkedIn, Indeed, Glassdoor, and company career pages.
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, List
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class JobDescriptionScraper(ABC):
    """Abstract base class for job description scrapers."""

    @abstractmethod
    async def fetch(self, url: str) -> Dict[str, str]:
        """Fetch job description from URL.

        Args:
            url: The job posting URL

        Returns:
            Dict containing job title, company, location, and description
        """
        pass


class LinkedInScraper(JobDescriptionScraper):
    """Scraper for LinkedIn job postings."""

    async def fetch(self, url: str) -> Dict[str, str]:
        """Fetch job description from LinkedIn.

        Args:
            url: LinkedIn job posting URL

        Returns:
            Dict containing job details
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract job description from meta tags or script tags
            description = self._extract_description(soup)
            title = self._extract_title(soup)
            company = self._extract_company(soup, url)
            location = self._extract_location(soup)

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "source": "linkedin",
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to scrape LinkedIn job: {str(e)}")
            return {
                "title": "",
                "company": "",
                "location": "",
                "description": "",
                "source": "linkedin",
                "url": url,
                "error": str(e),
            }

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from LinkedIn page."""
        # Try to find description in script tags with job data
        for script in soup.find_all("script"):
            if script.string and "description" in script.string.lower():
                try:
                    # Try to extract from JSON-like structure
                    match = re.search(r'"description"\s*:\s*"([^"]*)"', script.string)
                    if match:
                        return self._clean_text(match.group(1))
                except Exception:
                    continue

        # Fallback to meta description
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            return self._clean_text(meta_desc.get("content", ""))

        return ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from LinkedIn page."""
        # Try multiple selectors
        selectors = [
            ("h1", {"class": lambda x: x and "top-card" in str(x).lower()}),
            ("h1", {"class": "top-card__job-title"}),
            ("h1", {}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                return self._clean_text(element.get_text())

        return ""

    def _extract_company(self, soup: BeautifulSoup, url: str) -> str:
        """Extract company name from LinkedIn page."""
        # Try to find company name
        company_selectors = [
            ("a", {"class": lambda x: x and "company" in str(x).lower()}),
            ("span", {"class": lambda x: x and "company" in str(x).lower()}),
        ]

        for tag, attrs in company_selectors:
            element = soup.find(tag, attrs)
            if element:
                return self._clean_text(element.get_text())

        # Fallback: extract from URL
        if "linkedin.com/jobs/view" in url:
            parts = url.split("-")
            if len(parts) > 2:
                # Try to get company from URL pattern
                return "Company"

        return ""

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location from LinkedIn page."""
        location_selectors = [
            ("span", {"class": lambda x: x and "location" in str(x).lower()}),
            ("span", {"class": "top-card__location"}),
        ]

        for tag, attrs in location_selectors:
            element = soup.find(tag, attrs)
            if element:
                return self._clean_text(element.get_text())

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        return " ".join(text.split())


class IndeedScraper(JobDescriptionScraper):
    """Scraper for Indeed job postings."""

    async def fetch(self, url: str) -> Dict[str, str]:
        """Fetch job description from Indeed.

        Args:
            url: Indeed job posting URL

        Returns:
            Dict containing job details
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract job details
            title = self._extract_title(soup)
            company = self._extract_company(soup)
            location = self._extract_location(soup)
            description = self._extract_description(soup)

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "source": "indeed",
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to scrape Indeed job: {str(e)}")
            return {
                "title": "",
                "company": "",
                "location": "",
                "description": "",
                "source": "indeed",
                "url": url,
                "error": str(e),
            }

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from Indeed."""
        desc_container = soup.find("div", {"id": "jobDescriptionText"})
        if desc_container:
            return self._clean_text(desc_container.get_text())

        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            return self._clean_text(meta_desc.get("content", ""))

        return ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from Indeed."""
        title_elem = soup.find("h1", {"class": "jobsearch-JobInfoHeader-title"})
        if title_elem:
            return self._clean_text(title_elem.get_text())

        og_title = soup.find("meta", {"property": "og:title"})
        if og_title:
            return self._clean_text(og_title.get("content", ""))

        return ""

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name from Indeed."""
        company_elem = soup.find("div", {"class": "jobsearch-CompanyRating-withReviewIcon"})
        if company_elem:
            return self._clean_text(company_elem.get_text())

        company_link = soup.find("a", {"class": "jobsearch-CompanyInfo_without-link"})
        if company_link:
            return self._clean_text(company_link.get_text())

        return ""

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location from Indeed."""
        location_elem = soup.find("div", {"class": "jobsearch-JobInfoHeader-subtitle"})
        if location_elem:
            text = location_elem.get_text()
            # Location is usually after company name
            parts = text.split(" - ")
            if len(parts) > 1:
                return self._clean_text(parts[-1])

        meta_loc = soup.find("meta", {"name": "description"})
        if meta_loc:
            content = meta_loc.get("content", "")
            # Try to extract location from meta description
            return content

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        return " ".join(text.split())


class GenericScraper(JobDescriptionScraper):
    """Generic scraper for unknown job boards."""

    async def fetch(self, url: str) -> Dict[str, str]:
        """Fetch job description from generic URL.

        Args:
            url: Job posting URL

        Returns:
            Dict containing job details
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title = (
                soup.find("title")
                or soup.find("h1")
                or soup.find("meta", {"property": "og:title"})
            )
            title_text = ""
            if title:
                if hasattr(title, "get"):
                    title_text = title.get("content", "") or title.get_text()
                else:
                    title_text = str(title)

            # Extract description
            desc_elem = soup.find("meta", {"name": "description"}) or soup.find(
                "meta", {"property": "og:description"}
            )
            description = ""
            if desc_elem:
                description = desc_elem.get("content", "")

            # If no meta description, try to find main content
            if not description:
                main_content = soup.find("main") or soup.find("article") or soup.find(
                    "div", {"class": lambda x: x and "content" in str(x).lower()}
                )
                if main_content:
                    description = main_content.get_text()[:3000]  # Limit length

            return {
                "title": self._clean_text(title_text),
                "company": "",  # Hard to extract generically
                "location": "",  # Hard to extract generically
                "description": self._clean_text(description),
                "source": "generic",
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to scrape generic job URL: {str(e)}")
            return {
                "title": "",
                "company": "",
                "location": "",
                "description": "",
                "source": "generic",
                "url": url,
                "error": str(e),
            }

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        return " ".join(text.split())


class JobDescriptionScraperFactory:
    """Factory for creating appropriate job scraper instances."""

    _scrapers = {
        "linkedin.com": LinkedInScraper,
        "indeed.com": IndeedScraper,
    }

    @classmethod
    def get_scraper(cls, url: str) -> JobDescriptionScraper:
        """Get appropriate scraper for URL.

        Args:
            url: Job posting URL

        Returns:
            JobDescriptionScraper instance
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Remove www. prefix for matching
        domain = domain.replace("www.", "")

        # Find matching scraper
        for key, scraper_class in cls._scrapers.items():
            if key in domain:
                return scraper_class()

        # Use generic scraper for unknown domains
        return GenericScraper()


async def fetch_job_description(url: str) -> Dict[str, str]:
    """Fetch job description from URL using appropriate scraper.

    Args:
        url: Job posting URL

    Returns:
        Dict containing job title, company, location, and description
    """
    scraper = JobDescriptionScraperFactory.get_scraper(url)
    return await scraper.fetch(url)


async def extract_keywords_from_jd(jd_text: str) -> Dict[str, List[str]]:
    """Extract key information from job description.

    Args:
        jd_text: Job description text

    Returns:
        Dict containing skills, requirements, and responsibilities
    """
    # Common technical skills to look for
    tech_patterns = [
        r"\b(Python|JavaScript|Java|C\+\+|C#|Ruby|Go|Rust|Scala|Kotlin|Swift)\b",
        r"\b(React|Angular|Vue|Node\.js|Django|Flask|Spring|Rails|Laravel)\b",
        r"\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|CI/CD|Git)\b",
        r"\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b",
        r"\b(REST|GraphQL|gRPC|WebSocket)\b",
        r"\b(Machine Learning|AI|Deep Learning|TensorFlow|PyTorch)\b",
    ]

    skills = []
    for pattern in tech_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        skills.extend([m.title() if m.isupper() else m for m in matches])

    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            seen.add(skill_lower)
            unique_skills.append(skill)

    return {
        "skills": unique_skills,
        "experience_patterns": [],
        "requirements": [],
    }
