from typing import Any, Dict
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric

class CritiqueMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        draft = data.get("draft", "")
        qa_result = data.get("qa_result", "")
        enriched_data = data.get("enriched", {})
        
        if not draft or "failed" in draft.lower():
            return {**data, "critique": "Critique skipped due to draft errors."}
        
        try:
            # Use LLM to provide detailed critique
            prompt = prompt_loader.get_prompt("critique_prompt", draft=draft)
            
            critique_prompt = prompt + f"""

Provide a comprehensive critique of this job role preview, focusing on:

## Critical Analysis
1. **Factual Accuracy**: Cross-check details against source data
2. **Market Reality**: Are salary/requirements realistic for the role/level?
3. **Completeness**: Missing critical information?
4. **Tone & Style**: Appropriate for job seekers?
5. **Actionability**: Are recommendations specific and useful?

## Context
- QA Results: {qa_result}
- Source Job Data: {enriched_data}

## Content to Critique
{draft}

## Critique Format
**Strengths**: What works well
**Weaknesses**: Areas needing improvement  
**Factual Issues**: Any inaccuracies found
**Market Insights**: Industry-specific observations
**Recommendations**: Specific improvements
**Risk Assessment**: Potential issues for job seekers
**Overall Score**: [1-10] with justification

Be constructive but thorough. This critique helps ensure job seekers get accurate, helpful guidance.
"""
            
            critique_response = llm_client.call_llm(critique_prompt)
            
            # Extract overall score if present
            score = None
            if "overall score" in critique_response.lower():
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)/10|(\d+(?:\.\d+)?)\s*(?:out of|/)\s*10', critique_response.lower())
                if score_match:
                    score = float(score_match.group(1) or score_match.group(2))
            
            log_metric("critique_success", {
                "content_length": len(draft),
                "critique_length": len(critique_response),
                "quality_score": score
            })
            
            return {**data, "critique": critique_response, "quality_score": score}
            
        except Exception as e:
            log_metric("critique_error", {"error": str(e)})
            return {**data, "critique": f"Critique failed: {e}"} 