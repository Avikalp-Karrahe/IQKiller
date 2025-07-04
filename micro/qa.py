from typing import Any, Dict
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric

class QAMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        draft = data.get("draft", "")
        enriched_data = data.get("enriched", {})
        
        if not draft or "failed" in draft.lower():
            return {**data, "qa_result": "QA skipped due to draft errors."}
        
        try:
            # Use LLM to perform quality assurance
            prompt = prompt_loader.get_prompt("qa_prompt", draft=draft)
            
            qa_prompt = prompt + f"""

Review this job role preview and interview kit for:

1. **Accuracy**: Does the content match the job data?
2. **Completeness**: Are all sections well-developed?
3. **Clarity**: Is the language clear and actionable?
4. **Formatting**: Is the markdown properly structured?
5. **Relevance**: Is the advice practical and current?

Job data context: {enriched_data}

Content to review:
{draft}

Provide feedback in this format:
## QA Results
- **Overall Quality**: [Pass/Needs Improvement/Fail]
- **Issues Found**: [List specific issues or "None"]
- **Suggestions**: [Improvement recommendations]
- **Auto-fixes Applied**: [Any corrections made]

If minor issues are found, provide the corrected version after your analysis.
"""
            
            qa_response = llm_client.call_llm(qa_prompt)
            
            # Add bucket verification
            bucket_markdown = data.get("bucket_markdown", "")
            
            if bucket_markdown:
                required_headers = [
                    "### Team & Manager",
                    "### Tech Stack Snapshot", 
                    "### Business Context",
                    "### Comp & Leveling",
                    "### Career Trajectory",
                    "### Culture/WLB",
                    "### Interview Runway",
                    "### Onboarding & Tooling",
                    "### Location/Remote",
                    "### Strategic Risks"
                ]
                
                missing_headers = []
                for header in required_headers:
                    if header not in bucket_markdown:
                        missing_headers.append(header)
                
                if missing_headers:
                    log_metric("qa_grade", {"bucket_verification": "FAIL", "missing": missing_headers})
                    qa_response += f"\n\n**BUCKET VERIFICATION FAILED**: Missing headers: {missing_headers}"
                else:
                    log_metric("qa_grade", {"bucket_verification": "PASS"})
                    qa_response += f"\n\n**BUCKET VERIFICATION PASSED**: All 10 bucket headers present"
            
            # Check if auto-fixes were applied
            if "corrected version" in qa_response.lower() or "auto-fixes applied" in qa_response.lower():
                # Extract corrected content if available
                parts = qa_response.split("## Corrected Version")
                if len(parts) > 1:
                    corrected_draft = parts[1].strip()
                    data["draft"] = corrected_draft
                    log_metric("qa_auto_fix", {"fixes_applied": True})
            
            log_metric("qa_success", {
                "content_length": len(draft),
                "qa_response_length": len(qa_response)
            })
            
            return {**data, "qa_result": qa_response}
            
        except Exception as e:
            log_metric("qa_error", {"error": str(e)})
            return {**data, "qa_result": f"QA failed: {e}"} 