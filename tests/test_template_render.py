"""Test template rendering with dynamic fields."""
from app.services.resume.latex_generator import LaTeXGenerator
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_render_resume_template():
    """Test rendering the main resume template with dynamic fields."""

    # Setup data with all new fields
    data = {
        "user_information": {
            "name": "Test Candidate",
            "email": "test@example.com",
            "phone": "+1 555-0123",
            "address": "123 Test St, City, Country",
            "birthdate": "01.01.1990",
            "age": "34 y.o.",
            "linkedin": "linkedin.com/in/test",
            "github": "github.com/test",
            "profile_description": "Test profile description.",
            "languages": ["English (Native)", "Spanish (Fluent)"],
            "skills": {
                "hard_skills": ["Python", "LaTeX"],
                "soft_skills": ["Teamwork"]
            },
            "experiences": [],
            "education": []
        }
    }

    # Initialize generator pointing to real templates
    template_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../data/sample_latex_templates'))
    generator = LaTeXGenerator(template_dir)
    generator.json_data = data

    # Render
    output = generator.generate_from_template("resume_template.tex")

    # Verify
    print("Verifying template output...")

    # 1. Check for Hardcoded French
    if "French (Native)" in output and "French (Native)" not in str(data['user_information']['languages']):
        print("FAIL: Hardcoded 'French (Native)' found!")
        sys.exit(1)

    # 2. Check for Dynamic Languages
    if "Spanish (Fluent)" not in output:
        print("FAIL: Dynamic language 'Spanish (Fluent)' not found!")
        sys.exit(1)

    # 3. Check for Contact Info
    if "+1 555-0123" not in output:
        print("FAIL: Phone number not found!")
        sys.exit(1)

    if "123 Test St" not in output:
        print("FAIL: Address not found!")
        sys.exit(1)

    if "34 y.o." not in output:
        print("FAIL: Age not found!")
        sys.exit(1)

    print("SUCCESS: All dynamic fields rendered correctly and hardcoding removed.")


if __name__ == "__main__":
    try:
        test_render_resume_template()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
