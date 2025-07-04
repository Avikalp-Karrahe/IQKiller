"""
Advanced Gap Analysis - Provides true skills matching with semantic similarity
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

from metrics import log_metric
from llm_client import LLMClient


@dataclass
class SkillMatch:
    """Detailed skill matching result"""
    job_requirement: str
    resume_skill: str
    match_score: float
    match_type: str  # "strong", "partial", "weak", "missing"
    importance: str  # "required", "preferred", "nice_to_have"
    recommendation: str
    category: str


@dataclass
class GapAnalysisResult:
    """Complete gap analysis result"""
    overall_match_score: float
    strong_matches: List[SkillMatch]
    partial_matches: List[SkillMatch]
    gaps: List[SkillMatch]
    strengths_summary: str
    gaps_summary: str
    competitive_advantages: List[str]
    preparation_priority: List[str]
    interview_focus_areas: List[str]
    skill_categories_analysis: Dict[str, float]


class AdvancedSkillMatcher:
    """Advanced skill matching with semantic similarity"""

    def __init__(self):
        self.skill_synonyms = {
            # Programming Languages
            "python": ["python3", "py", "python programming"],
            "javascript": ["js", "ecmascript", "node.js", "nodejs"],
            "typescript": ["ts"],
            "react": ["reactjs", "react.js"],
            "vue": ["vue.js", "vuejs"],
            "angular": ["angularjs"],
            # Frameworks & Libraries
            "express": ["express.js", "expressjs"],
            "django": ["django framework"],
            "flask": ["flask framework"],
            "spring": ["spring boot", "spring framework"],
            "laravel": ["laravel framework"],
            # Databases
            "postgresql": ["postgres", "psql"],
            "mongodb": ["mongo"],
            "mysql": ["my sql"],
            # Cloud Platforms
            "aws": ["amazon web services"],
            "gcp": ["google cloud platform", "google cloud"],
            "azure": ["microsoft azure"],
            # DevOps & Tools
            "kubernetes": ["k8s"],
            "docker": ["containers", "containerization"],
            "jenkins": ["ci/cd"],
            "git": ["version control", "github", "gitlab"],
            # Data & ML
            "machine learning": ["ml", "artificial intelligence", "ai"],
            "deep learning": ["dl", "neural networks"],
            "tensorflow": ["tf"],
            "pytorch": ["torch"],
            "pandas": ["data analysis"],
            "numpy": ["numerical computing"],
            # Other
            "agile": ["scrum", "kanban"],
            "restful": ["rest api", "rest apis", "api development"],
            "microservices": ["micro services", "service oriented architecture"]
        }

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name using synonyms"""
        skill_lower = skill.lower().strip()

        # Direct match
        if skill_lower in self.skill_synonyms:
            return skill_lower

        # Check if it's a synonym
        for main_skill, synonyms in self.skill_synonyms.items():
            if skill_lower in synonyms:
                return main_skill

        return skill_lower

    def calculate_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate semantic similarity between two skills"""
        norm1 = self.normalize_skill(skill1)
        norm2 = self.normalize_skill(skill2)

        # Direct match after normalization
        if norm1 == norm2:
            return 1.0

        # Partial matching using SequenceMatcher
        similarity = SequenceMatcher(None, norm1, norm2).ratio()

        # Boost for containing relationships
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)

        return similarity

    def find_best_match(self, job_requirement: str,
                       resume_skills: List[str]) -> tuple[str, float]:
        """Find the best matching resume skill for a job requirement"""
        best_skill = ""
        best_score = 0.0

        for resume_skill in resume_skills:
            score = self.calculate_similarity(job_requirement, resume_skill)
            if score > best_score:
                best_score = score
                best_skill = resume_skill

        return best_skill, best_score


class AdvancedGapAnalysis:
    """Advanced gap analysis with true skills matching"""

    def __init__(self):
        self.matcher = AdvancedSkillMatcher()
        self.llm_client = LLMClient()

    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for gap analysis"""
        try:
            # Extract resume and job data
            resume_data = data.get("resume_data_enhanced", {})
            job_data = data.get("job_data_enhanced", {})

            if not resume_data or not job_data:
                return {**data, "gap_analysis_advanced": {
                    "error": "Missing resume or job data"}}

            # Perform advanced gap analysis
            analysis_result = await self._analyze_comprehensive_fit(
                resume_data, job_data)

            log_metric("gap_analysis_advanced_success", {
                "match_score": analysis_result.overall_match_score,
                "strong_matches": len(analysis_result.strong_matches),
                "gaps": len(analysis_result.gaps)
            })

            return {**data, "gap_analysis_advanced": self._format_result(
                analysis_result)}

        except Exception as e:
            log_metric("gap_analysis_advanced_error", {"error": str(e)})
            return {**data, "gap_analysis_advanced": {
                "error": f"Advanced gap analysis failed: {e}"}}

    async def _analyze_comprehensive_fit(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> GapAnalysisResult:
        """Perform comprehensive fit analysis"""

        # Extract skills from resume
        resume_skills = self._extract_resume_skills(resume_data)

        # Extract requirements from job
        job_requirements = self._extract_job_requirements(job_data)

        # Perform detailed matching
        skill_matches = self._match_skills_detailed(
            job_requirements, resume_skills)

        # Calculate overall score
        overall_score = self._calculate_overall_score(skill_matches)

        # Categorize matches
        strong_matches = [m for m in skill_matches if m.match_score >= 0.8]
        partial_matches = [m for m in skill_matches
                          if 0.4 <= m.match_score < 0.8]
        gaps = [m for m in skill_matches if m.match_score < 0.4]

        # Generate AI-powered analysis
        strengths_summary = await self._generate_strengths_summary(
            strong_matches, resume_data)
        gaps_summary = await self._generate_gaps_summary(gaps, job_data)

        # Extract competitive advantages
        competitive_advantages = self._identify_competitive_advantages(
            resume_data, job_data, strong_matches)

        # Generate preparation priorities
        preparation_priority = self._generate_preparation_priority(
            gaps, partial_matches)

        # Identify interview focus areas
        interview_focus = self._identify_interview_focus_areas(
            strong_matches, gaps)

        # Analyze by skill categories
        categories_analysis = self._analyze_skill_categories(skill_matches)

        return GapAnalysisResult(
            overall_match_score=overall_score,
            strong_matches=strong_matches,
            partial_matches=partial_matches,
            gaps=gaps,
            strengths_summary=strengths_summary,
            gaps_summary=gaps_summary,
            competitive_advantages=competitive_advantages,
            preparation_priority=preparation_priority,
            interview_focus_areas=interview_focus,
            skill_categories_analysis=categories_analysis
        )

    def _extract_resume_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract all skills from resume data"""
        all_skills = []

        # Get skills from structured skills section
        skills_obj = resume_data.get("skills", {})
        if isinstance(skills_obj, dict):
            for category, skills_list in skills_obj.items():
                if isinstance(skills_list, list):
                    all_skills.extend(skills_list)

        # Get skills from experience
        experience = resume_data.get("experience", [])
        for exp in experience:
            if isinstance(exp, dict):
                tech_skills = exp.get("technologies", [])
                if isinstance(tech_skills, list):
                    all_skills.extend(tech_skills)

        # Get skills from projects
        projects = resume_data.get("projects", [])
        for project in projects:
            if isinstance(project, dict):
                tech_skills = project.get("technologies", [])
                if isinstance(tech_skills, list):
                    all_skills.extend(tech_skills)

        # Deduplicate and clean
        return list(set([skill.strip() for skill in all_skills if skill]))

    def _extract_job_requirements(self,
                                 job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract requirements from job data"""
        requirements = []

        # Handle enhanced job parser structure
        for req_type in ["tech_requirements", "experience_requirements", 
                        "education_requirements", "soft_skill_requirements"]:
            structured_reqs = job_data.get(req_type, [])
            if isinstance(structured_reqs, list):
                # Convert JobRequirement objects to dicts if needed
                for req in structured_reqs:
                    if isinstance(req, dict):
                        requirements.append(req)
                    else:
                        # Handle dataclass objects
                        requirements.append({
                            "skill": getattr(req, 'skill', str(req)),
                            "importance": getattr(req, 'importance', 'required'),
                            "category": getattr(req, 'category', 'technical')
                        })

        # Fallback: legacy requirements key
        if not requirements:
            structured_reqs = job_data.get("requirements", [])
            if isinstance(structured_reqs, list):
                requirements.extend(structured_reqs)

        # Last fallback: extract from text fields
        if not requirements:
            requirements = self._extract_requirements_from_text(job_data)

        return requirements

    def _extract_requirements_from_text(self,
                                       job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract requirements from job description text"""
        requirements = []

        # Common skill patterns
        common_skills = [
            "python", "javascript", "react", "node.js", "sql", "aws",
            "docker", "kubernetes", "git", "machine learning", "tensorflow",
            "django", "flask", "express", "mongodb", "postgresql"
        ]

        # Extract from various text fields
        text_content = ""
        for field in ["description", "content", "scraped"]:
            if field in job_data:
                if isinstance(job_data[field], str):
                    text_content += job_data[field]
                elif isinstance(job_data[field], dict):
                    text_content += str(job_data[field])

        text_lower = text_content.lower()

        for skill in common_skills:
            if skill.lower() in text_lower:
                requirements.append({
                    "skill": skill,
                    "importance": "required",
                    "category": "technical"
                })

        return requirements

    def _match_skills_detailed(self, job_requirements: List[Dict[str, Any]],
                              resume_skills: List[str]) -> List[SkillMatch]:
        """Perform detailed skill matching"""
        matches = []

        for req in job_requirements:
            req_skill = req.get("skill", "")
            importance = req.get("importance", "required")
            category = req.get("category", "technical")

            # Find best match
            best_match, score = self.matcher.find_best_match(
                req_skill, resume_skills)

            # Determine match type
            if score >= 0.8:
                match_type = "strong"
            elif score >= 0.4:
                match_type = "partial"
            elif score > 0:
                match_type = "weak"
            else:
                match_type = "missing"

            # Generate recommendation
            recommendation = self._generate_skill_recommendation(
                req_skill, best_match, score, importance)

            matches.append(SkillMatch(
                job_requirement=req_skill,
                resume_skill=best_match if score > 0 else "Not Found",
                match_score=score,
                match_type=match_type,
                importance=importance,
                recommendation=recommendation,
                category=category
            ))

        return matches

    def _calculate_overall_score(self, matches: List[SkillMatch]) -> float:
        """Calculate weighted overall match score"""
        if not matches:
            return 0.0

        # Weight by importance
        importance_weights = {
            "required": 1.0,
            "preferred": 0.7,
            "nice_to_have": 0.3
        }

        total_weighted_score = 0.0
        total_weight = 0.0

        for match in matches:
            weight = importance_weights.get(match.importance, 0.5)
            total_weighted_score += match.match_score * weight
            total_weight += weight

        return (total_weighted_score / total_weight * 100) if total_weight > 0 else 0

    def _generate_skill_recommendation(self, job_skill: str, resume_skill: str,
                                     score: float, importance: str) -> str:
        """Generate actionable recommendation for skill match"""
        if score >= 0.8:
            return f"Highlight your {resume_skill} experience"
        elif score >= 0.4:
            return f"Connect your {resume_skill} to {job_skill} requirements"
        elif importance == "required":
            return f"Critical: Learn {job_skill} before applying"
        elif importance == "preferred":
            return f"Important: Gain experience with {job_skill}"
        else:
            return f"Nice-to-have: Consider learning {job_skill}"

    async def _generate_strengths_summary(self, strong_matches: List[SkillMatch],
                                        resume_data: Dict[str, Any]) -> str:
        """Generate AI-powered strengths summary"""
        if not strong_matches:
            return "No strong technical matches found."

        skills_list = [match.job_requirement for match in strong_matches[:5]]
        experience_years = resume_data.get("years_of_experience", 0)

        prompt = f"""
        Based on these strong skill matches: {', '.join(skills_list)} and
        {experience_years} years of experience, write a 2-sentence summary of
        the candidate's key strengths for this role.
        Focus on practical value and competitive advantages.
        """

        try:
            response = self.llm_client.call_llm(
                prompt, temperature=0.3, max_tokens=150)
            return response.strip()
        except Exception:
            return (f"Strong technical foundation in {', '.join(skills_list[:3])} "
                   f"with {experience_years} years of experience.")

    async def _generate_gaps_summary(self, gaps: List[SkillMatch],
                                   job_data: Dict[str, Any]) -> str:
        """Generate AI-powered gaps summary"""
        if not gaps:
            return "No significant skill gaps identified."

        critical_gaps = [gap.job_requirement for gap in gaps
                        if gap.importance == "required"]

        if not critical_gaps:
            return "No critical skill gaps. Focus on strengthening preferences."

        prompt = f"""
        The candidate is missing these required skills: {', '.join(critical_gaps[:3])}.
        Write a 2-sentence summary of the main gaps and preparation strategy.
        Be constructive and actionable.
        """

        try:
            response = self.llm_client.call_llm(
                prompt, temperature=0.3, max_tokens=150)
            return response.strip()
        except Exception:
            return (f"Key gaps in {', '.join(critical_gaps[:2])}. "
                   "Focus preparation on these critical areas.")

    def _identify_competitive_advantages(self, resume_data: Dict[str, Any],
                                       job_data: Dict[str, Any],
                                       strong_matches: List[SkillMatch]) -> List[str]:
        """Identify unique competitive advantages"""
        advantages = []

        # Experience level advantage
        years_exp = resume_data.get("years_of_experience", 0)
        if years_exp > 5:
            advantages.append(f"{years_exp}+ years of proven experience")

        # Education advantage
        education = resume_data.get("education", [])
        for edu in education:
            if isinstance(edu, dict) and "degree" in edu:
                degree = edu["degree"]
                if "master" in degree.lower() or "phd" in degree.lower():
                    advantages.append(f"Advanced degree: {degree}")
                    break

        # Skill combination advantages
        strong_skills = [match.job_requirement for match in strong_matches]
        if len(strong_skills) >= 3:
            advantages.append(
                f"Strong combination: {', '.join(strong_skills[:3])}")

        # Project portfolio
        projects = resume_data.get("projects", [])
        if len(projects) >= 2:
            advantages.append(f"Proven track record: {len(projects)} projects")

        return advantages[:4]  # Limit to top 4

    def _generate_preparation_priority(self, gaps: List[SkillMatch],
                                     partial_matches: List[SkillMatch]) -> List[str]:
        """Generate preparation priority list"""
        priorities = []

        # Critical gaps first
        critical_gaps = [gap.job_requirement for gap in gaps
                        if gap.importance == "required"]
        priorities.extend(critical_gaps[:3])

        # Important partial matches to strengthen
        important_partials = [match.job_requirement for match in partial_matches
                            if match.importance in ["required", "preferred"]]
        priorities.extend(important_partials[:2])

        return priorities[:5]

    def _identify_interview_focus_areas(self, strong_matches: List[SkillMatch],
                                      gaps: List[SkillMatch]) -> List[str]:
        """Identify areas to focus on during interview"""
        focus_areas = []

        # Highlight strengths
        if strong_matches:
            top_strengths = [match.job_requirement for match in strong_matches[:2]]
            focus_areas.extend([f"Demonstrate {skill} expertise"
                              for skill in top_strengths])

        # Address concerns proactively
        critical_gaps = [gap.job_requirement for gap in gaps
                        if gap.importance == "required"]
        if critical_gaps:
            focus_areas.append(
                f"Address learning plan for {critical_gaps[0]}")

        # General advice
        focus_areas.extend([
            "Emphasize problem-solving approach",
            "Show enthusiasm for learning"
        ])

        return focus_areas[:5]

    def _analyze_skill_categories(self, matches: List[SkillMatch]) -> Dict[str, float]:
        """Analyze performance by skill category"""
        categories = {}

        for match in matches:
            category = match.category
            if category not in categories:
                categories[category] = []
            categories[category].append(match.match_score)

        # Calculate averages
        category_scores = {}
        for category, scores in categories.items():
            if scores:
                category_scores[category] = sum(scores) / len(scores) * 100

        return category_scores

    def _format_result(self, result: GapAnalysisResult) -> Dict[str, Any]:
        """Format result for output"""
        return {
            "overall_match_score": result.overall_match_score,
            "strong_matches": [self._format_skill_match(m)
                             for m in result.strong_matches],
            "partial_matches": [self._format_skill_match(m)
                              for m in result.partial_matches],
            "gaps": [self._format_skill_match(m) for m in result.gaps],
            "strengths_summary": result.strengths_summary,
            "gaps_summary": result.gaps_summary,
            "competitive_advantages": result.competitive_advantages,
            "preparation_priority": result.preparation_priority,
            "interview_focus_areas": result.interview_focus_areas,
            "skill_categories_analysis": result.skill_categories_analysis,
            "detailed_matches": [self._format_skill_match(m)
                               for m in result.strong_matches +
                               result.partial_matches + result.gaps]
        }

    def _format_skill_match(self, match: SkillMatch) -> Dict[str, Any]:
        """Format individual skill match"""
        return {
            "job_requirement": match.job_requirement,
            "resume_skill": match.resume_skill,
            "match_score": round(match.match_score, 2),
            "match_type": match.match_type,
            "importance": match.importance,
            "recommendation": match.recommendation,
            "category": match.category
        } 