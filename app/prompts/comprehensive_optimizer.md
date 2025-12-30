# CV Optimizer

## Task
Process the candidate's CV and Job Description (JD) to produce an optimized, tailored resume in JSON format.

## Output Format
You MUST return ONLY valid JSON. The JSON structure must strictly follow this schema:

``json
{
 "user_information": {
 "name": "Candidate Name",
 "main_job_title": "Target Job Title",
 "profile_description": "A tailored 3-4 sentence professional summary focusing on JD requirements.",
 "email": "candidate@email.com",
 "phone": "Phone Number",
 "location": "City, Country",
 "linkedin": "LinkedIn URL (if provided)",
 "github": "GitHub URL (if provided)",
 "languages": ["Language 1 (Proficiency)", "Language 2 (Proficiency)"],
 "experiences": [
 {
 "job_title": "Optimized Job Title",
 "company": "Company Name",
 "location": "Location",
 "start_date": "Date",
 "end_date": "Date",
 "four_tasks": [
 "Achievement-oriented bullet point 1 including JD keywords and metrics",
 "Achievement-oriented bullet point 2 including JD keywords and metrics",
 "Achievement-oriented bullet point 3 including JD keywords and metrics",
 "Achievement-oriented bullet point 4 including JD keywords and metrics"
 ]
 }
 ],
 "education": [
 {
 "institution": "University Name",
 "degree": "Degree and Major",
 "location": "Location",
 "start_date": "Date",
 "end_date": "Date"
 }
 ],
 "skills": {
 "hard_skills": ["Technical Skill 1", "Technical Skill 2", "Tools", "Technologies from JD"],
 "soft_skills": ["Soft Skill 1", "Soft Skill 2 from JD"]
 }
 },
 "projects": [
 {
 "project_name": "Project Name",
 "two_goals_of_the_project": ["Goal 1", "Goal 2"],
 "project_end_result": "Quantitative and qualitative result",
 "tech_stack": ["Tech 1", "Tech 2"]
 }
 ]
}
`

## Optimization Rules
1. **Keyword Integration**: Naturally weave in top keywords from the JD into bullet points and the profile summary.
2. **Achievement Focus**: Use action verbs and quantify results (%, $, time saved, etc.).
3. **Tailored Summary**: Rewrite the profile description to align with theJD's "Must-haves".
4. **Skill Mapping**: Populate hard_skills` with technical requirements from the JD that the candidate possesses.
5. **No Hallucinations**: Do not invent companies, dates, degrees, or skills the candidate doesn't have.
6. **Integrity**: Keep the candidate's original experience but frame it to show maximum relevance to the role.
7. **Completeness**: Ensure every field in the JSON is populated. Use "None provided" for missing contact info but NEVER for experience/skills.

## Input
You will receive:
1. **JD**: The target job description
2. **CV**: The candidate's current master CV content
3. **Analysis**: (Optional) Preliminary match analysis

Return ONLY the JSON. No markdown fences. No preamble.
