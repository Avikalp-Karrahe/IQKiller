from typing import Any, Dict, List, Optional
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric
import json

class InterviewGuideMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        resume_data = data.get("resume_data", {})
        enriched_data = data.get("enriched", {})
        gap_analysis = data.get("gap_analysis", {})
        
        if not resume_data or "error" in resume_data:
            return {**data, "interview_guide": {"error": "No resume data available"}}
        
        if not enriched_data or enriched_data.get("error"):
            return {**data, "interview_guide": {"error": "No job data available"}}
        
        if not gap_analysis or "error" in gap_analysis:
            return {**data, "interview_guide": {"error": "No gap analysis available"}}
        
        try:
            # Generate personalized interview guide
            guide = self._generate_interview_guide(resume_data, enriched_data, gap_analysis)
            
            log_metric("interview_guide_success", {
                "sections_count": len(guide.get("sections", {})),
                "questions_count": sum(len(q) for q in guide.get("questions", {}).values()),
                "match_score": gap_analysis.get("match_score", 0)
            })
            
            return {**data, "interview_guide": guide}
            
        except Exception as e:
            log_metric("interview_guide_error", {"error": str(e)})
            return {**data, "interview_guide": {"error": f"Interview guide generation failed: {e}"}}
    
    def _generate_interview_guide(self, resume_data: Dict[str, Any], 
                                 job_data: Dict[str, Any], 
                                 gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive personalized interview guide"""
        
        # Extract key information
        role = job_data.get("role", "Unknown Role")
        company = job_data.get("company", "Unknown Company")
        match_score = gap_analysis.get("match_score", 0)
        strong_matches = gap_analysis.get("strong_matches", [])
        gaps = gap_analysis.get("gaps", [])
        
        # Generate introduction
        introduction = self._generate_introduction(role, company, resume_data, gap_analysis)
        
        # Generate skills analysis section
        skills_analysis = self._generate_skills_analysis(gap_analysis)
        
        # Generate interview process section
        interview_process = self._generate_interview_process(company, role)
        
        # Generate question sections
        questions = self._generate_question_sections(role, strong_matches, gaps, resume_data)
        
        # Generate preparation tips
        preparation_tips = self._generate_preparation_tips(gaps, strong_matches, match_score)
        
        # Generate talking points
        talking_points = self._generate_talking_points(resume_data, strong_matches)
        
        # Generate smart questions to ask
        smart_questions = self._generate_smart_questions(company, role, job_data)
        
        # Generate conclusion with resources
        conclusion = self._generate_conclusion(role, company, gaps)
        
        return {
            "introduction": introduction,
            "skills_analysis": skills_analysis,
            "interview_process": interview_process,
            "questions": questions,
            "preparation_tips": preparation_tips,
            "talking_points": talking_points,
            "smart_questions": smart_questions,
            "conclusion": conclusion,
            "metadata": {
                "role": role,
                "company": company,
                "match_score": match_score,
                "generated_at": self._get_timestamp()
            }
        }
    
    def _generate_introduction(self, role: str, company: str, 
                              resume_data: Dict[str, Any], 
                              gap_analysis: Dict[str, Any]) -> str:
        """Generate personalized introduction"""
        
        match_score = gap_analysis.get("match_score", 0)
        summary = gap_analysis.get("summary", "")
        
        # Extract user's background
        experience = resume_data.get("experience", [])
        years_exp = len(experience)
        
        recent_role = ""
        if experience:
            recent_role = experience[0].get("title", "") if isinstance(experience[0], dict) else ""
        
        prompt = f"""
Write a personalized interview guide introduction for:
- Target Role: {role} at {company}
- Candidate Background: {recent_role} with {years_exp} roles
- Match Score: {match_score}%
- Gap Summary: {summary}

Use a confident, mentor-like tone. Start with the primary keyword "{role} interview" in the first 100 words.
Address the candidate directly ("you") and reference their specific background.
Keep it ≤150 words, 3 sentences max per paragraph.

Focus on:
1. What makes this role exciting for someone with their background
2. Their competitive advantages 
3. What this guide will help them achieve
"""
        
        return llm_client.call_llm(prompt)
    
    def _generate_skills_analysis(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visual skills analysis section"""
        
        skills_map = gap_analysis.get("skills_map", {})
        match_score = gap_analysis.get("match_score", 0)
        summary = gap_analysis.get("summary", "")
        
        # Create bar chart data for visualization
        chart_data = {
            "strong_matches": len(skills_map.get("strong", [])),
            "partial_matches": len(skills_map.get("partial", [])),
            "gaps": len(skills_map.get("gaps", []))
        }
        
        return {
            "match_score": match_score,
            "summary": summary,
            "skills_breakdown": skills_map,
            "chart_data": chart_data
        }
    
    def _generate_interview_process(self, company: str, role: str) -> str:
        """Generate interview process section"""
        
        prompt = f"""
Describe the typical interview process for a {role} position at {company}.
If you don't know the specific company process, describe the general process for this role type.

Include:
1. Number of rounds typically
2. Types of interviews (phone, technical, behavioral, onsite)
3. Who you'll likely meet with
4. Timeline expectations
5. Any company-specific details if known

Use markdown formatting with headers. Keep conversational and actionable.
Max 200 words.
"""
        
        return llm_client.call_llm(prompt)
    
    def _generate_question_sections(self, role: str, strong_matches: List[str], 
                                   gaps: List[str], resume_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Generate categorized interview questions with personalized advice"""
        
        questions = {}
        
        # Technical questions (prioritize gaps)
        technical_questions = self._generate_technical_questions(role, gaps, strong_matches)
        if technical_questions:
            questions["technical"] = technical_questions
        
        # Behavioral questions
        behavioral_questions = self._generate_behavioral_questions(role, resume_data)
        if behavioral_questions:
            questions["behavioral"] = behavioral_questions
        
        # Company-specific questions
        company_questions = self._generate_company_questions(role)
        if company_questions:
            questions["company"] = company_questions
        
        return questions
    
    def _generate_technical_questions(self, role: str, gaps: List[str], 
                                     strong_matches: List[str]) -> List[Dict[str, str]]:
        """Generate technical questions with personalized approach guidance"""
        
        # Prioritize gap areas for question focus
        focus_areas = gaps[:3] if gaps else strong_matches[:3]
        
        prompt = f"""
Generate 5 technical interview questions for a {role} position.
Focus areas based on candidate needs: {', '.join(focus_areas)}

For each question, provide:
1. The question
2. A 2-3 sentence approach tailored to someone who needs to strengthen {focus_areas[0] if focus_areas else 'general skills'}

Format as JSON array:
[
  {{
    "question": "Question text",
    "approach": "Personalized approach advice",
    "difficulty": "beginner|intermediate|advanced"
  }}
]

Focus on practical, real-world questions that test understanding.
"""
        
        try:
            response = llm_client.call_llm(prompt)
            # Parse JSON response
            import json
            from text_extractor import robust_json_parse
            questions_data = robust_json_parse(response)
            if isinstance(questions_data, list):
                return questions_data
        except:
            pass
        
        # Fallback questions
        return [
            {
                "question": f"How would you approach solving a {role.lower()} problem?",
                "approach": "Focus on your systematic problem-solving process and mention relevant experience.",
                "difficulty": "intermediate"
            }
        ]
    
    def _generate_behavioral_questions(self, role: str, resume_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate behavioral questions with personalized advice"""
        
        # Extract key experiences for STAR method guidance
        experience = resume_data.get("experience", [])
        recent_achievements = []
        
        for exp in experience[:2]:  # Focus on recent experience
            if isinstance(exp, dict):
                achievements = exp.get("achievements", [])
                if achievements:
                    recent_achievements.extend(achievements[:2])
        
        prompt = f"""
Generate 5 behavioral interview questions for a {role} position.
Candidate's recent achievements: {', '.join(recent_achievements[:3])}

For each question, provide specific STAR method guidance using their background.

Format as JSON array:
[
  {{
    "question": "Question text",
    "approach": "STAR method guidance referencing their specific experience",
    "difficulty": "standard"
  }}
]

Focus on leadership, problem-solving, teamwork, and role-specific scenarios.
"""
        
        try:
            response = llm_client.call_llm(prompt)
            from text_extractor import robust_json_parse
            questions_data = robust_json_parse(response)
            if isinstance(questions_data, list):
                return questions_data
        except:
            pass
        
        # Fallback questions
        return [
            {
                "question": "Tell me about a challenging project you worked on.",
                "approach": "Use STAR method: Situation, Task, Action, Result. Draw from your recent experience.",
                "difficulty": "standard"
            }
        ]
    
    def _generate_company_questions(self, role: str) -> List[Dict[str, str]]:
        """Generate company-specific questions"""
        
        return [
            {
                "question": "Why are you interested in this role?",
                "approach": "Connect your career goals with the company's mission and this specific role's impact.",
                "difficulty": "standard"
            },
            {
                "question": "What do you know about our company?",
                "approach": "Research their recent news, mission, and values. Show genuine interest in their work.",
                "difficulty": "standard"
            }
        ]
    
    def _generate_preparation_tips(self, gaps: List[str], strong_matches: List[str], 
                                  match_score: int) -> Dict[str, List[str]]:
        """Generate personalized preparation tips"""
        
        tips = {}
        
        # Tips for gap areas (priority)
        if gaps:
            gap_tips = []
            for gap in gaps[:3]:
                gap_tips.append(f"Study {gap} fundamentals - focus on practical applications")
                gap_tips.append(f"Find online tutorials or courses for {gap}")
                gap_tips.append(f"Practice explaining {gap} concepts in simple terms")
            tips["priority_areas"] = gap_tips[:5]
        
        # Tips for strength areas
        if strong_matches:
            strength_tips = []
            for strength in strong_matches[:3]:
                strength_tips.append(f"Prepare advanced examples showcasing your {strength} expertise")
                strength_tips.append(f"Think of specific metrics/results from {strength} projects")
            tips["leverage_strengths"] = strength_tips[:5]
        
        # General tips based on match score
        if match_score < 60:
            tips["general"] = [
                "Focus heavily on demonstrating learning ability and enthusiasm",
                "Prepare questions that show your eagerness to grow",
                "Research the company thoroughly to show genuine interest"
            ]
        else:
            tips["general"] = [
                "Practice articulating your experience clearly and confidently",
                "Prepare specific examples that align with job requirements",
                "Focus on cultural fit and long-term career alignment"
            ]
        
        return tips
    
    def _generate_talking_points(self, resume_data: Dict[str, Any], 
                                strong_matches: List[str]) -> List[str]:
        """Generate specific talking points based on resume"""
        
        talking_points = []
        
        # From recent experience
        experience = resume_data.get("experience", [])
        if experience:
            recent_exp = experience[0]
            if isinstance(recent_exp, dict):
                achievements = recent_exp.get("achievements", [])
                talking_points.extend(achievements[:2])
        
        # From projects
        projects = resume_data.get("projects", [])
        for project in projects[:2]:
            if isinstance(project, dict):
                name = project.get("name", "")
                description = project.get("description", "")
                if name and description:
                    talking_points.append(f"{name}: {description}")
        
        # From strong matches
        for match in strong_matches[:3]:
            talking_points.append(f"Deep experience with {match} from multiple projects")
        
        return talking_points[:6]
    
    def _generate_smart_questions(self, company: str, role: str, 
                                 job_data: Dict[str, Any]) -> List[str]:
        """Generate thoughtful questions for the candidate to ask"""
        
        questions = [
            f"What does success look like for someone in this {role} role after 6 months?",
            f"What are the biggest challenges facing the team/company right now?",
            "What opportunities for growth and learning does this role offer?",
            "How does this role contribute to the company's strategic goals?",
            "What do you enjoy most about working at this company?"
        ]
        
        # Add role-specific questions
        if "engineer" in role.lower():
            questions.append("What's the team's approach to code reviews and technical debt?")
            questions.append("How do you balance feature development with technical improvements?")
        elif "data" in role.lower():
            questions.append("What data infrastructure and tools does the team use?")
            questions.append("How do you ensure data quality and reliability?")
        
        return questions[:7]
    
    def _generate_conclusion(self, role: str, company: str, gaps: List[str]) -> Dict[str, str]:
        """Generate conclusion with resource links"""
        
        # Focus on top gap for learning resource
        primary_gap = gaps[0] if gaps else "general interview skills"
        
        return {
            "summary": f"This personalized guide gives you a strategic advantage for your {role} interview at {company}. Focus your preparation on the priority areas identified, leverage your strengths, and demonstrate your learning mindset.",
            "success_story_link": f"Read about someone who successfully landed a {role} role",
            "learning_resource_link": f"Top {primary_gap} learning resources for interview prep",
            "questions_practice_link": f"Practice {role} interview questions"
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat() 