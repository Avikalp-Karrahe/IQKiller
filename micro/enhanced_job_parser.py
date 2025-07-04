"""
Enhanced Job Requirements Parser
Extracts structured job requirements with experience levels, context, and priorities
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from dataclasses import dataclass, asdict
from llm_client import LLMClient
from metrics import log_metric
import json

@dataclass
class JobRequirement:
    skill: str
    category: str  # technical, experience, education, soft_skill, certification
    importance: str  # required, preferred, nice_to_have
    experience_level: str  # entry, mid, senior, expert
    context: str  # Where this requirement was mentioned
    synonyms: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []

@dataclass
class JobStructuredData:
    role: str
    company: str
    location: str
    seniority_level: str
    tech_requirements: List[JobRequirement]
    experience_requirements: List[JobRequirement]
    education_requirements: List[JobRequirement]
    soft_skill_requirements: List[JobRequirement]
    responsibilities: List[str]
    nice_to_haves: List[str]
    years_experience_required: int
    salary_range: Tuple[Optional[int], Optional[int]]
    remote_type: str  # remote, hybrid, onsite
    company_stage: str  # startup, scale-up, enterprise
    
    def __post_init__(self):
        if not self.tech_requirements:
            self.tech_requirements = []
        if not self.experience_requirements:
            self.experience_requirements = []
        if not self.education_requirements:
            self.education_requirements = []
        if not self.soft_skill_requirements:
            self.soft_skill_requirements = []
        if not self.responsibilities:
            self.responsibilities = []
        if not self.nice_to_haves:
            self.nice_to_haves = []

class RequirementsNormalizer:
    """Normalizes job requirements and identifies synonyms"""
    
    def __init__(self):
        self.experience_indicators = {
            "entry": ["entry", "junior", "0-2 years", "new grad", "graduate", "recent grad", "0+ years"],
            "mid": ["mid", "intermediate", "2-5 years", "3-5 years", "2+ years", "3+ years"],
            "senior": ["senior", "5+ years", "5-8 years", "experienced", "6+ years", "7+ years"],
            "expert": ["expert", "lead", "principal", "8+ years", "10+ years", "architect"]
        }
        
        self.importance_indicators = {
            "required": ["required", "must have", "essential", "mandatory", "necessary"],
            "preferred": ["preferred", "desired", "strong preference", "ideal"],
            "nice_to_have": ["nice to have", "plus", "bonus", "would be great", "advantageous"]
        }
        
        self.category_patterns = {
            "technical": [
                r"\b(python|javascript|java|react|angular|vue|django|flask|aws|azure|docker|kubernetes)\b",
                r"\b(sql|nosql|postgresql|mongodb|redis|git|linux|api|rest|graphql)\b",
                r"\b(machine learning|ml|ai|data science|tensorflow|pytorch|pandas|numpy)\b"
            ],
            "experience": [
                r"\b(\d+)[\+\-\s]*years?\s+(of\s+)?experience\b",
                r"\bexperience\s+with\b",
                r"\bproficient\s+in\b",
                r"\bworked\s+with\b"
            ],
            "education": [
                r"\b(bachelor|master|phd|degree|bs|ms|ba|ma)\b",
                r"\b(computer science|engineering|mathematics|statistics)\b"
            ],
            "soft_skill": [
                r"\b(communication|leadership|teamwork|problem.solving|analytical)\b",
                r"\b(collaboration|mentoring|presentation|writing)\b"
            ]
        }
    
    def extract_experience_level(self, text: str) -> str:
        """Extract experience level from requirement text"""
        text_lower = text.lower()
        
        for level, indicators in self.experience_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return level
        
        return "mid"  # Default
    
    def extract_importance(self, text: str, context: str = "") -> str:
        """Extract importance level from requirement text"""
        combined_text = (text + " " + context).lower()
        
        for importance, indicators in self.importance_indicators.items():
            for indicator in indicators:
                if indicator in combined_text:
                    return importance
        
        return "required"  # Default
    
    def categorize_requirement(self, text: str) -> str:
        """Categorize a requirement"""
        text_lower = text.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return category
        
        return "technical"  # Default

class EnhancedJobParser:
    """Enhanced job parser that extracts structured requirements with context"""
    
    def __init__(self):
        self.normalizer = RequirementsNormalizer()
        self.llm_client = LLMClient()
    
    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        job_text = data.get("scraped", {}).get("content", "")
        enriched_data = data.get("enriched", {})
        
        if not job_text and not enriched_data:
            return {**data, "job_data_enhanced": {"error": "No job content available"}}
        
        try:
            # Extract structured job requirements
            job_data = await self._extract_job_requirements_structured(job_text, enriched_data)
            
            log_metric("job_parse_enhanced_success", {
                "tech_requirements": len(job_data.tech_requirements),
                "total_requirements": len(job_data.tech_requirements) + len(job_data.experience_requirements),
                "years_required": job_data.years_experience_required
            })
            
            return {**data, "job_data_enhanced": asdict(job_data)}
            
        except Exception as e:
            log_metric("job_parse_enhanced_error", {"error": str(e)})
            return {**data, "job_data_enhanced": {"error": f"Enhanced job parsing failed: {e}"}}
    
    async def _extract_job_requirements_structured(self, job_text: str, enriched_data: Dict[str, Any]) -> JobStructuredData:
        """Extract structured job requirements using LLM and pattern matching"""
        
        # First try LLM extraction for detailed analysis
        try:
            llm_data = await self._llm_extract_requirements(job_text)
            if llm_data:
                return llm_data
        except Exception as e:
            log_metric("job_llm_extraction_error", {"error": str(e)})
        
        # Fallback to pattern-based extraction
        return self._pattern_based_extraction(job_text, enriched_data)
    
    async def _llm_extract_requirements(self, job_text: str) -> Optional[JobStructuredData]:
        """Use LLM to extract detailed job requirements"""
        
        prompt = f"""
