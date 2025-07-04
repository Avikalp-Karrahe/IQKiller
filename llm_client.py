import time
import os
import requests
from typing import Any, Dict, Optional, List
import openai
import anthropic
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, LLM_CONFIG
from metrics import log_metric

class LLMClient:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.last_request_time = 0
        self.request_count = 0
        
    def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < 2:  # 2 second between requests
            time.sleep(2 - (current_time - self.last_request_time))
        self.last_request_time = time.time()
        
    def call_llm(self, prompt: str, provider: str = "openai", 
                 system: Optional[str] = None, timeout: Optional[float] = None, 
                 **kwargs) -> str:
        """Call LLM with system prompt and timeout support"""
        self._rate_limit()
        
        config = LLM_CONFIG[provider]
        start_time = time.time()
        
        # Track tokens for metrics
        prompt_tokens = len(prompt.split())
        if system:
            prompt_tokens += len(system.split())
        
        try:
            if provider == "openai":
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                
                call_kwargs = {
                    "model": config["model"],
                    "messages": messages,
                    "max_tokens": config["max_tokens"],
                    **kwargs
                }
                # Only add temperature if not already in kwargs
                if "temperature" not in kwargs:
                    call_kwargs["temperature"] = config["temperature"]
                if timeout:
                    call_kwargs["timeout"] = timeout
                
                response = self.openai_client.chat.completions.create(**call_kwargs)
                result = response.choices[0].message.content
                
                # Log token usage
                usage = response.usage
                tokens_in = usage.prompt_tokens if usage else prompt_tokens
                tokens_out = usage.completion_tokens if usage else len(result.split())
                
            elif provider == "anthropic":
                call_kwargs = {
                    "model": config["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": config["max_tokens"],
                    **kwargs
                }
                # Only add temperature if not already in kwargs
                if "temperature" not in kwargs:
                    call_kwargs["temperature"] = config["temperature"]
                if system:
                    call_kwargs["system"] = system
                if timeout:
                    call_kwargs["timeout"] = timeout
                
                response = self.anthropic_client.messages.create(**call_kwargs)
                result = response.content[0].text
                
                # Log token usage
                usage = response.usage
                tokens_in = usage.input_tokens if usage else prompt_tokens
                tokens_out = usage.output_tokens if usage else len(result.split())
            
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
            # Calculate approximate cost (rough estimates)
            usd_cost = self._calculate_cost(provider, tokens_in, tokens_out)
            
            # Log metrics with enhanced data
            log_metric("llm_call", {
                "provider": provider,
                "model": config["model"],
                "latency": time.time() - start_time,
                "success": True,
                "prompt_length": len(prompt),
                "response_length": len(result),
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "usd_cost": usd_cost
            })
            
            return result
            
        except Exception as e:
            log_metric("llm_error", {
                "provider": provider,
                "error": str(e),
                "latency": time.time() - start_time
            })
            
            # Try fallback provider
            fallback = LLM_CONFIG["fallback_provider"]
            if provider != fallback:
                log_metric("fallback_attempt", {"from": provider, "to": fallback})
                return self.call_llm(prompt, fallback, system=system, 
                                   timeout=timeout, **kwargs)
            else:
                raise Exception(f"Both LLM providers failed. Last error: {e}")
    
    def _calculate_cost(self, provider: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate approximate USD cost based on token usage"""
        # Rough pricing estimates (as of 2024)
        pricing = {
            "openai": {
                "gpt-4o-mini": {"input": 0.000150, "output": 0.000600}  # per 1K tokens
            },
            "anthropic": {
                "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}  # per 1K tokens
            }
        }
        
        model = LLM_CONFIG[provider]["model"]
        if provider in pricing and model in pricing[provider]:
            rates = pricing[provider][model]
            return (tokens_in * rates["input"] + tokens_out * rates["output"]) / 1000
        return 0.0


def openai_call(text: str, timeout: int) -> str:
    """
    Call gpt-4o-mini with temp=0 and max_tokens=400.
    Returns the JSON string from the assistant.
    Logs tokens_in, tokens_out, usd_cost via metrics.log_metric().
    Raises TimeoutError if the call exceeds `timeout` seconds.
    """
    system_prompt = """You are an information-extraction engine.
Return ONLY valid JSON with these lowercase keys:
company, role, location, seniority, posted_hours, salary_low, salary_high, 
mission, funding, evidence.
- mission: company's main value proposition/tagline
- funding: recent funding round info if mentioned
- evidence maps each non-null key to the sentence fragment (≤120 chars) that proves it
Use null if value missing. Do NOT output any extra text."""

    user_prompt = f"""Extract the JSON from this job description:
<<<
{text[:2000]}
>>>"""

    start_time = time.time()
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            max_tokens=400,
            timeout=timeout
        )
        
        result = response.choices[0].message.content or ""
        
        # Log metrics
        usage = response.usage
        tokens_in = usage.prompt_tokens if usage else len((system_prompt + user_prompt).split())
        tokens_out = usage.completion_tokens if usage else len(result.split())
        usd_cost = (tokens_in * 0.000150 + tokens_out * 0.000600) / 1000  # GPT-4o-mini pricing
        
        log_metric("llm_call", {
            "provider": "openai",
            "model": "gpt-4o-mini", 
            "latency": time.time() - start_time,
            "success": True,
            "prompt_length": len(user_prompt),
            "response_length": len(result),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "usd_cost": usd_cost
        })
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            raise TimeoutError(f"OpenAI call exceeded {timeout}s timeout")
        
        log_metric("llm_error", {
            "provider": "openai",
            "error": str(e),
            "latency": elapsed
        })
        raise


def google_search(query: str, top: int = 3, timeout: int = 5) -> List[str]:
    """
    SerpAPI/Bing wrapper for Google search.
    Returns list of relevant text snippets.
    Logs google_calls, google_latency_ms via metrics.log_metric().
    """
    start_time = time.time()
    
    try:
        # Use SerpAPI if available, otherwise fallback to basic search
        from config import SERPAPI_KEY
        if SERPAPI_KEY:
            url = "https://serpapi.com/search.json"
            params = {
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": top,
                "hl": "en",
                "gl": "us"
            }
            
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            snippets = []
            for result in data.get("organic_results", [])[:top]:
                snippet = result.get("snippet", "")
                if snippet:
                    snippets.append(snippet[:200])  # Limit snippet length
            
            # Log successful search
            log_metric("google_search", {
                "query": query,
                "results_count": len(snippets),
                "latency_ms": (time.time() - start_time) * 1000,
                "success": True
            })
            
            return snippets
        
        else:
            # Fallback: return empty results if no API key
            log_metric("google_search", {
                "query": query,
                "results_count": 0,
                "latency_ms": (time.time() - start_time) * 1000,
                "success": False,
                "error": "No SERPAPI_KEY available"
            })
            return []
            
    except Exception as e:
        log_metric("google_search", {
            "query": query,
            "results_count": 0,
            "latency_ms": (time.time() - start_time) * 1000,
            "success": False,
            "error": str(e)
        })
        return []


# Global client instance
llm_client = LLMClient() 