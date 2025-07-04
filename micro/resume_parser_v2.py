"""
Enhanced Resume Parser v2.0
Provides structured extraction of skills, experience, projects, and education
with proper normalization and context understanding.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import re
import json
from dataclasses import dataclass, asdict
from llm_client import llm_client
from metrics import log_metric
import tiktoken

@dataclass
class Experience:
    title: str
    company: str
    duration: str
    location: str = ""
    responsibilities: List[str] = None
    achievements: List[str] = None
    technologies: List[str] = None
    start_date: str = ""
    end_date: str = ""
    is_current: bool = False
    
    def __post_init__(self):
        if self.responsibilities is None:
            self.responsibilities = []
        if self.achievements is None:
            self.achievements = []
        if self.technologies is None:
            self.technologies = []

@dataclass
class Project:
    name: str
    description: str
    technologies: List[str] = None
    github_url: str = ""
    demo_url: str = ""
    duration: str = ""
    key_features: List[str] = None
    
    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []
        if self.key_features is None:
            self.key_features = []

@dataclass
class Education:
    degree: str
    field: str
    school: str
    graduation_year: str = ""
    gpa: str = ""
    relevant_courses: List[str] = None
    honors: List[str] = None
    
    def __post_init__(self):
        if self.relevant_courses is None:
            self.relevant_courses = []
        if self.honors is None:
            self.honors = []

@dataclass
class Skills:
    technical: List[str] = None
    programming_languages: List[str] = None
    frameworks: List[str] = None
    tools: List[str] = None
    databases: List[str] = None
    cloud_platforms: List[str] = None
    methodologies: List[str] = None
    soft_skills: List[str] = None
    
    def __post_init__(self):
        for field in ['technical', 'programming_languages', 'frameworks', 'tools', 
                      'databases', 'cloud_platforms', 'methodologies', 'soft_skills']:
            if getattr(self, field) is None:
                setattr(self, field, [])

@dataclass
class ResumeData:
    personal_info: Dict[str, str]
    summary: str
    skills: Skills
    experience: List[Experience]
    education: List[Education]
    projects: List[Project]
    certifications: List[Dict[str, str]]
    languages: List[str]
    years_of_experience: int = 0
    
    def __post_init__(self):
        if not self.certifications:
            self.certifications = []
        if not self.languages:
            self.languages = []

class SkillsNormalizer:
    """Normalizes and categorizes skills with synonym detection"""
    
    def __init__(self):
        self.skill_synonyms = {
            # Programming Languages
            "python": ["python", "python3", "python 3", "py"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "node js"],
            "typescript": ["typescript", "ts"],
            "java": ["java", "java 8", "java 11", "java 17"],
            "csharp": ["c#", "csharp", "c sharp", ".net", "dotnet"],
            "cpp": ["c++", "cpp", "c plus plus"],
            "go": ["go", "golang"],
            "rust": ["rust", "rust-lang"],
            "swift": ["swift", "ios development"],
            "kotlin": ["kotlin", "android development"],
            "r": ["r", "r programming"],
            "scala": ["scala"],
            "php": ["php", "php 7", "php 8"],
            "ruby": ["ruby", "ruby on rails", "ror"],
            
            # Web Frameworks
            "react": ["react", "reactjs", "react.js", "react js"],
            "angular": ["angular", "angularjs", "angular 2+"],
            "vue": ["vue", "vue.js", "vuejs", "vue js"],
            "svelte": ["svelte", "sveltekit"],
            "django": ["django", "django rest framework", "drf"],
            "flask": ["flask", "flask-restful"],
            "fastapi": ["fastapi", "fast api"],
            "express": ["express", "express.js", "expressjs"],
            "spring": ["spring", "spring boot", "spring framework"],
            "laravel": ["laravel"],
            "rails": ["rails", "ruby on rails", "ror"],
            
            # Databases
            "postgresql": ["postgresql", "postgres", "pg", "psql"],
            "mysql": ["mysql", "my sql"],
            "mongodb": ["mongodb", "mongo", "mongo db"],
            "redis": ["redis"],
            "elasticsearch": ["elasticsearch", "elastic search"],
            "cassandra": ["cassandra", "apache cassandra"],
            "dynamodb": ["dynamodb", "dynamo db"],
            "sqlite": ["sqlite", "sqlite3"],
            
            # Cloud Platforms
            "aws": ["aws", "amazon web services", "amazon aws"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud", "google cloud platform"],
            "heroku": ["heroku"],
            "digitalocean": ["digitalocean", "digital ocean"],
            "vercel": ["vercel"],
            "netlify": ["netlify"],
            
            # DevOps & Tools
            "docker": ["docker", "containerization", "containers"],
            "kubernetes": ["kubernetes", "k8s", "container orchestration"],
            "jenkins": ["jenkins", "ci/cd"],
            "github actions": ["github actions", "gh actions"],
            "terraform": ["terraform", "infrastructure as code", "iac"],
            "ansible": ["ansible"],
            "git": ["git", "version control", "source control"],
            "linux": ["linux", "unix", "ubuntu", "centos"],
            
            # Data Science & ML
            "machine learning": ["machine learning", "ml", "artificial intelligence", "ai"],
            "deep learning": ["deep learning", "neural networks"],
            "tensorflow": ["tensorflow", "tf"],
            "pytorch": ["pytorch", "torch"],
            "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
            "pandas": ["pandas", "data manipulation"],
            "numpy": ["numpy", "numerical computing"],
            "matplotlib": ["matplotlib", "data visualization"],
            "seaborn": ["seaborn"],
            "jupyter": ["jupyter", "jupyter notebooks"],
            
            # Testing
            "pytest": ["pytest", "python testing"],
            "jest": ["jest", "javascript testing"],
            "selenium": ["selenium", "web automation"],
            "cypress": ["cypress", "e2e testing"],
            
            # Methodologies
            "agile": ["agile", "scrum", "kanban"],
            "devops": ["devops", "dev ops"],
            "microservices": ["microservices", "micro services"],
            "rest api": ["rest", "rest api", "restful", "api development"],
            "graphql": ["graphql", "graph ql"],
        }
        
        self.skill_categories = {
            "programming_languages": ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "swift", "kotlin", "r", "scala", "php", "ruby"],
            "frameworks": ["react", "angular", "vue", "svelte", "django", "flask", "fastapi", "express", "spring", "laravel", "rails"],
            "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "sqlite"],
            "cloud_platforms": ["aws", "azure", "gcp", "heroku", "digitalocean", "vercel", "netlify"],
            "tools": ["docker", "kubernetes", "jenkins", "github actions", "terraform", "ansible", "git", "linux", "pytest", "jest", "selenium", "cypress"],
            "methodologies": ["agile", "devops", "microservices", "rest api", "graphql"]
        }
    
    def normalize_skill(self, skill: str) -> Optional[str]:
        """Normalize a skill to its canonical form"""
        skill_lower = skill.lower().strip()
        
        for canonical, synonyms in self.skill_synonyms.items():
            if skill_lower in synonyms:
                return canonical
        
        return skill_lower if len(skill_lower) > 1 else None
    
    def categorize_skill(self, normalized_skill: str) -> str:
        """Categorize a normalized skill"""
        for category, skills in self.skill_categories.items():
            if normalized_skill in skills:
                return category
        return "technical"
    
    def normalize_skill_list(self, skills: List[str]) -> Dict[str, List[str]]:
        """Normalize and categorize a list of skills"""
        categorized = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_platforms": [],
            "tools": [],
            "methodologies": [],
            "technical": []
        }
        
        for skill in skills:
            normalized = self.normalize_skill(skill)
            if normalized:
                category = self.categorize_skill(normalized)
                if normalized not in categorized[category]:
                    categorized[category].append(normalized)
        
        return categorized

class ResumeParserV2:
    """Enhanced resume parser with structured extraction and normalization"""
    
    def __init__(self):
        self.skills_normalizer = SkillsNormalizer()
    
    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        resume_text = data.get("resume_text", "")
        
        if not resume_text:
            return {**data, "resume_data_v2": {"error": "No resume content provided"}}
        
        try:
            # Extract structured resume data
            resume_data = await self._extract_resume_data_structured(resume_text)
            
            log_metric("resume_parse_v2_success", {
                "skills_count": len(self._get_all_skills(resume_data.skills)),
                "experience_count": len(resume_data.experience),
                "projects_count": len(resume_data.projects),
                "years_experience": resume_data.years_of_experience
            })
            
            return {**data, "resume_data_v2": asdict(resume_data)}
            
        except Exception as e:
            log_metric("resume_parse_v2_error", {"error": str(e)})
            return {**data, "resume_data_v2": {"error": f"Resume parsing v2 failed: {e}"}}
    
    async def _extract_resume_data_structured(self, resume_text: str) -> ResumeData:
        """Extract structured resume data using multiple approaches"""
        
        # First, try comprehensive LLM extraction
        try:
            structured_data = await self._llm_extract_structured(resume_text)
            if structured_data:
                return structured_data
        except Exception as e:
            log_metric("resume_llm_extraction_error", {"error": str(e)})
        
        # Fallback to section-based extraction
        return await self._section_based_extraction(resume_text)
    
    async def _llm_extract_structured(self, resume_text: str) -> Optional[ResumeData]:
        """Use LLM to extract structured resume data"""
        
        # Check token count and chunk if necessary
        token_count = self._count_tokens(resume_text)
        if token_count > 15000:
            # For very long resumes, extract in sections
            return await self._chunked_extraction(resume_text)
        
        prompt = f"""
