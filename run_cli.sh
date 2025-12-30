#!/bin/bash
# PowerCV CLI Wrapper Script
# This script provides easy access to PowerCV CLI commands

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Try to activate virtual environment if it exists
    if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
        source "$SCRIPT_DIR/.venv/bin/activate"
    fi
fi

# Display help when no arguments provided
if [ $# -eq 0 ]; then
    echo "PowerCV - AI-Powered Job Application Automation"
    echo ""
    echo "Usage: ./run.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  tailor       Tailor CV for a specific job"
    echo "  cover-letter Generate cover letter for a job"
    echo "  scrape       Scrape job description from URL"
    echo "  optimize     Full optimization (CV + Cover Letter)"
    echo "  batch        Batch process multiple jobs"
    echo "  init         Initialize example files"
    echo ""
    echo "Examples:"
    echo "  ./run.sh tailor --cv resume.txt --url \"https://linkedin.com/jobs/view/...\""
    echo "  ./run.sh optimize --cv resume.txt --jd job.txt --output ./output"
    echo "  ./run.sh batch --cv resume.txt --config jobs.yaml --output ./applications"
    echo ""
    echo "For more information, run: python -m app.cli.main --help"
    echo ""
    echo "Note: Make sure to set up your .env file with API keys first!"
    exit 0
fi

# Run the PowerCV CLI
cd "$SCRIPT_DIR"
python -m app.cli.main "$@"
