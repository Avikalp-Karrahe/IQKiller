"""
Personalized Interview Guide Generator
Uses advanced gap analysis to create truly personalized interview preparation content
"""

from typing import Any, Dict, List, Optional
from llm_client import LLMClient
from metrics import log_metric
import json
from dataclasses import dataclass, asdict

@dataclass
class InterviewQuestion:
    question: str
    category: str  # technical, behavioral, company, situational
    difficulty: str  # easy, medium, hard
    why_asked: str  # Why this question is relevant for this candidate
    approach_strategy: str  # How to approach answering
    example_points: List[str]  # Specific points from candidate's background to mention
    follow_up_questions: List[str]  # Likely follow-up questions

@dataclass
class PersonalizedGuideSection:
    title: str
    content: str
    why_important: str  # Why this section matters for this specific candidate
    action_items: List[str]
    time_to_complete: str

@dataclass
class PersonalizedInterviewGuide:
    header: Dict[str, Any]  # Match score, company info, etc.
    executive_summary: str
    skills_analysis: Dict[str, Any]
    interview_process: PersonalizedGuideSection
    technical_questions: List[InterviewQuestion]
    behavioral_questions: List[InterviewQuestion]
    company_questions: List[InterviewQuestion]
    preparation_strategy: PersonalizedGuideSection
    talking_points: PersonalizedGuideSection
    questions_to_ask: List[str]
    day_of_preparation: PersonalizedGuideSection
    success_metrics: List[str]

