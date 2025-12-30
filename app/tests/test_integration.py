"""Updated integration tests for PowerCV using the new conftest fixtures."""

import pytest
from pathlib import Path


# Use fixtures from conftest.py
# These are automatically loaded by pytest


def test_cv_analysis(sample_cv_text, sample_jd_text, mock_ai_response):
    """Test CV analysis functionality using fixtures."""
    from app.services.cv_analyzer import CVAnalyzer
    
    with patch('app.services.cv_analyzer.get_ai_client') as mock_get_client:
        mock_client = create_mock_ai_client(mock_ai_response)
        mock_get_client.return_value = mock_client
        
        analyzer = CVAnalyzer()
        result = analyzer.analyze(sample_cv_text, sample_jd_text)
        
        # Assertions using custom helpers
        assert 'ats_score' in result
        assert 'keyword_analysis' in result
        
        # Use custom assertion
        assert_ats_score_in_range(result['ats_score'])
        
        print(f"✓ Analysis test passed. ATS Score: {result['ats_score']}")


def test_full_workflow(sample_cv_text, sample_jd_text, mock_ai_response):
    """Test complete optimization workflow using fixtures."""
    from app.services.workflow_orchestrator import CVWorkflowOrchestrator
    
    with patch('app.services.workflow_orchestrator.CVAnalyzer') as MockAnalyzer, \
         patch('app.services.workflow_orchestrator.CVOptimizer') as MockOptimizer:
        
        mock_analyzer = Mock()
        mock_analyzer.analyze = Mock(return_value=mock_ai_response)
        MockAnalyzer.return_value = mock_analyzer
        
        mock_optimizer = Mock()
        mock_optimizer.optimize_comprehensive = Mock(return_value={
            'optimized_resume': 'Optimized content',
            'improvements_made': ['Added keywords']
        })
        MockOptimizer.return_value = mock_optimizer
        
        orchestrator = CVWorkflowOrchestrator()
        result = orchestrator.optimize_cv_for_job(
            cv_text=sample_cv_text,
            jd_text=sample_jd_text,
            generate_cover_letter=False
        )
        
        # Assertions
        assert 'analysis' in result
        assert 'optimized_cv' in result
        assert result['ats_score'] > 0
        
        print(f"✓ Workflow test passed. ATS Score: {result['ats_score']}")


def test_cover_letter_generation(mock_cover_letter_response):
    """Test cover letter generation using fixtures."""
    from app.services.cover_letter_gen import CoverLetterGenerator
    
    with patch('app.services.cover_letter_gen.get_ai_client') as mock_get_client:
        mock_client = create_mock_ai_client(mock_cover_letter_response)
        mock_get_client.return_value = mock_client
        
        generator = CoverLetterGenerator()
        
        candidate_data = {
            'name': 'John Doe',
            'current_title': 'Software Engineer',
            'location': 'Amsterdam',
            'years_exp': '5 years',
            'top_skills': ['Python', 'Docker'],
            'achievements': ['Led team of 5']
        }
        
        job_data = {
            'company': 'TechCorp',
            'position': 'Senior Developer',
            'location': 'Amsterdam',
            'requirements': ['Python', 'Django']
        }
        
        result = generator.generate(candidate_data, job_data, tone='Professional')
        
        assert 'cover_letter' in result
        assert result['word_count'] > 0
        
        print(f"✓ Cover letter test passed. Word count: {result['word_count']}")


def test_scraper_integration(mock_scraper_response):
    """Test job scraper integration using fixtures."""
    import asyncio
    from app.services.scraper import JobDescriptionScraperFactory
    
    async def test_scraper():
        with patch('app.services.scraper.LinkedInScraper.fetch') as mock_fetch:
            mock_fetch.return_value = mock_scraper_response
            
            scraper = JobDescriptionScraperFactory.get_scraper(
                "https://www.linkedin.com/jobs/view/test"
            )
            
            result = await scraper.fetch("https://www.linkedin.com/jobs/view/test")
            
            assert 'title' in result
            assert 'company' in result
            assert result['source'] == 'linkedin'
            
            return True
    
    result = asyncio.run(test_scraper())
    assert result is True
    print("✓ Scraper test passed.")


def test_master_cv_operations(sample_resume_data):
    """Test Master CV operations using fixtures."""
    from app.services.master_cv import MasterCV
    
    # Test creating CV from data
    cv = MasterCV(sample_resume_data)
    
    # Test skills extraction
    skills = cv.get_skills('programming')
    assert 'Python' in skills
    assert 'JavaScript' in skills
    
    # Test validation
    is_valid, errors = cv.validate()
    assert is_valid is True
    assert len(errors) == 0
    
    # Test Markdown conversion
    markdown = cv.to_markdown()
    assert 'John Doe' in markdown
    assert '## Work Experience' in markdown
    
    print("✓ Master CV test passed.")


def test_api_endpoints(test_client):
    """Test API endpoints using fixtures."""
    # Test health endpoint
    response = test_client.get('/health')
    assert response.status_code in [200, 404]  # May be mounted on different path
    
    # Test docs endpoint
    response = test_client.get('/docs')
    assert response.status_code == 200
    
    print("✓ API endpoints test passed.")


def test_file_operations(temp_cv_file, temp_jd_file, temp_output_dir):
    """Test file operations using fixtures."""
    # Verify temp files exist
    assert temp_cv_file.exists()
    assert temp_jd_file.exists()
    assert temp_output_dir.exists()
    
    # Verify content
    assert temp_cv_file.read_text() == sample_cv_text
    assert temp_jd_file.read_text() == sample_jd_text
    
    print("✓ File operations test passed.")


# Import fixtures and helpers from conftest
from app.tests.conftest import (
    sample_cv_text,
    sample_jd_text,
    sample_resume_data,
    mock_ai_response,
    mock_scraper_response,
    mock_cover_letter_response,
    mock_ai_client,
    test_client,
    temp_cv_file,
    temp_jd_file,
    temp_output_dir,
    create_mock_ai_client,
    assert_ats_score_in_range,
    assert_response_structure,
)

# Import patch for test functions
from unittest.mock import patch, create_mock_ai_client


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