Extract comprehensive structured data from this resume. Return ONLY valid JSON with this exact structure:

{{
  "personal_info": {{
    "name": "Full Name",
    "email": "email@domain.com",
    "phone": "+1234567890",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "website": "personal-website.com"
  }},
  "summary": "Professional summary or objective statement",
  "skills": {{
    "technical": ["skill1", "skill2"],
    "programming_languages": ["Python", "JavaScript"],
    "frameworks": ["React", "Django"],
    "tools": ["Git", "Docker"],
    "databases": ["PostgreSQL", "MongoDB"],
    "cloud_platforms": ["AWS", "Azure"],
    "methodologies": ["Agile", "DevOps"],
    "soft_skills": ["Leadership", "Communication"]
  }},
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Jan 2020 - Present",
      "location": "City, State",
      "start_date": "2020-01",
      "end_date": "Present",
      "is_current": true,
      "responsibilities": ["responsibility 1", "responsibility 2"],
      "achievements": ["achievement 1", "achievement 2"],
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "education": [
    {{
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "school": "University Name",
      "graduation_year": "2020",
      "gpa": "3.8",
      "relevant_courses": ["Data Structures", "Algorithms"],
      "honors": ["Dean's List", "Magna Cum Laude"]
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description of the project",
      "technologies": ["tech1", "tech2"],
      "github_url": "github.com/user/repo",
      "demo_url": "live-demo-url.com",
      "duration": "3 months",
      "key_features": ["feature1", "feature2"]
    }}
  ],
  "certifications": [
    {{
      "name": "Certification Name",
      "issuer": "Organization",
      "date": "2023",
      "credential_id": "123456"
    }}
  ],
  "languages": ["English (Native)", "Spanish (Conversational)"],
  "years_of_experience": 5
}}

