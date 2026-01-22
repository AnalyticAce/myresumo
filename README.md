# MyResumo <img src="https://img.shields.io/badge/version-2.0.0-blue" alt="Version 2.0.0"/>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Beta](https://img.shields.io/badge/Status-Beta-orange)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-8A2BE2?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTIgMmEyIDIgMCAwIDAgLTIgMnY3YTIgMiAwIDAgMCA0IDB2LTdhMiAyIDAgMCAwIC0yIC0yeiI+PC9wYXRoPjxwYXRoIGQ9Ik0yIDEyYTIgMiAwIDAgMCAtMiAydjdhMiAyIDAgMCAwIDQgMHYtN2EyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PHBhdGggZD0iTTIyIDEyYTIgMiAwIDAgMCAtMiAydjdhMiAyIDAgMCAwIDQgMHYtN2EyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PHBhdGggZD0iTTEyIDEyYTIgMiAwIDAgMCAtMiAydjdhMiAyIDAgMCAwIDQgMHYtN2EyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PHBhdGggZD0iTTYgNmEyIDIgMCAwIDAgLTIgMnYyYTIgMiAwIDAgMCA0IDB2LTJhMiAyIDAgMCAwIC0yIC0yeiI+PC9wYXRoPjxwYXRoIGQ9Ik0xOCA2YTIgMiAwIDAgMCAtMiAydjJhMiAyIDAgMCAwIDQgMHYtMmEyIDIgMCAwIDAgLTIgLTJ6Ij48L3BhdGg+PC9zdmc+)](https://github.com/AnalyticAce/MyResumo)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

## 📋 Overview

**MyResumo** is an AI-powered resume customization platform that tailors your professional profile to match specific job descriptions. By leveraging advanced natural language processing, it analyzes job requirements and adapts your resume to highlight relevant skills and experiences, significantly improving your chances of passing through Applicant Tracking Systems (ATS) and catching recruiters' attention.

<!-- <div align="center">
  <img src="https://github.com/AnalyticAce/MyResumo/blob/develop/.github/assets/demo-screenshot.png" alt="MyResumo Screenshot" width="800"/>
</div> -->

## ✨ Key Features

- **AI-Powered Resume Customization**: Automatically tailors your resume content to match job requirements
- **ATS Optimization**: Enhances keyword matching for better visibility in applicant tracking systems
- **Skills Gap Analysis**: Identifies missing skills based on job descriptions
- **Resume Generation**: Creates formatted, professional resumes in multiple formats
- **Version Management**: Track different versions of your resume for various applications

## 🖼️ Showcase

Below are screenshots showcasing the main features of MyResumo:
<div align="center">

### Landing Page
The landing page introduces users to the AI-powered resume optimization service, highlighting the key benefits of using MyResumo to tailor resumes for specific job applications.

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/landing-page.png" alt="MyResumo Landing Page"/>

### Dashboard
The user dashboard provides an overview of all your resumes, including ATS scores, last update dates, and quick access to actions like viewing, editing, downloading, or deleting each resume.

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/dashboard.png" alt="MyResumo Dashboard"/>

### Resume Optimization
The resume optimization page analyzes your resume against job descriptions, providing detailed feedback on missing keywords, skills, and suggestions for improvement.

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/optimized1.png" alt="Resume Optimization"/>

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/optimized2.png" alt="Resume Optimization"/>

### Resume Creation
The intuitive resume creation interface allows you to build professional resumes with AI assistance, ensuring they're optimized for both ATS systems and human reviewers.

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/creation.png" alt="Resume Creation"/>

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/result.png" alt="Resume Result"/>

### Resume View
The resume view page displays the generated resume in a clean, professional format, ready for download.

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/resume_view.png" alt="Resume View"/>

<img src="https://github.com/AnalyticAce/MyResumo/blob/main/.github/assets/resume_view2.png" alt="Resume View"/>

</div>

## 🚀 Technologies

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), Python 3.8+
- **Database**: MongoDB
- **Frontend**: Jinja2 templates, Alpine.js, HTML/CSS
- **AI Integration**: Deepseek API
- **Deployment**: Docker
- **Package Management**: uv

