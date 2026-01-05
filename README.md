# PowerCV <img src="https://img.shields.io/badge/version-2.0.0-blue" alt="Version 2.0.0"/>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Beta](https://img.shields.io/badge/Status-Beta-orange)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

## Overview

PowerCV is a platform for resume customization that adapts professional profiles to specific job descriptions. Using natural language processing, it analyzes job requirements and highlights relevant skills and experiences to improve ATS compatibility and recruiter visibility.

## Key Features

- **Resume Customization**: Tailors resume content to match job requirements.
- **ATS Optimization**: Improves keyword alignment for applicant tracking systems.
- **Gap Analysis**: Identifies missing skills based on job descriptions.
- **Resume Generation**: Produces formatted resumes in multiple formats.
- **Version Tracking**: Manages different resume versions for various applications.

## Showcase

PowerCV features a comprehensive dashboard for resume management, detailed optimization analysis, and AI-assisted content generation.


## Technologies

- **Backend**: FastAPI, Python 3.8+
- **Database**: MongoDB
- **Frontend**: Jinja2 templates, Alpine.js, HTML/CSS
- **PDF Engine**: Typst (Fast, modern Typesetting)
- **AI Integration**: Deepseek API, Cerebras
- **Deployment**: Docker
- **Package Management**: uv

> [!CAUTION]
> This application uses LLM models which may generate unpredictable responses. Review AI-generated content before submission. The application is in beta.

## Installation and Setup

### Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- MongoDB
- Typst CLI (for PDF generation)
- Deepseek API key

### Setting Up Dependencies

#### Install uv

uv is a fast Python package manager:

```bash
# Install uv using pip
pip install uv

# Or using the installer script
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Setup MongoDB

1. **Using Docker**:

```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

2. **Local Installation**:
 - [MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)
3. **MongoDB Atlas**:
 - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)

#### Setup AI Provider (Cerebras)

