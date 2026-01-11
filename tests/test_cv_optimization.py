"""Test CV optimization quality and data preservation."""
import pytest
from app.services.cv_validator import CVValidator


def test_preserve_contact_info():
    """Test that contact information is preserved."""
    original = """
    Name: Ilnar Nizametdinov
    Email: nizametdinov@gmail.com
    Phone: +31 6 53230968
    Address: 1441 DR Purmerend, The Netherlands
    """

    optimized = """
    Ilnar Nizametdinov
    Email: different@email.com
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert not validation['valid']
    assert any('phone' in err.lower() for err in validation['errors'])
    assert any('nizametdinov@gmail.com' in err for err in validation['errors'])


def test_no_language_hallucinations():
    """Test that no languages are invented."""
    original = """
    Languages: English (Proficient), Russian (Native), Tatar (Native)
    """

    optimized = """
    Languages: English (Proficient), Russian (Native), French (Fluent)
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert any('french' in warn.lower() for warn in validation['warnings'])


def test_preserve_education():
    """Test education section is preserved."""
    original = """
    EDUCATION
    Master's Degree, Mechanical Engineering - 2005-2010
    Moscow Politechnic University
    
    Bachelor's Degree, Economics - 2010-2013
    NIMB University
    """

    optimized = """
    EDUCATION
    Bachelor's Degree, Computer Science
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert any('master' in err.lower() for err in validation['errors'])


def test_preserve_github_linkedin():
    """Test that GitHub and LinkedIn URLs are preserved."""
    original = """
    Name: Ilnar Nizametdinov
    LinkedIn: https://linkedin.com/in/illnar
    GitHub: https://github.com/ILLnar-Nizami
    """

    optimized = """
    Ilnar Nizametdinov
    LinkedIn: https://linkedin.com/in/illnar
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert any('github' in err.lower() for err in validation['errors'])


def test_no_skill_hallucinations():
    """Test that skills are not invented."""
    original = """
    Skills:
    - Python, Go, TypeScript
    - Flask, FastAPI
    - Docker, Kubernetes
    """

    optimized = """
    Skills:
    - Python, Go, TypeScript
    - Flask, FastAPI
    - Docker, Kubernetes, Forklift Certified
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert any('forklift' in warn.lower() for warn in validation['warnings'])


def test_certifications_preserved():
    """Test that certifications section is not removed."""
    original = """
    CERTIFICATIONS
    - Python Programming
    - Go Development
    - DevOps Tools
    - Data Science & ML
    """

    optimized = """
    SKILLS
    Python, Go, Docker
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert any('certification' in warn.lower()
               for warn in validation['warnings'])


def test_valid_optimization_passes():
    """Test that a properly optimized CV passes validation."""
    original = """
    Name: Ilnar Nizametdinov
    Email: nizametdinov@gmail.com
    Phone: +31 6 53230968
    LinkedIn: https://linkedin.com/in/illnar
    GitHub: https://github.com/ILLnar-Nizami
    
    EDUCATION
    Master's Degree, Mechanical Engineering
    """

    optimized = """
    Ilnar Nizametdinov
    nizametdinov@gmail.com | +31 6 53230968
    LinkedIn: linkedin.com/in/illnar | GitHub: github.com/ILLnar-Nizami
    
    PROFILE
    Tech professional with expertise in backend development...
    
    EDUCATION
    Master's Degree, Mechanical Engineering
    """

    validation = CVValidator.validate_optimization(original, optimized)

    assert validation['valid']
    assert len(validation['errors']) == 0
