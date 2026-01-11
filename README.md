# PowerCV <img src="https://img.shields.io/badge/version-3.0.0--beta-blue" alt="Version 3.0.0-beta"/>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Beta](https://img.shields.io/badge/Status-Beta-orange)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-7.2.4-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

## Overview

PowerCV is a platform for resume customization that adapts professional profiles to specific job descriptions. Using natural language processing, it analyzes job requirements and highlights relevant skills and experiences to improve ATS compatibility and recruiter visibility.

**🎉 Latest Update (v3.0.0-beta)**: All critical application-breaking bugs have been resolved! The application now provides a complete, production-ready resume optimization experience with proper template selection, PDF generation, and professional file downloads.

## Key Features

- ** Resume Customization**: Tailors resume content to match job requirements using AI-powered analysis
- ** ATS Optimization**: Improves keyword alignment for applicant tracking systems with real-time scoring
- ** Gap Analysis**: Identifies missing skills based on job descriptions with visual analytics
- ** Resume Generation**: Produces formatted resumes in multiple professional templates
- ** Version Tracking**: Manages different resume versions for various applications
- ** Modern UI/UX**: Built with React 19 and TypeScript for optimal performance
- ** Real-time Updates**: Live resume editing with instant preview
- ** Responsive Design**: Mobile-first design for seamless cross-device experience
- ** Advanced Analytics**: Comprehensive resume performance tracking and insights
- ** Enterprise Security**: Production-ready security with environment validation

## Showcase

PowerCV features a comprehensive dashboard for resume management, detailed optimization analysis, and AI-assisted content generation.

## Technologies

### Frontend
- **Framework**: React 19.2.0 with TypeScript 5.0+
- **Build Tool**: Vite 7.2.4 for fast development and building
- **UI Library**: TailwindCSS with shadcn/ui components
- **State Management**: Zustand for lightweight state management
- **Data Fetching**: TanStack Query for server state management
- **Routing**: React Router DOM for navigation
- **HTTP Client**: Axios with interceptors for API communication
- **Testing**: Vitest with React Testing Library
- **Form Handling**: React Hook Form with Zod validation
- **Notifications**: Sonner for toast notifications

### Backend
- **Framework**: FastAPI, Python 3.8+
- **Database**: MongoDB with Pydantic models
- **AI Integration**: Deepseek API, Cerebras AI
- **PDF Engine**: Typst (Fast, modern Typesetting)
- **Authentication**: JWT-based auth system

### DevOps & Infrastructure
- **Containerization**: Docker with multi-stage builds
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Code Quality**: ESLint, Prettier, Ruff for linting
- **Security**: Snyk integration for vulnerability scanning
- **Monitoring**: Coverage reporting with Codecov
- **Package Management**: uv (Python), npm (Node.js)

> [!CAUTION]
> This application uses LLM models, which may generate unpredictable responses. Review AI-generated content before submission. The application is in beta.

## Quick Start

### 1. Start the Backend API

bash
# Navigate to project root
cd /home/illnar/Projects/PowerCV

# Start FastAPI backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

### 2. Start the Frontend Development Server

bash
# Open new terminal
cd /home/illnar/Projects/PowerCV/frontend

# Install dependencies
npm install

# Start development server
npm run dev

### 3. Access Your Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Environment Configuration

The app is pre-configured with environment files:
-.env - Local development
-.env.staging - Staging environment 
-.env.production - Production environment

Environment variables are automatically validated on startup.

## Installation and Setup

### Prerequisites

- **Backend**: Python 3.8+, MongoDB, Docker (for containerized deployment)
- **Frontend**: Node.js 20+, npm or yarn package manager
- **AI Services**: Deepseek/OpenAI/Cerebras.ai API key
- **PDF Generation**: Typst CLI (for PDF generation)
- **Development**: Git, VS Code (recommended)

### Setting Up Dependencies

#### Install uv

uv is a fast Python package manager:

bash
# Install uv using pip
pip install uv

# Or using the installer script
curl -LsSf https://astral.sh/uv/install.sh | sh

#### Setup MongoDB

1. **Using Docker**:

bash
docker run -d --name mongodb -p 27017:27017 mongo:latest

2. **Local Installation**:
 - [MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)
3. **MongoDB Atlas**:
 - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)

#### Setup AI Provider (Cerebras)

