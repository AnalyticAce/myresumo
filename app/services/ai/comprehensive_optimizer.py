"""Comprehensive AI Resume Optimization System.

This module implements the complete AI resume optimization system with modern
prompt-engineering techniques including role prompting, chain-of-thought,
step-back analysis, few-shot examples, and iterative refinement.

The system is designed for European job markets in 2025 with focus on:
- ATS optimization
- Human readability
- Psychological impact
- EU digital skills alignment
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from app.utils.token_tracker import TokenTracker


class ComprehensiveResumeOptimizer:
    """Complete AI Resume Optimization System.
    
    Implements the comprehensive optimization system with:
    - System prompt for role establishment
    - Master user prompt with all optimization tasks
    - Specialized prompts for specific needs
    - Skills master list for Europe 2025
    - Quick start workflows
    - Pro tips and EU alignment
    """
    
    # System prompt for role establishment
    SYSTEM_PROMPT = """You are a senior recruiter, hiring manager, and resume optimization specialist with 15+ years of experience placing candidates in competitive roles in Europe and globally.

You:
- Optimize resumes to maximize invitations to interviews and job offers
- Understand ATS (Applicant Tracking Systems) and human recruiters
- Write clearly, concisely, and professionally using impact-oriented language and metrics
- Follow instructions step by step and show intermediate reasoning only when explicitly requested

Your priorities, in order:
1) Relevance to target role and job description
2) Clarity and readability for humans
3) ATS-friendliness (keywords & structure)
4) Psychological impact (first impression, authority, social proof, consistency)

Never invent facts or metrics; if information is missing, ask clarifying questions or propose conservative, clearly marked suggestions."""
    
    # Master skills list for Europe 2025
    MASTER_SKILLS_LIST = """**MASTER SKILLS:**
Programming & Scripting: Python (Expert), Go (Skillful), Bash (Expert)
Web Frameworks & APIs: Flask (Expert), FastAPI (Skillful), Django (Skillful), REST APIs, GraphQL, OAuth2
Databases & Data: PostgreSQL, MySQL, MongoDB, Redis, ElasticSearch, SQL, Data Analysis
Testing & Automation: Pytest, Selenium, Postman, Swagger/OpenAPI, Test Automation
Cloud Platforms: AWS, GCP, Azure, Docker, Kubernetes, Terraform
DevOps & CI/CD: CI/CD Pipelines, Jenkins, GitHub Actions, GitLab CI, CircleCI
Systems & Infrastructure: Linux, Networking, System Administration
Digital Competences: API Design, Performance Optimization, Agile Development
Business Skills: Project Management, Procurement Strategies, Cost Optimization
Soft Skills: Communication, Problem-Solving, Teamwork, Adaptability, Technical Leadership
Languages: English (Highly proficient), Russian (Native), Tatar (Native)"""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Initialize the comprehensive optimizer.
        
        Args:
            model_name: OpenAI model name to use
            api_key: OpenAI API key
            api_base: OpenAI API base URL
            user_id: User ID for tracking
        """
        self.model_name = model_name or os.getenv("API_MODEL_NAME", "gpt-oss-120b")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("OPENAI_API_BASE")
        self.user_id = user_id
        self.llm = self._get_openai_model()
        self.output_parser = JsonOutputParser()
    
    def _get_openai_model(self) -> ChatOpenAI:
        """Initialize the OpenAI model with system prompt."""
        if self.model_name:
            return TokenTracker.get_tracked_langchain_llm(
                model_name=self.model_name,
                temperature=0,
                api_key=self.api_key,
                api_base=self.api_base,
                feature="comprehensive_resume_optimization",
                user_id=self.user_id,
                metadata={"model": "comprehensive_optimizer"}
            )
        return ChatOpenAI(temperature=0)
    
    def _get_master_prompt_template(self) -> PromptTemplate:
        """Get the master user prompt template with all optimization tasks."""
        template = f"""{self.SYSTEM_PROMPT}

### MASTER USER PROMPT

I want you to act as a resume optimization engine using modern prompt-engineering techniques (role prompting, chain-of-thought, step-back analysis, few-shot examples, iterative refinement).

### CONTEXT
**Target role:** {{target_role}}

**Target company (optional):** {{target_company}}

**Job description (JD):** {{job_description}}

**My current resume (plain text):** {{resume_text}}

### CONSTRAINTS
- Target region: Europe
- Max length: 1-2 pages depending on seniority
- Style: concise, quantified, results-oriented
- Focus on: {{focus_area}}

### TASKS (Execute in order)

1. **Step-back analysis:**
   - Identify real business problems this role solves
   - List 5-10 key skills/technologies/responsibilities (prioritized)
   - Map coverage in my resume: strong/partial/missing

2. **Keyword extraction (ATS-aware):**
   - Extract 15-25 critical keywords from JD
   - Mark each: "must-have"/"important"/"nice-to-have"

3. **Experience optimization (SOAR/STAR):**
   - Rewrite 3-6 bullets per relevant role
   - Include metrics (%, $, time saved, scale)
   - Connect each bullet to JD requirements

4. **Professional summary (3 versions):**
   - Version A: Conservative (works anywhere)
   - Version B: Tailored to {{target_company}} (their tone/keywords)
   - Version C: Bold/stand-out (differentiated)

5. **Skills optimization (Europe 2025):**
{self.MASTER_SKILLS_LIST}

6. **Psychological optimization:**
   - Order bullets: most impressive first (halo effect)
   - Signal authority/competence/reliability
   - Ensure career progression narrative

7. **Final resume:**
   Full rewritten resume, ATS-friendly structure:
   - Header (name/title/contact)
   - Professional Summary (pick best version)
   - Skills (3-5 categories, 8-15 total)
   - Experience (recent first)
   - Education/Certifications
   - Optional: Projects/Awards

### OUTPUT FORMAT
Use markdown with clear sections. End with "READY FOR INTERVIEW" when complete.

{{{{format_instructions}}}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "target_role", "target_company", "job_description", 
                "resume_text", "focus_area"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
    
    def _get_ats_keyword_prompt_template(self) -> PromptTemplate:
        """Get the ATS keyword and gap analysis prompt template."""
        template = f"""{self.SYSTEM_PROMPT}