Analyze this job posting and extract structured requirements. Return ONLY valid JSON:

{{
  "role": "Job Title",
  "company": "Company Name", 
  "location": "City, State",
  "seniority_level": "entry|mid|senior|lead",
  "years_experience_required": 5,
  "salary_range": [100000, 150000],
  "remote_type": "remote|hybrid|onsite",
  "company_stage": "startup|scale-up|enterprise",
  "tech_requirements": [
    {{
      "skill": "Python",
      "category": "technical",
      "importance": "required|preferred|nice_to_have", 
      "experience_level": "entry|mid|senior|expert",
      "context": "Where this was mentioned in the posting",
      "synonyms": ["Python3", "py"]
    }}
  ],
  "experience_requirements": [
    {{
      "skill": "Web development experience",
      "category": "experience",
      "importance": "required",
      "experience_level": "mid",
      "context": "Must have 3+ years building web applications",
      "synonyms": ["full-stack development", "web dev"]
    }}
  ],
  "education_requirements": [
    {{
      "skill": "Bachelor's degree",
      "category": "education", 
      "importance": "preferred",
      "experience_level": "entry",
      "context": "BS in Computer Science or equivalent",
      "synonyms": ["BS", "undergraduate degree"]
    }}
  ],
  "soft_skill_requirements": [
    {{
      "skill": "Communication",
      "category": "soft_skill",
      "importance": "required", 
      "experience_level": "mid",
      "context": "Strong written and verbal communication",
      "synonyms": ["written communication", "verbal skills"]
    }}
  ],
  "responsibilities": [
    "Design and develop web applications",
    "Collaborate with cross-functional teams"
  ],
  "nice_to_haves": [
    "Experience with cloud platforms",
    "Open source contributions"
  ]
}}

Guidelines:
1. Extract ALL technical skills, tools, frameworks, languages mentioned
2. Identify experience level indicators (junior, senior, X+ years)
3. Categorize by importance (required vs preferred vs nice-to-have)
4. Include context of where each requirement was mentioned
5. Add synonyms for technologies (React/ReactJS, ML/Machine Learning)
6. Parse salary ranges and years of experience
7. Determine company stage from description
8. Identify remote work policy