> [!CAUTION]
> This application utilizes LLM models which may generate unpredictable responses. Always review and verify AI-generated content before submitting to potential employers. The application is currently in beta, with ongoing improvements to the prompt engineering and output quality.

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- MongoDB instance (local or remote)
- Deepseek API key

### Setting Up Dependencies

#### Install uv (Fast Python Package Manager)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver:

```bash
# Install uv using pip
pip install uv

# Or using the recommended installer script
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Setup MongoDB

Options for MongoDB setup:

1. **Using Docker** (recommended for development):

```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

2. **Local Installation**:

   - [MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)
3. **MongoDB Atlas** (Cloud Hosted):

   - [Sign up for MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
   - Create a free tier cluster
   - Get your connection string from the dashboard

#### Get Deepseek API Key

1. Sign up at [Deepseek Platform](https://platform.deepseek.com/)
2. Navigate to API section and generate a new key
3. Save your API key securely for the next step

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
API_KEY=your_api_key_here
MONGODB_URI=mongodb://username:password@host:port/
```

### Using Official Docker Image (Recommended)

The fastest way to get started is to use our official Docker image:

```bash
docker pull ghcr.io/analyticace/myresumo:latest
```

Run the container with your environment variables:

```bash
docker run -d --name myresumo \
  -p 8080:8080 \
  -e API_KEY=your_api_key_here \
  -e API_BASE=https://api.deepseek.com/v1 \
  -e MODEL_NAME=deepseek-chat \
  -e MONGODB_URI=mongodb://username:password@host:port/ \
  ghcr.io/analyticace/myresumo:latest
```

## Alternative AI Models

MyResumo supports multiple AI backends to power its resume customization features:

### Environment Variable Configuration

You can easily switch between different AI providers by configuring these environment variables:

```bash
# For Deepseek (default)
API_KEY=your_deepseek_api_key
API_BASE=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# For OpenAI
API_KEY=your_openai_api_key
API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# For other providers, configure accordingly
```

When running the Docker container, simply pass these environment variables:

```bash
docker run -d --name myresumo \
   -p 8080:8080 \
   -e API_KEY=your_api_key_here \
   -e API_BASE=your_provider_base_url \
   -e MODEL_NAME=your_preferred_model \
   -e MONGODB_URI=mongodb://username:password@host:port/ \
   ghcr.io/analyticace/myresumo:latest
```

Access the application at `http://localhost:8080`

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/AnalyticAce/MyResumo.git
cd MyResumo
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:

```bash
uv pip install -r requirements.txt
```

4. Run development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

5. Access the application at `http://localhost:8080`

## 📚 API Documentation

Once the application is running, access the API documentation at:

- Interactive API docs: `http://localhost:8080/docs`
- OpenAPI specification: `http://localhost:8080/openapi.json`

## 🧪 Testing

Run the test suite with:

```bash
pytest tests/
```

## 📖 Usage Guide

1. **Upload Your Resume**: Submit your existing resume in PDF or DOCX format
2. **Add Job Description**: Paste the job description or upload it as a text file
3. **Generate Tailored Resume**: Let AI analyze and customize your resume
4. **Review and Edit**: Make any final adjustments to the generated content
5. **Export**: Download your optimized resume in your preferred format

## Code Quality

### Linting

This project uses [Ruff](https://github.com/charliermarsh/ruff) for code linting and formatting. Ruff is a fast Python linter written in Rust that helps maintain consistent code quality across the project.

#### CI Linting

Our GitHub Actions workflow automatically runs Ruff on all Python files whenever code is pushed or a pull request is created. The workflow:
- Checks code against our style rules
- Verifies code formatting
- Reports any issues directly in the PR or commit

#### Local Linting

To run the linter locally:

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

Our configuration (in `pyproject.toml`) enforces:
- Google-style docstrings
- Import sorting
- Standard Python code style conventions

## 🤝 Contributing

Contributions are welcome! Please check the [contribution guidelines](CONTRIBUTING.md) for more details.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Contact

**DOSSEH Shalom** - [LinkedIn](https://www.linkedin.com/in/shalom-dosseh-4a484a262)
