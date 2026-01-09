"""Validate PowerCV Cerebras integration installation."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def check_files():
    """Check all required files exist."""
    required_files = [
        "app/prompts/cv_analyzer.md",
        "app/prompts/cv_optimizer.md",
        "app/prompts/cover_letter.md",
        "app/prompts/prompt_loader.py",
        "app/services/cerebras_client.py",
        "app/services/cv_analyzer.py",
        "app/services/cv_optimizer.py",
        "app/services/cover_letter_gen.py",
        "app/services/workflow_orchestrator.py",
        ".env"
    ]

    missing = []
    for filepath in required_files:
        if not Path(filepath).exists():
            missing.append(filepath)

    if missing:
        print(" Missing files:")
        for f in missing:
            print(f"   - {f}")
        return False

    print(" All required files present")
    return True


def check_imports():
    """Check all imports work."""
    try:
        from app.prompts.prompt_loader import PromptLoader  # noqa: F401
        from app.services.cerebras_client import CerebrasClient  # noqa: F401
        from app.services.workflow_orchestrator import (
            CVWorkflowOrchestrator,  # noqa: F401
        )
        print(" All imports successful")
        return True
    except ImportError as e:
        print(f" Import error: {e}")
        return False


def check_prompts():
    """Check prompts can be loaded."""
    try:
        from app.prompts.prompt_loader import PromptLoader
        loader = PromptLoader()
        prompts = loader.load_all_prompts()
        print(f" Loaded {len(prompts)} prompts")
        return True
    except Exception as e:
        print(f" Prompt loading error: {e}")
        return False


def check_env():
    """Check environment variables."""
    load_dotenv()

    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key or api_key == "your_api_key_here_REPLACE_THIS":
        print("  Warning: CEREBRAS_API_KEY not set in .env")
        return False

    print(" Environment variables configured")
    return True


if __name__ == "__main__":
    print("--- PowerCV Installation Validation ---")
    results = [
        check_files(),
        check_imports(),
        check_prompts(),
        check_env()
    ]

    if all(results):
        print("\n Installation looks solid!")
    else:
        print("\n  Some checks failed. Please review the output above.")
        sys.exit(1)
