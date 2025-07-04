from typing import Any, Dict
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric

class DraftMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        enriched_data = data.get("enriched", {})
        scraped_text = data.get("scraped_text", "")
        
        if not enriched_data or enriched_data.get("error"):
            return {**data, "draft": "Unable to draft content due to enrichment errors."}
        
        try:
            # Prepare context for drafting
            context = {
                "role": enriched_data.get("role", "Unknown Role"),
                "company": enriched_data.get("company", "Unknown Company"),
                "level": enriched_data.get("level", "Unknown Level"),
                "requirements": enriched_data.get("requirements", []),
                "responsibilities": enriched_data.get("responsibilities", []),
                "tech_stack": enriched_data.get("tech_stack", []),
                "salary_range": enriched_data.get("salary_range", "Not specified"),
                "work_mode": enriched_data.get("work_mode", "Not specified")
            }
            
            # Use LLM to draft comprehensive content
            prompt = prompt_loader.get_prompt("draft_prompt", job_data=str(context))
            
            detailed_prompt = prompt + f"""

Based on this job data: {context}

Create a comprehensive role preview and interview preparation kit with:

## 🎯 Role Overview
- Role summary and key focus areas
- Company context and culture fit

## 📋 Key Responsibilities & Requirements
- Core responsibilities breakdown
- Must-have vs nice-to-have skills
- Technical requirements analysis

## 💰 Compensation & Benefits
- Salary analysis and market context
- Benefits and perquisites

## 🎯 Interview Preparation
- Likely interview questions based on the role
- Technical topics to review
- Company-specific research areas
- Questions to ask the interviewer

## 🚀 Next Steps
- Application strategy
- Timeline expectations
- Follow-up recommendations

Format as clear, actionable markdown suitable for job seekers.
"""
            
            draft_content = llm_client.call_llm(detailed_prompt)
            
            log_metric("draft_success", {
                "role": context["role"],
                "company": context["company"],
                "content_length": len(draft_content)
            })
            
            return {**data, "draft": draft_content}
            
        except Exception as e:
            log_metric("draft_error", {"error": str(e)})
            return {**data, "draft": f"Draft generation failed: {e}"} 