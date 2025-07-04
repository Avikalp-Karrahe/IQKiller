import re
import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from llm_client import openai_call
import openai
from config import OPENAI_API_KEY
from metrics import log_metric
import time
import os
import requests
import anthropic
from config import ANTHROPIC_API_KEY, LLM_CONFIG
import tiktoken

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
        data = robust_json_parse(json_str)
        
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
    """Extract job data using No-BS compact format with smart chunking for long inputs."""
    try:
        # Process long text if needed
        processed_text = await process_long_text(raw_text)
        
        # Get structured prompt
        system_prompt, user_prompt = build_nobs_prompt(processed_text)
        
        # Single OpenAI call with structured prompts
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        json_str = await call_llm_async(messages, temperature=0, max_tokens=800)
        
        # Parse JSON response using robust parser
        try:
            data = robust_json_parse(json_str)
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
                    data = robust_json_parse(response)
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

def robust_json_parse(json_str: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Robust JSON parsing that handles markdown code blocks and implements retry logic.
    
    Args:
        json_str: Raw JSON string that may contain markdown formatting
        max_retries: Number of retry attempts for cleaning and parsing
    
    Returns:
        Parsed JSON dictionary
    
    Raises:
        json.JSONDecodeError: If JSON cannot be parsed after all retries
    """
    if not json_str or not json_str.strip():
        return {}
    
    for attempt in range(max_retries + 1):
        try:
            # Clean the JSON string progressively
            cleaned = json_str.strip()
            
            # Remove markdown code blocks (```json ... ``` or ``` ... ```)
            cleaned = re.sub(r'^```(?:json)?\s*\n', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
            cleaned = re.sub(r'\n?\s*```\s*$', '', cleaned, flags=re.MULTILINE)
            
            # Remove leading/trailing whitespace and common prefixes
            cleaned = cleaned.strip()
            
            # Remove common LLM response prefixes
            prefixes_to_remove = [
                "Here's the JSON:",
                "Here is the JSON:",
                "JSON:",
                "Response:",
                "Result:",
            ]
            
            for prefix in prefixes_to_remove:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
            
            # Try to parse
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            if attempt == max_retries:
                # Log the error with context
                log_metric("json_parse_final_error", {
                    "error": str(e),
                    "original_length": len(json_str),
                    "cleaned_length": len(cleaned) if 'cleaned' in locals() else 0,
                    "attempts": attempt + 1
                })
                raise
            
            # For retries, try more aggressive cleaning
            if attempt < max_retries:
                # Try to extract JSON from within the string
                json_match = re.search(r'(\{.*\})', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON array
                    array_match = re.search(r'(\[.*\])', json_str, re.DOTALL)
                    if array_match:
                        json_str = array_match.group(1)
    
    return {} 

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text using tiktoken for accurate token counting.
    
    Args:
        text: Input text to count tokens for
        model: Model name for tokenizer (default: gpt-4o-mini)
    
    Returns:
        Number of tokens
    """
    try:
        # Get the encoding for the model
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough estimation if tiktoken fails
        return int(len(text.split()) * 1.3)  # Rough tokens-to-words ratio

def smart_chunk_text(text: str, max_tokens: int = 120000, overlap_tokens: int = 2000) -> List[str]:
    """
    Intelligently chunk text to stay under token limits with semantic boundaries.
    
    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk (default: 120K for 128K context)
        overlap_tokens: Tokens to overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Check if chunking is needed
    total_tokens = count_tokens(text)
    if total_tokens <= max_tokens:
        return [text]
    
    log_metric("chunking_required", {
        "total_tokens": total_tokens,
        "max_tokens": max_tokens,
        "estimated_chunks": (total_tokens // max_tokens) + 1
    })
    
    chunks = []
    
    # Try to split on semantic boundaries (paragraphs, sentences)
    paragraphs = text.split('\n\n')
    current_chunk = ""
    current_tokens = 0
    
    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        
        # If single paragraph is too large, split by sentences
        if paragraph_tokens > max_tokens:
            sentences = paragraph.split('. ')
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence)
                
                # If single sentence is still too large, force split by words
                if sentence_tokens > max_tokens:
                    words = sentence.split()
                    words_per_chunk = int(max_tokens / 1.3)  # Rough words per chunk
                    
                    for i in range(0, len(words), words_per_chunk):
                        word_chunk = ' '.join(words[i:i + words_per_chunk])
                        if current_chunk:
                            chunks.append(current_chunk)
                            # Add overlap from previous chunk
                            overlap_words = current_chunk.split()[-int(overlap_tokens / 1.3):]
                            current_chunk = ' '.join(overlap_words) + ' ' + word_chunk
                        else:
                            current_chunk = word_chunk
                        current_tokens = count_tokens(current_chunk)
                
                elif current_tokens + sentence_tokens > max_tokens:
                    # Start new chunk
                    if current_chunk:
                        chunks.append(current_chunk)
                        # Add overlap
                        overlap_words = current_chunk.split()[-int(overlap_tokens / 1.3):]
                        current_chunk = ' '.join(overlap_words) + '. ' + sentence
                    else:
                        current_chunk = sentence
                    current_tokens = count_tokens(current_chunk)
                else:
                    current_chunk += '. ' + sentence
                    current_tokens += sentence_tokens
        
        elif current_tokens + paragraph_tokens > max_tokens:
            # Start new chunk
            if current_chunk:
                chunks.append(current_chunk)
                # Add overlap
                overlap_words = current_chunk.split()[-int(overlap_tokens / 1.3):]
                current_chunk = ' '.join(overlap_words) + '\n\n' + paragraph
            else:
                current_chunk = paragraph
            current_tokens = count_tokens(current_chunk)
        else:
            current_chunk += '\n\n' + paragraph
            current_tokens += paragraph_tokens
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    log_metric("chunking_completed", {
        "chunks_created": len(chunks),
        "avg_tokens_per_chunk": sum(count_tokens(chunk) for chunk in chunks) / len(chunks)
    })
    
    return chunks

async def summarize_chunk(chunk: str) -> str:
    """
    Summarize a chunk of text to reduce token count while preserving key information.
    
    Args:
        chunk: Text chunk to summarize
    
    Returns:
        Summarized text
    """
    system_prompt = """You are a job description summarizer. Extract and preserve all key information including:
- Company name and role title
- Location and work type
- Salary/compensation information  
- Required skills and qualifications
- Job responsibilities
- Company information and benefits
- Contact/application details

Maintain specific details while removing redundant text. Keep all technical terms, skill names, and specific requirements."""
    
    user_prompt = f"""Summarize this job posting section, preserving all key details:

{chunk}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return await call_llm_async(messages, temperature=0, max_tokens=1000)

async def process_long_text(text: str) -> str:
    """
    Process text that exceeds token limits by chunking and summarizing.
    
    Args:
        text: Input text that may be too long
    
    Returns:
        Processed text suitable for analysis
    """
    # Check if processing is needed
    total_tokens = count_tokens(text)
    if total_tokens <= 120000:  # Under 120K tokens, safe for 128K context
        return text
    
    log_metric("long_text_processing_start", {
        "original_tokens": total_tokens,
        "threshold": 120000
    })
    
    # Chunk the text
    chunks = smart_chunk_text(text, max_tokens=100000, overlap_tokens=1000)
    
    # Summarize chunks concurrently
    summary_tasks = [summarize_chunk(chunk) for chunk in chunks]
    summaries = await asyncio.gather(*summary_tasks, return_exceptions=True)
    
    # Filter out failed summaries and combine
    valid_summaries = []
    for i, summary in enumerate(summaries):
        if isinstance(summary, str):
            valid_summaries.append(summary)
        else:
            log_metric("chunk_summary_error", {"chunk_index": i, "error": str(summary)})
    
    # Combine summaries
    processed_text = '\n\n'.join(valid_summaries)
    final_tokens = count_tokens(processed_text)
    
    log_metric("long_text_processing_complete", {
        "original_tokens": total_tokens,
        "final_tokens": final_tokens,
        "compression_ratio": final_tokens / total_tokens,
        "chunks_processed": len(chunks),
        "successful_summaries": len(valid_summaries)
    })
    
    return processed_text 