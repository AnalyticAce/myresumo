# PowerCV n8n Integration

This directory contains n8n workflow templates and instructions for integrating PowerCV with n8n automation. The workflows enable automated CV analysis, optimization, batch processing, error handling, and cover letter generation through a visual interface.

## Quick Start

1. **Access n8n**: Open http://localhost:5678 in your browser
2. **Login**: Use credentials from.env file (admin/secure_n8n_password_123!)
3. **Import Workflow**: Either create a new workflow from scratch using the instructions below, or import the provided JSON workflow files directly

## Available Workflow Templates

This directory includes four production-ready n8n workflow templates designed for different automation scenarios. Each workflow is self-contained and can be imported directly into n8n.

### 1. Basic Optimization Workflow (03_basic_optimization.json)

This workflow provides a streamlined CV optimization pipeline that accepts CV text and job description, analyzes match quality, and returns optimization recommendations. It is ideal for single-user interactions and straightforward optimization tasks.

**Key Features:**
- Accepts CV and job description via webhook
- Calls the PowerCV analyze endpoint to score ATS compatibility
- Generates keyword recommendations
- Returns structured optimization feedback

**Webhook Payload Example:**
json
{
 "cv_text": "Experienced Python developer with Django and FastAPI expertise...",
 "jd_text": "Looking for a Senior Python Developer with FastAPI experience...",
 "user_id": "candidate_001"
}

### 2. Batch Processor Workflow (04_batch_processor.json)

This workflow handles bulk CV processing for scenarios where multiple candidates or multiple job positions need to be processed simultaneously. It includes progress tracking, error aggregation, and comprehensive reporting.

**Key Features:**
- Processes multiple CVs in a single execution
- Supports both array inputs and single-item processing
- Tracks processing status and generates completion reports
- Handles partial failures gracefully without interrupting entire batch
- Returns detailed results for each processed item

**Webhook Payload Example:**
json
{
 "batch": [
 {"cv_text": "Candidate 1 resume...", "jd_text": "Job description...", "user_id": "user_1"},
 {"cv_text": "Candidate 2 resume...", "jd_text": "Job description...", "user_id": "user_2"}
 ],
 "generate_reports": true
}

### 3. Error Handler Workflow (05_error_handler.json)

This workflow implements reliable error handling patterns for production deployments. It catches failures, logs detailed error information, implements retry logic with exponential backoff, and provides graceful degradation.

**Key Features:**
- Catches and categorizes errors from API calls
- Implements retry logic with configurable attempts and delays
- Logs detailed error information for debugging
- Provides fallback responses when primary services fail
- Tracks error metrics for monitoring

**Use Case:** Ideal as a wrapper around other workflows or for critical automation paths where reliability is paramount.

### 4. Cover Letter Generator Workflow (06_cover_letter_generator.json)

This workflow focuses on generating personalized cover letters by analyzing both the candidate's CV and the target job description. It extracts key qualifications, matches them to job requirements, and produces compelling narrative content.

**Key Features:**
- Analyzes CV to extract key skills and experiences
- Parses job description for requirements and preferences
- Generates personalized cover letter content
- Supports multiple tone options (professional, conversational, technical)
- Returns both plain text and formatted versions

**Webhook Payload Example:**
json
{
 "cv_text": "Full-stack developer with React and Node.js experience...",
 "jd_text": "Seeking a Full-stack Developer to join our product team...",
 "user_id": "applicant_042",
 "tone": "professional",
 "focus_points": ["leadership experience", "team collaboration"]
}

## Workflow Setup

### Manual Configuration

#### Basic CV Analysis Workflow

1. **Webhook Node**
 - Trigger: Webhook
 - HTTP Method: POST
 - Path: cv-analysis
 - Response Mode: Respond immediately

2. **HTTP Request Node** (Analyze CV)
 - URL: http://powercv-api:8080/api/n8n/analyze
 - Method: POST
 - Authentication: Header Auth
 - Headers:
 - X-API-Key: n8n_sec_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
 - Content-Type: application/json
 - Body JSON:
 json
 {
 "cv_text": "={{ $json.body.cv_text }}",
 "jd_text": "={{ $json.body.jd_text }}",
 "user_id": "={{ $json.body.user_id || 'n8n_workflow' }}"
 }
 

3. **Respond to Webhook Node**
 - Respond with: JSON
 - Response Body: {{ $node['Analyze CV'].json }}

#### Full CV Optimization Workflow

Add these nodes after the analysis:

4. **If Node** (Check Success)
 - Condition: {{ $node['Analyze CV'].json.success }} == true

5. **HTTP Request Node** (Optimize CV)
 - URL: http://powercv-api:8080/api/n8n/optimize
 - Same authentication as analyze
 - Body JSON:
 json
 {
 "cv_text": "={{ $node['Webhook'].json.body.cv_text }}",
 "jd_text": "={{ $node['Webhook'].json.body.jd_text }}",
 "user_id": "={{ $node['Webhook'].json.body.user_id || 'n8n_workflow' }}",
 "generate_cover_letter": "={{ $node['Webhook'].json.body.generate_cover_letter || true }}"
 }
 

