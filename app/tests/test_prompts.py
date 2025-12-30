# PowerCV Prompt Testing Framework
# For Cerebras AI API Integration

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PromptType(Enum):
    ANALYZER = "analyzer"
    OPTIMIZER = "optimizer"
    COVER_LETTER = "cover_letter"


@dataclass
class TestResult:
    prompt_type: PromptType
    success: bool
    response_time: float
    response_length: int
    errors: List[str]
    warnings: List[str]
    quality_score: float
    output: str


class CerebrasPromptTester:
    """Test and validate Cerebras AI prompt responses for PowerCV"""
    
    def __init__(self, api_key: str, api_base: str, model: str):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.test_results = []
    
    def load_prompts(self) -> Dict[PromptType, str]:
        """Load system prompts from files"""
        return {
            PromptType.ANALYZER: self._load_prompt_file("prompts/cv_analyzer.md"),
            PromptType.OPTIMIZER: self._load_prompt_file("prompts/cv_optimizer.md"),
            PromptType.COVER_LETTER: self._load_prompt_file("prompts/cover_letter.md"),
        }
    
    def _load_prompt_file(self, filepath: str) -> str:
        """Load prompt from markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
    
    def test_analyzer_prompt(
        self,
        cv_text: str,
        jd_text: str,
        system_prompt: str
    ) -> TestResult:
        """Test CV Analyzer prompt"""
        start_time = time.time()
        errors = []
        warnings = []
        
        # Build user message
        user_message = f"""
**JOB DESCRIPTION:**
{jd_text}

**CANDIDATE CV:**
{cv_text}
"""
        
        # Call API
        try:
            response = self._call_cerebras_api(system_prompt, user_message)
            response_time = time.time() - start_time
            
            # Validate response
            validation_result = self._validate_analyzer_response(response)
            errors.extend(validation_result['errors'])
            warnings.extend(validation_result['warnings'])
            
            quality_score = self._calculate_quality_score(
                validation_result, 
                response_time,
                len(response)
            )
            
            return TestResult(
                prompt_type=PromptType.ANALYZER,
                success=len(errors) == 0,
                response_time=response_time,
                response_length=len(response),
                errors=errors,
                warnings=warnings,
                quality_score=quality_score,
                output=response
            )
            
        except Exception as e:
            return TestResult(
                prompt_type=PromptType.ANALYZER,
                success=False,
                response_time=time.time() - start_time,
                response_length=0,
                errors=[f"API Error: {str(e)}"],
                warnings=[],
                quality_score=0.0,
                output=""
            )
    
    def test_optimizer_prompt(
        self,
        original_section: str,
        jd_text: str,
        focus_keywords: List[str],
        system_prompt: str
    ) -> TestResult:
        """Test CV Optimizer prompt"""
        start_time = time.time()
        errors = []
        warnings = []
        
        user_message = f"""
**TARGET JOB DESCRIPTION:**
{jd_text}

**ORIGINAL CV SECTION:**
{original_section}

**OPTIMIZATION FOCUS:**
Emphasize technical keywords, quantify achievements, improve STAR structure

**MUST-INCLUDE KEYWORDS:**
{', '.join(focus_keywords)}
"""
        
        try:
            response = self._call_cerebras_api(system_prompt, user_message)
            response_time = time.time() - start_time
            
            validation_result = self._validate_optimizer_response(
                response, 
                focus_keywords
            )
            errors.extend(validation_result['errors'])
            warnings.extend(validation_result['warnings'])
            
            quality_score = self._calculate_quality_score(
                validation_result,
                response_time,
                len(response)
            )
            
            return TestResult(
                prompt_type=PromptType.OPTIMIZER,
                success=len(errors) == 0,
                response_time=response_time,
                response_length=len(response),
                errors=errors,
                warnings=warnings,
                quality_score=quality_score,
                output=response
            )
            
        except Exception as e:
            return TestResult(
                prompt_type=PromptType.OPTIMIZER,
                success=False,
                response_time=time.time() - start_time,
                response_length=0,
                errors=[f"API Error: {str(e)}"],
                warnings=[],
                quality_score=0.0,
                output=""
            )
    
    def test_cover_letter_prompt(
        self,
        candidate_data: Dict,
        job_data: Dict,
        system_prompt: str
    ) -> TestResult:
        """Test Cover Letter Generator prompt"""
        start_time = time.time()
        errors = []
        warnings = []
        
        user_message = f"""
