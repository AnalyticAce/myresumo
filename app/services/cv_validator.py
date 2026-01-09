"""Validate optimized CV against original to prevent data loss and hallucinations."""
import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)


class CVValidator:
    """Validate that optimization preserved critical information."""

    @staticmethod
    def extract_contact_info(cv_text: str) -> Dict:
        """Extract contact information from CV.

        Args:
            cv_text: CV text to extract contact info from

        Returns:
            dict: Extracted contact information
        """
        info = {}

        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        if email_match:
            info['email'] = email_match.group()

        # Phone (international format)
        phone_match = re.search(r'\+\d{1,3}\s?\d{1,4}?\s?\d{4,}', cv_text)
        if phone_match:
            info['phone'] = phone_match.group()

        # LinkedIn
        linkedin_match = re.search(
            r'linkedin\.com/in/[\w-]+', cv_text, re.IGNORECASE)
        if linkedin_match:
            info['linkedin'] = linkedin_match.group()

        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', cv_text, re.IGNORECASE)
        if github_match:
            info['github'] = github_match.group()

        # Birthdate
        birthdate_match = re.search(r'\d{2}\.\d{2}\.\d{4}', cv_text)
        if birthdate_match:
            info['birthdate'] = birthdate_match.group()

        return info

    @staticmethod
    def validate_optimization(original: str, optimized: str) -> Dict:
        """Validate that critical information is preserved.

        Args:
            original: Original CV text
            optimized: Optimized CV text or JSON

        Returns:
            dict: Validation results with errors and warnings
        """
        errors = []
        warnings = []

        # Convert optimized to string if it's a dict/JSON
        if isinstance(optimized, dict):
            import json
            optimized = json.dumps(optimized)

        # Extract contact info from both
        orig_contact = CVValidator.extract_contact_info(original)
        opt_contact = CVValidator.extract_contact_info(optimized)

        # Check email
        if orig_contact.get('email') and orig_contact['email'] not in optimized:
            errors.append(f"Missing email: {orig_contact['email']}")

        # Check phone
        if orig_contact.get('phone'):
            # Normalize phone for comparison
            phone_normalized = orig_contact['phone'].replace(
                ' ', '').replace('-', '')
            optimized_normalized = optimized.replace(' ', '').replace('-', '')
            if phone_normalized not in optimized_normalized:
                errors.append(f"Missing phone: {orig_contact['phone']}")

        # Check LinkedIn
        if orig_contact.get('linkedin') and orig_contact['linkedin'].lower() not in optimized.lower():
            errors.append(f"Missing LinkedIn: {orig_contact['linkedin']}")

        # Check GitHub
        if orig_contact.get('github') and orig_contact['github'].lower() not in optimized.lower():
            errors.append(f"Missing GitHub: {orig_contact['github']}")

        # Check birthdate
        if orig_contact.get('birthdate') and orig_contact['birthdate'] not in optimized:
            warnings.append(f"Missing birthdate: {orig_contact['birthdate']}")

        # Check for common hallucinations (languages)
        hallucination_languages = [
            'french', 'german', 'spanish', 'italian', 'portuguese',
            'chinese', 'japanese', 'korean', 'arabic'
        ]

        for lang in hallucination_languages:
            if lang in optimized.lower() and lang not in original.lower():
                warnings.append(
                    f"Possible hallucination: '{lang}' language not in original")

        # Check for hallucinated skills
        hallucination_skills = [
            'forklift certified', 'forklift', 'cdl license', 'crane operator'
        ]

        for skill in hallucination_skills:
            if skill in optimized.lower() and skill not in original.lower():
                warnings.append(
                    f"Possible hallucination: '{skill}' not in original")

        # Check education section
        if 'Master' in original and 'Master' not in optimized:
            errors.append("Missing Master's degree")

        if 'Bachelor' in original and 'Bachelor' not in optimized:
            errors.append("Missing Bachelor's degree")

        # Check certifications
        cert_keywords = ['certification', 'certified', 'certificate']
        orig_has_certs = any(keyword in original.lower()
                             for keyword in cert_keywords)
        opt_has_certs = any(keyword in optimized.lower()
                            for keyword in cert_keywords)

        if orig_has_certs and not opt_has_certs:
            warnings.append("Certifications section may be missing")

        # Check for address
        if 'address' in original.lower() or 'netherlands' in original.lower():
            if 'netherlands' in original.lower() and 'netherlands' not in optimized.lower():
                warnings.append("Address/location may be missing")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'original_contact': orig_contact,
            'optimized_contact': opt_contact
        }

    @staticmethod
    def validate_required_fields(cv_text: str) -> Dict:
        """Check that all required fields are present.

        Args:
            cv_text: CV text to validate

        Returns:
            dict: Validation results
        """
        required_fields = {
            'name': False,
            'email': False,
            'phone': False,
            'education': False,
            'experience': False
        }

        cv_lower = cv_text.lower()

        # Check for email
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text):
            required_fields['email'] = True

        # Check for phone
        if re.search(r'\+\d{1,3}', cv_text):
            required_fields['phone'] = True

        # Check for education
        if 'education' in cv_lower or 'degree' in cv_lower or 'university' in cv_lower:
            required_fields['education'] = True

        # Check for experience
        if 'experience' in cv_lower or 'employment' in cv_lower or 'work' in cv_lower:
            required_fields['experience'] = True

        # Name is harder to detect automatically
        if len(cv_text.split('\n')[0]) < 50:  # First line is likely name
            required_fields['name'] = True

        missing_fields = [field for field,
                          present in required_fields.items() if not present]

        return {
            'valid': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'present_fields': [field for field, present in required_fields.items() if present]
        }
