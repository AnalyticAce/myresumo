"""CLI Automation Tool for PowerCV.

This module provides a command-line interface for automating job-seeking tasks
including CV tailoring and cover letter generation.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.scraper import fetch_job_description, extract_keywords_from_jd
from app.services.workflow_orchestrator import CVWorkflowOrchestrator
from app.services.cover_letter_gen import CoverLetterGenerator
from app.utils.shared_utils import ValidationHelper, ErrorHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PowerCVCLI:
    """Command-line interface for PowerCV automation."""

    def __init__(self):
        """Initialize CLI with required services."""
        self.orchestrator = CVWorkflowOrchestrator()
        self.cover_letter_gen = CoverLetterGenerator()

    async def run(self, args: argparse.Namespace):
        """Execute the requested command.

        Args:
            args: Parsed command-line arguments
        """
        command = args.command

        if command == "tailor":
            await self._cmd_tailor(args)
        elif command == "cover-letter":
            await self._cmd_cover_letter(args)
        elif command == "scrape":
            await self._cmd_scrape(args)
        elif command == "optimize":
            await self._cmd_optimize(args)
        elif command == "batch":
            await self._cmd_batch(args)
        elif command == "init":
            self._cmd_init(args)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    async def _cmd_tailor(self, args: argparse.Namespace):
        """Tailor CV for a specific job.

        Args:
            args: Command-line arguments
        """
        cv_path = Path(args.cv)
        jd_path = Path(args.jd) if args.jd else None
        jd_url = args.url
        output = Path(args.output) if args.output else None

        if not cv_path.exists():
            logger.error(f"CV file not found: {cv_path}")
            sys.exit(1)

        # Load CV
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_text = f.read()

        # Get job description
        if jd_url:
            logger.info(f"Fetching job description from: {jd_url}")
            jd_data = await fetch_job_description(jd_url)
            jd_text = jd_data.get("description", "")
            if not jd_text:
                logger.error("Failed to extract job description from URL")
                sys.exit(1)
            logger.info(f"Extracted job: {jd_data.get('title', 'Unknown')}")
        elif jd_path and jd_path.exists():
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        else:
            logger.error("Please provide job description via --url or --jd")
            sys.exit(1)

        logger.info("Starting CV optimization...")
        result = self.orchestrator.optimize_cv_for_job(
            cv_text=cv_text,
            jd_text=jd_text,
            generate_cover_letter=False,
        )

        # Extract optimized CV content
        optimized_cv = result.get("optimized_cv", {})
        if isinstance(optimized_cv, dict):
            content = optimized_cv.get("optimized_resume", "") or json.dumps(
                optimized_cv, indent=2
            )
        else:
            content = str(optimized_cv)

        # Save or print output
        if output:
            self._save_output(output, content, result)
            logger.info(f"Tailored CV saved to: {output}")
        else:
            print("\n" + "=" * 60)
            print("TAILORED CV")
            print("=" * 60)
            print(content)

        # Print summary
        self._print_summary(result)

    async def _cmd_cover_letter(self, args: argparse.Namespace):
        """Generate cover letter.

        Args:
            args: Command-line arguments
        """
        cv_path = Path(args.cv)
        jd_path = Path(args.jd) if args.jd else None
        jd_url = args.url
        output = Path(args.output) if args.output else None
        tone = args.tone

        if not cv_path.exists():
            logger.error(f"CV file not found: {cv_path}")
            sys.exit(1)

        # Load CV
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_text = f.read()

        # Get job description
        if jd_url:
            logger.info(f"Fetching job description from: {jd_url}")
            jd_data = await fetch_job_description(jd_url)
            jd_text = jd_data.get("description", "")
        elif jd_path and jd_path.exists():
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        else:
            logger.error("Please provide job description via --url or --jd")
            sys.exit(1)

        logger.info("Generating cover letter...")
        result = self.orchestrator.optimize_cv_for_job(
            cv_text=cv_text,
            jd_text=jd_text,
            generate_cover_letter=True,
        )

        cover_letter = result.get("cover_letter", {})

        # Save or print output
        if output:
            content = cover_letter.get("cover_letter", "") or json.dumps(
                cover_letter, indent=2
            )
            self._save_output(output, content, result)
            logger.info(f"Cover letter saved to: {output}")
        else:
            print("\n" + "=" * 60)
            print("COVER LETTER")
            print("=" * 60)
            print(cover_letter.get("cover_letter", ""))

    async def _cmd_scrape(self, args: argparse.Namespace):
        """Scrape job description from URL.

        Args:
            args: Command-line arguments
        """
        url = args.url
        output = Path(args.output) if args.output else None

        try:
            # Validate URL
            validated_url = ValidationHelper.validate_url(url)
            logger.info(f"Fetching job description from: {validated_url}")

            result = await fetch_job_description(validated_url)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
                logger.info(f"Job description saved to: {output}")
            else:
                print("\n" + "=" * 60)
                print("JOB DESCRIPTION")
                print("=" * 60)
                print(json.dumps(result, indent=2))

        except ValueError as e:
            logger.error(f"URL validation error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            sys.exit(1)

    async def _cmd_optimize(self, args: argparse.Namespace):
        """Full optimization: CV + Cover Letter.

        Args:
            args: Command-line arguments
        """
        cv_path = Path(args.cv)
        jd_path = Path(args.jd) if args.jd else None
        jd_url = args.url
        output_dir = Path(args.output) if args.output else Path(".")

        if not cv_path.exists():
            logger.error(f"CV file not found: {cv_path}")
            sys.exit(1)

        # Load CV
        with open(cv_path, "r", encoding="utf-8") as f:
            cv_text = f.read()

        # Get job description
        if jd_url:
            logger.info(f"Fetching job description from: {jd_url}")
            jd_data = await fetch_job_description(jd_url)
            jd_text = jd_data.get("description", "")
            job_title = jd_data.get("title", "job")
        elif jd_path and jd_path.exists():
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
            job_title = jd_path.stem
        else:
            logger.error("Please provide job description via --url or --jd")
            sys.exit(1)

        logger.info("Starting full optimization...")

        # Run optimization workflow
        result = self.orchestrator.optimize_cv_for_job(
            cv_text=cv_text,
            jd_text=jd_text,
            generate_cover_letter=True,
        )

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize job title for filenames
        safe_job_title = "".join(
            c if c.isalnum() or c in "-_ " else "_" for c in job_title
        ).strip()
        safe_job_title = safe_job_title.replace(" ", "_")[:30]

        # Save tailored CV
        cv_output = output_dir / f"cv_{safe_job_title}.txt"
        optimized_cv = result.get("optimized_cv", {})
        if isinstance(optimized_cv, dict):
            cv_content = optimized_cv.get("optimized_resume", "") or json.dumps(
                optimized_cv, indent=2
            )
        else:
            cv_content = str(optimized_cv)

        with open(cv_output, "w", encoding="utf-8") as f:
            f.write(cv_content)
        logger.info(f"Tailored CV saved to: {cv_output}")

        # Save cover letter
        cl_output = output_dir / f"cover_letter_{safe_job_title}.txt"
        cover_letter = result.get("cover_letter", {})
        cl_content = cover_letter.get("cover_letter", "") or json.dumps(
            cover_letter, indent=2
        )

        with open(cl_output, "w", encoding="utf-8") as f:
            f.write(cl_content)
        logger.info(f"Cover letter saved to: {cl_output}")

        # Save analysis report
        analysis_output = output_dir / f"analysis_{safe_job_title}.json"
        analysis = {
            "ats_score": result.get("ats_score", 0),
            "matching_skills": result.get("matching_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "recommendation": result.get("recommendation", ""),
            "timestamp": datetime.now().isoformat(),
        }

        with open(analysis_output, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2)
        logger.info(f"Analysis report saved to: {analysis_output}")

        # Print summary
        print("\n" + "=" * 60)
        print("OPTIMIZATION COMPLETE")
        print("=" * 60)
        print(f"ATS Score: {result.get('ats_score', 'N/A')}%")
        print(f"Matched Skills: {', '.join(result.get('matching_skills', [])[:10])}")
        print(f"Missing Skills: {', '.join(result.get('missing_skills', [])[:5])}")
        print(f"\nFiles generated:")
        print(f"  - {cv_output}")
        print(f"  - {cl_output}")
        print(f"  - {analysis_output}")

    async def _cmd_batch(self, args: argparse.Namespace):
        """Batch process multiple job applications.

        Args:
            args: Command-line arguments
        """
        config_path = Path(args.config)
        output_dir = Path(args.output) if args.output else Path("output")
        cv_path = Path(args.cv)

        if not cv_path.exists():
            logger.error(f"Master CV file not found: {cv_path}")
            sys.exit(1)

        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            sys.exit(1)

        # Load config
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Load master CV
        with open(cv_path, "r", encoding="utf-8") as f:
            master_cv = f.read()

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Process each job
        jobs = config.get("jobs", [])
        logger.info(f"Processing {len(jobs)} jobs...")

        results = []
        for i, job in enumerate(jobs, 1):
            logger.info(f"Processing job {i}/{len(jobs)}: {job.get('title', 'Unknown')}")

            try:
                # Fetch job description
                jd_url = job.get("url")
                jd_text = job.get("description", "")

                if jd_url:
                    jd_data = await fetch_job_description(jd_url)
                    jd_text = jd_data.get("description", "")

                if not jd_text:
                    logger.warning(f"No job description for: {job.get('title')}")
                    continue

                # Run optimization
                result = self.orchestrator.optimize_cv_for_job(
                    cv_text=master_cv,
                    jd_text=jd_text,
                    generate_cover_letter=True,
                )

                # Generate safe filename
                job_title = job.get("title", f"job_{i}")
                safe_title = "".join(
                    c if c.isalnum() or c in "-_ " else "_" for c in job_title
                ).strip()
                safe_title = safe_title.replace(" ", "_")[:30]

                # Save outputs
                cv_output = output_dir / f"cv_{safe_title}.txt"
                optimized_cv = result.get("optimized_cv", {})
                if isinstance(optimized_cv, dict):
                    cv_content = optimized_cv.get("optimized_resume", "") or json.dumps(
                        optimized_cv, indent=2
                    )
                else:
                    cv_content = str(optimized_cv)

                with open(cv_output, "w", encoding="utf-8") as f:
                    f.write(cv_content)

                cl_output = output_dir / f"cover_letter_{safe_title}.txt"
                cover_letter = result.get("cover_letter", {})
                cl_content = cover_letter.get("cover_letter", "") or json.dumps(
                    cover_letter, indent=2
                )

                with open(cl_output, "w", encoding="utf-8") as f:
                    f.write(cl_content)

                results.append(
                    {
                        "job": job_title,
                        "company": job.get("company", ""),
                        "ats_score": result.get("ats_score", 0),
                        "cv_file": str(cv_output),
                        "cl_file": str(cl_output),
                    }
                )

                logger.info(f"  ✓ Completed: {job_title} (ATS: {result.get('ats_score')}%)")

            except Exception as e:
                logger.error(f"  ✗ Failed: {job.get('title')} - {str(e)}")
                results.append(
                    {"job": job.get("title"), "error": str(e), "status": "failed"}
                )

        # Save batch summary
        summary_output = output_dir / "batch_summary.json"
        with open(summary_output, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "total_jobs": len(jobs),
                    "successful": sum(1 for r in results if "error" not in r),
                    "failed": sum(1 for r in results if "error" in r),
                    "results": results,
                },
                f,
                indent=2,
            )

        # Print summary
        print("\n" + "=" * 60)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Total jobs: {len(jobs)}")
        print(f"Successful: {sum(1 for r in results if 'error' not in r)}")
        print(f"Failed: {sum(1 for r in results if 'error' in r)}")
        print(f"\nOutput directory: {output_dir}")
        print(f"Summary: {summary_output}")

    def _cmd_init(self, args: argparse.Namespace):
        """Initialize PowerCV configuration files.

        Args:
            args: Command-line arguments
        """
        output_dir = Path(args.output) if args.output else Path(".")

        # Create example master CV
        master_cv_example = output_dir / "master_cv.txt"
        if not master_cv_example.exists():
            example_cv = """John Doe
