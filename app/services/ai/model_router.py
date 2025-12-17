
import os
import json
import logging
from enum import Enum
from typing import Dict, Any, Optional
import time
from app.utils.token_tracker import TokenTracker

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tier definitions"""
    FAST = 1        # 3B model (e.g., qwen2.5:3b)
    BALANCED = 2    # 7B model (e.g., mistral:7b)
    DEEP = 3        # Heavy model (optional)


class TaskComplexity(Enum):
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3


class ModelRouter:
    """
    Routes tasks to the appropriate model based on complexity.
    Adapts the user's architectural plan to use Ollama backend.
    """
    _instance = None
    _models: Dict[ModelTier, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Configuration - these could be loaded from env
        # Use env var for BALANCED to respect user's speed choice (Qwen), default to Mistral if not set
        provider = (os.getenv("API_TYPE") or os.getenv("LLM_PROVIDER") or "").lower()
        cerebras_key = os.getenv("CEREBRAS_API_KEY")
        forced_provider = (os.getenv("FORCE_LLM_PROVIDER") or "").lower()
        force_local = forced_provider in {"ollama", "local"} or provider in {"ollama", "local"}

        if cerebras_key and not force_local:
            default_fast = os.getenv("CEREBRAS_MODEL_NAME", "llama3.3-70b")
            default_balanced = os.getenv("CEREBRAS_MODEL_NAME", "llama3.3-70b")
        else:
            default_fast = "qwen2.5:3b"
            default_balanced = "mistral:7b-instruct-v0.3-q4_K_M"

        fast_model = (
            os.getenv("FAST_MODEL_NAME")
            or os.getenv("ROUTER_FAST_MODEL")
            or default_fast
        )
        balanced_model = (
            os.getenv("BALANCED_MODEL_NAME")
            or os.getenv("ROUTER_BALANCED_MODEL")
            or os.getenv("MODEL_NAME")
            or default_balanced
        )
        deep_model = (
            os.getenv("DEEP_MODEL_NAME")
            or os.getenv("ROUTER_DEEP_MODEL")
            or balanced_model
        )

        self.tier_config = {
            ModelTier.FAST: fast_model,
            ModelTier.BALANCED: balanced_model,
            ModelTier.DEEP: deep_model,
        }

        # Task mapping
        self.task_mapping = {
            'extract_keywords': ModelTier.FAST,
            'format_text': ModelTier.FAST,
            'split_sections': ModelTier.FAST,
            'ats_score': ModelTier.FAST,
            'parse_resume_structure': ModelTier.FAST,

            'rewrite_bullets': ModelTier.BALANCED,
            'write_summary': ModelTier.BALANCED,
            'optimize_skills': ModelTier.BALANCED,

            'psychological_optimize': ModelTier.BALANCED,  # Or DEEP if available
            'gap_analysis': ModelTier.BALANCED
        }

    def get_model(self, tier: ModelTier):
        """Lazy load model for specific tier"""
        if tier not in self._models:
            model_name = self.tier_config.get(tier)
            logger.info(f"Initializing {tier.name} model: {model_name}")

            temperature = 0.0 if tier == ModelTier.FAST else 0.6
            self._models[tier] = TokenTracker.get_tracked_langchain_llm(
                model_name=model_name,
                temperature=temperature,
                feature=f"router_{tier.name.lower()}",
                max_tokens=8192,
            )
        return self._models[tier]

    def route_task(self, task_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using the appropriate model tier.
        """
        tier = self.task_mapping.get(task_name, ModelTier.BALANCED)
        model = self.get_model(tier)

        start_time = time.time()
        logger.info(f"Routing task '{task_name}' to {tier.name} model")

        try:
            result = self._execute_task(model, task_name, **kwargs)
        except Exception as e:
            logger.error(
                f"Error executing task {task_name} on {tier.name}: {e}")
            # Fallback logic could go here (e.g. try BALANCED if FAST fails)
            raise e

        execution_time = time.time() - start_time

        return {
            'result': result,
            'tier': tier.name,
            'execution_time': execution_time
        }

    def _execute_task(self, model, task_name: str, **kwargs):
        """Internal task execution router"""

        def _clean_llm_text(text: str) -> str:
            if not isinstance(text, str):
                return str(text)
            cleaned = text.strip()
            cleaned = cleaned.strip('"').strip("'")
            for prefix in [
                "optimized bullet:",
                "rewritten bullet:",
                "final bullet:",
                "bullet:",
                "here is the rewritten bullet point:",
                "here's a rewritten bullet point:",
                "here is a rewritten bullet point:",
            ]:
                if cleaned.lower().startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
            # If the model still returned explanations, keep only the actual bullet.
            for splitter in [
                "\n",
                "this rewritten bullet point",
                "alternatively",
                "let me know",
                "this rewritten bullet",
                "this bullet point",
            ]:
                idx = cleaned.lower().find(splitter)
                if idx > 0:
                    cleaned = cleaned[:idx].strip()
            cleaned = cleaned.replace("\n", " ").strip()
            return cleaned

        if task_name == 'extract_keywords':
            job_description = kwargs.get('job_description', '')
            prompt = f"""You are an ATS optimization expert.

            TASK:
            Extract 20 critical ATS keywords from the job description.

            RULES:
            - Focus ONLY on role requirements/responsibilities (skills, tools, processes, safety, quality).
            - EXCLUDE marketing/company story, funding/investors, social links, product hype.
            - Prefer concrete terms like: assembly, calibration, quality control, hand tools, power tools, sensors, optics, documentation, test procedures, safety.
            - Output ONLY a comma-separated list. No commentary.

            JOB DESCRIPTION:
            {job_description[:3500]}
            """
            response = model.invoke(prompt).content
            return [k.strip() for k in response.split(',') if k.strip()]

        elif task_name == 'rewrite_bullets':
            bullets = kwargs.get('bullets', [])
            keywords = kwargs.get('keywords', [])
            job_description = kwargs.get('job_description', '')
            role_context = kwargs.get('role_context', '')
            keywords_str = ", ".join(keywords[:10])  # Top 10 critical

            bullets = [b for b in bullets if isinstance(b, str) and b.strip()]
            if not bullets:
                return ["Managed key responsibilities."]

            prompt = f"""You are an expert ATS optimizer and recruiter.

            TARGET JOB DESCRIPTION (for relevance):
            {job_description[:1800]}

            CONTEXT ABOUT THIS ROLE (from candidate resume):
            {role_context}

            TASK:
            Rewrite ALL resume bullet points below to be highly relevant to the target job and ATS-friendly.

            STRICT RULES:
            1) Output ONLY a valid JSON array of strings. No markdown, no explanations.
            2) Return the SAME NUMBER of bullets as input.
            3) Each bullet MUST be meaningfully different. Do NOT repeat the same idea with different wording.
               - Cover different angles: documentation, reporting, stakeholder communication, process adherence, issue escalation, audit trail.
               - Avoid repeating phrases like "ensure accuracy" in every bullet.
            4) Preserve the core meaning of each original bullet.
               - Do NOT invent tools, systems, projects, or domain experience.
               - You may reframe using transferable skills (quality mindset, documentation, troubleshooting, process discipline).
            5) You may include keywords ONLY if they are truthful/transferable.
               Keywords to prioritize: {keywords_str}
            6) No placeholder numbers like X%/Y%.
            7) 1 sentence per bullet (max 220 characters). Start with a strong verb.

            ORIGINAL BULLETS (JSON array):
            {json.dumps(bullets, ensure_ascii=False)}
            """

            response = model.invoke(prompt).content
            try:
                import re
                arr_match = re.search(r"\[.*\]", response, re.DOTALL)
                if arr_match:
                    parsed = json.loads(arr_match.group(0))
                else:
                    parsed = json.loads(response)

                if isinstance(parsed, list):
                    cleaned = [_clean_llm_text(x) for x in parsed if isinstance(x, str)]
                    if len(cleaned) < len(bullets):
                        cleaned.extend([_clean_llm_text(b) for b in bullets[len(cleaned):]])
                    return cleaned[: len(bullets)]
            except Exception:
                pass

            optimized = []
            for bullet in bullets:
                per_bullet_prompt = f"""You are an expert ATS optimizer and recruiter.

                TARGET JOB DESCRIPTION (for relevance):
                {job_description[:2000]}

                CONTEXT ABOUT THIS ROLE (from candidate resume):
                {role_context}

                TASK:
                Rewrite ONE resume bullet point to be highly relevant to the target job and ATS-friendly.

                STRICT RULES:
                1) Return ONLY the rewritten bullet text. No explanations, no extra lines, no alternatives.
                2) Preserve the core meaning of the original bullet.
                   - Do NOT replace software work with mechanical assembly, or invent new duties.
                   - You may reframe using transferable skills (quality mindset, testing, documentation, troubleshooting, process discipline).
                3) Do NOT invent tools, projects, or domain experience.
                   - If the candidate did not mention robotics/lasers/optics, do not add them.
                4) You may include keywords ONLY if they are truthful/transferable from the original bullet.
                   Keywords to prioritize: {keywords_str}
                5) If you don't know exact numbers, do NOT use placeholders like X%/Y%.
                   Prefer: measurable outcomes without numbers (e.g., "improved accuracy", "reduced rework").
                6) Keep it 1 sentence (max 220 characters). Start with a strong verb.

                ORIGINAL BULLET:
                {bullet}

                REWRITTEN BULLET:"""

                r = model.invoke(per_bullet_prompt).content
                optimized.append(_clean_llm_text(r))
            return optimized

        elif task_name == 'write_summary':
            experience = kwargs.get('experience', '')
            keywords = kwargs.get('keywords', [])
            job_description = kwargs.get('job_description', '')
            kw_str = ", ".join(keywords[:8])

            # Based on PROMPT #9: Professional Summary Generator
            prompt = f"""Create an IDEAL professional summary for this resume, tailored to the target job.
            
            SUMMARY REQUIREMENTS:
            - Length: 3-4 sentences (no more than 100 words).
            - Sentence 1: HOOK - Why am I interesting for this role?
            - Sentence 2: WHAT I did (Specialization).
            - Sentence 3: RESULTS (Numbers and impact).
            - Sentence 4: WHAT'S NEXT (How I can contribute in this role/team).
            - Keywords to include: {kw_str}

            STRICT RULES:
            - Do NOT mention the company name from the job description (e.g., do not write "Carbon Robotics").
            - You MAY refer generically to "the team", "the manufacturing organization", or "this role".
            
            TONE:
            - Confident but not arrogant.
            - Professional but human.
            - Focus on VALUE, not just skills.
            
            Experience Context:
            {experience[:1500]}

            Target Job Context:
            {job_description[:1200]}
            
            Output ONLY the summary text. No labels."""

            return _clean_llm_text(model.invoke(prompt).content)

        elif task_name == 'optimize_skills':
            kw_str = ", ".join(keywords[:15])
            prompt = f"""You are an expert Resume Skills Optimizer working with ATS systems.

            TASK:
            Preserve the original skills structure exactly. Only append missing skills from the job description.

            Target keywords: {kw_str}
            Target job description:
            {job_description[:1200]}

            Original Skills section:
            {content}

            OUTPUT:
            Return ONLY valid JSON: {{"hard_skills": [...], "soft_skills": [...]}}.
            CRITICAL RULES:
            - Keep ALL original skills with their exact wording
            - Only ADD skills that are present in the job description but missing from the original
            - Do NOT reorder or restructure existing skills
            - Do NOT mix categories:
              - hard_skills = tools/technologies/methods/domains/certifications (e.g., Python, Docker, Welding, Mechanical assembly)
              - soft_skills = interpersonal/behavioral skills only (e.g., Communication, Teamwork, Adaptability)
            - If the original has categories/subsections, preserve that structure in the arrays
            """
            return model.invoke(prompt).content.strip()

        elif task_name == 'parse_resume_structure':
            # Parse raw text into structured JSON matching ResumeData schema
            content = kwargs.get('content', '')
            prompt = f"""You are an expert Resume Parser.
            Extract the following sections from the resume text into a *strict* JSON object.
            
            CRITICAL INSTRUCTION:
            - The input text may have formatting issues (e.g. "WorkExperience", "PythonDeveloper").
            - You MUST fix all spacing, capitalization, and typos in the extracted data.
            - "PythonBackendDeveloper" -> "Python Backend Developer"
            
            Return JSON with these exact keys:
            - "name": string
            - "email": string
            - "phone": string
            - "location": string (city/country if present)
            - "address": string (full address if present)
            - "linkedin": string
            - "github": string
            - "languages": List[string]
            - "hobbies": List[string]
            - "profile_description": string (summary)
            - "experiences": List of objects (include ALL roles you can find), each with:
                - "job_title": string
                - "company": string
                - "start_date": string (e.g. "2020-01")
                - "end_date": string (e.g. "Present" or "2022-05")
                - "location": string (optional)
                - "four_tasks": List[string] (min 1, max 6 achievements)
            - "education": List of objects, each with:
                - "institution": string
                - "degree": string
                - "location": string (city/country if explicitly present in the resume line, e.g., after institution name or in parentheses)
                - "start_date": string
                - "end_date": string
                - "description": string (optional)
            - "skills": Object with:
                - "hard_skills": List[string]
                - "soft_skills": List[string]

            SKILLS RULES:
            - Put ALL tools/technologies/methods/domains into "hard_skills".
              Examples: programming languages, frameworks, databases, CI/CD, cloud, Linux, welding, assembly, procurement.
            - Put ONLY interpersonal/behavioral skills into "soft_skills".
              Examples: communication, teamwork, adaptability, problem-solving, attention to detail.
            - Do NOT leave hard_skills empty if any tools/technologies are present.
            
            RESUME TEXT:
            {content[:60000]}
            
            Output ONLY valid JSON.
            """

            # Use raw invoke to get JSON
            return model.invoke(prompt).content

        else:
            # Generic valid prompt pass-through if needed
            if 'prompt' in kwargs:
                return model.invoke(kwargs['prompt']).content
            else:
                raise ValueError(f"Unknown task: {task_name}")


class CascadeRouter(ModelRouter):
    """
    Router that attempts a task with a lower tier first, then escalates based on quality.
    """

    def route_with_cascade(self, task_name: str, **kwargs) -> Dict[str, Any]:
        # For now, default to standard routing.
        # True cascade requires defining quality_check logic per task.
        # Implemented as a simple wrapper for now to satisfy the interface.
        return self.route_task(task_name, **kwargs)