### ATS KEYWORD & GAP ANALYSIS

Analyze JD vs resume for ATS gaps:

Job Description:
{{job_description}}

Resume:
{{resume_text}}

1) Extract 20 keywords from JD, categorize, prioritize
2) Table: Keyword | Priority | Coverage | Fix
3) Bullet-level rewrite suggestions for top 5 gaps

{{{{format_instructions}}}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["job_description", "resume_text"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
    
    def _get_hidden_achievements_prompt_template(self) -> PromptTemplate:
        """Get the hidden achievements extraction prompt template."""
        template = f"""{self.SYSTEM_PROMPT}

### HIDDEN ACHIEVEMENTS EXTRACTION

Extract hidden achievements from this role:

Role: {{role_description}}

Ask 8 specific questions starting "Tell me more about when you..."
Focus: problems solved, scale, before/after, metrics
Then rewrite as 5 SOAR bullets.

{{{{format_instructions}}}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["role_description"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
    
    def _get_three_version_prompt_template(self) -> PromptTemplate:
        """Get the 3-version resume (Tree-of-Thought) prompt template."""
        template = f"""{self.SYSTEM_PROMPT}

### 3-VERSION RESUME (Tree-of-Thought)

Create 3 resume positioning variants for this JD:

Job Description:
{{job_description}}

Resume:
{{resume_text}}

1) Results-focused ($$/ROI/business impact)
2) Leadership-focused (teams/mentoring/collaboration)  
3) Technical-depth (architecture/scale/innovation)

Each: summary + 4 bullets + when to use.

