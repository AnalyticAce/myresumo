# PowerCV <img src="https://img.shields.io/badge/version-2.0.0-blue" alt="Version 2.0.0"/>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Beta](https://img.shields.io/badge/Status-Beta-orange)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-8A2BE2?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTIgMmEyIDIgMCAwIDAgLTIgMnY3YTIgMiAwIDAgMCA0IDB2LTdhMiAyIDAgMCAwIC0yIC0yeiI+PC9wYXRoPjxwYXRoIGQ9Ik0yIDEyYTIgMiAwIDAgMCAtMiAydjdhMiAyIDAgMCAwIDQgMHYtN2EyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PHBhdGggZD0iTTIyIDEyYTIgMiAwIDAgMCAtMiAydjdhMiAyIDAgMCAwIDQgMHYtN2EyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PHBhdGggZD0iTTEyIDEyYTIgMiAwIDAgMCAtMiAydjdhMiAyIDAgMCAwIDQgMHYtN2EyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PHBhdGggZD0iTTYgNmEyIDIgMCAwIDAgLTIgMnYyYTIgMiAwIDAgMCA0IDB2LTJhMiAyIDAgMCAwIC0yIC0yeiI+PC9wYXRoPjxwYXRoIGQ9Ik0xOCA2YTIgMiAwIDAgMCAtMiAydjJhMiAyIDAgMCAwIDQgMHYtMmEyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PC9zdmc+)](https://github.com/AnalyticAce/PowerCV)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-009688)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-47A248)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-8A2BE2)](https://github.com/AnalyticAce/PowerCV)
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

Screenshots of the main features:
<div align="center">

### Landing Page
The landing page introduces the resume optimization service and the benefits of tailoring resumes for specific applications.

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/landing-page.png" alt="PowerCV Landing Page"/>

### Dashboard
The dashboard provides an overview of resumes, ATS scores, and management tools.

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/dashboard.png" alt="PowerCV Dashboard"/>

### Resume Optimization
The optimization page compares resumes against job descriptions, providing feedback on keywords and skills.

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/optimized1.png" alt="Resume Optimization"/>

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/optimized2.png" alt="Resume Optimization"/>

### Resume Creation
The interface for building resumes with AI assistance for ATS and recruiter review.

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/creation.png" alt="Resume Creation"/>

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/result.png" alt="Resume Result"/>

### Resume View
The resume view page displays the generated resume in a professional format.

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/resume_view.png" alt="Resume View"/>

<img src="https://github.com/AnalyticAce/PowerCV/blob/main/.github/assets/resume_view2.png" alt="Resume View"/>

</div>

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

#### Get Deepseek API Key

1. Sign up at [Deepseek Platform](https://platform.deepseek.com/)
2. Generate an API key in the dashboard.

### Environment Variables

Create a .env file in the project root:

```
API_KEY=your_api_key_here
MONGODB_URI=mongodb://username:password@host:port/
```

### Using Docker

Download the Docker image:

```bash
docker pull ghcr.io/analyticace/myresumo:latest
```

Run the container:

```bash
docker run -d --name myresumo \
 -p 8080:8080 \
 -e API_KEY=your_api_key_here \
 -e API_BASE=https://api.deepseek.com/v1 \
 -e MODEL_NAME=deepseek-chat \
 -e MONGODB_URI=mongodb://username:password@host:port/ \
 ghcr.io/analyticace/myresumo:latest
```

## AI Models

PowerCV supports multiple AI backends.

### Configuration

Switch between providers by updating environment variables:

```bash
# For Deepseek (default)
API_KEY=your_deepseek_api_key
API_BASE=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# For OpenAI
API_KEY=your_openai_api_key
API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

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

**DOSSEH Shalom** - [LinkedIn](https://www.linkedin.com/in/shalom-dosseh-4a484a262) - [GitHub](https://github.com/AnalyticAce)

Project Link: [https://github.com/AnalyticAce/PowerCV](https://github.com/AnalyticAce/PowerCV)
