"""Prompts for AI-generated cover letters."""

COVER_LETTER_SYSTEM_PROMPT = """You are an expert career advisor and professional resume writer. 
Your task is to create a highly tailored cover letter that highlights the candidate's qualifications 
and aligns them with the job requirements. The cover letter should be professional, compelling, 
and demonstrate why the candidate is the perfect fit for the position."""

COVER_LETTER_PROMPT = """Please write a {tone} cover letter for the position of {job_title} at {company_name}.

Job Description:
{job_description}

Candidate's Resume:
{resume}

Additional Instructions:
- Length: {length}
- Tone: {tone}
- Additional instructions: {additional_instructions or 'None provided'}

Structure the cover letter with the following sections:
1. Professional header with contact information
2. Date and recipient information
3. Salutation
4. Opening paragraph that mentions the position and company
5. 2-3 body paragraphs highlighting relevant experience and skills
6. Closing paragraph expressing enthusiasm and next steps
7. Professional closing and signature

Make sure to:
- Tailor the content specifically to the job description
- Highlight the most relevant experiences and skills
- Use professional but engaging language
- Keep it concise and to the point
- Include specific examples of achievements
- Show knowledge about the company when possible"""
