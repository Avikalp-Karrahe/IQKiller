from typing import Any, Dict, Optional
from metrics import log_metric

class RenderMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        draft = data.get("draft", "")
        qa_result = data.get("qa_result", "")
        critique = data.get("critique", "")
        enriched_data = data.get("enriched", {})
        quality_score = data.get("quality_score")
        
        try:
            # Create comprehensive markdown output
            rendered = self._create_final_output(draft, qa_result, critique, enriched_data, quality_score)
            
            # Add bucket processing
            bucket_facts = data.get("bucket_facts", {})
            bucket_markdown = ""
            if bucket_facts:
                from bucket_map import map_facts
                from render_buckets import render_buckets
                
                buckets = map_facts(bucket_facts)
                bucket_markdown = render_buckets(bucket_facts, buckets)
                
                log_metric("bucket_missing", {
                    "empty_buckets": len([k for k, v in buckets.items() if not v or (len(v) == 1 and "research needed" in v[0].lower())])
                })
            
            log_metric("render_success", {
                "total_length": len(rendered),
                "has_qa": bool(qa_result),
                "has_critique": bool(critique),
                "quality_score": quality_score,
                "has_buckets": bool(bucket_markdown)
            })
            
            return {**data, "rendered_markdown": rendered, "bucket_markdown": bucket_markdown}
            
        except Exception as e:
            log_metric("render_error", {"error": str(e)})
            fallback = f"# Job Analysis Results\n\n{draft}\n\n---\n\nQA: {qa_result}\n\nCritique: {critique}"
            return {**data, "rendered_markdown": fallback, "bucket_markdown": ""}
    
    def _create_final_output(self, draft: str, qa_result: str, critique: str, enriched_data: Dict, quality_score: Optional[float] = None) -> str:
        """Create comprehensive final output"""
        
        # Header with quality indicator
        quality_indicator = ""
        if quality_score:
            if quality_score >= 8:
                quality_indicator = "🟢 High Quality"
            elif quality_score >= 6:
                quality_indicator = "🟡 Good Quality"
            else:
                quality_indicator = "🔴 Needs Improvement"
        
        # Extract key job info for header
        role = enriched_data.get("role", "Unknown Role")
        company = enriched_data.get("company", "Unknown Company")
        level = enriched_data.get("level", "")
        
        header = f"""# 🎯 {role} at {company}
{f"**Level**: {level}" if level else ""}
{f"**Quality**: {quality_indicator}" if quality_indicator else ""}

---
"""
        
        # Main content (the draft)
        main_content = draft if draft else "Content generation failed."
        
        # QA and Critique sections (collapsible)
        qa_section = ""
        if qa_result and qa_result != "QA skipped due to draft errors.":
            qa_section = f"""

<details>
<summary>📋 Quality Assurance Results</summary>

{qa_result}

</details>
"""
        
        critique_section = ""
        if critique and critique != "Critique skipped due to draft errors.":
            critique_section = f"""

<details>
<summary>🔍 Expert Critique</summary>

{critique}

</details>
"""
        
        # Footer with metadata
        tech_stack = enriched_data.get("tech_stack", [])
        work_mode = enriched_data.get("work_mode", "")
        salary_range = enriched_data.get("salary_range", "")
        
        metadata = []
        if tech_stack:
            metadata.append(f"**Tech Stack**: {', '.join(tech_stack[:5])}")
        if work_mode:
            metadata.append(f"**Work Mode**: {work_mode}")
        if salary_range and salary_range != "Not specified":
            metadata.append(f"**Salary**: {salary_range}")
        
        footer = ""
        if metadata:
            footer = f"""

---
## 📊 Quick Facts
{chr(10).join([f"- {item}" for item in metadata])}
"""
        
        # Combine all sections
        final_output = header + main_content + qa_section + critique_section + footer
        
        return final_output 