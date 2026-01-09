"""Unit tests for utility functions."""
import pytest
from bson import ObjectId
from app.utils.shared_utils import JSONParser
from app.utils.validation import ValidationHelper


class TestJSONParser:
    """Test JSONParser utility."""

    def test_clean_json_response(self):
        """Test JSON response cleaning."""
        json_str = '```json\n{"key": "value"}\n```'
        cleaned = JSONParser.clean_json_response(json_str)
        assert "```" not in cleaned
        assert "key" in cleaned

    def test_safe_json_parse(self):
        """Test safe JSON parsing with fallback."""
        result = JSONParser.safe_json_parse(
            '{"key": "value"}', {"fallback": True})
        assert result["key"] == "value"

        result = JSONParser.safe_json_parse('invalid json', {"fallback": True})
        assert result["fallback"] is True


class TestValidationHelper:
    """Test ValidationHelper utility."""

    def test_validate_url(self):
        """Test URL validation."""
        valid_url = "https://www.linkedin.com/jobs/123"
        result = ValidationHelper.validate_url(valid_url)
        assert result == valid_url

        with pytest.raises(ValueError):
            ValidationHelper.validate_url("not-a-url")

    def test_validate_text_input(self):
        """Test text input validation."""
        text = "This is a valid text input for testing purposes"
        result = ValidationHelper.validate_text_input(
            text, max_length=200, field_name="test")
        assert result == text

        with pytest.raises(ValueError):
            ValidationHelper.validate_text_input(
                "short", max_length=200, field_name="test", min_length=10)