Job posting:
{job_text}
"""
        
        try:
            response = self.llm_client.call_llm(prompt, temperature=0, max_tokens=4000)
            
            # Clean response to extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
            else:
                json_str = response
            
            data = json.loads(json_str)
            
            # Convert to structured objects
            return self._convert_to_job_data(data)
            
        except json.JSONDecodeError as e:
            log_metric("job_json_parse_error", {"error": str(e), "response": response[:500]})
            return None
        except Exception as e:
            log_metric("job_llm_error", {"error": str(e)})
            return None
    
    def _pattern_based_extraction(self, job_text: str, enriched_data: Dict[str, Any]) -> JobStructuredData:
        """Fallback pattern-based extraction"""
        
        # Extract basic info from enriched data
        role = enriched_data.get("role", "Unknown Role")
        company = enriched_data.get("company", "Unknown Company")
        location = enriched_data.get("location", "")
        
        # Extract years of experience
        years_exp = self._extract_years_experience(job_text)
        
        # Extract technical requirements using patterns
        tech_requirements = self._extract_technical_requirements_pattern(job_text)
        
        # Extract salary range
        salary_range = self._extract_salary_range(job_text)
        
        return JobStructuredData(
            role=role,
            company=company,
            location=location,
            seniority_level=self._determine_seniority(job_text, years_exp),
            tech_requirements=tech_requirements,
            experience_requirements=[],
            education_requirements=[],
            soft_skill_requirements=[],
            responsibilities=[],
            nice_to_haves=[],
            years_experience_required=years_exp,
            salary_range=salary_range,
            remote_type=self._extract_remote_type(job_text),
            company_stage=self._determine_company_stage(job_text)
        )
    
    def _convert_to_job_data(self, data: Dict[str, Any]) -> JobStructuredData:
        """Convert parsed JSON to JobStructuredData objects"""
        
        # Convert requirement lists
        tech_reqs = []
        for req_data in data.get("tech_requirements", []):
            tech_reqs.append(JobRequirement(**req_data))
        
        exp_reqs = []
        for req_data in data.get("experience_requirements", []):
            exp_reqs.append(JobRequirement(**req_data))
        
        edu_reqs = []
        for req_data in data.get("education_requirements", []):
            edu_reqs.append(JobRequirement(**req_data))
        
        soft_reqs = []
        for req_data in data.get("soft_skill_requirements", []):
            soft_reqs.append(JobRequirement(**req_data))
        
        # Handle salary range
        salary_data = data.get("salary_range", [None, None])
        if isinstance(salary_data, list) and len(salary_data) >= 2:
            salary_range = (salary_data[0], salary_data[1])
        else:
            salary_range = (None, None)
        
        return JobStructuredData(
            role=data.get("role", "Unknown Role"),
            company=data.get("company", "Unknown Company"),
            location=data.get("location", ""),
            seniority_level=data.get("seniority_level", "mid"),
            tech_requirements=tech_reqs,
            experience_requirements=exp_reqs,
            education_requirements=edu_reqs,
            soft_skill_requirements=soft_reqs,
            responsibilities=data.get("responsibilities", []),
            nice_to_haves=data.get("nice_to_haves", []),
            years_experience_required=data.get("years_experience_required", 0),
            salary_range=salary_range,
            remote_type=data.get("remote_type", "onsite"),
            company_stage=data.get("company_stage", "enterprise")
        )
    
    def _extract_years_experience(self, text: str) -> int:
        """Extract years of experience required"""
        
        # Pattern for X+ years
        pattern = r'(\d+)\+?\s*years?\s+(?:of\s+)?experience'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            return int(matches[0])
        
        # Check for seniority indicators
        if any(word in text.lower() for word in ['senior', 'lead', 'principal']):
            return 5
        elif any(word in text.lower() for word in ['junior', 'entry', 'graduate']):
            return 0
        
        return 2  # Default
    
    def _extract_technical_requirements_pattern(self, text: str) -> List[JobRequirement]:
        """Extract technical requirements using pattern matching"""
        
        # Common tech patterns
        tech_patterns = [
            r'\b(Python|JavaScript|Java|C\+\+|C#|Ruby|Go|Rust|Swift|Kotlin)\b',
            r'\b(React|Angular|Vue|Django|Flask|Spring|Rails|Laravel)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Git|SQL|NoSQL)\b',
            r'\b(Machine Learning|ML|AI|Deep Learning|TensorFlow|PyTorch)\b',
            r'\b(PostgreSQL|MongoDB|Redis|MySQL|Elasticsearch)\b'
        ]
        
        requirements = []
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Determine importance and experience level from context
                context_start = max(0, text.lower().find(match.lower()) - 50)
                context_end = min(len(text), text.lower().find(match.lower()) + len(match) + 50)
                context = text[context_start:context_end]
                
                importance = self.normalizer.extract_importance(match, context)
                experience_level = self.normalizer.extract_experience_level(context)
                
                req = JobRequirement(
                    skill=match,
                    category="technical",
                    importance=importance,
                    experience_level=experience_level,
                    context=context.strip(),
                    synonyms=[]
                )
                requirements.append(req)
        
        return requirements
    
    def _extract_salary_range(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract salary range from text"""
        
        # Pattern for salary ranges
        patterns = [
            r'\$(\d+)k?\s*-\s*\$?(\d+)k?',
            r'\$(\d+),?(\d+)?\s*-\s*\$?(\d+),?(\d+)?',
            r'(\d+)k?\s*-\s*(\d+)k?\s*(?:per\s+year|annually|\$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                match = matches[0]
                try:
                    if len(match) >= 2:
                        low = int(match[0]) * 1000 if 'k' in text.lower() else int(match[0])
                        high = int(match[1]) * 1000 if 'k' in text.lower() else int(match[1])
                        return (low, high)
                except:
                    continue
        
        return (None, None)
    
    def _determine_seniority(self, text: str, years_exp: int) -> str:
        """Determine seniority level"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['senior', 'sr.', 'lead', 'principal']):
            return "senior"
        elif any(word in text_lower for word in ['junior', 'jr.', 'entry', 'graduate']):
            return "entry"
        elif years_exp >= 5:
            return "senior"
        elif years_exp <= 1:
            return "entry"
        else:
            return "mid"
    
    def _extract_remote_type(self, text: str) -> str:
        """Extract remote work type"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['remote', 'work from home', 'distributed']):
            return "remote"
        elif any(word in text_lower for word in ['hybrid', 'flexible', 'part remote']):
            return "hybrid"
        else:
            return "onsite"
    
    def _determine_company_stage(self, text: str) -> str:
        """Determine company stage"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['startup', 'early stage', 'seed', 'series a']):
            return "startup"
        elif any(word in text_lower for word in ['scale up', 'series b', 'series c', 'growth']):
            return "scale-up"
        elif any(word in text_lower for word in ['fortune', 'enterprise', 'established', 'public company']):
            return "enterprise"
        else:
            return "enterprise"  # Default 