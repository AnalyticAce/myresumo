# Changelog - Patch 2025-12-30

Summary of fixes and improvements made to PowerCV to resolve startup and runtime issues.

## Server Startup & Core Infrastructure
- **Fixed Critical Syntax Error**: Resolved an orphaned `except` block in `app/database/repositories/cover_letter_repository.py`.
- **FastAPI Parameter Validation**: Corrected route parameter definitions in `app/main.py` (replaced `Field` with `Body` and `Query`) to fix Uvicorn `AssertionError`.
- **Pydantic V2 Migration**: Updated models and configuration in `app/main.py` to be compatible with Pydantic V2 (e.g., `pattern` vs `regex`, `json_schema_extra` vs `schema_extra`).
- **Merge Conflict Resolution**: Cleaned up persistent merge conflict markers and resolved duplicate imports in `app/main.py` and `app/services/__init__.py`.

## Database & Environment
- **Fixed MongoDB URI Construction**: Repaired the logic in `app/database/connector.py` that was double-appending database names.
- **Local Environment Support**: Corrected the `MONGODB_URI` in `.env` from Docker-specific `mongodb:27018` to `localhost:27017`.
- **Improved Logging**: Masked sensitive MongoDB credentials in the logs.

## Application Logic & Validation
- **Increased Processable Lengths**: Raised character limits in `app/services/cv_analyzer.py` and `app/main.py` to accommodate detailed resumes (CV: 25,000 chars, JD: 15,000 chars).
- **Refined AI Prompts**: Humanized and professionalized system prompts in `app/prompts/` by removing role-play "expert" fluff for more direct results.
- **Dependency Verification**: Confirmed presence and functionality of `bs4` and `lxml` for job scraping features.

## Documentation
- **Professionalized Tone**: Updated `README.md` and API descriptions to maintain a consistent, professional brand voice.

## CV Optimization Quality & Integrity (2025-12-31)
- **New High-Integrity Prompt**: Replaced `comprehensive_optimizer.md` with strict rules preventing data loss and hallucinations.
- **Automated Validation**: Created `CVValidator` class to check for missing contact info, hallucinated skills/languages, and data integrity.
- **Service Integration**: Integrated validation into `CVOptimizer.optimize_comprehensive()` with automatic error/warning logging.
- **Comprehensive Tests**: Added `tests/test_cv_optimization.py` with 8 test cases covering contact preservation, hallucination detection, and data integrity.
- **Validation Results**: Optimization responses now include `_validation` field with errors, warnings, and contact info comparison.
