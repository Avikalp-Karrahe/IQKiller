from typing import Any, Dict, List, Optional, Set
import re
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric

class GapAnalysisMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        resume_data = data.get("resume_data", {})
        enriched_data = data.get("enriched", {})
        
        if not resume_data or "error" in resume_data:
            return {**data, "gap_analysis": {"error": "No resume data available"}}
        
        if not enriched_data or enriched_data.get("error"):
            return {**data, "gap_analysis": {"error": "No job data available"}}
        
        try:
            # Perform comprehensive gap analysis
            gap_analysis = self._analyze_gaps(resume_data, enriched_data)
            
            log_metric("gap_analysis_success", {
                "match_score": gap_analysis.get("match_score", 0),
                "strong_matches": len(gap_analysis.get("strong_matches", [])),
                "gaps": len(gap_analysis.get("gaps", []))
            })
            
            return {**data, "gap_analysis": gap_analysis}
            
        except Exception as e:
            log_metric("gap_analysis_error", {"error": str(e)})
            return {**data, "gap_analysis": {"error": f"Gap analysis failed: {e}"}}
    
    def _analyze_gaps(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed gap analysis between resume and job requirements"""
        
        # Extract skills from resume
        resume_skills = self._extract_resume_skills(resume_data)
        
        # Extract requirements from job
        job_requirements = self._extract_job_requirements(job_data)
        
        # Perform skill matching
        strong_matches = []
        partial_matches = []
        gaps = []
        
        for req in job_requirements:
            req_lower = req.lower()
            match_type = self._find_skill_match(req_lower, resume_skills)
            
            if match_type == "strong":
                strong_matches.append(req)
            elif match_type == "partial":
                partial_matches.append(req)
            else:
                gaps.append(req)
        
        # Calculate match score (0-100)
        total_requirements = len(job_requirements)
        if total_requirements == 0:
            match_score = 50  # Default if no requirements found
        else:
            strong_weight = 1.0
            partial_weight = 0.5
            score = (len(strong_matches) * strong_weight + len(partial_matches) * partial_weight) / total_requirements * 100
            match_score = min(100, max(0, round(score)))
        
        # Generate narrative summary
        summary = self._generate_summary(strong_matches, partial_matches, gaps, match_score)
        
        # Create skills map for visualization
        skills_map = self._create_skills_map(strong_matches, partial_matches, gaps)
        
        return {
            "match_score": match_score,
            "strong_matches": strong_matches,
            "partial_matches": partial_matches,
            "gaps": gaps,
            "summary": summary,
            "skills_map": skills_map,
            "resume_skills_count": len(resume_skills),
            "job_requirements_count": total_requirements
        }
    
    def _extract_resume_skills(self, resume_data: Dict[str, Any]) -> Set[str]:
        """Extract all skills from resume data"""
        skills = set()
        
        # Technical skills
        skills_section = resume_data.get("skills", {})
        if isinstance(skills_section, dict):
            for skill_category in skills_section.values():
                if isinstance(skill_category, list):
                    skills.update([skill.lower() for skill in skill_category])
        
        # Skills from experience
        experience = resume_data.get("experience", [])
        for exp in experience:
            if isinstance(exp, dict):
                technologies = exp.get("technologies", [])
                if isinstance(technologies, list):
                    skills.update([tech.lower() for tech in technologies])
        
        # Skills from projects
        projects = resume_data.get("projects", [])
        for proj in projects:
            if isinstance(proj, dict):
                technologies = proj.get("technologies", [])
                if isinstance(technologies, list):
                    skills.update([tech.lower() for tech in technologies])
        
        return skills
    
    def _extract_job_requirements(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract requirements from job data"""
        requirements = []
        
        # From requirements field
        job_reqs = job_data.get("requirements", [])
        if isinstance(job_reqs, list):
            requirements.extend(job_reqs)
        elif isinstance(job_reqs, str):
            # Split by common delimiters
            requirements.extend(re.split(r'[,;\n•\-]', job_reqs))
        
        # From tech stack
        tech_stack = job_data.get("tech_stack", [])
        if isinstance(tech_stack, list):
            requirements.extend(tech_stack)
        elif isinstance(tech_stack, str):
            requirements.extend(re.split(r'[,;\n•\-]', tech_stack))
        
        # From responsibilities (extract technical terms)
        responsibilities = job_data.get("responsibilities", [])
        if isinstance(responsibilities, list):
            for resp in responsibilities:
                if isinstance(resp, str):
                    # Extract technical terms
                    tech_terms = self._extract_tech_terms(resp)
                    requirements.extend(tech_terms)
        
        # Clean and deduplicate
        cleaned_requirements = []
        for req in requirements:
            if isinstance(req, str):
                cleaned = req.strip().strip('•-').strip()
                if cleaned and len(cleaned) > 2:
                    cleaned_requirements.append(cleaned)
        
        return list(set(cleaned_requirements))
    
    def _extract_tech_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        # Common tech terms and patterns
        tech_patterns = [
            r'\b(Python|JavaScript|Java|C\+\+|C#|Ruby|Go|Rust|Swift|Kotlin)\b',
            r'\b(React|Angular|Vue|Django|Flask|Spring|Rails|Laravel)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Git|SQL|NoSQL)\b',
            r'\b(Machine Learning|ML|AI|Deep Learning|TensorFlow|PyTorch)\b',
            r'\b(Data Science|Analytics|Statistics|Pandas|NumPy)\b',
            r'\b(API|REST|GraphQL|Microservices|DevOps|CI/CD)\b'
        ]
        
        terms = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.extend([match.lower() for match in matches])
        
        return terms
    
    def _find_skill_match(self, requirement: str, resume_skills: Set[str]) -> str:
        """Find the type of match between requirement and resume skills"""
        req_clean = requirement.lower().strip()
        
        # Strong match: exact match or very close
        if req_clean in resume_skills:
            return "strong"
        
        # Check for partial matches
        for skill in resume_skills:
            # Substring match (both directions)
            if (req_clean in skill and len(req_clean) > 2) or (skill in req_clean and len(skill) > 2):
                return "partial"
            
            # Similar technologies (e.g., React/ReactJS, Python/Python3)
            if self._are_similar_technologies(req_clean, skill):
                return "strong"
        
        return "none"
    
    def _are_similar_technologies(self, tech1: str, tech2: str) -> bool:
        """Check if two technologies are similar/related"""
        similar_groups = [
            ["python", "python3", "python2"],
            ["javascript", "js", "node.js", "nodejs"],
            ["react", "reactjs", "react.js"],
            ["angular", "angularjs"],
            ["vue", "vue.js", "vuejs"],
            ["docker", "containerization"],
            ["kubernetes", "k8s"],
            ["aws", "amazon web services"],
            ["gcp", "google cloud platform", "google cloud"],
            ["azure", "microsoft azure"],
            ["sql", "mysql", "postgresql", "postgres"],
            ["nosql", "mongodb", "cassandra"],
            ["machine learning", "ml", "artificial intelligence", "ai"],
            ["tensorflow", "tf"],
            ["pytorch", "torch"]
        ]
        
        for group in similar_groups:
            if tech1 in group and tech2 in group:
                return True
        
        return False
    
    def _generate_summary(self, strong_matches: List[str], partial_matches: List[str], 
                         gaps: List[str], match_score: int) -> str:
        """Generate narrative summary of the gap analysis"""
        
        summary_parts = []
        
        # Overall assessment
        if match_score >= 80:
            summary_parts.append(f"Excellent match ({match_score}% compatibility)!")
        elif match_score >= 60:
            summary_parts.append(f"Good match ({match_score}% compatibility) with some areas for growth.")
        elif match_score >= 40:
            summary_parts.append(f"Moderate match ({match_score}% compatibility) requiring focused preparation.")
        else:
            summary_parts.append(f"Challenging match ({match_score}% compatibility) needing significant upskilling.")
        
        # Strengths
        if strong_matches:
            top_strengths = strong_matches[:3]
            summary_parts.append(f"Your strongest assets are {', '.join(top_strengths)}.")
        
        # Gaps to address
        if gaps:
            priority_gaps = gaps[:3]
            summary_parts.append(f"Focus your preparation on {', '.join(priority_gaps)}.")
        
        return " ".join(summary_parts)
    
    def _create_skills_map(self, strong_matches: List[str], partial_matches: List[str], 
                          gaps: List[str]) -> Dict[str, List[str]]:
        """Create a skills map for visualization"""
        return {
            "strong": strong_matches[:10],  # Limit for display
            "partial": partial_matches[:10],
            "gaps": gaps[:10]
        } 