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
