from typing import Any, Dict, List, Optional
from metrics import log_metric

class GuideRenderMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        interview_guide = data.get("interview_guide", {})
        
        if not interview_guide or "error" in interview_guide:
            return {**data, "rendered_guide": "# Interview Guide Generation Failed\n\nPlease try again with valid resume and job data."}
        
        try:
            # Render comprehensive markdown guide
            rendered_guide = self._render_interview_guide(interview_guide)
            
            log_metric("guide_render_success", {
                "total_length": len(rendered_guide),
                "sections_count": len(interview_guide.keys())
            })
            
            return {**data, "rendered_guide": rendered_guide}
            
        except Exception as e:
            log_metric("guide_render_error", {"error": str(e)})
            fallback = self._create_fallback_guide(interview_guide)
            return {**data, "rendered_guide": fallback}
    
    def _render_interview_guide(self, guide: Dict[str, Any]) -> str:
        """Render complete interview guide in Interview Query style"""
        
        metadata = guide.get("metadata", {})
        role = metadata.get("role", "Unknown Role")
        company = metadata.get("company", "Unknown Company")
        match_score = metadata.get("match_score", 0)
        
        # Build comprehensive guide
        sections = []
        
        # Header
        sections.append(self._render_header(role, company, match_score))
        
        # Introduction
        sections.append(self._render_introduction(guide.get("introduction", "")))
        
        # Skills Analysis with visual
        sections.append(self._render_skills_analysis(guide.get("skills_analysis", {})))
        
        # Interview Process
        sections.append(self._render_interview_process(company, guide.get("interview_process", "")))
        
        # Question Sections
        sections.append(self._render_questions(guide.get("questions", {}), role))
        
        # Preparation Strategy
        sections.append(self._render_preparation_tips(guide.get("preparation_tips", {})))
        
        # Talking Points
        sections.append(self._render_talking_points(guide.get("talking_points", [])))
        
        # Smart Questions to Ask
        sections.append(self._render_smart_questions(guide.get("smart_questions", [])))
        
        # Conclusion with Resources
        sections.append(self._render_conclusion(guide.get("conclusion", {})))
        
        return "\n\n".join(sections)
    
    def _render_header(self, role: str, company: str, match_score: int) -> str:
        """Render header with match score indicator"""
        
        # Match score indicator
        if match_score >= 80:
            score_indicator = "🟢 Excellent Match"
            score_color = "green"
        elif match_score >= 60:
            score_indicator = "🟡 Good Match"
            score_color = "yellow"
        elif match_score >= 40:
            score_indicator = "🟠 Moderate Match"
            score_color = "orange"
        else:
            score_indicator = "🔴 Challenging Match"
            score_color = "red"
        
        return f"""# 🎯 Personalized Interview Guide: {role} at {company}

**Match Score**: {score_indicator} ({match_score}%)

---"""
    
    def _render_introduction(self, introduction: str) -> str:
        """Render introduction section"""
        return f"""## Introduction

{introduction}"""
    
    def _render_skills_analysis(self, skills_analysis: Dict[str, Any]) -> str:
        """Render skills analysis with visual chart"""
        
        match_score = skills_analysis.get("match_score", 0)
        summary = skills_analysis.get("summary", "")
        skills_breakdown = skills_analysis.get("skills_breakdown", {})
        chart_data = skills_analysis.get("chart_data", {})
        
        # Create text-based bar chart
        strong_count = chart_data.get("strong_matches", 0)
        partial_count = chart_data.get("partial_matches", 0)
        gaps_count = chart_data.get("gaps", 0)
        total = strong_count + partial_count + gaps_count
        
        if total > 0:
            strong_bar = "█" * min(20, int((strong_count / total) * 20))
            partial_bar = "▒" * min(20, int((partial_count / total) * 20))
            gaps_bar = "░" * min(20, int((gaps_count / total) * 20))
        else:
            strong_bar = partial_bar = gaps_bar = ""
        
        chart = f"""
### Skills Match Analysis

**Overall Assessment**: {summary}

#### Skills Breakdown
```
Strong Matches  {strong_bar} {strong_count}
Partial Matches {partial_bar} {partial_count}  
Skill Gaps      {gaps_bar} {gaps_count}
```
"""
        
        # Add detailed breakdowns
        if skills_breakdown:
            if skills_breakdown.get("strong"):
                chart += f"\n**✅ Your Strengths**: {', '.join(skills_breakdown['strong'][:5])}"
            
            if skills_breakdown.get("partial"):
                chart += f"\n\n**⚡ Areas to Highlight**: {', '.join(skills_breakdown['partial'][:5])}"
            
            if skills_breakdown.get("gaps"):
                chart += f"\n\n**📚 Priority Learning**: {', '.join(skills_breakdown['gaps'][:5])}"
        
        return chart
    
    def _render_interview_process(self, company: str, process_content: str) -> str:
        """Render interview process section"""
        return f"""## What Is the Interview Process Like at {company}?

{process_content}"""
    
    def _render_questions(self, questions: Dict[str, List[Dict]], role: str) -> str:
        """Render all question sections"""
        
        sections = []
        
        # Technical Questions
        if questions.get("technical"):
            sections.append(self._render_question_section(
                "Technical & Problem-Solving Questions",
                questions["technical"],
                f"These questions test your technical knowledge for the {role} role. Focus on demonstrating both your understanding and problem-solving approach."
            ))
        
        # Behavioral Questions
        if questions.get("behavioral"):
            sections.append(self._render_question_section(
                "Behavioral & Experience Questions",
                questions["behavioral"],
                "Use the STAR method (Situation, Task, Action, Result) to structure your responses. Draw from specific examples in your background."
            ))
        
        # Company Questions
        if questions.get("company"):
            sections.append(self._render_question_section(
                "Company & Culture Questions",
                questions["company"],
                "These questions assess your interest in the company and cultural fit. Research thoroughly and be genuine in your responses."
            ))
        
        return "\n\n".join(sections)
    
    def _render_question_section(self, title: str, questions: List[Dict], intro: str) -> str:
        """Render individual question section"""
        
        section = f"""## {title}

{intro}

"""
        
        for i, q in enumerate(questions, 1):
            question_text = q.get("question", "")
            approach = q.get("approach", "")
            difficulty = q.get("difficulty", "")
            
            # Add difficulty indicator
            if difficulty == "advanced":
                diff_icon = "🔴"
            elif difficulty == "intermediate":
                diff_icon = "🟡"
            else:
                diff_icon = "🟢"
            
            section += f"""**{i}. {question_text}** {diff_icon}

{approach}

"""
        
        return section.strip()
    
    def _render_preparation_tips(self, tips: Dict[str, List[str]]) -> str:
        """Render preparation tips section"""
        
        section = "## Preparation Strategy\n\n"
        
        # Priority areas (gaps)
        if tips.get("priority_areas"):
            section += "### 🎯 Priority Focus Areas\n\n"
            for tip in tips["priority_areas"]:
                section += f"- {tip}\n"
            section += "\n"
        
        # Leverage strengths
        if tips.get("leverage_strengths"):
            section += "### 💪 Leverage Your Strengths\n\n"
            for tip in tips["leverage_strengths"]:
                section += f"- {tip}\n"
            section += "\n"
        
        # General tips
        if tips.get("general"):
            section += "### 📋 General Interview Tips\n\n"
            for tip in tips["general"]:
                section += f"- {tip}\n"
            section += "\n"
        
        return section.strip()
    
    def _render_talking_points(self, talking_points: List[str]) -> str:
        """Render talking points section"""
        
        if not talking_points:
            return ""
        
        section = "## Key Talking Points\n\n"
        section += "Highlight these specific achievements and experiences during your interview:\n\n"
        
        for point in talking_points:
            section += f"- {point}\n"
        
        return section
    
    def _render_smart_questions(self, questions: List[str]) -> str:
        """Render smart questions section"""
        
        if not questions:
            return ""
        
        section = "## Smart Questions to Ask\n\n"
        section += "End your interview strong by asking thoughtful questions:\n\n"
        
        for question in questions:
            section += f"- {question}\n"
        
        return section
    
    def _render_conclusion(self, conclusion: Dict[str, str]) -> str:
        """Render conclusion with resources"""
        
        summary = conclusion.get("summary", "")
        
        section = f"""## Conclusion

{summary}

### Additional Resources

- [Success Story]({conclusion.get('success_story_link', '#')})
- [Learning Resources]({conclusion.get('learning_resource_link', '#')})
- [Practice Questions]({conclusion.get('questions_practice_link', '#')})

---

**Good luck with your interview!** 🚀

*This personalized guide was generated based on your specific background and the target role requirements.*"""
        
        return section
    
    def _create_fallback_guide(self, guide: Dict[str, Any]) -> str:
        """Create fallback guide if rendering fails"""
        
        return f"""# Personalized Interview Guide

## Summary
This guide was generated to help you prepare for your interview.

## Content
{str(guide)}

---
*Please try regenerating for better formatting.*""" 