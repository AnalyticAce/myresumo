"""Test JSON repair logic."""
import pytest
from app.utils.shared_utils import JSONParser


def test_repair_truncated_json_object():
    """Test repairing a truncated JSON object."""
    truncated = '{"key": "value", "list": [1, 2, 3'
    repaired = JSONParser.repair_json(truncated)
    assert repaired == '{"key": "value", "list": [1, 2, 3]}'


def test_repair_truncated_json_list():
    """Test repairing a truncated JSON list."""
    truncated = '[{"id": 1}, {"id": 2'
    repaired = JSONParser.repair_json(truncated)
    assert repaired == '[{"id": 1}, {"id": 2}]'


def test_repair_nested_structures():
    """Test repairing deeply nested structures."""
    truncated = '{"a": {"b": {"c": [1, 2'
    repaired = JSONParser.repair_json(truncated)
    assert repaired == '{"a": {"b": {"c": [1, 2]}}}'


def test_repair_open_string():
    """Test repairing a truncated string within JSON."""
    truncated = '{"name": "Ilnar'
    repaired = JSONParser.repair_json(truncated)
    assert repaired == '{"name": "Ilnar"}'


def test_repair_complex_cv_structure():
    """Test repairing a complex CV-like structure."""
    truncated = '''{
  "user_information": {
    "name": "Candidate",
    "skills": {
      "hard": ["Python", "Go"],
      "soft": ["Lead'''

    repaired = JSONParser.repair_json(truncated)
    import json
    parsed = json.loads(repaired)

    assert parsed['user_information']['name'] == "Candidate"
    assert parsed['user_information']['skills']['hard'] == ["Python", "Go"]
    assert parsed['user_information']['skills']['soft'] == ["Lead"]


if __name__ == "__main__":
    # verification run
    test_repair_truncated_json_object()
    test_repair_truncated_json_list()
    test_repair_nested_structures()
    test_repair_open_string()
    test_repair_complex_cv_structure()
    print("All JSON repair tests passed!")
