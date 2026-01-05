"""Simple model router using Cerebras AI directly without LangChain."""

import os
import json
import logging
from enum import Enum
from typing import Dict, Any, Optional
import time
from openai import OpenAI
from app.config import computed_settings as settings

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tier definitions"""
    FAST = 1        # Fast model
    BALANCED = 2    # Balanced model
    DEEP = 3        # Deep model


class TaskComplexity(Enum):
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3


class SimpleModelRouter:
    """
    Simple model router that uses Cerebras AI directly.
    Routes tasks to the appropriate model based on complexity.
    """
    _instance = None
    _client: Optional[OpenAI] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Initialize Cerebras AI client
            if not self._client:
                self._client = OpenAI(
                    base_url=settings.API_BASE,
                    api_key=settings.CEREBRASAI_API_KEY
                )
            
            # Configuration
            provider = (os.getenv("API_TYPE") or os.getenv("LLM_PROVIDER") or "").lower()
            cerebras_key = os.getenv("CEREBRASAI_API_KEY")
            forced_provider = (os.getenv("FORCE_LLM_PROVIDER") or "").lower()
            force_local = forced_provider in {"ollama", "local"} or provider in {"ollama", "local"}

            if cerebras_key and not force_local:
                default_fast = os.getenv("CEREBRAS_MODEL_NAME", settings.API_MODEL_NAME)
                default_balanced = os.getenv("CEREBRAS_MODEL_NAME", settings.API_MODEL_NAME)
            else:
                default_fast = settings.API_MODEL_NAME
                default_balanced = settings.API_MODEL_NAME

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

                'psychological_optimize': ModelTier.BALANCED,
                'gap_analysis': ModelTier.BALANCED
            }
            
            self.initialized = True

    def get_model_name(self, tier: ModelTier) -> str:
        """Get model name for specific tier"""
        return self.tier_config.get(tier, settings.API_MODEL_NAME)

    def route_task(self, task_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using the appropriate model tier.
        """
        tier = self.task_mapping.get(task_name, ModelTier.BALANCED)
        model_name = self.get_model_name(tier)

        start_time = time.time()
        logger.info(f"Routing task '{task_name}' to {tier.name} model: {model_name}")

        try:
            result = self._execute_task(model_name, task_name, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Task '{task_name}' completed in {duration:.2f}s")
            
            # Add metadata that multi_model_optimizer expects
            if isinstance(result, dict):
                result['tier'] = tier.name
                result['execution_time'] = duration
            
            return result
        except Exception as e:
            logger.error(f"Task '{task_name}' failed: {str(e)}")
            duration = time.time() - start_time
            logger.error(f"Failed after {duration:.2f}s")
            raise

    def _execute_task(self, model_name: str, task_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific task using the model."""
        temperature = 0.0 if task_name in ['extract_keywords', 'parse_resume_structure'] else 0.6
        
        # Get the appropriate prompt for the task
        prompt = self._get_prompt_for_task(task_name, **kwargs)
        
        if not prompt:
            raise ValueError(f"No prompt defined for task: {task_name}")

        try:
            response = self._client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(task_name)},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=8192
            )
            
            result_text = response.choices[0].message.content
            return self._parse_result(task_name, result_text)
            
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {str(e)}")
            raise

    def _get_system_prompt(self, task_name: str) -> str:
        """Get system prompt for the task."""
        prompts = {
            'extract_keywords': "You are an expert at extracting keywords from text. Return only a JSON array of strings.",
            'format_text': "You are an expert at formatting text. Return clean, well-formatted text.",
            'split_sections': "You are an expert at splitting resumes into sections. Return a JSON object with section names as keys.",
            'ats_score': "You are an expert ATS analyzer. Return a JSON with score and analysis.",
            'parse_resume_structure': "You are an expert resume parser. Return structured JSON data.",
            'rewrite_bullets': "You are an expert resume writer. Rewrite bullet points to be more impactful.",
            'write_summary': "You are an expert resume writer. Write compelling professional summaries.",
            'optimize_skills': "You are an expert resume optimizer. Optimize skills section for ATS.",
            'psychological_optimize': "You are an expert in resume psychology. Optimize for psychological impact.",
            'gap_analysis': "You are an expert career analyst. Analyze gaps between resume and job requirements."
        }
        return prompts.get(task_name, "You are a helpful assistant.")

    def _get_prompt_for_task(self, task_name: str, **kwargs) -> str:
        """Get the prompt for a specific task."""
        if task_name == 'extract_keywords':
            text = kwargs.get('text', '')
            return f"Extract important keywords from this text:\n\n{text}\n\nReturn only a JSON array of strings."
        
        elif task_name == 'parse_resume_structure':
            resume_text = kwargs.get('resume_text', '')
            return f"""Parse this resume into structured JSON. IMPORTANT: 
1. ONLY extract and structure the EXACT information present in the resume
2. DO NOT invent or hallucinate any details that are not in the original text
3. Preserve all real experiences, skills, education, and contact information exactly as written
4. If a section is missing, leave it empty or null
5. Return valid JSON with these exact keys: contact, summary, experience (array), education (array), skills (object with hard_skills and soft_skills), projects (array)

Resume text:
{resume_text}"""
        
        elif task_name == 'format_text':
            text = kwargs.get('text', '')
            return f"Format this text cleanly:\n\n{text}"
        
        elif task_name == 'split_sections':
            text = kwargs.get('text', '')
            return f"Split this resume into logical sections. Return JSON with section names as keys and content as values:\n\n{text}"
        
        elif task_name == 'ats_score':
            resume_text = kwargs.get('resume_text', '')
            job_description = kwargs.get('job_description', '')
            return f"Score this resume against the job description. Return JSON with score (0-100), matching_skills, missing_skills, recommendation:\n\nResume:\n{resume_text}\n\nJob:\n{job_description}"
        
        elif task_name == 'rewrite_bullets':
            bullets = kwargs.get('bullets', [])
            job_description = kwargs.get('job_description', '')
            bullets_text = '\n'.join(bullets)
            return f"Rewrite these bullet points to be more impactful for this job:\n\nBullets:\n{bullets_text}\n\nJob:\n{job_description}"
        
        elif task_name == 'write_summary':
            existing_summary = kwargs.get('existing_summary', '')
            job_desc = kwargs.get('job_description', '')
            return f"""Write a professional summary based on the person's ACTUAL experience.
IMPORTANT:
1. Write in FIRST PERSON using "I", "my", "me" (NOT third person like "John is...")
2. ONLY use information from their existing experience and skills
3. DO NOT invent fake companies, achievements, or qualifications
4. Keep it realistic and grounded in what they've actually done
5. Target it towards this job description: {job_desc}
5. If they have an existing summary, improve it while preserving key facts

Existing summary: {existing_summary}"""
        
        elif task_name == 'optimize_skills':
            existing_skills = kwargs.get('skills', '')
            job_desc = kwargs.get('job_description', '')
            return f"""Optimize this skills section for the job. 
IMPORTANT:
1. ONLY work with the ACTUAL skills the person has listed
2. DO NOT invent new skills they don't possess
3. Reorganize and phrase existing skills to better match the job
4. Remove irrelevant skills, add relevant keywords for ATS
5. Target this job: {job_desc}

Current skills: {existing_skills}"""
        
        elif task_name == 'psychological_optimize':
            text = kwargs.get('text', '')
            return f"Optimize this text for psychological impact and persuasion:\n\n{text}"
        
        elif task_name == 'gap_analysis':
            resume_text = kwargs.get('resume_text', '')
            job_description = kwargs.get('job_description', '')
            return f"Analyze gaps between this resume and job description. Return JSON with gaps and recommendations:\n\nResume:\n{resume_text}\n\nJob:\n{job_description}"
        
        else:
            return kwargs.get('prompt', '')

    def _parse_result(self, task_name: str, result_text: str) -> Dict[str, Any]:
        """Parse the result based on task type."""
        import json
        import re
        
        try:
            # Try to extract JSON from the response
            if task_name in ['extract_keywords', 'parse_resume_structure', 'split_sections', 'ats_score', 'optimize_skills', 'gap_analysis']:
                json_match = re.search(r'\{.*\}|\[.*\]', result_text, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group(0))
                    # For extract_keywords, the parsed_data is a list, so wrap it
                    if task_name == 'extract_keywords' and isinstance(parsed_data, list):
                        return {'result': parsed_data}
                    # For other tasks that return JSON, wrap the result
                    elif isinstance(parsed_data, dict):
                        return {'result': parsed_data}
                    else:
                        return parsed_data
            
            # For text-based tasks, return the text directly
            return {'result': result_text}
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            return {'result': result_text}


# Singleton instance
router = SimpleModelRouter()