john.doe@email.com | +31 6 12345678 | Amsterdam, Netherlands
linkedin.com/in/johndoe | github.com/johndoe

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience in full-stack development,
specializing in Python, JavaScript, and cloud technologies. Proven track record
of building scalable web applications and leading development teams.

WORK EXPERIENCE

Senior Software Engineer - TechCorp BV, Amsterdam
2022 - Present
- Led development of microservices architecture using Python and Docker
- Improved system performance by 40% through optimization of database queries
- Mentored 5 junior developers and established code review practices
- Implemented CI/CD pipelines reducing deployment time by 60%

Software Engineer - StartupXYZ, Rotterdam
2020 - 2022
- Developed full-stack web applications using React and Node.js
- Built RESTful APIs serving 100k+ daily requests
- Integrated payment processing systems (Stripe, PayPal)
- Collaborated with product team to define technical requirements

Junior Developer - WebAgency, Utrecht
2018 - 2020
- Created responsive websites using HTML, CSS, JavaScript
- Developed custom WordPress themes and plugins
- Maintained client websites and resolved technical issues

EDUCATION

Bachelor of Computer Science - University of Amsterdam
2014 - 2018

SKILLS
- Languages: Python, JavaScript, TypeScript, SQL, HTML/CSS
- Frameworks: React, Django, FastAPI, Flask
- Databases: PostgreSQL, MongoDB, Redis
- DevOps: Docker, Kubernetes, AWS, CI/CD, Git
- Tools: GitHub, Jira, Figma, Postman

