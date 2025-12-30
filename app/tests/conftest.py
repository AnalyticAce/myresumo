"""Pytest configuration and shared fixtures for PowerCV tests.

This module provides centralized fixtures for testing, reducing boilerplate
and ensuring consistent test setup across all test modules.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Generator, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (default)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers and ordering."""
    # Add 'unit' marker to tests that don't have any marker
    for item in items:
        if not item.get_closest_marker('integration') and not item.get_closest_marker('slow'):
            if 'test_api' in str(item.fspath) or 'test_integration' in str(item.fspath):
                pass  # These will be marked differently
            else:
                # Default to unit marker
                marker = item.get_closest_marker('unit')
                if marker is None:
                    item.add_marker(pytest.mark.unit)


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Automatically mock environment variables for all tests.

    This prevents accidental API calls to real services.
    """
    env_vars = {
        'API_KEY': 'sk-test-mock-key-for-testing',
        'API_BASE': 'https://api.deepseek.com/v1',
        'MODEL_NAME': 'deepseek-chat',
        'CEREBRAS_API_KEY': '',
        'CEREBRAS_API_BASE': 'https://api.cerebras.ai/v1',
        'CEREBRAS_MODEL': 'gpt-oss-120b',
        'OPENAI_API_KEY': '',
        'OPENAI_API_BASE': 'https://api.openai.com/v1',
        'MONGODB_URI': 'mongodb://localhost:27017/powercv-test',
        'REDIS_URL': 'redis://localhost:6379',
        'DEBUG': 'false',
        'LOG_LEVEL': 'warning',
    }

    with patch.dict('os.environ', env_vars, clear=False):
        yield env_vars


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_cv_text() -> str:
    """Sample CV text for testing."""
    return """
John Doe
john.doe@example.com | +31 6 12345678 | Amsterdam, Netherlands
linkedin.com/in/johndoe | github.com/johndoe

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience in full-stack development,
specializing in Python, JavaScript, and cloud technologies.

WORK EXPERIENCE

Senior Software Engineer - TechCorp BV, Amsterdam
2022 - Present
- Led development of microservices architecture using Python and Docker
- Improved system performance by 40% through optimization of database queries
- Mentored 5 junior developers and established code review practices

Software Engineer - StartupXYZ, Rotterdam
2020 - 2022
- Developed full-stack web applications using React and Node.js
- Built RESTful APIs serving 100k+ daily requests

EDUCATION
Bachelor of Computer Science - University of Amsterdam, 2014-2018

SKILLS
- Languages: Python, JavaScript, TypeScript, SQL
- Frameworks: React, Django, FastAPI
- Databases: PostgreSQL, MongoDB, Redis
- DevOps: Docker, Kubernetes, AWS, CI/CD
"""


@pytest.fixture
def sample_jd_text() -> str:
    """Sample job description for testing."""
    return """
Senior Python Developer - TechCorp International

We are looking for a Senior Python Developer to join our team in Amsterdam.

Requirements:
- 5+ years of experience with Python
- Experience with Django or FastAPI frameworks
- Knowledge of PostgreSQL and Redis
- Experience with Docker and AWS
- Bachelor's degree in Computer Science

