"""Test HTML/CSS to PDF generation."""
from app.services.resume.html_generator import HTMLGenerator
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_html_pdf_generation():
    """Test generating a PDF from HTML template."""

    output_path = "test_resume.pdf"

    # Clean up previous run
    if os.path.exists(output_path):
        os.remove(output_path)

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
            "languages": ["English (Native)", "French (Beginner)"],
            "skills": {
                "hard_skills": ["Python", "FastAPI", "Docker"],
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
                        "Built scalable APIs.",
                        "Mentored juniors."
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
    # Assuming code is running from project root
    generator = HTMLGenerator()  # Default templates dir
    generator.json_data = data

    print("Generating PDF...")
    success = generator.generate_pdf("modern_resume.html", output_path)

    if not success:
        print("FAIL: generate_pdf returned False")
        sys.exit(1)

    if not os.path.exists(output_path):
        print("FAIL: PDF file not found")
        sys.exit(1)

    # Check file size to ensure it's not empty
    size = os.path.getsize(output_path)
    print(f"PDF generated successfully. Size: {size} bytes")

    if size < 1000:
        print("WARNING: PDF seems suspiciously small.")

    print("SUCCESS")

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)


if __name__ == "__main__":
    test_html_pdf_generation()
