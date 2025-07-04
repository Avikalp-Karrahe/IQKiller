from typing import Any, Dict, List, Optional
from metrics import log_metric

class EnhancedGuideRenderer:
    """Enhanced guide renderer for PersonalizedInterviewGuide data structure"""
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render PersonalizedInterviewGuide to formatted markdown"""
        
        interview_guide = data.get("personalized_guide", {})
        resume_data = data.get("resume_data_enhanced", {})
        job_data = data.get("job_data_enhanced", {})
        gap_analysis = data.get("gap_analysis_advanced", {})
        
        if not interview_guide or "error" in interview_guide:
            return {**data, "rendered_guide": "# Interview Guide Generation Failed\n\nPlease try again with valid resume and job data."}
        
        try:
            # Render comprehensive markdown guide
            rendered_guide = self._render_personalized_guide(
                interview_guide, job_data, gap_analysis
            )
            
            log_metric("guide_render_success", {
                "total_length": len(rendered_guide),
                "sections_count": 12
            })
            
            return {**data, "rendered_guide": rendered_guide}
            
        except Exception as e:
            log_metric("guide_render_error", {"error": str(e)})
            fallback = self._create_fallback_guide(interview_guide, job_data, gap_analysis)
            return {**data, "rendered_guide": fallback}
    
    def _render_personalized_guide(self, guide: Dict[str, Any], job_data: Dict[str, Any], gap_analysis: Dict[str, Any]) -> str:
        """Render complete personalized interview guide"""
        
        # Extract data with fallbacks
        header = guide.get("header", {})
        role = header.get("role", job_data.get("role", "Data Scientist"))
        company = header.get("company", job_data.get("company", "Spotify"))
        match_score = header.get("match_score", gap_analysis.get("overall_match_score", 0))
        match_level = header.get("match_level", "Good Match")
        match_emoji = header.get("match_emoji", "🟢")
        
        sections = []
        
        # Header with correct match score
        sections.append(f"""# 🎯 Personalized Interview Guide: {role} at {company}

**Match Score**: {match_emoji} {match_level} ({match_score:.1f}%)

---""")
        
        # Executive Summary
        executive_summary = guide.get("executive_summary", "")
        if executive_summary:
            sections.append(f"""## Introduction

{executive_summary}""")
        
        # Skills Analysis
        skills_analysis = guide.get("skills_analysis", {})
        if skills_analysis:
            sections.append(self._render_skills_analysis(skills_analysis, gap_analysis))
        
        # Interview Process
        interview_process = guide.get("interview_process", {})
        if interview_process:
            sections.append(f"""## What Is the Interview Process Like at {company}?

{interview_process.get('content', '')}

**Why This Matters**: {interview_process.get('why_important', '')}

**Action Items** ({interview_process.get('time_to_complete', '30 minutes')}):
{self._format_action_items(interview_process.get('action_items', []))}""")
        
        # Technical Questions
        technical_questions = guide.get("technical_questions", [])
        if technical_questions:
            sections.append(self._render_questions_section(
                "🔧 Technical & Problem-Solving Questions",
                technical_questions,
                f"These questions test your technical knowledge for the {role} role. Focus on demonstrating both your understanding and problem-solving approach."
            ))
        
        # Behavioral Questions  
        behavioral_questions = guide.get("behavioral_questions", [])
        if behavioral_questions:
            sections.append(self._render_questions_section(
                "🎯 Behavioral & Experience Questions", 
                behavioral_questions,
                "Use the STAR method (Situation, Task, Action, Result) to structure your responses. Draw from specific examples in your background."
            ))
        
        # Company Questions
        company_questions = guide.get("company_questions", [])
        if company_questions:
            sections.append(self._render_questions_section(
                "🏢 Company & Culture Questions",
                company_questions, 
                f"These questions assess your interest in {company} and cultural fit. Research thoroughly and be genuine in your responses."
            ))
        
        # Preparation Strategy
        preparation_strategy = guide.get("preparation_strategy", {})
        if preparation_strategy:
            sections.append(f"""## 🎯 Preparation Strategy

{preparation_strategy.get('content', '')}

**Why This Matters**: {preparation_strategy.get('why_important', '')}

**Action Items** ({preparation_strategy.get('time_to_complete', '2-3 hours')}):
{self._format_action_items(preparation_strategy.get('action_items', []))}""")
        
        # Key Talking Points
        talking_points = guide.get("talking_points", {})
        if talking_points:
            sections.append(f"""## 💬 Key Talking Points

Highlight these specific achievements and experiences during your interview:

{talking_points.get('content', '')}

**Why This Matters**: {talking_points.get('why_important', '')}

**Action Items** ({talking_points.get('time_to_complete', '1 hour')}):
{self._format_action_items(talking_points.get('action_items', []))}""")
        
        # Smart Questions to Ask
        questions_to_ask = guide.get("questions_to_ask", [])
        if questions_to_ask:
            sections.append(f"""## ❓ Smart Questions to Ask

Show your engagement and strategic thinking with these questions:

{self._format_questions_list(questions_to_ask)}""")
        
        # Day-of Preparation
        day_of_preparation = guide.get("day_of_preparation", {})
        if day_of_preparation:
            sections.append(f"""## 📅 Day-of-Interview Preparation

{day_of_preparation.get('content', '')}

**Action Items** ({day_of_preparation.get('time_to_complete', '1 hour before')}):
{self._format_action_items(day_of_preparation.get('action_items', []))}""")
        
        # Success Metrics
        success_metrics = guide.get("success_metrics", [])
        if success_metrics:
            sections.append(f"""## ✅ Success Metrics