Nice to have:
- Kubernetes experience
- Machine learning knowledge
- Team leadership experience
"""


@pytest.fixture
def sample_resume_data() -> Dict[str, Any]:
    """Sample structured resume data for testing."""
    return {
        'profile': {
            'name': 'John Doe',
            'title': 'Senior Software Engineer',
            'email': 'john.doe@example.com',
            'phone': '+31 6 12345678',
            'location': 'Amsterdam, Netherlands',
            'linkedin': 'linkedin.com/in/johndoe',
            'github': 'github.com/johndoe'
        },
        'experience': [
            {
                'company': 'TechCorp BV',
                'role': 'Senior Software Engineer',
                'period': '2022 - Present',
                'achievements': [
                    'Led development of microservices architecture using Python and Docker',
                    'Improved system performance by 40% through optimization',
                    'Mentored 5 junior developers'
                ]
            },
            {
                'company': 'StartupXYZ',
                'role': 'Software Engineer',
                'period': '2020 - 2022',
                'achievements': [
                    'Developed full-stack web applications using React and Node.js',
                    'Built RESTful APIs serving 100k+ daily requests'
                ]
            }
        ],
        'skills': {
            'programming': ['Python', 'JavaScript', 'TypeScript', 'SQL'],
            'frameworks': ['React', 'Django', 'FastAPI'],
            'databases': ['PostgreSQL', 'MongoDB', 'Redis'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'CI/CD']
        },
        'education': [
            {
                'institution': 'University of Amsterdam',
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'period': '2014 - 2018'
            }
        ]
    }


@pytest.fixture
def mock_ai_response() -> Dict[str, Any]:
    """Mock AI API response for testing."""
    return {
        'ats_score': 85,
        'summary': 'Strong candidate with relevant Python and cloud experience',
        'keyword_analysis': {
            'matched_keywords': [
                {'keyword': 'Python', 'jd_mentions': 3, 'cv_mentions': 2},
                {'keyword': 'Docker', 'jd_mentions': 2, 'cv_mentions': 2},
                {'keyword': 'AWS', 'jd_mentions': 2, 'cv_mentions': 1}
            ],
            'missing_critical': [
                {'keyword': 'Django', 'importance': 'high'},
                {'keyword': 'PostgreSQL', 'importance': 'high'}
            ],
            'missing_nice_to_have': [
                {'keyword': 'Kubernetes', 'importance': 'medium'}
            ]
        },
        'experience_analysis': {
            'relevant_roles': [
                {
                    'title': 'Senior Software Engineer - TechCorp BV',
                    'match_score': 9,
                    'key_achievements': ['Led development of microservices architecture']
                }
            ],
            'transferable_roles': []
        },
        'skill_gaps': {
            'critical': ['Django', 'PostgreSQL'],
            'important': ['Kubernetes'],
            'nice_to_have': ['Machine Learning']
        },
        'strengths': [
            'Strong Python experience',
            'Cloud infrastructure knowledge',
            'Team leadership'
        ],
        'recommendations': [
            'Add PostgreSQL experience to skills section',
            'Highlight Django projects if available'
        ]
    }


@pytest.fixture
def mock_scraper_response() -> Dict[str, Any]:
    """Mock job scraper response for testing."""
    return {
        'title': 'Senior Python Developer',
        'company': 'TechCorp International',
        'location': 'Amsterdam, Netherlands',
        'description': 'We are looking for a Senior Python Developer...',
        'source': 'linkedin',
        'url': 'https://www.linkedin.com/jobs/view/senior-python-developer-at-techcorp-123456'
    }


# =============================================================================
# Mock Client Fixtures
# =============================================================================

@pytest.fixture
def mock_ai_client(mock_ai_response):
    """Create a mock AI client for testing."""
    mock_client = Mock()
    mock_client.chat_completion = Mock(return_value=json.dumps(mock_ai_response))
    return mock_client


@pytest.fixture
def mock_ai_client_async(mock_ai_response):
    """Create a mock async AI client for testing."""
    mock_client = AsyncMock()
    mock_client.chat_completion = AsyncMock(return_value=json.dumps(mock_ai_response))
    return mock_client


@pytest.fixture
def mock_cover_letter_response():
    """Mock cover letter generation response."""
    return {
        'cover_letter': '''Dear Hiring Manager,

I am writing to express my strong interest in the Senior Python Developer position at TechCorp International. With over 5 years of experience in Python development and a proven track record of building scalable microservices architectures, I am confident in my ability to contribute meaningfully to your team.

My experience includes leading the development of high-performance systems using Python and Docker, achieving a 40% improvement in system performance through strategic optimization. I have extensive experience with cloud technologies and modern development practices that align well with your requirements.

I am excited about the opportunity to bring my technical expertise and leadership skills to TechCorp and contribute to your continued success.

Sincerely,
John Doe''',
        'word_count': 120,
        'tone': 'Professional'
    }


def create_mock_ai_client(response: Dict[str, Any]) -> Mock:
    """Helper function to create a mock AI client."""
    mock_client = Mock()
    mock_client.chat_completion = Mock(return_value=json.dumps(response))
    return mock_client


# ==============================================================================
# API Client Fixtures
# ==============================================================================

@pytest.fixture
def test_client():
    """Create a FastAPI test client."""
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=False)


# ==============================================================================
# File System Fixtures
# ==============================================================================

@pytest.fixture
def temp_cv_file(tmp_path, sample_cv_text) -> Path:
    """Create a temporary CV file for testing."""
    file_path = tmp_path / "test_cv.txt"
    file_path.write_text(sample_cv_text)
    return file_path


@pytest.fixture
def temp_jd_file(tmp_path, sample_jd_text) -> Path:
    """Create a temporary job description file for testing."""
    file_path = tmp_path / "test_jd.txt"
    file_path.write_text(sample_jd_text)
    return file_path


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Create a temporary output directory for testing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


# ==============================================================================
# Database Fixtures (Optional - for future implementation)
# ==============================================================================

@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing.

    This is a placeholder for when database integration is added.
    Currently returns a mock object.
    """
    mock_session = Mock()
    mock_session.query = Mock()
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.rollback = Mock()
    mock_session.close = Mock()
    return mock_session


# ==============================================================================
# Helper Functions
# ==============================================================================

def load_json_fixture(fixture_name: str) -> Dict[str, Any]:
    """Load a JSON fixture from the test_data directory."""
    fixture_path = Path(__file__).parent / "test_data" / f"{fixture_name}.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


# ==============================================================================
# Custom Assertions
# ==============================================================================

def assert_ats_score_in_range(score, min_score=0, max_score=100):
    """Assert that ATS score is within valid range."""
    assert isinstance(score, (int, float)), f"ATS score must be numeric, got {type(score)}"
    assert min_score <= score <= max_score, f"ATS score {score} outside range [{min_score}, {max_score}]"


def assert_response_structure(response_data, required_fields: list):
    """Assert that response contains all required fields."""
    for field in required_fields:
        assert field in response_data, f"Response missing required field: {field}"
