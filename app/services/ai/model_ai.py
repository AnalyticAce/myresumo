"""AI-powered resume optimization module.

This module provides the AtsResumeOptimizer class that leverages AI language models
to analyze and optimize resumes based on job descriptions, improving compatibility
with Applicant Tracking Systems (ATS).
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from app.services.ai.ats_scoring import ATSScorerLLM
from app.utils.token_tracker import TokenTracker


class AtsResumeOptimizer:
    """ATS Resume Optimizer.

    A class that uses AI language models to optimize resumes for Applicant Tracking
    Systems (ATS) based on specific job descriptions.

    This class leverages OpenAI's language models to analyze a job description and a
    provided resume, then generates an ATS-optimized version of the resume in JSON format.
    The optimization focuses on incorporating relevant keywords, formatting for ATS
    readability, and highlighting the most relevant experience for the target position.

    Attributes:
    ----------
        model_name: The name of the OpenAI model to use for processing
        resume: The resume text to be optimized
        api_key: OpenAI API key for authentication
        api_base: Base URL for the OpenAI API
        llm: The initialized language model instance
        output_parser: Parser for converting LLM output to JSON format
        ats_scorer: ATSScorerLLM instance for scoring resume and extracting missing skills

    Methods:
    -------
        _get_openai_model()
            Initialize the OpenAI model with appropriate settings
        _get_prompt_template(missing_skills=None)
            Create the PromptTemplate for ATS resume optimization with missing skills
        _setup_chain()
            Set up the processing pipeline for job descriptions and resumes
        generate_ats_optimized_resume_json(job_description)
            Generate an ATS-optimized resume in JSON format based on the provided job description

    Example:
        >>> # Note: Ensure to replace "your_api_key" and "your resume text" with actual values
        >>> optimizer = AtsResumeOptimizer(api_key="your_api_key", resume="your resume text")
        >>> optimized_resume = optimizer.generate_ats_optimized_resume_json("job description text")
        >>> print(optimized_resume)
        >>> # Output: JSON object with optimized resume
    """

    def __init__(
        self,
        model_name: str = None,
        resume: str = None,
        api_key: str = None,
        api_base: str = None,
        user_id: str = None,
    ) -> None:
        """Initialize the AI model for resume processing.

        Args:
            model_name: The name of the OpenAI model to use.
            resume: The resume text to be optimized.
            api_key: OpenAI API key for authentication.
            api_base: Base URL for the OpenAI API.
            user_id: Optional user ID for token tracking.
        """
        self.model_name = model_name or os.getenv("MODEL_NAME")
        self.resume = resume
        self.api_key = api_key or os.getenv("API_KEY")
        self.api_base = api_base or os.getenv(
            "API_BASE") or os.getenv("OLLAMA_BASE_URL")
        self.user_id = user_id

        # Initialize LLM component and output parser
        self.llm = self._get_openai_model()
        self.output_parser = JsonOutputParser()
        self.chain = None

        # Initialize ATS scorer for skill extraction and analysis
        self.ats_scorer = None
        if self.api_key and self.api_base and self.model_name:
            self.ats_scorer = ATSScorerLLM(
                model_name=self.model_name,
                api_key=self.api_key,
                api_base=self.api_base,
                user_id=self.user_id,
            )

        self._setup_chain()

    def _get_openai_model(self) -> ChatOpenAI:
        """Initialize the OpenAI model with appropriate settings.

        Returns:
            ChatOpenAI: Configured language model instance with token tracking
        """
        if self.model_name:
            # Create LLM instance with token tracking for usage monitoring
            return TokenTracker.get_tracked_langchain_llm(
                model_name=self.model_name,
                temperature=0,
                api_key=self.api_key,
                api_base=self.api_base,
                feature="resume_optimization",
                user_id=self.user_id,
                metadata={"resume_length": len(
                    self.resume) if self.resume else 0}
            )
        else:
            # Fallback to standard model if no specific model is configured
            return ChatOpenAI(temperature=0)

    def _get_prompt_template(self, missing_skills: List[str] = None) -> PromptTemplate:
        """Create the PromptTemplate for ATS resume optimization with missing skills.
        
        Implements advanced prompting techniques including:
        - Chain-of-Thought (CoT) prompting
        - Role-based prompting
        - Multi-step reasoning
        - Structured output requirements
        - Multi-prompt chaining (inspired by quick-start guide)

        Args:
            missing_skills: List of skills from the job description that are missing from the resume
        """
        prompt = """# ROLE: Expert ATS Optimization Specialist & Career Strategist (10+ years experience)