{{{{format_instructions}}}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["job_description", "resume_text"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
    
    def _get_iterative_improvement_prompt_template(self) -> PromptTemplate:
        """Get the iterative improvement (scoring loop) prompt template."""
        template = f"""{self.SYSTEM_PROMPT}

### ITERATIVE IMPROVEMENT (Scoring Loop)

Score and improve my resume for this JD:

Job Description:
{{job_description}}

Resume:
{{resume_text}}

Score 0-100: Relevance | Clarity | Metrics | Leadership | Impact
Top 3 weaknesses → targeted rewrites → new scores

{{{{format_instructions}}}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["job_description", "resume_text"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
    
    async def optimize_resume_master(
        self,
        target_role: str,
        job_description: str,
        resume_text: str,
        target_company: str = "",
        focus_area: str = "backend/data/DevOps/leadership"
    ) -> Dict[str, Any]:
        """Execute the master optimization prompt with all tasks.
        
        Args:
            target_role: Target job title
            job_description: Full job description
            resume_text: Current resume text
            target_company: Target company (optional)
            focus_area: Focus area for optimization
            
        Returns:
            Dict containing the complete optimization results
        """
        try:
            prompt = self._get_master_prompt_template()
            chain = prompt | self.llm | self.output_parser
            
            result = await chain.ainvoke({
                "target_role": target_role,
                "target_company": target_company,
                "job_description": job_description,
                "resume_text": resume_text,
                "focus_area": focus_area
            })
            
            return result
            
        except Exception as e:
            raise Exception(f"Master optimization failed: {str(e)}")
    
    async def analyze_ats_keywords(
        self,
        job_description: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """Analyze ATS keywords and gaps.
        
        Args:
            job_description: Job description text
            resume_text: Resume text
            
        Returns:
            Dict containing ATS keyword analysis
        """
        try:
            prompt = self._get_ats_keyword_prompt_template()
            chain = prompt | self.llm | self.output_parser
            
            result = await chain.ainvoke({
                "job_description": job_description,
                "resume_text": resume_text
            })
            
            return result
            
        except Exception as e:
            raise Exception(f"ATS keyword analysis failed: {str(e)}")
    
    async def extract_hidden_achievements(
        self,
        role_description: str
    ) -> Dict[str, Any]:
        """Extract hidden achievements from a role.
        
        Args:
            role_description: Description of the role
            
        Returns:
            Dict containing hidden achievements and SOAR bullets
        """
        try:
            prompt = self._get_hidden_achievements_prompt_template()
            chain = prompt | self.llm | self.output_parser
            
            result = await chain.ainvoke({
                "role_description": role_description
            })
            
            return result
            
        except Exception as e:
            raise Exception(f"Hidden achievements extraction failed: {str(e)}")
    
    async def create_three_versions(
        self,
        job_description: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """Create 3 resume positioning variants.
        
        Args:
            job_description: Job description text
            resume_text: Resume text
            
        Returns:
            Dict containing 3 resume versions
        """
        try:
            prompt = self._get_three_version_prompt_template()
            chain = prompt | self.llm | self.output_parser
            
            result = await chain.ainvoke({
                "job_description": job_description,
                "resume_text": resume_text
            })
            
            return result
            
        except Exception as e:
            raise Exception(f"Three-version creation failed: {str(e)}")
    
    async def iterative_improvement(
        self,
        job_description: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """Execute iterative improvement with scoring loop.
        
        Args:
            job_description: Job description text
            resume_text: Resume text
            
        Returns:
            Dict containing iterative improvement results
        """
        try:
            prompt = self._get_iterative_improvement_prompt_template()
            chain = prompt | self.llm | self.output_parser
            
            result = await chain.ainvoke({
                "job_description": job_description,
                "resume_text": resume_text
            })
            
            return result
            
        except Exception as e:
            raise Exception(f"Iterative improvement failed: {str(e)}")
    
    def get_quick_start_workflows(self) -> Dict[str, str]:
        """Get quick start workflow descriptions.
        
        Returns:
            Dict containing workflow descriptions
        """
        return {
            "5_minute_ats": "Use MASTER PROMPT with only Tasks 1-2,5. Pick Version A summary.",
            "20_minute_ready": "Full MASTER PROMPT. Pick best summary. Use 3 skill categories.",
            "60_minute_max": "MASTER PROMPT + ITERATIVE LOOP + 3-VERSION RESUME."
        }
    
    def get_pro_tips(self) -> List[str]:
        """Get pro tips for resume optimization.
        
        Returns:
            List of pro tips
        """
        return [
            "ALWAYS paste full JD - drives 80% of optimization quality",
            "Use Version B summary for named companies",
            "Pick 8-12 skills per job matching JD exactly",
            "First 3 bullets per role = most impressive achievements",
            "Every bullet needs a metric (%/time/scale/$/users)",
            "Tailor EVERY resume - generic = zero interviews",
            "Test readability: send to friend before applying",
            "Track results: sent → responses → interviews"
        ]
    
    def get_eu_2025_alignment(self) -> Dict[str, List[str]]:
        """Get EU 2025 alignment requirements.
        
        Returns:
            Dict containing EU 2025 alignment requirements
        """
        return {
            "ats_friendly": [
                "standard headings",
                "keywords from JD",
                "no graphics/tables",
                "simple formatting"
            ],
            "eu_digital_skills": [
                "cloud platforms",
                "data literacy",
                "DevOps practices",
                "cybersecurity awareness"
            ],
            "soft_skills_demand": [
                "communication",
                "adaptability",
                "continuous learning",
                "teamwork",
                "problem-solving"
            ],
            "regional": [
                "multilingualism advantage",
                "EU data protection awareness",
                "cross-cultural competence"
            ]
        }


if __name__ == "__main__":
    # Test the comprehensive optimizer
    optimizer = ComprehensiveResumeOptimizer()
    
    # Example usage
    async def test_optimizer():
        result = await optimizer.optimize_resume_master(
            target_role="Senior Backend Developer",
            job_description="Sample JD...",
            resume_text="Sample resume...",
            target_company="Tech Corp",
            focus_area="backend"
        )
        print(json.dumps(result, indent=2))
    
    # Run test
    import asyncio
    asyncio.run(test_optimizer())