Important guidelines:
1. Extract ALL skills mentioned, including those in job descriptions and projects
2. Normalize technology names (e.g., "React.js" → "React", "ML" → "Machine Learning")
3. Calculate years_of_experience from work history
4. Parse dates in YYYY-MM format when possible
5. Group similar skills appropriately
6. Extract quantifiable achievements when possible
7. If information is missing, omit the field or use empty array/string

Resume text:
{resume_text}
"""
        
        try:
            response = llm_client.call_llm(prompt, temperature=0, max_tokens=4000)
            data = json.loads(response)
            
            # Convert to structured objects
            return self._convert_to_resume_data(data)
            
        except json.JSONDecodeError as e:
            log_metric("resume_json_parse_error", {"error": str(e)})
            return None
        except Exception as e:
            log_metric("resume_llm_error", {"error": str(e)})
            return None
    
    async def _chunked_extraction(self, resume_text: str) -> ResumeData:
        """Extract data from long resumes by processing in chunks"""
        
        sections = self._split_resume_sections(resume_text)
        
        # Extract each section separately
        personal_info = await self._extract_personal_info(sections.get("header", ""))
        summary = await self._extract_summary(sections.get("summary", ""))
        skills = await self._extract_skills(sections.get("skills", ""))
        experience = await self._extract_experience(sections.get("experience", ""))
        education = await self._extract_education(sections.get("education", ""))
        projects = await self._extract_projects(sections.get("projects", ""))
        certifications = await self._extract_certifications(sections.get("certifications", ""))
        
        # Calculate years of experience
        years_exp = self._calculate_years_experience(experience)
        
        return ResumeData(
            personal_info=personal_info,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            languages=[],
            years_of_experience=years_exp
        )
    
    async def _section_based_extraction(self, resume_text: str) -> ResumeData:
        """Fallback extraction using regex and basic parsing"""
        
        # Basic regex-based extraction
        personal_info = self._extract_personal_info_regex(resume_text)
        skills = self._extract_skills_regex(resume_text)
        
        return ResumeData(
            personal_info=personal_info,
            summary="",
            skills=skills,
            experience=[],
            education=[],
            projects=[],
            certifications=[],
            languages=[],
            years_of_experience=0
        )
    
    def _convert_to_resume_data(self, data: Dict[str, Any]) -> ResumeData:
        """Convert parsed JSON to ResumeData objects"""
        
        # Parse skills with normalization
        skills_data = data.get("skills", {})
        all_skills = []
        for skill_list in skills_data.values():
            if isinstance(skill_list, list):
                all_skills.extend(skill_list)
        
        normalized_skills = self.skills_normalizer.normalize_skill_list(all_skills)
        skills = Skills(**normalized_skills)
        
        # Parse experience
        experience = []
        for exp_data in data.get("experience", []):
            exp = Experience(**exp_data)
            experience.append(exp)
        
        # Parse education
        education = []
        for edu_data in data.get("education", []):
            edu = Education(**edu_data)
            education.append(edu)
        
        # Parse projects
        projects = []
        for proj_data in data.get("projects", []):
            proj = Project(**proj_data)
            projects.append(proj)
        
        return ResumeData(
            personal_info=data.get("personal_info", {}),
            summary=data.get("summary", ""),
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=data.get("certifications", []),
            languages=data.get("languages", []),
            years_of_experience=data.get("years_of_experience", 0)
        )
    
    def _get_all_skills(self, skills: Skills) -> List[str]:
        """Get all skills as a flat list"""
        all_skills = []
        for field in ['technical', 'programming_languages', 'frameworks', 'tools', 
                      'databases', 'cloud_platforms', 'methodologies']:
            all_skills.extend(getattr(skills, field, []))
        return all_skills
    
    def _split_resume_sections(self, resume_text: str) -> Dict[str, str]:
        """Split resume into sections using common headers"""
        
        sections = {}
        current_section = "header"
        current_content = []
        
        # Common section headers
        section_patterns = {
            r'(experience|work experience|employment|professional experience)': 'experience',
            r'(education|academic background)': 'education',
            r'(skills|technical skills|core competencies)': 'skills',
            r'(projects|personal projects|side projects)': 'projects',
            r'(summary|objective|profile)': 'summary',
            r'(certifications|licenses)': 'certifications'
        }
        
        lines = resume_text.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            section_found = False
            for pattern, section_name in section_patterns.items():
                if re.search(pattern, line_lower):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_personal_info_regex(self, text: str) -> Dict[str, str]:
        """Extract personal information using regex"""
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        email = email_match.group() if email_match else ""
        
        # Phone
        phone_match = re.search(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
        phone = phone_match.group() if phone_match else ""
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        linkedin = f"https://{linkedin_match.group()}" if linkedin_match else ""
        
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        github = f"https://{github_match.group()}" if github_match else ""
        
        return {
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github
        }
    
    def _extract_skills_regex(self, text: str) -> Skills:
        """Extract skills using regex patterns"""
        
        # Common technical skills to look for
        tech_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL', 
            'AWS', 'Docker', 'Git', 'Machine Learning', 'Data Science',
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Django', 'Flask',
            'PostgreSQL', 'MongoDB', 'Redis', 'Kubernetes', 'Jenkins'
        ]
        
        found_skills = []
        for skill in tech_keywords:
            if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        # Normalize skills
        normalized = self.skills_normalizer.normalize_skill_list(found_skills)
        
        return Skills(**normalized)
    
    def _calculate_years_experience(self, experience: List[Experience]) -> int:
        """Calculate total years of experience"""
        if not experience:
            return 0
        
        # Simple calculation based on number of roles
        # In practice, you'd want to parse dates and calculate overlap
        return len(experience)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            encoding = tiktoken.encoding_for_model("gpt-4o-mini")
            return len(encoding.encode(text))
        except:
            # Fallback: approximate as 4 chars per token
            return len(text) // 4
    
    # Placeholder methods for individual section extraction
    # These would be implemented with specific LLM calls for each section
    
    async def _extract_personal_info(self, text: str) -> Dict[str, str]:
        return self._extract_personal_info_regex(text)
    
    async def _extract_summary(self, text: str) -> str:
        return text.strip()
    
    async def _extract_skills(self, text: str) -> Skills:
        return self._extract_skills_regex(text)
    
    async def _extract_experience(self, text: str) -> List[Experience]:
        return []
    
    async def _extract_education(self, text: str) -> List[Education]:
        return []
    
    async def _extract_projects(self, text: str) -> List[Project]:
        return []
    
    async def _extract_certifications(self, text: str) -> List[Dict[str, str]]:
        return [] 