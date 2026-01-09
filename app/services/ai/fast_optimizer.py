
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from app.utils.token_tracker import TokenTracker

logger = logging.getLogger(__name__)


class KeywordCache:
    """Simple in-memory cache for keywords to avoid re-extraction."""
    _cache = {}
    _ttl = 3600  # 1 hour

    @classmethod
    def get(cls, key):
        if key in cls._cache:
            data, timestamp = cls._cache[key]
            if time.time() - timestamp < cls._ttl:
                return data
            else:
                del cls._cache[key]
        return None

    @classmethod
    def set(cls, key, value):
        cls._cache[key] = (value, time.time())


class UltraFastResumeOptimizer:
    """Optimizes resume sections in parallel using ThreadPoolExecutor.
    """

    def __init__(self, model_name: str, api_key: str, api_base: str, max_workers: int = 5):
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.max_workers = max_workers

        # We create a separate LLM instance/chain factory here or reusing existing
        # Ideally, we create a lightweight chain function.
        self.llm = TokenTracker.get_tracked_langchain_llm(
            model_name=self.model_name,
            temperature=0.2,
            api_key=self.api_key,
            api_base=self.api_base,
            feature="fast_optimization"
        )

    def optimize_resume(self, resume_data: Dict, job_description: str) -> Dict:
        """Main entry point for fast optimization.
        Breaks the resume into sections and optimizes them concurrently.
        """
        start_time = time.time()
        logger.info("Starting fast parallel resume optimization")

        # 1. Extract Keywords (Cached)
        keywords = self._get_keywords(job_description)
        logger.info(
            f"Keywords extracted: {len(keywords)} in {time.time() - start_time:.2f}s")

        # 2. Prepare Tasks
        # We need to optimize: Profile Summary, Experience (each job), Projects (each project)
        # Skills are usually just re-ordered or keyword injected.

        tasks = []

        # Task: User Information / Profile Summary
        if "user_information" in resume_data:
            tasks.append({
                "type": "summary",
                "content": resume_data["user_information"],
                "target": "user_information"
            })

        # Tasks: Experience (One task per job)
        if "experiences" in resume_data.get("user_information", {}):
            for i, exp in enumerate(resume_data["user_information"]["experiences"]):
                tasks.append({
                    "type": "experience",
                    "content": exp,
                    "index": i,
                    "target": "experience"
                })

        # Tasks: Projects (One task per project)
        if "projects" in resume_data and resume_data["projects"]:
            for i, proj in enumerate(resume_data["projects"]):
                tasks.append({
                    "type": "project",
                    "content": proj,
                    "index": i,
                    "target": "project"
                })

        # Skills optimization can be done quickly in main thread or parallel, let's parallelize
        if "skills" in resume_data.get("user_information", {}):
            tasks.append({
                "type": "skills",
                "content": resume_data["user_information"]["skills"],
                "target": "skills"
            })

        # 3. Parallel Execution
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self._optimize_section, task, keywords): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()

                    if task["target"] == "user_information":
                        results["user_information"] = result

                    elif task["target"] == "experience":
                        if "experiences" not in results:
                            results["experiences"] = {}
                        results["experiences"][task["index"]] = result

                    elif task["target"] == "project":
                        if "projects" not in results:
                            results["projects"] = {}
                        results["projects"][task["index"]] = result

                    elif task["target"] == "skills":
                        results["skills"] = result

                except Exception as e:
                    logger.error(
                        f"Error optimizing section {task['type']}: {e}")
                    # Fallback to original content?
                    pass

        # 4. Re-assemble Resume Data
        optimized_resume = resume_data.copy()

        # Update Summary
        if "user_information" in results:
            # We assume result returns partial update (e.g. updated summary string)
            # Actually, simpler: we update specific fields.
            # Let's say _optimize_section returns a dict of updated fields.
            optimized_resume["user_information"].update(
                results["user_information"])

        # Update Experiences
        if "experiences" in results:
            # Sort by index to maintain order
            sorted_indices = sorted(results["experiences"].keys())
            orig_exps = optimized_resume["user_information"]["experiences"]
            for idx in sorted_indices:
                orig_exps[idx] = results["experiences"][idx]

        # Update Projects
        if "projects" in results and "projects" in optimized_resume:
            sorted_indices = sorted(results["projects"].keys())
            orig_projs = optimized_resume["projects"]
            for idx in sorted_indices:
                orig_projs[idx] = results["projects"][idx]

        # Update Skills
        if "skills" in results:
            optimized_resume["user_information"]["skills"] = results["skills"]

        logger.info(
            f"Total optimization time: {time.time() - start_time:.2f}s")
        return optimized_resume

    def _get_keywords(self, job_description: str) -> List[str]:
        """Extract keywords using cache or minimal LLM call"""
        cached_key = hashlib.md5(job_description.encode()).hexdigest()
        cached = KeywordCache.get(cached_key)
        if cached:
            return cached

        prompt = f"""Extract 15 key technical skills and keywords from this job description. 
        Return ONLY a comma-separated list.
        
        JD: {job_description[:1500]}
        """
        try:
            response = self.llm.invoke(prompt).content
            keywords = [k.strip() for k in response.split(",") if k.strip()]
            KeywordCache.set(cached_key, keywords)
            return keywords
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    def _optimize_section(self, task: Dict, keywords: List[str]) -> Dict:
        """Router for optimizing specific sections with specific prompts"""
        content = task["content"]
        keywords_str = ", ".join(keywords[:8])  # Top 8 keywords

        if task["type"] == "summary":
            # Profile Summary Optimization
            prompt = f"""Rewrite this professional profile summary to align with these keywords: {keywords_str}.
            Write in FIRST PERSON using "I", "my", "me" (NOT third person).
            Use strong "Power Verbs". Keep it punchy (3-4 sentences).
            Current: {content.get('profile_description', '')}
            
            Return ONLY the rewritten text.
            """
            new_summary = self.llm.invoke(prompt).content.strip()
            return {"profile_description": new_summary}

        elif task["type"] == "experience":
            # SOAR Optimization for Experience
            # content is an 'Experience' dict
            role = content.get("job_title", "")
            company = content.get("company", "")
            tasks = content.get("four_tasks", [])
            tasks_text = "\n".join(tasks)

            prompt = f"""Optimize this work experience for role '{role}' at '{company}'.
             Integrate keywords: {keywords_str}.
             Rewrite the bullet points using the SOAR (Situation, Obstacle, Action, Result) method.
             Quantify results where possible.
             Output must be a JSON list of strings (bullet points).
             
             Current Bullets:
             {tasks_text}
             
             Return ONLY a JSON list, e.g. ["Point 1", "Point 2"]
             """
            response = self.llm.invoke(prompt).content
            try:
                # Extract JSON list
                import re
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    new_tasks = json.loads(match.group(0))
                    # Ensure constraints (1-6 items)
                    new_tasks = new_tasks[:6]
                    content_copy = content.copy()
                    content_copy["four_tasks"] = new_tasks
                    return content_copy
                else:
                    return content  # Fail gracefully
            except:
                return content

        elif task["type"] == "project":
            # Project Optimization
            goals = content.get("two_goals_of_the_project", [])
            goals_text = "\n".join(goals)

            prompt = f"""Optimize these project goals using keywords: {keywords_str}.
             Make them impact-focused.
             
             Current Goals:
             {goals_text}
             
             Return ONLY a JSON list of strings.
             """
            response = self.llm.invoke(prompt).content
            try:
                import re
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    new_goals = json.loads(match.group(0))
                    content_copy = content.copy()
                    content_copy["two_goals_of_the_project"] = new_goals[:4]
                    return content_copy
                else:
                    return content
            except:
                return content

        elif task["type"] == "skills":
            # Skills Optimization
            hard = content.get("hard_skills", [])
            soft = content.get("soft_skills", [])

            prompt = f"""Reorder and enhance these skills based on importance: {keywords_str}.
             Add missing relevant skills from the list if applicable.
             
             Hard Skills: {hard}
             Soft Skills: {soft}
             
             Return JSON object: {{"hard_skills": [...], "soft_skills": [...]}}
             """
            response = self.llm.invoke(prompt).content
            try:
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    new_skills = json.loads(match.group(0))
                    return new_skills
                else:
                    return content
            except:
                return content

        return content