## CONTEXT:
You are a senior ATS optimization specialist with 15+ years of experience at Fortune 500 companies.
Your expertise includes:
- ATS algorithm behavior and scoring
- Resume parsing technology
- HR recruitment workflows
- Industry-specific hiring practices
- Career transition strategies

## TASK:
Optimize the following resume to achieve >90% ATS match rate for the target job while maintaining human readability and impact.

**CRITICAL SUCCESS FACTORS (from 500+ successful optimizations):**
1. **First 10-second test**: Ensure the top 1/3 of the resume immediately communicates value
2. **SOAR Method**: Every bullet point must follow Situation-Obstacle-Action-Result
3. **Metrics in every bullet**: Every claim must be supported by quantifiable results
4. **ATS Keywords**: Must match 80%+ of the job description's hard skills
5. **Readability**: Must pass 8th-grade reading level for maximum ATS compatibility

## INPUT DATA:

### JOB DESCRIPTION:
{job_description}

### CURRENT RESUME:
{resume}

## INSTRUCTIONS (THINK STEP BY STEP):

### 1. JOB ANALYSIS (MUST BE THOROUGH)
**A. Extract Critical Requirements**
- [ ] Identify must-have vs nice-to-have skills
- [ ] Note any red flags in the job description
- [ ] Highlight any special requirements (security clearances, etc.)

**B. Skills Mapping**
- [ ] Extract all technical skills and tools
- [ ] Identify soft skills and behavioral traits
- [ ] Note any industry-specific terminology

**C. Seniority & Culture**
- [ ] Determine experience level (Entry/Mid/Senior/Exec)
- [ ] Identify company culture indicators
- [ ] Note any leadership/management requirements

### 2. RESUME AUDIT (BE RUTHLESS)
**A. Formatting Check**
- [ ] Single-column layout
- [ ] Standard fonts (Arial, Calibri, Times New Roman)
- [ ] No tables, text boxes, or graphics
- [ ] Proper section headers (Work, Education, Skills)

**B. Content Quality**
- [ ] Every bullet starts with a power verb
- [ ] All claims are quantified
- [ ] No responsibilities, only achievements
- [ ] No pronouns (I, me, my)

**C. ATS Optimization**
- [ ] Keywords from job description present
- [ ] No headers/footers
- [ ] Standard file format (.docx or .pdf)
- [ ] Proper contact information format