**JOB DETAILS:**
- Company: {job_data['company']}
- Position: {job_data['position']}
- Location: {job_data['location']}
- Key Requirements: {', '.join(job_data['requirements'])}

**CANDIDATE PROFILE:**
- Name: {candidate_data['name']}
- Current Title: {candidate_data['current_title']}
- Location: {candidate_data['location']}
- Years of Experience: {candidate_data['years_exp']}
- Top 3 Technical Skills: {', '.join(candidate_data['top_skills'])}
- Top 3 Achievements: {chr(10).join(f"  • {a}" for a in candidate_data['achievements'])}

**TONE PREFERENCE:**
Professional
"""
        
        try:
            response = self._call_cerebras_api(system_prompt, user_message)
            response_time = time.time() - start_time
            
            validation_result = self._validate_cover_letter_response(response)
            errors.extend(validation_result['errors'])
            warnings.extend(validation_result['warnings'])
            
            quality_score = self._calculate_quality_score(
                validation_result,
                response_time,
                len(response)
            )
            
            return TestResult(
                prompt_type=PromptType.COVER_LETTER,
                success=len(errors) == 0,
                response_time=response_time,
                response_length=len(response),
                errors=errors,
                warnings=warnings,
                quality_score=quality_score,
                output=response
            )
            
        except Exception as e:
            return TestResult(
                prompt_type=PromptType.COVER_LETTER,
                success=False,
                response_time=time.time() - start_time,
                response_length=0,
                errors=[f"API Error: {str(e)}"],
                warnings=[],
                quality_score=0.0,
                output=""
            )
    
    def _call_cerebras_api(self, system_prompt: str, user_message: str) -> str:
        """Call Cerebras API (stub - implement with actual API client)"""
        # TODO: Replace with actual Cerebras API call integration test
        # Example using requests:
        # import requests
        # response = requests.post(
        #     f"{self.api_base}/chat/completions",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     json={
        #         "model": self.model,
        #         "messages": [
        #             {"role": "system", "content": system_prompt},
        #             {"role": "user", "content": user_message}
        #         ],
        #         "temperature": 0.7,
        #         "max_tokens": 2000
        #     }
        # )
        # return response.json()['choices'][0]['message']['content']
        
        raise NotImplementedError("Implement Cerebras API call here")
    
    def _validate_analyzer_response(self, response: str) -> Dict:
        """Validate analyzer JSON output"""
        errors = []
        warnings = []
        
        # Check if response is JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            errors.append("Response is not valid JSON")
            return {'errors': errors, 'warnings': warnings}
        
        # Check required fields
        required_fields = [
            'ats_score',
            'summary',
            'keyword_analysis',
            'experience_analysis',
            'skill_gaps',
            'strengths',
            'optimization_priorities',
            'recommendations'
        ]
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate ats_score range
        if 'ats_score' in data:
            if not (0 <= data['ats_score'] <= 100):
                errors.append(f"Invalid ats_score: {data['ats_score']} (must be 0-100)")
        
        # Validate array lengths
        if 'strengths' in data and len(data['strengths']) < 3:
            warnings.append("Less than 3 strengths identified")
        
        if 'recommendations' in data and len(data['recommendations']) < 3:
            warnings.append("Less than 3 recommendations provided")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_optimizer_response(
        self, 
        response: str, 
        required_keywords: List[str]
    ) -> Dict:
        """Validate optimizer output"""
        errors = []
        warnings = []
        
        # Check response length
        if len(response) < 200:
            errors.append("Response too short (< 200 characters)")
        
        # Check for required sections
        required_sections = [
            '=== OPTIMIZED SECTION ===',
            '=== CHANGES MADE ===',
            '=== KEYWORD COVERAGE ==='
        ]
        
        for section in required_sections:
            if section not in response:
                errors.append(f"Missing section: {section}")
        
        # Check keyword incorporation
        response_lower = response.lower()
        missing_keywords = []
        for keyword in required_keywords:
            if keyword.lower() not in response_lower:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            warnings.append(f"Keywords not incorporated: {', '.join(missing_keywords)}")
        
        # Check for action verbs in optimized section
        action_verbs = [
            'developed', 'engineered', 'architected', 'implemented',
            'designed', 'optimized', 'automated', 'led', 'mentored'
        ]
        
        if not any(verb in response_lower for verb in action_verbs):
            warnings.append("No strong action verbs detected in optimized section")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_cover_letter_response(self, response: str) -> Dict:
        """Validate cover letter output"""
        errors = []
        warnings = []
        
        # Check for required sections
        if '=== FINAL COVER LETTER ===' not in response:
            errors.append("Missing final cover letter section")
        
        if '=== KEYWORD COVERAGE ===' not in response:
            errors.append("Missing keyword coverage section")
        
        # Extract letter content
        if '=== FINAL COVER LETTER ===' in response:
            letter_start = response.find('=== FINAL COVER LETTER ===')
            letter_end = response.find('===', letter_start + 30)
            letter_content = response[letter_start:letter_end] if letter_end > 0 else response[letter_start:]
            
            # Count words
            word_count = len(letter_content.split())
            if word_count < 200:
                errors.append(f"Cover letter too short: {word_count} words (minimum 200)")
            elif word_count > 400:
                warnings.append(f"Cover letter too long: {word_count} words (recommended max 350)")
            
            # Check for placeholder text
            placeholders = ['[Company Name]', '[Position]', '[Hiring Manager]']
            for placeholder in placeholders:
                if placeholder in letter_content:
                    warnings.append(f"Placeholder not replaced: {placeholder}")
            
            # Check structure
            if 'Dear' not in letter_content and 'Hello' not in letter_content:
                warnings.append("Missing proper greeting")
            
            if 'Sincerely' not in letter_content and 'Best regards' not in letter_content:
                warnings.append("Missing proper closing")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _calculate_quality_score(
        self,
        validation_result: Dict,
        response_time: float,
        response_length: int
    ) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0
        
        # Deduct for errors (critical)
        score -= len(validation_result['errors']) * 20
        
        # Deduct for warnings (minor)
        score -= len(validation_result['warnings']) * 5
        
        # Deduct for slow response (> 10 seconds)
        if response_time > 10:
            score -= (response_time - 10) * 2
        
        # Deduct for very short responses (< 500 chars)
        if response_length < 500:
            score -= (500 - response_length) / 10
        
        return max(0.0, min(100.0, score))
    
    def run_full_test_suite(
        self,
        test_cv: str,
        test_jd: str,
        test_section: str,
        test_keywords: List[str],
        candidate_data: Dict,
        job_data: Dict
    ) -> Dict[PromptType, TestResult]:
        """Run complete test suite for all prompts"""
        prompts = self.load_prompts()
        results = {}
        
        print("Testing Analyzer Prompt...")
        results[PromptType.ANALYZER] = self.test_analyzer_prompt(
            test_cv, test_jd, prompts[PromptType.ANALYZER]
        )
        
        print("Testing Optimizer Prompt...")
        results[PromptType.OPTIMIZER] = self.test_optimizer_prompt(
            test_section, test_jd, test_keywords, prompts[PromptType.OPTIMIZER]
        )
        
        print("Testing Cover Letter Prompt...")
        results[PromptType.COVER_LETTER] = self.test_cover_letter_prompt(
            candidate_data, job_data, prompts[PromptType.COVER_LETTER]
        )
        
        return results
    
    def generate_test_report(self, results: Dict[PromptType, TestResult]) -> str:
        """Generate HTML test report"""
        report = """
