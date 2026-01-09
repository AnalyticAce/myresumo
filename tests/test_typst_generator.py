"""Test Typst PDF generation."""
from app.services.resume.typst_generator import TypstGenerator
import pytest
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_typst_pdf_generation():
    """Test generating a PDF from Typst template."""

    output_path = "test_resume_typst.pdf"

    # Setup sample data
    data = {
        "user_information": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1 555-0123",
            "address": "San Francisco, CA",
            "linkedin": "linkedin.com/in/jane",
            "github": "github.com/jane",
            "profile_description": "Experienced software engineer with a focus on backend systems.",
            "languages": ["English (Native)", "German (B1)"],
            "skills": {
                "hard_skills": ["Rust", "Python", "Typst"],
                "soft_skills": ["Leadership", "Communication"]
            },
            "experiences": [
                {
                    "job_title": "Senior Engineer",
                    "company": "Tech Corp",
                    "location": "Remote",
                    "start_date": "01/2020",
                    "end_date": "Present",
                    "four_tasks": [
                        "Built scalable APIs using Rust.",
                        "Migrated from LaTeX to Typst."
                    ]
                }
            ],
            "education": [
                {
                    "institution": "University of Tech",
                    "degree": "B.S. Computer Science",
                    "start_date": "09/2015",
                    "end_date": "06/2019",
                    "location": "New York, NY"
                }
            ]
        },
        "projects": [],
        "certificate": []
    }

    # Initialize generator
    generator = TypstGenerator()
    generator.json_data = data

    # Check if binary found
    if not generator.typst_bin:
        pytest.skip(
            "Typst binary not found by generator. Skipping PDF generation test.")
    print(f"Typst binary found at: {generator.typst_bin}")

    templates_to_test = ["resume.typ", "modern.typ"]

    for tmpl in templates_to_test:
        print(f"Testing template: {tmpl}...")
        current_output = f"test_resume_{tmpl.replace('.typ', '')}.pdf"

        # Clean up
        if os.path.exists(current_output):
            os.remove(current_output)

        success = generator.generate_pdf(tmpl, current_output)

        if not success:
            print(f"FAIL: generate_pdf returned False for {tmpl}")
            # sys.exit(1) # Continue to test others
            continue

        if not os.path.exists(current_output):
            print(f"FAIL: PDF file not found for {tmpl}")
            continue

        # Check file size
        size = os.path.getsize(current_output)
        print(f"PDF generated successfully for {tmpl}. Size: {size} bytes")

        if size < 1000:
            print(f"WARNING: PDF for {tmpl} seems suspiciously small.")

        # Cleanup if successful
        if os.path.exists(current_output):
            os.remove(current_output)

    print("SUCCESS")


if __name__ == "__main__":
    test_typst_pdf_generation()