class PersonalizedInterviewGuideGenerator:
    """Generates truly personalized interview guides based on advanced gap analysis"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        resume_data = data.get("resume_data_enhanced", {})
        job_data = data.get("job_data_enhanced", {})
        gap_analysis = data.get("gap_analysis_advanced", {})
        
        if not all([resume_data, job_data, gap_analysis]):
            return {**data, "personalized_guide": {"error": "Missing required data for personalized guide"}}
        
        try:
            # Generate personalized interview guide
            guide = await self._generate_personalized_guide(resume_data, job_data, gap_analysis)
            
            log_metric("personalized_guide_success", {
                "overall_match_score": gap_analysis.get("overall_match_score", 0),
                "technical_questions": len(guide.technical_questions),
                "behavioral_questions": len(guide.behavioral_questions),
                "total_action_items": sum(len(section.action_items) for section in [
                    guide.preparation_strategy, guide.talking_points, guide.day_of_preparation
                ])
            })
            
            return {**data, "personalized_guide": asdict(guide)}
            
        except Exception as e:
            log_metric("personalized_guide_error", {"error": str(e)})
            return {**data, "personalized_guide": {"error": f"Personalized guide generation failed: {e}"}}
    
    async def _generate_personalized_guide(self, resume_data: Dict[str, Any], 
                                         job_data: Dict[str, Any], 
                                         gap_analysis: Dict[str, Any]) -> PersonalizedInterviewGuide:
        """Generate the complete personalized interview guide"""
        
        # Extract key information
        role = job_data.get("role", "Unknown Role")
        company = job_data.get("company", "Unknown Company")
        match_score = gap_analysis.get("overall_match_score", 0)
        candidate_name = resume_data.get("personal_info", {}).get("name", "")
        
        # Generate header information
        header = self._create_header(role, company, match_score, gap_analysis)
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            resume_data, job_data, gap_analysis
        )
        
        # Create skills analysis visualization
        skills_analysis = self._create_skills_analysis(gap_analysis)
        
        # Generate personalized sections
        interview_process = await self._generate_interview_process_section(
            job_data, gap_analysis
        )
        
        technical_questions = await self._generate_technical_questions(
            job_data, gap_analysis, resume_data
        )
        
        behavioral_questions = await self._generate_behavioral_questions(
            job_data, resume_data, gap_analysis
        )
        
        company_questions = await self._generate_company_questions(
            job_data, gap_analysis
        )
        
        preparation_strategy = await self._generate_preparation_strategy(
            gap_analysis, job_data
        )
        
        talking_points = await self._generate_talking_points(
            resume_data, gap_analysis
        )
        
        questions_to_ask = await self._generate_questions_to_ask(
            job_data, gap_analysis
        )
        
        day_of_preparation = await self._generate_day_of_preparation(
            gap_analysis, job_data
        )
        
        success_metrics = self._generate_success_metrics(gap_analysis)
        
        return PersonalizedInterviewGuide(
            header=header,
            executive_summary=executive_summary,
            skills_analysis=skills_analysis,
            interview_process=interview_process,
            technical_questions=technical_questions,
            behavioral_questions=behavioral_questions,
            company_questions=company_questions,
            preparation_strategy=preparation_strategy,
            talking_points=talking_points,
            questions_to_ask=questions_to_ask,
            day_of_preparation=day_of_preparation,
            success_metrics=success_metrics
        )
    
    def _create_header(self, role: str, company: str, match_score: float, 
                      gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create header with match visualization"""
        
        # Determine match level and color
        if match_score >= 85:
            match_level = "Excellent Match"
            match_emoji = "🟢"
        elif match_score >= 70:
            match_level = "Strong Match"
            match_emoji = "🟡"
        elif match_score >= 55:
            match_level = "Good Match"
            match_emoji = "🟠"
        else:
            match_level = "Developing Match"
            match_emoji = "🔴"
        
        strong_matches = len(gap_analysis.get("strong_matches", []))
        missing_skills = len(gap_analysis.get("missing_skills", []))
        
        return {
            "role": role,
            "company": company,
            "match_score": round(match_score, 1),
            "match_level": match_level,
            "match_emoji": match_emoji,
            "strong_matches_count": strong_matches,
            "missing_skills_count": missing_skills,
            "total_requirements": gap_analysis.get("total_requirements", 0)
        }
    
    async def _generate_executive_summary(self, resume_data: Dict[str, Any], 
                                        job_data: Dict[str, Any], 
                                        gap_analysis: Dict[str, Any]) -> str:
        """Generate personalized executive summary"""
        
        role = job_data.get("role", "Unknown Role")
        company = job_data.get("company", "Unknown Company")
        match_score = gap_analysis.get("overall_match_score", 0)
        years_exp = resume_data.get("years_of_experience", 0)
        strengths = gap_analysis.get("strengths_summary", "")
        gaps = gap_analysis.get("gaps_summary", "")
        competitive_advantages = gap_analysis.get("competitive_advantages", [])
        
        prompt = f"""
Write a personalized executive summary for an interview guide. This should sound like a knowledgeable mentor who has analyzed their specific background.

Candidate Profile:
- Years of experience: {years_exp}
- Target role: {role} at {company}
- Match score: {match_score}%
- Strengths: {strengths}
- Gaps to address: {gaps}
- Competitive advantages: {', '.join(competitive_advantages[:3])}

Guidelines:
- Start with "{role} interview" in first 100 words
- Address the candidate directly ("you")
- Be specific about their unique position
- Reference their actual background
- Confident, mentor-like tone
- 3-4 sentences max
- Actionable and encouraging

Example tone: "Your background in Python and machine learning puts you in a strong position for this Data Scientist role at TechCorp. With 5+ years of experience, you bring the technical depth they're seeking, and your AWS skills differentiate you from other candidates. Focus your preparation on demonstrating your model deployment experience and be ready to discuss your specific ML project outcomes."
"""
        
        try:
            return self.llm_client.call_llm(prompt, temperature=0.3, max_tokens=300)
        except:
            return f"You're well-positioned for this {role} role at {company} with a {match_score}% match score."
    
    def _create_skills_analysis(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create visual skills analysis"""
        
        strong_matches = gap_analysis.get("strong_matches", [])
        partial_matches = gap_analysis.get("partial_matches", [])
        missing_skills = gap_analysis.get("missing_skills", [])
        
        # Create text-based visualization
        skills_breakdown = {
            "strong": [match.get("skill_name", "") for match in strong_matches[:8]],
            "partial": [match.get("skill_name", "") for match in partial_matches[:6]],
            "missing": [match.get("skill_name", "") for match in missing_skills[:6]]
        }
        
        # Generate bar chart representation
        total_skills = len(strong_matches) + len(partial_matches) + len(missing_skills)
        
        if total_skills > 0:
            strong_percentage = len(strong_matches) / total_skills * 100
            partial_percentage = len(partial_matches) / total_skills * 100
            missing_percentage = len(missing_skills) / total_skills * 100
        else:
            strong_percentage = partial_percentage = missing_percentage = 0
        
        return {
            "skills_breakdown": skills_breakdown,
            "percentages": {
                "strong": round(strong_percentage, 1),
                "partial": round(partial_percentage, 1),
                "missing": round(missing_percentage, 1)
            },
            "summary": gap_analysis.get("strengths_summary", ""),
            "categories_analysis": gap_analysis.get("skill_categories_analysis", {})
        }
    
    async def _generate_interview_process_section(self, job_data: Dict[str, Any], 
                                                gap_analysis: Dict[str, Any]) -> PersonalizedGuideSection:
        """Generate personalized interview process section"""
        
        company = job_data.get("company", "Unknown Company")
        role = job_data.get("role", "Unknown Role")
        seniority = job_data.get("seniority_level", "mid")
        company_stage = job_data.get("company_stage", "enterprise")
        match_score = gap_analysis.get("overall_match_score", 0)
        
        prompt = f"""
Describe the likely interview process for a {role} position at {company} ({company_stage} company, {seniority} level).

Context:
- Candidate match score: {match_score}%
- Company stage: {company_stage}
- Role level: {seniority}

Include:
1. Typical number of rounds
2. Types of interviews expected
3. Key stakeholders they'll meet
4. Timeline and logistics
5. Company-specific insights if available
6. What to expect given their match score

Keep it practical and specific. Use markdown formatting.
Max 250 words.
"""
        
        try:
            content = self.llm_client.call_llm(prompt, temperature=0, max_tokens=400)
        except:
            content = f"Typical {role} interviews include 3-4 rounds: phone screen, technical assessment, team interviews, and final round."
        
        why_important = f"Understanding {company}'s process helps you prepare appropriately for each stage and set proper expectations."
        
        action_items = [
            f"Research {company}'s interview style on Glassdoor",
            "Prepare for technical screening",
            "Ready examples for behavioral questions",
            "Prepare thoughtful questions for each interviewer"
        ]
        
        return PersonalizedGuideSection(
            title="Interview Process",
            content=content,
            why_important=why_important,
            action_items=action_items,
            time_to_complete="30 minutes research"
        )
    
    async def _generate_technical_questions(self, job_data: Dict[str, Any], 
                                          gap_analysis: Dict[str, Any], 
                                          resume_data: Dict[str, Any]) -> List[InterviewQuestion]:
        """Generate personalized technical questions"""
        
        strong_matches = gap_analysis.get("strong_matches", [])
        missing_skills = gap_analysis.get("missing_skills", [])
        role = job_data.get("role", "Unknown Role")
        
        # Focus on areas where candidate has gaps or needs to demonstrate strength
        focus_areas = []
        
        # Add strong areas to showcase
        for match in strong_matches[:3]:
            focus_areas.append({
                "skill": match.get("skill_name", ""),
                "type": "strength",
                "context": f"Highlight your {match.get('skill_name', '')} expertise"
            })
        
        # Add gap areas they need to address
        for match in missing_skills[:3]:
            if match.get("importance") == "required":
                focus_areas.append({
                    "skill": match.get("skill_name", ""),
                    "type": "gap",
                    "context": f"Be prepared for basic {match.get('skill_name', '')} questions"
                })
        
        questions = []
        
        for area in focus_areas[:6]:  # Limit to 6 technical questions
            question = await self._generate_single_technical_question(
                area, role, resume_data
            )
            if question:
                questions.append(question)
        
        return questions
    
    async def _generate_single_technical_question(self, focus_area: Dict[str, Any], 
                                                role: str, resume_data: Dict[str, Any]) -> Optional[InterviewQuestion]:
        """Generate a single personalized technical question"""
        
        skill = focus_area["skill"]
        area_type = focus_area["type"]
        
        # Get candidate's relevant experience
        relevant_projects = []
        for project in resume_data.get("projects", []):
            if isinstance(project, dict):
                if skill.lower() in str(project.get("technologies", [])).lower():
                    relevant_projects.append(project.get("name", ""))
        
        # Get relevant work experience
        relevant_experience = []
        for exp in resume_data.get("experience", []):
            if isinstance(exp, dict):
                if skill.lower() in str(exp.get("technologies", [])).lower():
                    relevant_experience.append(exp.get("title", ""))
        
        prompt = f"""
Generate a technical interview question for a {role} position focusing on {skill}.

Context:
- Question type: {"showcase strength" if area_type == "strength" else "assess knowledge"}
- Candidate has {skill} in: {', '.join(relevant_projects + relevant_experience) or 'limited context'}
- This should be {"medium-hard" if area_type == "strength" else "easy-medium"} difficulty

Return JSON:
{{
  "question": "Specific technical question",
  "difficulty": "easy|medium|hard",
  "why_asked": "Why this matters for this candidate specifically",
  "approach_strategy": "How candidate should approach answering",
  "example_points": ["Specific points from their background to mention"],
  "follow_up_questions": ["Likely follow-up questions"]
}}

Make it specific to their background and the role.
"""
        
        try:
            response = self.llm_client.call_llm(prompt, temperature=0.3, max_tokens=600)
            
            # Parse JSON response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                
                return InterviewQuestion(
                    question=data.get("question", ""),
                    category="technical",
                    difficulty=data.get("difficulty", "medium"),
                    why_asked=data.get("why_asked", ""),
                    approach_strategy=data.get("approach_strategy", ""),
                    example_points=data.get("example_points", []),
                    follow_up_questions=data.get("follow_up_questions", [])
                )
        except:
            pass
        
        return None
    
    async def _generate_behavioral_questions(self, job_data: Dict[str, Any], 
                                           resume_data: Dict[str, Any], 
                                           gap_analysis: Dict[str, Any]) -> List[InterviewQuestion]:
        """Generate personalized behavioral questions"""
        
        role = job_data.get("role", "Unknown Role")
        company_stage = job_data.get("company_stage", "enterprise")
        years_exp = resume_data.get("years_of_experience", 0)
        
        # Generate questions based on candidate's background and role requirements
        behavioral_focus = []
        
        if years_exp < 3:
            behavioral_focus.extend(["learning agility", "collaboration", "problem-solving"])
        elif years_exp >= 5:
            behavioral_focus.extend(["leadership", "mentoring", "conflict resolution"])
        else:
            behavioral_focus.extend(["project management", "cross-functional collaboration", "initiative"])
        
        if company_stage == "startup":
            behavioral_focus.append("adaptability")
        elif company_stage == "enterprise":
            behavioral_focus.append("process improvement")
        
        questions = []
        
        for focus in behavioral_focus[:4]:  # Limit to 4 behavioral questions
            question = await self._generate_single_behavioral_question(
                focus, role, resume_data
            )
            if question:
                questions.append(question)
        
        return questions
    
    async def _generate_single_behavioral_question(self, focus_area: str, role: str, 
                                                 resume_data: Dict[str, Any]) -> Optional[InterviewQuestion]:
        """Generate a single personalized behavioral question"""
        
        # Get relevant experience for this behavioral area
        recent_roles = []
        for exp in resume_data.get("experience", [])[:2]:  # Last 2 roles
            if isinstance(exp, dict):
                recent_roles.append({
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "achievements": exp.get("achievements", [])
                })
        
        prompt = f"""
Generate a behavioral interview question for a {role} position focusing on {focus_area}.

Candidate context:
- Recent roles: {', '.join([r['title'] for r in recent_roles])}
- Key achievements: {', '.join([ach for role in recent_roles for ach in role.get('achievements', [])[:2]])}

Return JSON:
{{
  "question": "STAR-format behavioral question",
  "difficulty": "medium",
  "why_asked": "Why this matters for this specific candidate and role",
  "approach_strategy": "How to structure the STAR response",
  "example_points": ["Specific experiences from their background to reference"],
  "follow_up_questions": ["Likely follow-up questions"]
}}

Make the question specific and give them concrete examples from their background to use.
"""
        
        try:
            response = self.llm_client.call_llm(prompt, temperature=0.3, max_tokens=600)
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                
                return InterviewQuestion(
                    question=data.get("question", ""),
                    category="behavioral",
                    difficulty=data.get("difficulty", "medium"),
                    why_asked=data.get("why_asked", ""),
                    approach_strategy=data.get("approach_strategy", ""),
                    example_points=data.get("example_points", []),
                    follow_up_questions=data.get("follow_up_questions", [])
                )
        except:
            pass
        
        return None
    
    async def _generate_company_questions(self, job_data: Dict[str, Any], 
                                        gap_analysis: Dict[str, Any]) -> List[InterviewQuestion]:
        """Generate company-specific questions"""
        
        company = job_data.get("company", "Unknown Company")
        role = job_data.get("role", "Unknown Role")
        company_stage = job_data.get("company_stage", "enterprise")
        
        questions = []
        
        # Generate 2-3 company-specific questions
        for topic in ["company culture", "role challenges", "team dynamics"][:3]:
            question = await self._generate_single_company_question(
                topic, company, role, company_stage
            )
            if question:
                questions.append(question)
        
        return questions
    
    async def _generate_single_company_question(self, topic: str, company: str, 
                                              role: str, stage: str) -> Optional[InterviewQuestion]:
        """Generate a single company-specific question"""
        
        prompt = f"""
Generate a company-specific interview question about {topic} for {role} at {company} ({stage} company).

Return JSON:
{{
  "question": "Company-specific question they might ask",
  "difficulty": "medium",
  "why_asked": "Why this company asks this question",
  "approach_strategy": "How to answer effectively",
  "example_points": ["Key points to include in answer"],
  "follow_up_questions": ["Likely follow-up questions"]
}}

Make it specific to the company stage and role.
"""
        
        try:
            response = self.llm_client.call_llm(prompt, temperature=0.3, max_tokens=500)
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                
                return InterviewQuestion(
                    question=data.get("question", ""),
                    category="company",
                    difficulty=data.get("difficulty", "medium"),
                    why_asked=data.get("why_asked", ""),
                    approach_strategy=data.get("approach_strategy", ""),
                    example_points=data.get("example_points", []),
                    follow_up_questions=data.get("follow_up_questions", [])
                )
        except:
            pass
        
        return None
    
    async def _generate_preparation_strategy(self, gap_analysis: Dict[str, Any], 
                                           job_data: Dict[str, Any]) -> PersonalizedGuideSection:
        """Generate personalized preparation strategy"""
        
        priority_items = gap_analysis.get("preparation_priority", [])
        missing_skills = gap_analysis.get("missing_skills", [])
        match_score = gap_analysis.get("overall_match_score", 0)
        
        strategy_content = f"""
## Your Preparation Roadmap

Based on your {match_score}% match score, here's your personalized preparation strategy:

### Immediate Priorities (Next 2-3 Days)
{chr(10).join([f'- {item}' for item in priority_items[:3]])}

        ### This Week
{chr(10).join([f'- Review {skill.get("job_requirement", skill.get("skill_name", ""))} basics' for skill in missing_skills[:3] if skill.get("importance") == "required" and (skill.get("job_requirement") or skill.get("skill_name"))])}

### Study Schedule
- **Technical prep**: 60% of time on gap areas
- **Behavioral prep**: 25% of time on STAR examples  
- **Company research**: 15% of time on culture/mission
"""
        
        why_important = f"This targeted approach maximizes your preparation time by focusing on your specific gaps and strengths."
        
        action_items = [
            "Complete priority technical reviews",
            "Prepare 5-7 STAR behavioral examples",
            "Practice explaining your project experiences",
            "Research company's recent news and developments"
        ]
        
        return PersonalizedGuideSection(
            title="Preparation Strategy",
            content=strategy_content,
            why_important=why_important,
            action_items=action_items,
            time_to_complete="5-7 hours over 3-5 days"
        )
    
    async def _generate_talking_points(self, resume_data: Dict[str, Any], 
                                     gap_analysis: Dict[str, Any]) -> PersonalizedGuideSection:
        """Generate personalized talking points from resume"""
        
        strong_matches = gap_analysis.get("strong_matches", [])
        competitive_advantages = gap_analysis.get("competitive_advantages", [])
        
        # Extract key achievements
        key_achievements = []
        for exp in resume_data.get("experience", [])[:2]:
            if isinstance(exp, dict):
                achievements = exp.get("achievements", [])[:2]
                key_achievements.extend(achievements)
        
        # Extract notable projects
        notable_projects = []
        for project in resume_data.get("projects", [])[:3]:
            if isinstance(project, dict):
                notable_projects.append({
                    "name": project.get("name", ""),
                    "description": project.get("description", ""),
                    "technologies": project.get("technologies", [])
                })
        
        content = f"""
## Your Key Talking Points

### Lead with Your Strengths
{chr(10).join([f'- **{match.get("resume_skill", match.get("job_requirement", ""))}**: Highlight your {match.get("resume_skill", "")} experience' for match in strong_matches[:3] if match.get("resume_skill") or match.get("job_requirement")])}

### Competitive Advantages
{chr(10).join([f'- {advantage}' for advantage in competitive_advantages[:3]])}

### Project Highlights
{chr(10).join([f'- **{proj["name"]}**: {proj["description"][:100]}...' for proj in notable_projects[:3] if proj.get("name") and proj.get("description")])}

### Achievement Examples
{chr(10).join([f'- {achievement[:100]}...' for achievement in key_achievements[:3] if achievement])}
"""
        
        why_important = "These talking points are directly pulled from your background and align with what this role values most."
        
        action_items = [
            "Practice describing each project in 2-3 minutes",
            "Quantify achievements with specific numbers",
            "Prepare follow-up details for each talking point",
            "Connect each point back to the role requirements"
        ]
        
        return PersonalizedGuideSection(
            title="Key Talking Points",
            content=content,
            why_important=why_important,
            action_items=action_items,
            time_to_complete="2 hours preparation"
        )
    
    async def _generate_questions_to_ask(self, job_data: Dict[str, Any], 
                                       gap_analysis: Dict[str, Any]) -> List[str]:
        """Generate smart questions for the candidate to ask"""
        
        company = job_data.get("company", "Unknown Company")
        role = job_data.get("role", "Unknown Role")
        company_stage = job_data.get("company_stage", "enterprise")
        missing_skills = gap_analysis.get("missing_skills", [])
        
        questions = [
            f"What does success look like for a {role} in the first 90 days?",
            f"How does the team approach professional development and learning?",
            f"What are the biggest technical challenges facing the team right now?",
            f"How does {company} support career growth for {role}s?",
            f"What's the collaboration like between {role} and other teams?"
        ]
        
        # Add questions about learning opportunities for missing skills
        if missing_skills:
            skill_names = [skill.get("job_requirement", skill.get("skill_name", "")) for skill in missing_skills[:2] if skill.get("job_requirement") or skill.get("skill_name")]
            if skill_names:
                questions.append(f"Are there opportunities to develop skills in {', '.join(skill_names)}?")
        
        return questions[:6]
    
    async def _generate_day_of_preparation(self, gap_analysis: Dict[str, Any], 
                                         job_data: Dict[str, Any]) -> PersonalizedGuideSection:
        """Generate day-of interview preparation"""
        
        match_score = gap_analysis.get("overall_match_score", 0)
        strong_matches = gap_analysis.get("strong_matches", [])
        
        content = f"""
## Day-of-Interview Checklist

### Morning Review (30 minutes)
- Review your top 3 strengths: {', '.join([m.get('resume_skill', m.get('job_requirement', '')) for m in strong_matches[:3] if m.get('resume_skill') or m.get('job_requirement')])}
- Practice your 2-minute elevator pitch
- Review company's recent news/updates
- Check logistics (time, location, interviewer names)

### Mental Preparation
- Confidence booster: You have a {match_score}% match score
- Remember your competitive advantages
- Focus on learning and growth mindset for any gaps

### Final Reminders
- Bring copies of resume and portfolio
- Prepare notepad for notes and questions
- Arrive 10 minutes early
- Dress appropriately for company culture
"""
        
        why_important = "Last-minute preparation builds confidence and ensures you're mentally ready to showcase your best self."
        
        action_items = [
            "Set up outfit and materials the night before",
            "Do a practice run of your travel route",
            "Review your talking points one final time",
            "Get good sleep and eat a proper breakfast"
        ]
        
        return PersonalizedGuideSection(
            title="Day-of Preparation",
            content=content,
            why_important=why_important,
            action_items=action_items,
            time_to_complete="30 minutes morning of"
        )
    
    def _generate_success_metrics(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """Generate success metrics for the interview"""
        
        match_score = gap_analysis.get("overall_match_score", 0)
        strong_matches = len(gap_analysis.get("strong_matches", []))
        
        metrics = [
            f"Successfully demonstrate {strong_matches} core strengths",
            "Ask 3-4 thoughtful questions about the role/team",
            "Share specific examples from your background",
            "Show enthusiasm for learning and growth"
        ]
        
        if match_score >= 70:
            metrics.append("Position yourself as a strong candidate ready to contribute immediately")
        else:
            metrics.append("Show strong learning agility and potential for growth")
        
        return metrics 