<!DOCTYPE html>
<html>
<head>
    <title>PowerCV Prompt Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #2c3e50; }
        .test-result { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #ecf0f1; }
        .success { border-left-color: #27ae60; }
        .failure { border-left-color: #e74c3c; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-label { font-weight: bold; color: #7f8c8d; }
        .metric-value { font-size: 1.2em; color: #2c3e50; }
        .error { color: #e74c3c; margin: 5px 0; }
        .warning { color: #f39c12; margin: 5px 0; }
        .output { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; max-height: 400px; }
        .score { font-size: 2em; font-weight: bold; }
        .score-good { color: #27ae60; }
        .score-ok { color: #f39c12; }
        .score-bad { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PowerCV Prompt Test Report</h1>
        <p><strong>Test Date:</strong> {date}</p>
"""
        
        from datetime import datetime
        report = report.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        for prompt_type, result in results.items():
            status_class = "success" if result.success else "failure"
            score_class = "score-good" if result.quality_score >= 80 else "score-ok" if result.quality_score >= 60 else "score-bad"
            
            report += f"""
        <div class="test-result {status_class}">
            <h2>{prompt_type.value.upper()} Prompt</h2>
            
            <div class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value">{' PASS' if result.success else ' FAIL'}</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Quality Score:</span>
                <span class="metric-value score {score_class}">{result.quality_score:.1f}/100</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Response Time:</span>
                <span class="metric-value">{result.response_time:.2f}s</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Response Length:</span>
                <span class="metric-value">{result.response_length} chars</span>
            </div>
"""
            
            if result.errors:
                report += "<h3>Errors:</h3>"
                for error in result.errors:
                    report += f'<div class="error"> {error}</div>'
            
            if result.warnings:
                report += "<h3>Warnings:</h3>"
                for warning in result.warnings:
                    report += f'<div class="warning"> {warning}</div>'
            
            report += f"""
            <h3>Output Sample (first 1000 chars):</h3>
            <pre class="output">{result.output[:1000]}...</pre>
        </div>
"""
        
        report += """
    </div>
</body>
</html>
"""
        return report


# Example usage
if __name__ == "__main__":
    # Configuration
    API_KEY = "your_cerebras_api_key"
    API_BASE = "https://api.cerebras.ai/v1"
    MODEL = "llama3.1-8b"  # or your preferred Cerebras model
    
    # Initialize tester
    tester = CerebrasPromptTester(API_KEY, API_BASE, MODEL)
    
    # Test data
    test_cv = """
    [Your CV text from the document]
    """
    
    test_jd = """
    Backend Developer - Python & Microservices
    
    We are seeking an experienced Backend Developer to join our team.
    
    Requirements:
    - 2+ years Python development experience
    - Expert knowledge of Flask or FastAPI
    - Experience with Docker and Kubernetes
    - REST API design and development
    - PostgreSQL or MySQL experience
    - CI/CD pipeline setup and maintenance
    
    Nice to have:
    - GraphQL experience
    - AWS/GCP cloud platforms
    - Test-driven development
    """
    
    test_section = """
    PYTHON BACKEND DEVELOPER - Jan 2023 - Present
    Freelance Remote
    
    • Develop REST APIs with Flask, boosting backend efficiency and response times.
    • Design Dockerized microservices for scalable deployments, enhancing system reliability.
    • Create automated ETL pipelines, ensuring flawless data processing and deployment success.
    """
    
    test_keywords = ["Python", "Flask", "Docker", "microservices", "REST API"]
    
    candidate_data = {
        "name": "John Doe",
        "current_title": "Backend Developer",
        "location": "Amsterdam, Netherlands",
        "years_exp": "2+",
        "top_skills": ["Python", "Flask/FastAPI", "Docker"],
        "achievements": [
            "Automated ETL pipelines with 100% deployment success",
            "Designed Dockerized microservices architecture",
            "Mentored junior developers in Python best practices"
        ]
    }
    
    job_data = {
        "company": "TechCorp BV",
        "position": "Senior Backend Developer",
        "location": "Amsterdam, Netherlands",
        "requirements": [
            "Python expertise with Flask/FastAPI",
            "Microservices architecture",
            "Docker and Kubernetes",
            "CI/CD pipeline experience"
        ]
    }
    
    # Run tests
    results = tester.run_full_test_suite(
        test_cv, test_jd, test_section, test_keywords, 
        candidate_data, job_data
    )
    
    # Generate report
    report = tester.generate_test_report(results)
    
    # Save report
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\nTest Summary:")
    for prompt_type, result in results.items():
        status = " PASS" if result.success else " FAIL"
        print(f"{prompt_type.value.upper()}: {status} (Score: {result.quality_score:.1f}/100)")
