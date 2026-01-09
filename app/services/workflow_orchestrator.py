"""Orchestrate complete CV optimization workflow."""
import logging
import re
from typing import Dict, List, Optional

from ..utils.shared_utils import TextProcessor
from .cover_letter_gen import CoverLetterGenerator
from .cv_analyzer import CVAnalyzer
from .cv_optimizer import CVOptimizer

logger = logging.getLogger(__name__)


class CVWorkflowOrchestrator:
    """Orchestrate the complete CV optimization workflow."""

    def __init__(self):
        """Initialize all services."""
        self.analyzer = CVAnalyzer()
        self.optimizer = CVOptimizer()
        self.cover_letter_gen = CoverLetterGenerator()
        logger.info("WorkflowOrchestrator initialized")

    def optimize_cv_for_job(
        self,
        cv_text: str,
        jd_text: str,
        generate_cover_letter: bool = True,
        email: Optional[str] = None
    ) -> Dict:
        """Complete workflow: analyze → optimize → generate cover letter.

        Args:
            cv_text: Full CV text
            jd_text: Job description text
            generate_cover_letter: Whether to generate cover letter

        Returns:
            dict: Complete results including analysis, optimized CV, cover letter
        """
        logger.info("Starting complete optimization workflow")

        # Step 1: Analyze
        logger.info("Step 1/3: Analyzing CV against job description...")
        analysis = self.analyzer.analyze(cv_text, jd_text)

        # Step 2: Comprehensive Optimization (One-shot)
        logger.info("Step 2/3: Performing comprehensive optimization...")
        optimized_data = self.optimizer.optimize_comprehensive(
            cv_text, jd_text, analysis, email
        )

        # Step 3: Cover letter (optional)
        cover_letter = None
        if generate_cover_letter:
            logger.info("Step 3/3: Generating cover letter...")
            cover_letter = self._generate_cover_letter(analysis, jd_text)

        # Extract skills for the dashboard/API
        matching_skills = analysis.get('keyword_analysis', {}).get(
            'matched_keywords', [])
        missing_skills = analysis.get('keyword_analysis', {}).get(
            'missing_critical', [])

        result = {
            'analysis': analysis,
            'optimized_cv': optimized_data,  # Now returns the full dict structure
            'cover_letter': cover_letter,
            'ats_score': analysis.get('ats_score', 0),
            'matching_skills': [k.get('keyword') for k in matching_skills if k.get('keyword')],
            'missing_skills': [k.get('keyword') for k in missing_skills if k.get('keyword')],
            'recommendation': analysis.get('summary', '')
        }

        logger.info(f"Workflow completed. ATS Score: {result['ats_score']}")
        return result

    def _optimize_cv_sections(
        self,
        cv_text: str,
        jd_text: str,
        analysis: Dict
    ) -> Dict:
        """Optimize individual CV sections based on analysis.

        Args:
            cv_text: Original CV text
            jd_text: Job description
            analysis: Analysis results from analyzer

        Returns:
            dict: Optimized CV sections
        """
        # Extract keywords from analysis
        keywords = []
        if 'keyword_analysis' in analysis:
            matched = analysis['keyword_analysis'].get('matched_keywords', [])
            missing = analysis['keyword_analysis'].get('missing_critical', [])

            # Get top keywords for optimization
            keywords = [k['keyword'] for k in matched[:10]]
            if missing:
                keywords += [k['keyword'] for k in missing[:5]]

        # Parse CV into sections and optimize each
        optimized_sections = {}

        # Extract and optimize professional summary first
        summary_section = TextProcessor.extract_section(
            cv_text, ['PROFESSIONAL SUMMARY', 'SUMMARY', 'PROFILE'])
        if summary_section:
            optimized_summary = self.optimizer.optimize_professional_summary(
                summary_section, jd_text, keywords
            )
            optimized_sections['summary'] = optimized_summary.get(
                'optimized_content', summary_section)

        # Extract and optimize experience section
        experience_section = TextProcessor.extract_section(
            cv_text, ['EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE'])
        if experience_section:
            optimized_experience = self.optimizer.optimize_section(
                experience_section, jd_text, keywords, "experience"
            )
            optimized_sections['experience'] = optimized_experience.get(
                'optimized_content', experience_section)

        # Extract and optimize skills section
        skills_section = TextProcessor.extract_section(
            cv_text, ['SKILLS', 'TECHNICAL SKILLS', 'SKILLS & EXPERTISE'])
        if skills_section:
            optimized_skills = self.optimizer.optimize_section(
                skills_section, jd_text, keywords, "skills"
            )
            optimized_sections['skills'] = optimized_skills.get(
                'optimized_content', skills_section)

        # Extract education section (preserve as-is, no optimization)
        education_section = TextProcessor.extract_section(
            cv_text, ['EDUCATION', 'ACADEMIC', 'EDUCATION & CERTIFICATIONS'])
        if education_section:
            optimized_sections['education'] = education_section

        # Preserve contact info (extract and keep as-is)
        contact_info = TextProcessor.extract_contact_info(cv_text)
        if contact_info:
            optimized_sections['contact'] = contact_info

        # Preserve any other sections without optimization
        other_sections = self._extract_other_sections(cv_text, [
            'PROFESSIONAL SUMMARY', 'SUMMARY', 'PROFILE',
            'EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE',
            'SKILLS', 'TECHNICAL SKILLS', 'SKILLS & EXPERTISE',
            'EDUCATION', 'ACADEMIC', 'EDUCATION & CERTIFICATIONS'
        ])
        for section_name, section_content in other_sections.items():
            if section_content.strip():  # Only add non-empty sections
                optimized_sections[section_name.lower().replace(
                    ' ', '_')] = section_content

        logger.info(f"Optimized {len(optimized_sections)} CV sections")
        return optimized_sections

    def _generate_cover_letter(
        self,
        analysis: Dict,
        jd_text: str
    ) -> Optional[Dict]:
        """Generate cover letter based on analysis.

        Args:
            analysis: CV analysis results
            jd_text: Job description

        Returns:
            dict: Cover letter and metadata
        """
        # Extract candidate info from analysis
        candidate_data = {
            'name': self._extract_name_from_analysis(analysis),
            'current_title': self._extract_current_title_from_analysis(analysis),
            'location': self._extract_location_from_analysis(analysis),
            'years_exp': self._extract_experience_from_analysis(analysis),
            'top_skills': self._extract_skills_from_analysis(analysis),
            'achievements': self._extract_achievements_from_analysis(analysis)
        }

        # Extract job info from JD
        job_data = {
            'company': 'Target Company',  # This could be extracted from JD
            'position': self._extract_position_from_jd(jd_text),
            'location': self._extract_location_from_jd(jd_text),
            'requirements': self._extract_requirements_from_jd(jd_text)
        }

        return self.cover_letter_gen.generate(candidate_data, job_data)

    def _extract_other_sections(self, cv_text: str, exclude_headers: List[str]) -> Dict[str, str]:
        """Extract all CV sections except specified ones.

        Args:
            cv_text: Full CV text
            exclude_headers: Headers to exclude from extraction

        Returns:
            dict: Mapping of section names to content
        """
        sections = {}
        lines = cv_text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()

            # Check if this is a section header
            if line and len(line) < 50 and line.isupper() and not any(char.isdigit() for char in line):
                # This looks like a section header
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)

                # Check if this should be excluded
                should_exclude = any(header in line.upper()
                                     for header in exclude_headers)
                if not should_exclude:
                    current_section = line
                    current_content = []
                else:
                    current_section = None
                    current_content = []
            elif current_section:
                # Add content to current section
                current_content.append(line)

        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _extract_name_from_analysis(self, analysis: Dict) -> str:
        """Extract candidate name from analysis."""
        # Try to find name in experience analysis or other sections
        if 'experience_analysis' in analysis:
            relevant_roles = analysis['experience_analysis'].get(
                'relevant_roles', [])
            if relevant_roles:
                return relevant_roles[0].get('title', '').split(' - ')[0] or 'Candidate'
        return 'Candidate'

    def _extract_current_title_from_analysis(self, analysis: Dict) -> str:
        """Extract current job title from analysis."""
        if 'experience_analysis' in analysis:
            relevant_roles = analysis['experience_analysis'].get(
                'relevant_roles', [])
            if relevant_roles:
                return relevant_roles[0].get('title', 'Professional')
        return 'Professional'

    def _extract_location_from_analysis(self, analysis: Dict) -> str:
        """Extract location from analysis."""
        # Location might not be in analysis, return default
        return 'Netherlands'

    def _extract_experience_from_analysis(self, analysis: Dict) -> str:
        """Extract years of experience from analysis."""
        # This is a rough estimate based on roles
        if 'experience_analysis' in analysis:
            relevant_roles = analysis['experience_analysis'].get(
                'relevant_roles', [])
            if len(relevant_roles) >= 2:
                return '3+ years'
            elif len(relevant_roles) >= 1:
                return '2+ years'
        return 'Experienced'

    def _extract_skills_from_analysis(self, analysis: Dict) -> List[str]:
        """Extract top skills from analysis."""
        skills = []
        if 'keyword_analysis' in analysis:
            matched = analysis['keyword_analysis'].get('matched_keywords', [])
            skills = [k.get('keyword', '')
                      for k in matched[:8] if k.get('keyword')]
        return skills

    def _extract_achievements_from_analysis(self, analysis: Dict) -> List[str]:
        """Extract achievements from analysis."""
        achievements = []
        if 'experience_analysis' in analysis:
            relevant_roles = analysis['experience_analysis'].get(
                'relevant_roles', [])
            for role in relevant_roles:
                role_achievements = role.get('key_achievements', [])
                if isinstance(role_achievements, str):
                    role_achievements = [role_achievements]
                achievements.extend(role_achievements[:3])
        return achievements[:10]

    def _extract_position_from_jd(self, jd_text: str) -> str:
        """Extract position from job description with improved patterns."""
        lines = jd_text.split('\n')
        patterns = [
            r'(?:position|role|job title|title)\s*:\s*(.*)',
            r'^([^:\n]{5,50}(?:developer|engineer|manager|lead|specialist|architect)[^:\n]*)'
        ]

        for line in lines[:15]:
            line_stripped = line.strip()
            for pattern in patterns:
                match = re.search(pattern, line_stripped, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

        return 'Professional'

    def _extract_location_from_jd(self, jd_text: str) -> str:
        """Extract location from job description with improved detection."""
        # Check for specific Netherlands cities first
        cities = ['Amsterdam', 'Rotterdam', 'Utrecht',
                  'Eindhoven', 'Purmerend', 'The Hague', 'Den Haag']
        for city in cities:
            if re.search(rf'\b{city}\b', jd_text, re.IGNORECASE):
                return f"{city}, Netherlands"

        if 'netherlands' in jd_text.lower():
            return 'Netherlands'

        # Look for "Location: ..."
        match = re.search(r'location\s*:\s*(.*)', jd_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return 'Remote/Hybrid'

    def _extract_requirements_from_jd(self, jd_text: str) -> List[str]:
        """Extract key requirements from job description dynamically."""
        requirements = []
        # Common tech keywords
        tech_keywords = [
            'python', 'docker', 'kubernetes', 'flask', 'fastapi', 'postgresql', 'mongodb',
            'aws', 'gcp', 'azure', 'ci/cd', 'git', 'rest api', 'microservices', 'redis',
            'elasticsearch', 'kafka', 'terraform', 'ansible', 'jenkins', 'pytest'
        ]

        # Dynamic extraction of bullet points from a "Requirements" section
        req_match = re.search(
            r'(?:requirements|qualifications|what we are looking for)\s*:?\s*\n(.*?)(?:\n\n|\n[A-Z]|$)', jd_text, re.IGNORECASE | re.DOTALL)
        if req_match:
            req_text = req_match.group(1)
            bullets = re.findall(
                r'(?:^|\n)\s*[•\-\*]\s*(.*?)(?=\n|$)', req_text)
            if bullets:
                requirements.extend([b.strip() for b in bullets[:5]])

        # Fallback/Supplemental: Check for tech keywords
        found_tech = []
        for keyword in tech_keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', jd_text, re.IGNORECASE):
                found_tech.append(keyword.title() if len(
                    keyword) > 3 else keyword.upper())

        # Combine and deduplicate
        combined = list(dict.fromkeys(requirements + found_tech))
        return combined[:10]
