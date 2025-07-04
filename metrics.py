import json
import time
from typing import Any, Dict, Optional

def log_metric(event: str, data: Dict[str, Any]) -> None:
    """Enhanced logging with support for tokens, cost, and latency metrics"""
    log = {"event": event, "timestamp": time.time(), **data}
    
    # Add structured fields for better analytics
    if event == "llm_call":
        # Ensure all required fields are present
        log.setdefault("tokens_in", 0)
        log.setdefault("tokens_out", 0)
        log.setdefault("usd_cost", 0.0)
        log.setdefault("latency", 0.0)
        log.setdefault("success", False)
    
    elif event == "enrich_latency":
        # Track enrichment performance
        log.setdefault("enrich_parallel_seconds", data.get("total_seconds", 0))
        log.setdefault("facts_count", 0)
    
    print(json.dumps(log))
    # TODO: Add hook for HF Analytics API 

def log_cost_summary(provider: str, total_tokens_in: int, total_tokens_out: int, 
                     total_cost: float, request_count: int) -> None:
    """Log cost summary for a session"""
    log_metric("cost_summary", {
        "provider": provider,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "total_usd_cost": total_cost,
        "request_count": request_count,
        "avg_cost_per_request": total_cost / request_count if request_count > 0 else 0.0
    })

def log_parallel_performance(serial_time_estimate: float, parallel_time_actual: float) -> None:
    """Log parallel execution performance gains"""
    speedup = serial_time_estimate / parallel_time_actual if parallel_time_actual > 0 else 1.0
    log_metric("parallel_performance", {
        "serial_time_estimate": serial_time_estimate,
        "parallel_time_actual": parallel_time_actual,
        "speedup_factor": speedup,
        "time_saved_seconds": serial_time_estimate - parallel_time_actual
    })

def log_llm_call(provider: str, model: str, latency: float, success: bool, 
                 prompt_length: int, response_length: int, tokens_in: int = 0, 
                 tokens_out: int = 0, usd_cost: float = 0.0) -> None:
    """Log LLM call metrics with enhanced token and cost tracking."""
    
    log_metric("llm_call", {
        "provider": provider,
        "model": model,
        "latency": latency,
        "success": success,
        "prompt_length": prompt_length,
        "response_length": response_length,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "usd_cost": usd_cost
    })

def log_google_search(query: str, results_count: int, latency_ms: float, 
                      success: bool, error: Optional[str] = None) -> None:
    """Log Google search call metrics."""
    
    data = {
        "query": query,
        "results_count": results_count,
        "latency_ms": latency_ms,
        "success": success
    }
    
    if error:
        data["error"] = error
    
    log_metric("google_search", data)

def log_patch_missing(company: str, patches_applied: int, source_map: Dict[str, str]) -> None:
    """Log Google patching metrics."""
    
    log_metric("patch_missing", {
        "company": company,
        "patches_applied": patches_applied,
        "source_map": source_map,
        "google_calls": len([v for v in source_map.values() if v == "google"])
    })

def log_enrich_latency(company: str, total_seconds: float, facts_count: int, 
                       enrich_parallel_seconds: Optional[float] = None) -> None:
    """Log enrichment pipeline latency."""
    
    data = {
        "company": company,
        "total_seconds": total_seconds,
        "facts_count": facts_count
    }
    
    if enrich_parallel_seconds is not None:
        data["enrich_parallel_seconds"] = enrich_parallel_seconds
    
    log_metric("enrich_latency", data)

def log_render_success(total_length: int, has_qa: bool, has_critique: bool, 
                       quality_score: Optional[float] = None, has_buckets: bool = False) -> None:
    """Log successful render metrics."""
    
    log_metric("render_success", {
        "total_length": total_length,
        "has_qa": has_qa,
        "has_critique": has_critique,
        "quality_score": quality_score,
        "has_buckets": has_buckets
    })

def log_cache_hit(input_text: str) -> None:
    """Log cache hit for input."""
    
    log_metric("cache_hit", {
        "input": input_text[:100] + "..." if len(input_text) > 100 else input_text
    })

def log_cache_miss(input_text: str) -> None:
    """Log cache miss for input."""
    
    log_metric("cache_miss", {
        "input": input_text[:100] + "..." if len(input_text) > 100 else input_text
    }) 