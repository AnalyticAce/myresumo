"""Test enhanced error handling and debugging capabilities."""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.utils.error_handler import (
    DetailedError, ErrorHandler, ValidationError, ConfigurationError,
    ErrorContext, create_error_response
)
from app.utils.validation import ValidationHelper


class TestDetailedError:
    """Test DetailedError class."""
    
    def test_detailed_error_creation(self):
        """Test creating a detailed error."""
        error = DetailedError(
            message="Test error",
            error_code="TEST_ERROR",
            context={"key": "value"},
            user_friendly_message="User friendly message"
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.context["key"] == "value"
        assert error.user_friendly_message == "User friendly message"
        assert error.timestamp is not None
    
    def test_detailed_error_to_dict(self):
        """Test converting detailed error to dictionary."""
        error = DetailedError(
            message="Test error",
            error_code="TEST_ERROR",
            context={"key": "value"}
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test error"
        assert error_dict["context"]["key"] == "value"
        assert error_dict["timestamp"] is not None


class TestErrorHandler:
    """Test ErrorHandler class."""
    
    def test_log_error(self):
        """Test error logging."""
        error = ValueError("Test error")
        context = {"operation": "test"}
        
        with patch('app.utils.error_handler.logger') as mock_logger:
            error_details = ErrorHandler.log_error(error, context)
            
            assert error_details["error_type"] == "ValueError"
            assert error_details["message"] == "Test error"
            assert error_details["context"] == context
            assert error_details["timestamp"] is not None
            mock_logger.warning.assert_called_once()
    
    def test_create_http_exception(self):
        """Test creating HTTP exception."""
        error = ValueError("Test error")
        
        with patch('app.utils.error_handler.logger') as mock_logger:
            http_exception = ErrorHandler.create_http_exception(
                error,
                status_code=400,
                user_message="User message"
            )
            
            assert http_exception.status_code == 400
            assert "User message" in str(http_exception.detail)
            mock_logger.warning.assert_called_once()
    
    def test_handle_ai_api_error_timeout(self):
        """Test handling AI API timeout error."""
        error = Exception("Request timeout")
        
        http_exception = ErrorHandler.handle_ai_api_error(
            error,
            provider="test_provider",
            operation="test_operation"
        )
        
        assert http_exception.status_code == 408
        assert "taking too long to respond" in str(http_exception.detail)
    
    def test_handle_ai_api_error_connection(self):
        """Test handling AI API connection error."""
        error = Exception("Connection failed")
        
        http_exception = ErrorHandler.handle_ai_api_error(
            error,
            provider="test_provider",
            operation="test_operation"
        )
        
        assert http_exception.status_code == 503
        assert "Unable to connect" in str(http_exception.detail)
    
    def test_handle_ai_api_error_authentication(self):
        """Test handling AI API authentication error."""
        error = Exception("Authentication failed")
        
        http_exception = ErrorHandler.handle_ai_api_error(
            error,
            provider="test_provider",
            operation="test_operation"
        )
        
        assert http_exception.status_code == 401
        assert "Authentication" in str(http_exception.detail)
    
    def test_handle_ai_api_error_rate_limit(self):
        """Test handling AI API rate limit error."""
        error = Exception("Rate limit exceeded")
        
        http_exception = ErrorHandler.handle_ai_api_error(
            error,
            provider="test_provider",
            operation="test_operation"
        )
        
        assert http_exception.status_code == 429
        assert "Rate limit" in str(http_exception.detail)


class TestValidationHelper:
    """Test ValidationHelper class."""
    
    def test_validate_url_valid(self):
        """Test valid URL validation."""
        url = "https://www.linkedin.com/jobs/view/123456"
        result = ValidationHelper.validate_url(url)
        assert result == url
    
    def test_validate_url_invalid_scheme(self):
        """Test invalid URL scheme."""
        url = "ftp://example.com"
        with pytest.raises(ValueError, match="HTTP or HTTPS protocol"):
            ValidationHelper.validate_url(url)
    
    def test_validate_url_empty(self):
        """Test empty URL."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ValidationHelper.validate_url("")
    
    def test_validate_text_input_valid(self):
        """Test valid text input."""
        text = "This is a valid text input"
        result = ValidationHelper.validate_text_input(text, 100, "test_field")
        assert result == text
    
    def test_validate_text_input_too_short(self):
        """Test text input too short."""
        text = "short"
        with pytest.raises(ValueError, match="must be at least 10 characters"):
            ValidationHelper.validate_text_input(text, 100, "test_field")
    
    def test_validate_text_input_too_long(self):
        """Test text input too long."""
        text = "a" * 101
        with pytest.raises(ValueError, match="is too long"):
            ValidationHelper.validate_text_input(text, 100, "test_field")
    
    def test_validate_email_valid(self):
        """Test valid email."""
        email = "test@example.com"
        result = ValidationHelper.validate_email(email)
        assert result == email.lower()
    
    def test_validate_email_invalid(self):
        """Test invalid email."""
        email = "invalid-email"
        with pytest.raises(ValueError, match="Invalid email format"):
            ValidationHelper.validate_email(email)
    
    def test_validate_phone_valid(self):
        """Test valid phone number."""
        phone = "+1234567890"
        result = ValidationHelper.validate_phone(phone)
        assert result == phone
    
    def test_validate_phone_invalid(self):
        """Test invalid phone number."""
        phone = "123"
        with pytest.raises(ValueError, match="too short"):
            ValidationHelper.validate_phone(phone)
    
    def test_validate_template_name_valid(self):
        """Test valid template name."""
        template = "resume.typ"
        available_templates = ["resume.typ", "modern.typ"]
        result = ValidationHelper.validate_template_name(template, available_templates)
        assert result == template
    
    def test_validate_template_name_invalid(self):
        """Test invalid template name."""
        template = "invalid.typ"
        available_templates = ["resume.typ", "modern.typ"]
        with pytest.raises(ValueError, match="not available"):
            ValidationHelper.validate_template_name(template, available_templates)


class TestErrorContext:
    """Test ErrorContext class."""
    
    def test_error_context_success(self):
        """Test error context on successful operation."""
        with patch('app.utils.error_handler.log_performance') as mock_log:
            with ErrorContext("test_operation", {"key": "value"}):
                pass
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            assert call_args[0] == "test_operation"
            assert isinstance(call_args[1], float)
    
    def test_error_context_failure(self):
        """Test error context on failed operation."""
        with patch('app.utils.error_handler.ErrorHandler.log_error') as mock_log:
            try:
                with ErrorContext("test_operation", {"key": "value"}):
                    raise ValueError("Test error")
            except ValueError:
                pass
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            assert isinstance(call_args[0], ValueError)
            assert call_args[1]["operation"] == "test_operation"


class TestCreateErrorResponse:
    """Test error response creation."""
    
    def test_create_error_response(self):
        """Test creating error response."""
        response = create_error_response(
            error_code="TEST_ERROR",
            message="Test message",
            details={"key": "value"},
            status_code=400
        )
        
        assert response["error"] is True
        assert response["error_code"] == "TEST_ERROR"
        assert response["message"] == "Test message"
        assert response["details"]["key"] == "value"
        assert response["timestamp"] is not None


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = ValidationError(
            field="test_field",
            message="Test validation error",
            value="test_value"
        )
        
        assert error.field == "test_field"
        assert error.message == "Test validation error"
        assert error.value == "test_value"
        assert "Validation error for test_field" in str(error)


class TestConfigurationError:
    """Test ConfigurationError class."""
    
    def test_configuration_error_creation(self):
        """Test creating configuration error."""
        error = ConfigurationError(
            message="Test config error",
            config_key="TEST_KEY",
            expected_type="string",
            provider="test_provider"
        )
        
        assert error.error_code == "CONFIGURATION_ERROR"
        assert error.context["config_key"] == "TEST_KEY"
        assert error.context["expected_type"] == "string"
        assert error.context["provider"] == "test_provider"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
