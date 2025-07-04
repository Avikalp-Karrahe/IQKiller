from typing import Any, Dict, List, Optional
import re
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric
from text_extractor import extract_nobs, robust_json_parse

class ResumeParserMicroFunction:
    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        resume_text = data.get("resume_text", "")
        
        if not resume_text:
            return {**data, "resume_data": {"error": "No resume content provided"}}
        
        try:
            # Extract structured resume data
            resume_data = await self._extract_resume_data(resume_text)
            
            log_metric("resume_parse_success", {
                "skills_count": len(resume_data.get("skills", {}).get("technical", [])),
                "experience_count": len(resume_data.get("experience", [])),
                "projects_count": len(resume_data.get("projects", []))
            })
            
            return {**data, "resume_data": resume_data}
            
        except Exception as e:
            log_metric("resume_parse_error", {"error": str(e)})
            return {**data, "resume_data": {"error": f"Resume parsing failed: {e}"}}
    
    async def _extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured data from resume using LLM"""
        
        # Use robust extraction for large resumes
        structured_data = await extract_nobs(resume_text)
        
        if not structured_data or "error" in structured_data:
            # Fallback to basic LLM extraction
            prompt = f"""
Extract structured data from this resume:

{resume_text}

Return JSON with:
{{
  "personal_info": {{
    "name": "string",
    "email": "string", 
    "phone": "string",
    "location": "string",
    "linkedin": "string",
    "github": "string"
  }},
  "summary": "professional summary/objective",
  "skills": {{
    "technical": ["skill1", "skill2"],
    "programming_languages": ["Python", "JavaScript"],
    "frameworks": ["React", "Django"],
    "tools": ["Git", "Docker"],
    "databases": ["PostgreSQL", "MongoDB"],
    "cloud": ["AWS", "Azure"]
  }},
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Jan 2020 - Present",
      "location": "City, State",
      "responsibilities": ["bullet point 1", "bullet point 2"],
      "achievements": ["achievement 1", "achievement 2"],
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "education": [
    {{
      "degree": "Bachelor of Science",
      "field": "Computer Science", 
      "school": "University Name",
      "graduation": "2020",
      "gpa": "3.8",
      "relevant_courses": ["Data Structures", "Algorithms"]
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["tech1", "tech2"],
      "github": "github.com/repo",
      "demo": "live-demo-url"
    }}
  ],
  "certifications": [
    {{
      "name": "Certification Name",
      "issuer": "Organization",
      "date": "2023",
      "credential_id": "123456"
    }}
  ]
}}

Only return valid JSON, no extra text.
"""
            
            llm_response = llm_client.call_llm(prompt)
            
            # Parse JSON response
            try:
                resume_data = robust_json_parse(llm_response)
                if not resume_data:
                    raise ValueError("No valid JSON returned")
                return resume_data
            except Exception as e:
                log_metric("resume_llm_parse_error", {"error": str(e)})
                # Return basic extracted data as fallback
                return self._basic_extraction(resume_text)
        
        return structured_data
    
    def _basic_extraction(self, resume_text: str) -> Dict[str, Any]:
        """Basic regex-based extraction as fallback"""
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        email = email_match.group() if email_match else ""
        
        # Extract phone
        phone_match = re.search(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', resume_text)
        phone = phone_match.group() if phone_match else ""
        
        # Extract GitHub
        github_match = re.search(r'github\.com/[\w-]+', resume_text, re.IGNORECASE)
        github = f"https://{github_match.group()}" if github_match else ""
        
        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', resume_text, re.IGNORECASE)
        linkedin = f"https://{linkedin_match.group()}" if linkedin_match else ""
        
        # Extract common technical skills
        tech_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL', 
            'AWS', 'Docker', 'Git', 'Machine Learning', 'Data Science',
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Django', 'Flask'
        ]
        
        found_skills = []
        for skill in tech_keywords:
            if re.search(rf'\b{re.escape(skill)}\b', resume_text, re.IGNORECASE):
                found_skills.append(skill)
        
        return {
            "personal_info": {
                "email": email,
                "phone": phone,
                "github": github,
                "linkedin": linkedin
            },
            "skills": {
                "technical": found_skills
            },
            "extraction_method": "basic_fallback"
        } 