6. **Respond to Webhook Node** (Success)
 - Response Body: {{ $node['Optimize CV'].json }}

7. **Respond to Webhook Node** (Error)
 - Response Body:
 json
 {
 "success": false,
 "error": "CV analysis failed",
 "details": "={{ $node['Analyze CV'].json }}"
 }
 

## API Endpoints Reference

### PowerCV n8n API

All endpoints require the API key header: X-API-Key: n8n_sec_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

### API Endpoints Available

- **Health Check**: GET /api/n8n/health
- **Analyze CV**: POST /api/n8n/analyze
- **Optimize CV**: POST /api/n8n/optimize
- **List Providers**: GET /api/n8n/providers (Cerebras only)
- **Scrape Job**: POST /api/v1/scrape
- **Structured Optimize**: POST /api/v1/optimize-structured

### Request/Response Examples

#### Analyze CV Request

json
{
 "cv_text": "Python Developer with 5 years experience...",
 "jd_text": "Looking for a Senior Python Developer...",
 "user_id": "test_user"
}

#### Analyze CV Response

json
{
 "success": true,
 "ats_score": 90,
 "matched_keywords": ["Python", "FastAPI", "Docker"],
 "missing_keywords": ["AWS", "Kubernetes"],
 "top_recommendations": ["Add AWS experience to skills section", "Highlight Kubernetes project involvement"],
 "user_id": "test_user"
}

#### Optimize CV Request

json
{
 "cv_text": "Python Developer with 5 years experience...",
 "jd_text": "Looking for a Senior Python Developer...",
 "user_id": "test_user",
 "generate_cover_letter": true
}

#### Scrape Job Request

json
{
 "url": "https://jobs.example.com/position/12345",
 "extract_company": true
}

## Docker Services

- **PowerCV API**: http://localhost:8080
- **n8n Interface**: http://localhost:5678
- **MongoDB**: mongodb://localhost:27018/powercv

## Environment Variables

Key variables for n8n integration (in.env):
- N8N_API_KEY: API key for authenticating n8n requests
- N8N_USER: n8n admin username
- N8N_PASSWORD: n8n admin password
- AI_PROVIDER: Current AI provider (cerebras)
- MONGODB_URI: MongoDB connection string
- CEREBRAS_API_KEY: API key for Cerebras LLM service

## Testing

Use curl to test endpoints directly:

bash
# Health check
curl -H "X-API-Key: n8n_sec_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2" \
 http://localhost:8080/api/n8n/health

# Analyze CV
curl -X POST -H "Content-Type: application/json" \
 -H "X-API-Key: n8n_sec_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2" \
 -d '{"cv_text":"Python Developer...","jd_text":"Looking for...","user_id":"test"}' \
 http://localhost:8080/api/n8n/analyze

# Scrape job posting
curl -X POST -H "Content-Type: application/json" \
 -H "X-API-Key: n8n_sec_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2" \
 -d '{"url":"https://example.com/job/12345","extract_company":true}' \
 http://localhost:8080/api/v1/scrape

## Workflow Best Practices

### Error Handling

Always implement error handling in production workflows. Use the Error Handler workflow (05_error_handler.json) as a reference pattern. Key considerations include:

- Set appropriate timeout values for HTTP requests (60 seconds recommended)
- Configure retry logic for transient failures (3 attempts with exponential backoff)
- Log errors with sufficient context for debugging
- Return meaningful error messages to webhook callers

### Rate Limiting

Be mindful of API rate limits when running batch operations. The Batch Processor workflow (04_batch_processor.json) includes built-in rate limiting. For custom implementations:

- Add delay nodes between API calls (1-2 seconds recommended)
- Monitor response headers for rate limit indicators
- Implement backoff strategies when limits are approached

### Security

- Never commit API keys to version control
- Use environment variables for sensitive credentials
- Rotate API keys periodically
- Restrict webhook URLs to authorized systems
- Implement request validation before processing

## Monitoring and Maintenance

### Health Checks

The PowerCV API exposes a health check endpoint at /api/n8n/health. Configure n8n to monitor this endpoint and alert on failures. Sample monitoring configuration:

yaml
health_check:
 endpoint: http://powercv-api:8080/api/n8n/health
 interval: 30s
 timeout: 5s
 retries: 3

### Logging

Access logs through the n8n execution history. For persistent logging:

- Configure n8n to send execution logs to external systems
- Use the error workflow to capture and forward critical errors
- Set up alerts for repeated failures

### Performance Optimization

- Use n8n's built-in caching for repeated API calls
- Batch multiple operations where possible
- Optimize webhook response payloads to minimize bandwidth
- Monitor n8n instance resources and scale as needed