1. Get Cerebras API key from [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Add to your.env file (or pass as env vars):
 env
 CEREBRAS_API_KEY=your_key_here
 CEREBRAS_MODEL=gpt-oss-120b
 

### Environment Variables

 **Security Note**: Never commit.env files to version control. The.env file is already ignored by.gitignore.

1. Copy the environment template:
 bash
 cp env-template.txt.env
 

2. Fill in your actual values in.env:
 env
 # AI Provider (required)
 CEREBRAS_API_KEY=your_actual_cerebras_key

 # Database (required)
 MONGODB_URI=mongodb://username:password@host:port/powercv

 # Security (change in production!)
 SECRET_KEY=your_unique_secret_key

 # Other services (as needed)
 N8N_API_KEY=your_n8n_key
 SENTRY_DSN=your_sentry_dsn
 

3. All sensitive data should be stored in.env - never hardcoded in the codebase.

### CV Templates

PowerCV supports multiple professional CV templates:

| Template | Description | File | Status |
|----------|-------------|------|--------|
| **Classic** | Clean, traditional layout | resume.typ | Active |
| **Modern** | Contemporary two-column design | modern.typ | Active |
| **Brilliant CV** | Professional template with icons | brilliant-cv/cv.typ | Active |
| **good CV** | LaTeX-based simple design | good-cv/cv.tex | Template ready |
| **Simple XD** | Minimal ATS-friendly design | simple-xd-resume/cv.typ | Active |
| **RenderCV Classic** | Highly customizable classic design | rendercv-classic/cv.typ | Active |
| **RenderCV Modern** | Modern minimalist design | rendercv-modern/cv.typ | Active |

#### Template Selection

Choose your template during CV optimization:

json
POST /api/optimize-resume
{
 "cv_text": "Your CV content...",
 "jd_text": "Job description...",
 "template": "brilliant-cv/cv.typ",
 "generate_cover_letter": true
}

Available template options:
- "resume.typ" (default)
- "modern.typ"
- "brilliant-cv/cv.typ"
- "good-cv/cv.tex" (LaTeX support needed)
- "simple-xd-resume/cv.typ"
- "rendercv-classic/cv.typ"
- "rendercv-modern/cv.typ"

**Note**: good CV template requires LaTeX installation (xelatex) for PDF generation. Currently falls back to the default template.

### Using Docker

#### Prerequisites

Before running Docker containers, ensure you have the required environment variables set:

1. **Required for all containers**:
 bash
 # Copy and edit the template
 cp env-template.txt.env
 # Edit.env with your actual values
 

2. **For local development** (optional):
 bash
 # Copy development overrides (provides safe defaults)
 cp docker-compose.override.yml docker-compose.override.yml
 # Edit with your preferred development passwords/keys
 

#### Starting Services

Download the Docker image:

bash
docker pull ghcr.io/analyticace/myresumo:latest

Run the container:

bash
docker run -d --name myresumo \
 -p 8080:8080 \
 -e CEREBRAS_API_KEY=your_key_here \
 -e CEREBRAS_MODEL=gpt-oss-120b \
 -e MONGODB_URI=mongodb://username:password@host:port/ \
 ghcr.io/analyticace/myresumo:latest

## AI Models

PowerCV supports multiple AI backends.

### Configuration

### Configuration

PowerCV uses **Cerebras** for high-performance inference. Ensure CEREBRAS_API_KEY is set. Other providers (Deepseek, OpenAI) are supported, but Cerebras is the recommended default for speed.

### Cerebras AI Integration

PowerCV uses Cerebras AI for fast CV optimization (v2 endpoints).

#### Setup

1. Get Cerebras API key from [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Add to.env:
 env
 CEREBRAS_API_KEY=your_key_here
 CEREBRAS_MODEL=gpt-oss-120b
 

#### API Endpoints (v2)

- POST /api/v2/optimize - CV optimization workflow
- POST /api/v2/analyze - CV analysis
- POST /api/v2/cover-letter - Cover letter generation

#### Testing

bash
# Run integration tests
pytest app/tests/test_integration.py -v

# Run specific test
python app/tests/test_integration.py

Access the application at http://localhost:8080.

### Local Development

1. Clone the repository:

bash
git clone https://github.com/AnalyticAce/PowerCV.git
cd PowerCV

2. Create and activate a virtual environment:

bash
uv venv
source.venv/bin/activate

3. Install dependencies:

bash
uv pip install -r requirements.txt

4. Run development server:

bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

## API Documentation

Access the API documentation at:

- Interactive API docs: http://localhost:8080/docs
- OpenAPI specification: http://localhost:8080/openapi.json

## Testing

### Frontend Testing

bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

### Backend Testing

bash
# Run test suite
pytest tests/

# Run integration tests
pytest app/tests/test_integration.py -v

# Run specific test
python app/tests/test_integration.py

### CI/CD Testing

- **Automated Testing**: GitHub Actions runs tests on all pull requests
- **Coverage Reporting**: Codecov integration for coverage tracking
- **Security Scanning**: Snyk integration for vulnerability detection
- **Quality Gates**: Tests must pass before deployment

### Test Coverage

- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API endpoint testing
- **E2E Tests**: End-to-end user flow testing (planned)
- **Performance Tests**: Load testing and performance monitoring

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
 bash
 pip install ruff
 

2. Run the linter:
 bash
 ruff check.
 

3. Check formatting:
 bash
 ruff format --check.
 

4. Auto-format code:
 bash
 ruff format.
 

## Contributing

Please check the [contribution guidelines](CONTRIBUTING.md).

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.

## Roadmap

### **Current Position: Beta Testing Phase (v3.0.0-beta)**

> [!IMPORTANT]
> **PowerCV is currently in BETA testing phase.** We need human testing before production release. Please test thoroughly and report any issues.

### Completed Features (v3.0.0-beta)

- [x] **Modern Frontend Stack**: Migrated from Alpine.js to React 19 + TypeScript
- [x] **Advanced UI/UX**: Built with TailwindCSS and shadcn/ui components
- [x] **Real-time Updates**: Live resume editing with instant preview
- [x] **Comprehensive Testing**: Unit and integration tests with Vitest
- [x] **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- [x] **Environment Management**: Multi-environment configuration with validation
- [x] **Security Integration**: Automated security scanning and vulnerability detection
- [x] **Performance Monitoring**: Coverage reporting and quality gates
- [x] **Mobile Responsive**: Cross-device compatible design
- [x] **Advanced Analytics**: Resume performance tracking and insights

### **Current Development Phase**

**Status**: **Beta Testing - Human Validation Required**

- [ ] **User Testing**: Real-world user feedback collection
- [ ] **Bug Fixes**: Address issues found during beta testing
- [ ] **Performance Optimization**: Improve based on user testing
- [ ] **Documentation Updates**: Refine based on user feedback

### **Planned Features (Post-Beta)**

- [ ] **Multi-language Support**: Internationalization (i18n) implementation
- [ ] **Advanced AI Features**: Enhanced resume analysis with ML models
- [ ] **Collaboration Tools**: Real-time collaborative editing
- [ ] **Export Options**: Additional format support (DOCX, HTML)
- [ ] **Resume Analytics Dashboard**: Advanced metrics and visualization
- [ ] **AI Interview Coach**: Interview preparation suggestions
- [ ] **Job Platform Integration**: Direct integration with LinkedIn, Indeed
- [ ] **Cover Letter Templates**: Professional template library
- [ ] **Skill Assessment**: Automated skill gap analysis
- [ ] **Resume A/B Testing**: Performance comparison tools
- [ ] **API Rate Limiting**: Enhanced API management
- [ ] **User Authentication**: OAuth integration (Google, GitHub)
- [ ] **Team Collaboration**: Multi-user workspace features
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Browser Extension**: Quick resume optimization from job sites
- [ ] **PDF Parsing**: Advanced PDF extraction and analysis
- [ ] **Resume Templates**: Expanded template marketplace
- [ ] **Custom Branding**: Personal branding tools
- [ ] **Email Integration**: Automated follow-up reminders

### **Next Milestone: Production Release (v3.0.0)**

**Requirements for Production:**
- [ ] Complete beta testing with at least 50 human users
- [ ] Fix all critical bugs found during testing
- [ ] Achieve 95%+ test coverage
- [ ] Complete security audit
- [ ] Finalize production documentation

**Target Release Date**: After successful beta testing completion

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Ilnar Nizametdinov** - [LinkedIn](https://www.linkedin.com/in/illnar/) - [GitHub](https://github.com/ILLnar-Nizami)

Project Link: [https://github.com/ILLnar-Nizami/PowerCV](https://github.com/ILLnar-Nizami/PowerCV)