CERTIFICATIONS
- AWS Certified Solutions Architect
- Python Institute PCEP Certified Entry-Level Python Programmer
"""
            with open(master_cv_example, "w", encoding="utf-8") as f:
                f.write(example_cv)
            logger.info(f"Created example master CV: {master_cv_example}")

        # Create example batch config
        batch_config_example = output_dir / "batch_jobs.yaml"
        if not batch_config_example.exists():
            example_config = """# PowerCV Batch Job Configuration
# Edit this file to batch process multiple job applications

jobs:
  # Job 1: LinkedIn example
  - title: Senior Python Developer
    company: TechCorp
    url: https://www.linkedin.com/jobs/view/senior-python-developer-at-techcorp-123456

  # Job 2: Indeed example
  - title: Software Engineer
    company: StartupXYZ
    description: |
      We are looking for a Software Engineer to join our team.

      Requirements:
      - 3+ years experience with Python
      - Experience with web frameworks (Django, Flask)
      - Knowledge of PostgreSQL and Docker
      - Bachelor's degree in Computer Science or equivalent

      We offer:
      - Competitive salary
      - Remote work options
      - Professional development budget

  # Job 3: Another position
  - title: Backend Developer
    company: Enterprise Inc
    description: "Looking for a Backend Developer with Python and AWS experience..."