### 3. OPTIMIZATION STRATEGY (BE STRATEGIC)
**A. Achievement Mapping**
- [ ] Select top 3-5 career achievements
- [ ] Ensure each maps to job requirements
- [ ] Quantify all achievements ($, %, #, time)

**B. Keyword Integration**
- [ ] Primary keywords in first 1/3 of resume
- [ ] Secondary keywords throughout
- [ ] Include variations (e.g., "ML" and "Machine Learning")

**C. Structure Optimization**
- [ ] Most relevant experience first
- [ ] Education/certifications if required
- [ ] Skills section with exact job title keywords

### 4. IMPLEMENT CHANGES (BE PRECISE)
**A. Bullet Point Formula**
- [ ] Start with power verb (Led, Spearheaded, Engineered)
- [ ] Include metric within first 10 words
- [ ] Show business impact (increased X by Y%)
- [ ] Add context (team size, budget, scope)

**B. Keyword Placement**
- [ ] Job title in professional summary
- [ ] Skills in skills section (exact match)
- [ ] Technologies in experience bullets
- [ ] Certifications in education/certifications

**C. Readability Optimization**
- [ ] 8th-grade reading level
- [ ] Short paragraphs (2-3 lines max)
- [ ] Bullet points (3-5 per role)
- [ ] White space between sections

## OUTPUT FORMAT (STRICT JSON):
{{
    "optimized_resume": "Fully reformatted resume with ATS optimizations",
    "analysis": {{
        "job_title": "Extracted job title",
        "job_level": "Entry/Mid/Senior/Executive",
        "hard_skills_matched": ["list", "of", "matched", "skills"],
        "hard_skills_missing": ["list", "of", "missing", "skills"],
        "soft_skills_identified": ["list", "of", "key", "soft", "skills"],
        "ats_score_before": 0-100,
        "ats_score_after": 0-100,
        "improvement_areas": ["list", "of", "key", "improvements"],
        "top_achievements": ["list", "of", "top", "3-5", "achievements"]
    }},
    "optimization_details": {{
        "keywords_added": ["list", "of", "keywords", "added"],
        "achievements_enhanced": ["list", "of", "enhanced", "achievements"],
        "formatting_changes": ["list", "of", "format", "changes"],
        "sections_modified": ["list", "of", "modified", "sections"]
    }}
}}

## ADDITIONAL INSTRUCTIONS:
1. **Content Rules**
   - Use industry-specific terminology from the job description
   - Maintain consistent verb tense (past for previous roles, present for current)
   - Focus on achievements with metrics (increase, reduce, save, grow)
   - Include 3-5 quantifiable metrics per role
   
2. **Formatting Rules**
   - Use standard section headers (Work Experience, Education, Skills)
   - Use standard job titles that ATS systems recognize
   - Maintain consistent date format (MM/YYYY - MM/YYYY)
   - Use bullet points (not paragraphs)
   
3. **ATS Optimization**
   - Place important keywords in the first 1/3 of the resume
   - Include variations of keywords (e.g., "ML" and "Machine Learning")
   - Avoid headers/footers, tables, and graphics
   - Use standard fonts (Arial, Calibri, Times New Roman)
   
4. **Readability**
   - Target 8th-grade reading level
   - Keep bullet points to 1-2 lines
   - Use white space effectively
   - Bold important achievements
   
5. **Required Sections**
   - Contact Information
   - Professional Summary (3-4 lines)
   - Work Experience (reverse chronological)
   - Education
   - Skills (match job description)
   - Certifications (if relevant)
   
6. **Pro Tips**
   - Use the exact job title in your professional summary
   - Mirror the language from the job description
   - Focus on recent experience (last 10-15 years)
   - Remove irrelevant personal information (age, photo, etc.)
   - Save as .docx for best ATS compatibility"""

        # Add missing skills section if provided
        if missing_skills:
            prompt += f"\n\n## MISSING SKILLS TO INCORPORATE:\n{', '.join(missing_skills)}"

        return PromptTemplate(
            template=prompt,
            input_variables=["job_description", "resume"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )

    def _setup_chain(self, missing_skills: Optional[List[str]] = None) -> None:
        """Set up the processing pipeline for job descriptions and resumes.

        This method configures the functional composition approach with the pipe operator
        to create a processing chain from prompt template to language model.

        Args:
            missing_skills: List of skills identified as missing that should be incorporated
                        into the optimization prompt.
        """
        prompt_template = self._get_prompt_template(missing_skills)
        self.chain = prompt_template | self.llm

    def generate_ats_optimized_resume_json(
        self, job_description: str
    ) -> Dict[str, Any]:
        """Generate an ATS-optimized resume in JSON format.

        This method performs a comprehensive ATS analysis of the resume against the job
        description, extracts valuable insights such as missing skills and keyword matches,
        and then uses this information to generate an optimized resume tailored to the
        specific job requirements.

        Args:
            job_description: The target job description.

        Returns:
        -------
            dict: The optimized resume in JSON format with additional ATS metrics.
        """
        if not self.resume:
            return {"error": "Resume not provided"}

        try:
            missing_skills = []
            score_results = {}

            # Step 1: Analyze resume against job description to identify skill gaps
            if self.ats_scorer:
                try:
                    score_results = self.ats_scorer.compute_match_score(
                        self.resume, job_description
                    )
                    missing_skills = score_results.get("missing_skills", [])
                    matching_skills = score_results.get("matching_skills", [])

                    # Reconfigure processing chain with identified missing skills
                    self._setup_chain(missing_skills)

                    print(
                        f"Initial ATS Score: {score_results.get('final_score', 'N/A')}%")
                    print(
                        f"Found {len(missing_skills)} missing skills to incorporate")
                    print(
                        f"Found {len(matching_skills)} matching skills to emphasize")
                except Exception as e:
                    print(
                        f"Warning: ATS scoring failed, proceeding without skill recommendations: {str(e)}")
                    pass

            # Step 2: Generate optimized resume using LLM
            result = self.chain.invoke(
                {"job_description": job_description, "resume": self.resume}
            )

            # Step 3: Parse and format the LLM response
            try:
                # Extract content from different response types
                if hasattr(result, "content"):
                    content = result.content
                else:
                    content = result

                # Step 4: Parse JSON and add ATS metrics
                try:
                    # Direct JSON parsing
                    json_result = json.loads(content)

                    # Enrich result with ATS analysis metrics
                    if score_results:
                        json_result["ats_metrics"] = {
                            "initial_score": score_results.get("final_score", 0),
                            "matching_skills": score_results.get("matching_skills", []),
                            "missing_skills": score_results.get("missing_skills", []),
                            "recommendation": score_results.get("recommendation", "")
                        }

                    return json_result
                except json.JSONDecodeError:
                    # Fallback 1: Extract JSON from code blocks
                    json_match = re.search(
                        r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                    if json_match:
                        json_str = json_match.group(1)
                        json_result = json.loads(json_str)

                        # Enrich result with ATS analysis metrics
                        if score_results:
                            json_result["ats_metrics"] = {
                                "initial_score": score_results.get("final_score", 0),
                                "matching_skills": score_results.get("matching_skills", []),
                                "missing_skills": score_results.get("missing_skills", []),
                                "recommendation": score_results.get("recommendation", "")
                            }

                        return json_result

                    # Fallback 2: Find any JSON-like structure in the response
                    json_str = re.search(r"(\{[\s\S]*\})", content)
                    if json_str:
                        json_result = json.loads(json_str.group(1))

                        # Enrich result with ATS analysis metrics
                        if score_results:
                            json_result["ats_metrics"] = {
                                "initial_score": score_results.get("final_score", 0),
                                "matching_skills": score_results.get("matching_skills", []),
                                "missing_skills": score_results.get("missing_skills", []),
                                "recommendation": score_results.get("recommendation", "")
                            }

                        return json_result

                    # No valid JSON found in the response
                    return {
                        "error": f"Could not extract valid JSON from response: {content[:100]}..."
                    }
            except Exception as e:
                return {
                    "error": f"JSON parsing error: {str(e)}",
                    "raw_response": str(result)[:500],
                }

        except Exception as e:
            return {"error": f"Error processing request: {str(e)}"}


if __name__ == "__main__":
    with open("../../../data/sample_resumes/resume.txt", "r") as f:
        resume = f.read()

    with open("../../../data/sample_descriptions/job_description_1.txt", "r") as f:
        job_description = f.read()

    API_KEY = "sk-********************"
    API_BASE = "https://api.deepseek.com/v1"
    MODEL_NAME = "deepseek-chat"

    model = AtsResumeOptimizer(
        model_name=MODEL_NAME,
        resume=resume,
        api_key=API_KEY,
        api_base=API_BASE,
    )

    result = model.generate_ats_optimized_resume_json(job_description)

    print(json.dumps(result, indent=2))