You'll know the interview went well if:

{self._format_success_metrics(success_metrics)}""")
        
        # Footer
        sections.append(f"""## 🚀 Conclusion

You're well-prepared for this {role} interview at {company}! Your {match_score:.1f}% match score indicates strong alignment with their requirements.

**Remember**: 
- Be authentic and confident
- Ask thoughtful questions  
- Show enthusiasm for {company}
- Highlight your unique value proposition

Good luck with your interview! 🚀

---

*This personalized guide was generated based on your specific background and the target role requirements.*""")
        
        return "\n\n".join(sections)
    
    def _render_skills_analysis(self, skills_analysis: Dict[str, Any], gap_analysis: Dict[str, Any]) -> str:
        """Render skills analysis with proper data"""
        
        # Get data from gap_analysis as fallback
        strong_matches = gap_analysis.get("strong_matches", [])
        partial_matches = gap_analysis.get("partial_matches", [])
        gaps = gap_analysis.get("gaps", [])
        
        # Create visual representation
        strong_count = len(strong_matches)
        partial_count = len(partial_matches)
        gaps_count = len(gaps)
        total = strong_count + partial_count + gaps_count
        
        if total > 0:
            strong_bar = "█" * min(20, int((strong_count / total) * 20)) if strong_count > 0 else ""
            partial_bar = "▒" * min(20, int((partial_count / total) * 20)) if partial_count > 0 else ""
            gaps_bar = "░" * min(20, int((gaps_count / total) * 20)) if gaps_count > 0 else ""
        else:
            strong_bar = partial_bar = gaps_bar = ""
        
        # Get skill names
        strong_names = [match.get("resume_skill", match.get("job_requirement", "")) for match in strong_matches[:5]]
        partial_names = [match.get("resume_skill", match.get("job_requirement", "")) for match in partial_matches[:5]]
        gap_names = [gap.get("job_requirement", "") for gap in gaps[:5]]
        
        return f"""## 📊 Skills Match Analysis

**Overall Assessment**: {skills_analysis.get('summary', 'Strong technical background with relevant experience in data science and analytics.')}

### Skills Breakdown
```
Strong Matches  {strong_bar} {strong_count}
Partial Matches {partial_bar} {partial_count}  
Skill Gaps      {gaps_bar} {gaps_count}
```

**✅ Your Strengths**: {', '.join(strong_names) if strong_names else 'Core technical skills identified'}

{f"**⚡ Areas to Highlight**: {', '.join(partial_names)}" if partial_names else ""}

{f"**📚 Priority Learning**: {', '.join(gap_names)}" if gap_names else ""}"""
    
    def _render_questions_section(self, title: str, questions: List[Dict], intro: str) -> str:
        """Render questions with proper formatting"""
        
        section = f"""## {title}

{intro}

"""
        
        for i, q in enumerate(questions, 1):
            question_text = q.get("question", "")
            difficulty = q.get("difficulty", "medium")
            why_asked = q.get("why_asked", "")
            approach_strategy = q.get("approach_strategy", "")
            example_points = q.get("example_points", [])
            
            # Difficulty indicator
            if difficulty == "hard":
                diff_icon = "🔴"
            elif difficulty == "medium":
                diff_icon = "🟡"
            else:
                diff_icon = "🟢"
            
            section += f"""### {diff_icon} Question {i}: {question_text}

**Why they ask this**: {why_asked}

**How to approach**: {approach_strategy}

{f"**Key points to mention**: {', '.join(example_points[:3])}" if example_points else ""}

---

"""
        
        return section.rstrip()
    
    def _format_action_items(self, items: List[str]) -> str:
        """Format action items as bullet list"""
        return "\n".join([f"- {item}" for item in items]) if items else "- Review your background and prepare examples"
    
    def _format_questions_list(self, questions: List[str]) -> str:
        """Format questions as numbered list"""
        return "\n".join([f"{i}. {q}" for i, q in enumerate(questions, 1)]) if questions else "1. What excites you most about this role?"
    
    def _format_success_metrics(self, metrics: List[str]) -> str:
        """Format success metrics as bullet list"""
        return "\n".join([f"- {metric}" for metric in metrics]) if metrics else "- Strong rapport with interviewers\n- Technical discussions flow naturally\n- You feel confident about your responses"
    
    def _create_fallback_guide(self, guide: Dict[str, Any], job_data: Dict[str, Any], gap_analysis: Dict[str, Any]) -> str:
        """Create fallback guide if rendering fails"""
        
        role = job_data.get("role", "Data Scientist")
        company = job_data.get("company", "the company")
        match_score = gap_analysis.get("overall_match_score", 0)
        
        return f"""# 🎯 Interview Guide: {role} at {company}

**Match Score**: {match_score:.1f}%

## Summary
You have a strong background that aligns well with this {role} position. Focus your preparation on highlighting your relevant experience and technical skills.

## Key Preparation Areas
- Review your technical projects and be ready to discuss them in detail
- Prepare specific examples using the STAR method
- Research {company} and prepare thoughtful questions
- Practice explaining complex concepts in simple terms

## Technical Focus Areas
Based on your background, be prepared to discuss:
- Data analysis and visualization
- Programming experience (Python, SQL, etc.)
- Statistical methods and machine learning
- Project outcomes and business impact

Good luck with your interview! 🚀""" 