"""
            with open(batch_config_example, "w", encoding="utf-8") as f:
                f.write(example_config)
            logger.info(f"Created example batch config: {batch_config_example}")

        # Create .env example
        env_example = output_dir / ".env.example"
        if not env_example.exists():
            env_content = """# PowerCV Environment Variables
# Copy this file to .env and fill in your values

# API Keys
API_KEY=your_api_key_here
API_BASE=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# Cerebras API (optional alternative)
CEREBRAS_API_KEY=
CEREBRAS_API_BASE=https://api.cerebras.ai/v1
CEREBRAS_MODEL=gpt-oss-120b

# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/powercv

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8080
"""
            with open(env_example, "w", encoding="utf-8") as f:
                f.write(env_content)
            logger.info(f"Created .env.example: {env_example}")

        logger.info(f"PowerCV initialization complete in: {output_dir}")

    def _save_output(self, output_path: Path, content: str, result: Dict):
        """Save output to file.

        Args:
            output_path: Path to save file
            content: Content to save
            result: Full result object for metadata
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _print_summary(self, result: Dict):
        """Print optimization summary.

        Args:
            result: Optimization result
        """
        print("\n" + "=" * 60)
        print("OPTIMIZATION SUMMARY")
        print("=" * 60)
        print(f"ATS Score: {result.get('ats_score', 'N/A')}%")
        print(f"Matched Skills: {', '.join(result.get('matching_skills', [])[:10])}")
        print(f"Missing Skills: {', '.join(result.get('missing_skills', [])[:5])}")
        print(f"\nRecommendation: {result.get('recommendation', 'N/A')[:200]}")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="PowerCV - AI-Powered Job Application Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Tailor CV for a LinkedIn job
  powercv tailor --cv resume.txt --url "https://linkedin.com/jobs/view/..."

  # Generate cover letter
  powercv cover-letter --cv resume.txt --jd job_description.txt --tone professional

  # Scrape job description from URL
  powercv scrape --url "https://indeed.com/jobs?q=python&l=amsterdam"

  # Full optimization (CV + Cover Letter)
  powercv optimize --cv resume.txt --url "https://linkedin.com/jobs/view/..." --output ./output

  # Batch process multiple jobs
  powercv batch --cv resume.txt --config jobs.yaml --output ./applications

  # Initialize example files
  powercv init --output ./my_applications
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Tailor command
    tailor_parser = subparsers.add_parser("tailor", help="Tailor CV for a specific job")
    tailor_parser.add_argument(
        "--cv", required=True, help="Path to your CV file (txt/md)"
    )
    tailor_parser.add_argument(
        "--jd", help="Path to job description file (txt/md)"
    )
    tailor_parser.add_argument(
        "--url", help="URL to job posting (LinkedIn, Indeed, etc.)"
    )
    tailor_parser.add_argument(
        "--output", "-o", help="Output file path for tailored CV"
    )

    # Cover letter command
    cl_parser = subparsers.add_parser(
        "cover-letter", help="Generate cover letter for a job"
    )
    cl_parser.add_argument(
        "--cv", required=True, help="Path to your CV file (txt/md)"
    )
    cl_parser.add_argument(
        "--jd", help="Path to job description file (txt/md)"
    )
    cl_parser.add_argument(
        "--url", help="URL to job posting (LinkedIn, Indeed, etc.)"
    )
    cl_parser.add_argument(
        "--output", "-o", help="Output file path for cover letter"
    )
    cl_parser.add_argument(
        "--tone",
        default="Professional",
        choices=["Professional", "Enthusiastic", "Formal", "Casual"],
        help="Tone for the cover letter",
    )

    # Scrape command
    scrape_parser = subparsers.add_parser(
        "scrape", help="Scrape job description from URL"
    )
    scrape_parser.add_argument(
        "--url", required=True, help="URL to job posting"
    )
    scrape_parser.add_argument(
        "--output", "-o", help="Output file path for scraped content"
    )

    # Optimize command
    opt_parser = subparsers.add_parser(
        "optimize", help="Full optimization (CV + Cover Letter)"
    )
    opt_parser.add_argument(
        "--cv", required=True, help="Path to your CV file (txt/md)"
    )
    opt_parser.add_argument(
        "--jd", help="Path to job description file (txt/md)"
    )
    opt_parser.add_argument(
        "--url", help="URL to job posting (LinkedIn, Indeed, etc.)"
    )
    opt_parser.add_argument(
        "--output", "-o", default="./output", help="Output directory (default: ./output)"
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch", help="Batch process multiple job applications"
    )
    batch_parser.add_argument(
        "--cv", required=True, help="Path to your master CV file (txt/md)"
    )
    batch_parser.add_argument(
        "--config", required=True, help="Path to batch configuration YAML file"
    )
    batch_parser.add_argument(
        "--output", "-o", default="./output", help="Output directory (default: ./output)"
    )

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize PowerCV with example files"
    )
    init_parser.add_argument(
        "--output", "-o", default=".", help="Output directory for example files"
    )

    return parser


async def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = PowerCVCLI()
    await cli.run(args)


def entry_point():
    """Entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
