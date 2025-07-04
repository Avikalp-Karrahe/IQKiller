import re
import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from llm_client import openai_call
import openai
from config import OPENAI_API_KEY
from metrics import log_metric

async def call_llm_async(messages: List[Dict[str, str]], temperature: float = 0, 
                        max_tokens: int = 400) -> str:
    """Async wrapper for OpenAI API calls."""
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        log_metric("chunk_extraction_error", {"error": str(e)})
        return ""

@dataclass
class JobCore:
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    seniority: Optional[str] = None
    posted_hours: Optional[str] = None
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    mission: Optional[str] = None
    funding: Optional[str] = None
    must_have: Optional[str] = None
    nice_to_have: Optional[str] = None
    tech_q: Optional[str] = None
    behav_q: Optional[str] = None
    perks: Optional[str] = None
    posted_days: Optional[int] = None
    source_map: dict = field(default_factory=dict)

def extract_entities(raw: str) -> JobCore:
    """Extract job entities using GPT-4o-mini with expanded field set."""
    try:
        json_str = openai_call(raw, timeout=4)
        data = json.loads(json_str)
        
        # Convert posted_hours to posted_days
        posted_days = None
        posted_hours_raw = data.get("posted_hours")
        if posted_hours_raw:
            if isinstance(posted_hours_raw, str):
                import re
                hours_match = re.search(r'(\d+)\s*hours?\s+ago', posted_hours_raw, re.IGNORECASE)
                days_match = re.search(r'(\d+)\s*days?\s+ago', posted_hours_raw, re.IGNORECASE)
                weeks_match = re.search(r'(\d+)\s*weeks?\s+ago', posted_hours_raw, re.IGNORECASE)
                
                if hours_match:
                    hours = int(hours_match.group(1))
                    posted_days = max(1, hours // 24)
                elif days_match:
                    posted_days = int(days_match.group(1))
                elif weeks_match:
                    posted_days = int(weeks_match.group(1)) * 7
            elif isinstance(posted_hours_raw, (int, float)):
                hours = int(posted_hours_raw)
                posted_days = max(1, hours // 24) if hours < 168 else hours // 24
        
        return JobCore(
            company=data.get("company") or "",
            role=data.get("role") or "",
            location=data.get("location") or "",
            seniority=data.get("seniority") or "",
            posted_days=posted_days,
            salary_low=data.get("salary_low"),
            salary_high=data.get("salary_high"),
            mission=data.get("mission"),
            funding=data.get("funding"),
            source_map={}
        )
        
    except Exception as e:
        # Return empty JobCore on any failure
        return JobCore(
            company="",
            role="",
            location="",
            seniority="",
            posted_days=None,
            salary_low=None,
            salary_high=None,
            mission=None,
            funding=None,
            source_map={}
        )

def build_prompt(chunk: str) -> tuple[str, str]:
    """Build system and user prompts for chunk extraction."""
    system = """You are an information-extraction engine.
Return ONLY JSON with any of these keys you can find:
company, role, location, seniority, posted_hours,
salary_low, salary_high, mission, funding,
must_have, nice_to_have, tech_q, behav_q, perks.
Omit keys you cannot fill. No other text."""
    
    user = f"""Extract what you can from:
<<<
{chunk}
<<<"""
    
    return system, user

def build_nobs_prompt(full_text: str) -> tuple[str, str]:
    """Build system and user prompts for Interview Query-style extraction."""
    system_prompt = """You are an interview preparation specialist creating personalized guides.
Return ONLY JSON with these keys if you can find them:
title, company, location, work_type, salary_band, mission, must_have,
nice_to_have, why_it_matters, perks, red_flags, apply_link,
technical_questions, behavioral_questions, talking_points, company_intel,
smart_questions, role_challenges, success_metrics, salary_context.

Arrays ≤6 unique items, each <10 words. mission ≤25 words, why_it_matters ≤30.
technical_questions: likely technical interview questions for this role.
behavioral_questions: behavioral questions this company/role might ask.
talking_points: specific achievements/experiences to highlight.
company_intel: key company facts to mention (funding, growth, mission).
smart_questions: thoughtful questions to ask interviewer.
role_challenges: main challenges/problems this role will solve.
success_metrics: how success is measured in this role.
salary_context: negotiation context (market rate, equity, growth stage).
Leave a key out if not present. No other text."""
    
    user_prompt = f"""Create personalized interview prep guide for this job:
<<<
{full_text}
>>>"""
    
    return system_prompt, user_prompt

async def extract_nobs(raw_text: str) -> Dict[str, Any]:
    """Extract job data using No-BS compact format with single OpenAI call."""
    try:
        # Get structured prompt
        system_prompt, user_prompt = build_nobs_prompt(raw_text)
        
        # Single OpenAI call with structured prompts
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        json_str = await call_llm_async(messages, temperature=0, max_tokens=800)
        
        # Parse JSON response
        try:
            data = json.loads(json_str) if json_str.strip() else {}
            log_metric("nobs_extraction_success", {"fields": len(data)})
            
            # Ensure fallback data for empty results
            if not data:
                return {"title": "Unknown Role", "company": "Unknown Company"}
            
            return data
        except json.JSONDecodeError as e:
            log_metric("nobs_json_parse_error", {"error": str(e), "response": json_str})
            # Fallback: try to extract partial data
            return {"title": "Unknown Role", "company": "Unknown Company"}
            
    except Exception as e:
        log_metric("nobs_extraction_error", {"error": str(e)})
        return {"title": "Extraction Failed", "company": "Unknown Company"}

def create_chunks(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Find a good break point (end of sentence or word)
        break_point = text.rfind('.', start, end)
        if break_point == -1:
            break_point = text.rfind(' ', start, end)
        if break_point == -1:
            break_point = end
        
        chunks.append(text[start:break_point])
        start = break_point - overlap
        
    return chunks

def merge_job_cores(cores: List['JobCore']) -> 'JobCore':
    """Merge multiple JobCore objects using first-non-null strategy."""
    merged = JobCore()
    
    for field_name in JobCore.__dataclass_fields__:
        for core in cores:
            value = getattr(core, field_name)
            if value is not None:
                setattr(merged, field_name, value)
                break
                
    return merged

async def extract_batch(raw: str) -> 'JobCore':
    """Extract job entities using concurrent chunked processing."""
    try:
        # Split text into overlapping chunks
        chunks = create_chunks(raw, chunk_size=2000, overlap=200)
        log_metric("chunks_created", {"count": len(chunks)})
        
        # Process all chunks concurrently
        tasks = []
        for chunk in chunks:
            system_prompt, user_prompt = build_prompt(chunk)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            tasks.append(call_llm_async(messages, temperature=0, max_tokens=400))
        
        # Wait for all chunks to complete
        start_time = asyncio.get_event_loop().time()
        responses = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        log_metric("gpt_calls", {"count": len(chunks)})
        log_metric("batch_extraction_latency", {"latency": end_time - start_time})
        
        # Parse and merge results
        job_cores = []
        for response in responses:
            if response.strip():
                try:
                    data = json.loads(response)
                    job_cores.append(JobCore(**{k: v for k, v in data.items() 
                                                if k in JobCore.__dataclass_fields__}))
                except (json.JSONDecodeError, TypeError):
                    continue
        
        if not job_cores:
            return JobCore()
            
        # Merge using first-non-null strategy
        return merge_job_cores(job_cores)
        
    except Exception as e:
        log_metric("batch_extraction_error", {"error": str(e)})
        return JobCore() 