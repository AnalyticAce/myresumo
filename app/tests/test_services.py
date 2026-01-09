"""Comprehensive tests for PowerCV services."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
from datetime import datetime
import json

from app.services.cv_optimizer import CVOptimizer
from app.services.workflow_orchestrator import CVWorkflowOrchestrator
from app.services.cv_analyzer import CVAnalyzer
from app.utils.shared_utils import JSONParser, TextProcessor, MetricsHelper, UtilsErrorHandler


class TestJSONParser:
    """Test JSONParser utility class."""

    def test_clean_json_response_with_fences(self):
        """Test cleaning JSON response with markdown fences."""
        response = "```json\n{\"name\": \"test\"}\n```"
        result = JSONParser.clean_json_response(response)
        assert result == '{"name": "test"}'

    def test_clean_json_response_without_fences(self):
        """Test cleaning JSON response without markdown fences."""
        response = '{"name": "test"}'
        result = JSONParser.clean_json_response(response)
        assert result == '{"name": "test"}'

    def test_clean_json_response_with_array(self):
        """Test cleaning JSON response with array."""
        response = "```json\n[1, 2, 3]\n```"
        result = JSONParser.clean_json_response(response)
        assert result == '[1, 2, 3]'

    def test_safe_json_parse_success(self):
        """Test successful JSON parsing."""
        response = '{"name": "test"}'
        result = JSONParser.safe_json_parse(response, {"fallback": True})
        assert result == {"name": "test"}

    def test_safe_json_parse_with_fallback(self):
        """Test JSON parsing with fallback on error."""
        response = "invalid json"
        fallback = {"fallback": True}
        result = JSONParser.safe_json_parse(response, fallback)
        assert result == fallback

    def test_repair_json_truncated(self):
        """Test repairing truncated JSON."""
        json_str = '{"name": "test", "items": [1, 2'
        result = JSONParser.repair_json(json_str)
        assert result.endswith(']}')

    def test_repair_json_empty(self):
        """Test repairing empty JSON."""
        json_str = ""
        result = JSONParser.repair_json(json_str)
        assert result == ""


class TestTextProcessor:
    """Test TextProcessor utility class."""

    def test_clean_text(self):
        """Test text cleaning."""
        text = "hello    world"
        result = TextProcessor.clean_text(text)
        assert result == "hello world"

    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        text = ""
        result = TextProcessor.clean_text(text)
        assert result == ""

    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Python, Java, Python, JavaScript"
        patterns = [r'[A-Za-z]+']
        result = TextProcessor.extract_keywords(text, patterns)
        # Should have unique keywords
        assert len(result) <= 4

    def test_extract_section_found(self):
        """Test section extraction when found."""
        cv_text = "EXPERIENCE\nJob 1\nSKILLS\nPython"
        headers = ["EXPERIENCE", "SKILLS"]
        result = TextProcessor.extract_section(cv_text, headers)
        assert result is not None
        assert "Job 1" in result

    def test_extract_section_not_found(self):
        """Test section extraction when not found."""
        cv_text = "Some random text"
        headers = ["EXPERIENCE"]
        result = TextProcessor.extract_section(cv_text, headers)
        assert result is None

    def test_extract_contact_info(self):
        """Test contact info extraction."""
        cv_text = "Email: test@example.com\nPhone: 123-456-7890"
        result = TextProcessor.extract_contact_info(cv_text)
        assert result is not None
        assert "test@example.com" in result


class TestMetricsHelper:
    """Test MetricsHelper utility class."""

    def test_calculate_ats_score(self):
        """Test ATS score calculation."""
        matched = [{"keyword": "python"}, {"keyword": "java"}]
        total = ["python", "java", "javascript"]
        result = MetricsHelper.calculate_ats_score(matched, total)
        assert result == 66  # 2/3 * 100

    def test_calculate_ats_score_empty_total(self):
        """Test ATS score with empty total keywords."""
        matched = [{"keyword": "python"}]
        total = []
        result = MetricsHelper.calculate_ats_score(matched, total)
        assert result == 0

    def test_extract_ats_score_from_text(self):
        """Test extracting ATS score from text."""
        result = MetricsHelper.extract_ats_score_from_text("85/100")
        assert result == 85

    def test_extract_ats_score_from_percent(self):
        """Test extracting ATS score from percentage."""
        result = MetricsHelper.extract_ats_score_from_text("75%")
        assert result == 75

    def test_extract_ats_score_from_int(self):
        """Test extracting ATS score from integer."""
        result = MetricsHelper.extract_ats_score_from_text(90)
        assert result == 90

    def test_extract_ats_score_capped_at_100(self):
        """Test ATS score is capped at 100."""
        result = MetricsHelper.extract_ats_score_from_text("150")
        assert result == 100


class TestUtilsErrorHandler:
    """Test UtilsErrorHandler utility class."""

    def test_create_error_response(self):
        """Test creating standardized error response."""
        result = UtilsErrorHandler.create_error_response("Test error", "TEST_ERROR")
        assert result["error"] is True
        assert result["error_code"] == "TEST_ERROR"
        assert result["message"] == "Test error"
        assert "timestamp" in result


class TestCVOptimizer:
    """Test CVOptimizer service."""

    def test_init(self):
        """Test CVOptimizer initialization."""
        opt = CVOptimizer()
        assert opt is not None

    @patch('app.services.cv_optimizer.get_ai_client')
    def test_optimize_comprehensive(self, mock_client_factory):
        """Test comprehensive CV optimization."""
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client
        mock_client.chat_completion.return_value = '{"user_information": {"name": "Test"}}'

        opt = CVOptimizer()
        result = opt.optimize_comprehensive("CV", "JD")
        assert "user_information" in result

    @patch('app.services.cv_optimizer.get_ai_client')
    def test_optimize_section(self, mock_client_factory):
        """Test section optimization."""
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client
        mock_client.chat_completion.return_value = '{"optimized_content": "Improved"}'

        opt = CVOptimizer()
        result = opt.optimize_section(
            original_section="Original",
            jd_text="Job Description",
            keywords=["python"],
            optimization_focus="experience"
        )
        assert "optimized_content" in result


class TestCVAnalyzer:
    """Test CVAnalyzer service."""

    def test_init(self):
        """Test CVAnalyzer initialization."""
        analyzer = CVAnalyzer()
        assert analyzer is not None

    @patch('app.services.cv_analyzer.get_ai_client')
    def test_analyze(self, mock_client_factory):
        """Test CV analysis."""
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client
        mock_client.chat_completion.return_value = '{"ats_score": 85}'

        analyzer = CVAnalyzer()
        # Use at least 10 characters to pass validation
        result = analyzer.analyze("This is a test CV text for analysis", "This is a job description for testing")
        assert "ats_score" in result


class TestWorkflowOrchestrator:
    """Test CVWorkflowOrchestrator service."""

    def test_init(self):
        """Test orchestrator initialization."""
        orch = CVWorkflowOrchestrator()
        assert orch is not None

    @patch('app.services.workflow_orchestrator.CoverLetterGenerator')
    @patch('app.services.workflow_orchestrator.CVAnalyzer')
    @patch('app.services.workflow_orchestrator.CVOptimizer')
    def test_optimize_cv_for_job(self, mock_opt_cls, mock_analyzer_cls, mock_cl_cls):
        """Test CV optimization workflow."""
        mock_analyzer = MagicMock()
        mock_analyzer_cls.return_value = mock_analyzer
        mock_analyzer.analyze.return_value = {
            "ats_score": 75,
            "matching_skills": ["Python"],
            "missing_skills": ["Java"],
            "keyword_analysis": {
                "matched_keywords": [{"keyword": "Python"}],
                "missing_critical": []
            }
        }

        mock_opt = MagicMock()
        mock_opt_cls.return_value = mock_opt
        mock_opt.optimize_comprehensive.return_value = {
            "user_information": {"name": "Test", "email": "test@test.com"}
        }

        mock_cl_gen = MagicMock()
        mock_cl_gen.generate.return_value = {"content": "Test cover letter"}
        mock_cl_cls.return_value = mock_cl_gen

        orch = CVWorkflowOrchestrator()
        result = orch.optimize_cv_for_job("CV text", "JD text", generate_cover_letter=False)

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "optimized_cv" in result

    @patch('app.services.workflow_orchestrator.CoverLetterGenerator')
    @patch('app.services.workflow_orchestrator.CVAnalyzer')
    @patch('app.services.workflow_orchestrator.CVOptimizer')
    def test_optimize_cv_for_job_with_cover_letter(self, mock_opt_cls, mock_analyzer_cls, mock_cl_cls):
        """Test CV optimization with cover letter generation."""
        mock_analyzer = MagicMock()
        mock_analyzer_cls.return_value = mock_analyzer
        mock_analyzer.analyze.return_value = {
            "ats_score": 75,
            "matching_skills": ["Python"],
            "missing_skills": ["Java"],
            "keyword_analysis": {
                "matched_keywords": [{"keyword": "Python"}],
                "missing_critical": []
            }
        }

        mock_opt = MagicMock()
        mock_opt_cls.return_value = mock_opt
        mock_opt.optimize_comprehensive.return_value = {
            "user_information": {"name": "Test", "email": "test@test.com"}
        }

        mock_cl_gen = MagicMock()
        mock_cl_gen.generate.return_value = {"content": "Test cover letter"}
        mock_cl_cls.return_value = mock_cl_gen

        orch = CVWorkflowOrchestrator()
        result = orch.optimize_cv_for_job("CV text", "JD text", generate_cover_letter=True)

        assert isinstance(result, dict)
        assert "cover_letter" in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_json_parser_empty_response(self):
        """Test JSON parser with empty response."""
        result = JSONParser.safe_json_parse("", {"fallback": True})
        assert result == {"fallback": True}

    def test_text_processor_none_input(self):
        """Test text processor with None input."""
        result = TextProcessor.extract_section(None, ["EXPERIENCE"])
        assert result is None

    def test_metrics_helper_extract_invalid(self):
        """Test metrics helper with invalid input."""
        result = MetricsHelper.extract_ats_score_from_text("no numbers here")
        assert result == 0

    def test_cv_optimizer_fallback_structure(self):
        """Test CV optimizer returns fallback on invalid response."""
        with patch('app.services.cv_optimizer.get_ai_client') as mock_client:
            mock_client.return_value.chat_completion.return_value = "invalid json"

            opt = CVOptimizer()
            result = opt.optimize_comprehensive("CV", "JD")
            assert "user_information" in result
