"""Unit tests for core services."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.cv_optimizer import CVOptimizer
from app.services.workflow_orchestrator import CVWorkflowOrchestrator


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
            "missing_skills": ["Java"]
        }

        mock_opt = MagicMock()
        mock_opt_cls.return_value = mock_opt
        mock_opt.optimize_comprehensive.return_value = {
            "user_information": {"name": "Test", "email": "test@test.com"}
        }

        # Mock CoverLetterGenerator to prevent AI client initialization
        mock_cl_gen = MagicMock()
        mock_cl_gen.generate.return_value = {"content": "Test cover letter"}
        mock_cl_cls.return_value = mock_cl_gen

        orch = CVWorkflowOrchestrator()
        result = orch.optimize_cv_for_job("CV text", "JD text")

        assert isinstance(result, dict)