1. Get Cerebras API key from [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Add to your `.env` file (or pass as env vars):
   ```env
   CEREBRAS_API_KEY=your_key_here
   CEREBRAS_MODEL=gpt-oss-120b
   ```

### Environment Variables

⚠️ **Security Note**: Never commit `.env` files to version control. The `.env` file is already ignored by `.gitignore`.

1. Copy the environment template:
   ```bash
   cp env-template.txt .env
   ```

2. Fill in your actual values in `.env`:
   ```env
   # AI Provider (required)
   CEREBRAS_API_KEY=your_actual_cerebras_key

   # Database (required)
   MONGODB_URI=mongodb://username:password@host:port/powercv

   # Security (change in production!)
   SECRET_KEY=your_unique_secret_key

   # Other services (as needed)
   N8N_API_KEY=your_n8n_key
   SENTRY_DSN=your_sentry_dsn
   ```

3. All sensitive data should be stored in `.env` - never hardcoded in the codebase.

### CV Templates

PowerCV supports multiple professional CV templates:

| Template | Description | File | Status |
|----------|-------------|------|--------|
| **Classic** | Clean, traditional layout | `resume.typ` | ✅ Active |
| **Modern** | Contemporary two-column design | `modern.typ` | ✅ Active |
| **Brilliant CV** | Professional template with icons | `brilliant-cv/cv.typ` | ✅ Active |
| **Awesome CV** | LaTeX-based elegant design | `awesome-cv/cv.tex` | 🔄 Template ready, LaTeX compilation pending |
| **Simple XD** | Minimal ATS-friendly design | `simple-xd-resume/cv.typ` | ✅ Active |

#### Template Selection

Choose your template during CV optimization:

```json
POST /api/optimize-resume
{
  "cv_text": "Your CV content...",
  "jd_text": "Job description...",
  "template": "brilliant-cv/cv.typ",
  "generate_cover_letter": true
}
```

Available template options:
- `"resume.typ"` (default)
- `"modern.typ"`
- `"brilliant-cv/cv.typ"`
- `"awesome-cv/cv.tex"` (LaTeX support needed)
- `"simple-xd-resume/cv.typ"`

**Note**: Awesome CV template requires LaTeX installation (`xelatex`) for PDF generation. Currently falls back to default template.

### Using Docker

#### Prerequisites

Before running Docker containers, ensure you have the required environment variables set:

1. **Required for all containers**:
   ```bash
   # Copy and edit the template
   cp env-template.txt .env
   # Edit .env with your actual values
   ```

2. **For local development** (optional):
   ```bash
   # Copy development overrides (provides safe defaults)
   cp docker-compose.override.yml docker-compose.override.yml
   # Edit with your preferred development passwords/keys
   ```

#### Starting Services

Download the Docker image:

```bash
docker pull ghcr.io/analyticace/myresumo:latest
```

Run the container:

```bash
docker run -d --name myresumo \
 -p 8080:8080 \
 -e CEREBRAS_API_KEY=your_key_here \
 -e CEREBRAS_MODEL=gpt-oss-120b \
 -e MONGODB_URI=mongodb://username:password@host:port/ \
 ghcr.io/analyticace/myresumo:latest
```

## AI Models

PowerCV supports multiple AI backends.

### Configuration

### Configuration

PowerCV uses **Cerebras** for high-performance inference. Ensure `CEREBRAS_API_KEY` is set. Other providers (Deepseek, OpenAI) are supported but Cerebras is the recommended default for speed.

### Cerebras AI Integration

PowerCV uses Cerebras AI for fast CV optimization (v2 endpoints).

#### Setup

1. Get Cerebras API key from [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Add to .env:
   ```env
   CEREBRAS_API_KEY=your_key_here
   CEREBRAS_MODEL=gpt-oss-120b
   ```

#### API Endpoints (v2)

- POST /api/v2/optimize - CV optimization workflow
- POST /api/v2/analyze - CV analysis
- POST /api/v2/cover-letter - Cover letter generation

#### Testing

```bash
# Run integration tests
pytest app/tests/test_integration.py -v

# Run specific test
python app/tests/test_integration.py
```

Access the application at http://localhost:8080.

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/AnalyticAce/PowerCV.git
cd PowerCV
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
uv pip install -r requirements.txt
```

4. Run development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## API Documentation

Access the API documentation at:

- Interactive API docs: http://localhost:8080/docs
- OpenAPI specification: http://localhost:8080/openapi.json

## Testing

Run the test suite:

```bash
pytest tests/
```

## Usage Guide

1. **Upload Resume**: Submit resume in PDF or DOCX format.
2. **Add Job Description**: Provide the job description text.
3. **Generate Resume**: Analyze and customize resume content.
4. **Review**: Edit generated content as needed.
5. **Export**: Download the optimized resume.

## Code Quality

### Linting

This project uses [Ruff](https://github.com/charliermarsh/ruff) for code linting and formatting.

#### CI Linting

GitHub Actions runs Ruff on all Python files.

#### Local Linting

1. Install Ruff:
   ```bash
   pip install ruff
   ```

2. Run the linter:
   ```bash
   ruff check .
   ```

3. Check formatting:
   ```bash
   ruff format --check .
   ```

4. Auto-format code:
   ```bash
   ruff format .
   ```

## Contributing

Please check the [contribution guidelines](CONTRIBUTING.md).

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.

## Roadmap

- [ ] Multi-language support
- [ ] Resume analytics dashboard
- [ ] Resume advice through conversational AI
- [ ] Interview preparation suggestions
- [ ] Cover letter generation
- [ ] Integration with job search platforms
- [ ] PDF parsing and extraction

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Ilnar Nizametdinov** - [LinkedIn](https://www.linkedin.com/in/illnar/) - [GitHub](https://github.com/ILLnar-Nizami)

Project Link: [https://github.com/ILLnar-Nizami/PowerCV](https://github.com/ILLnar-Nizami/PowerCV)
