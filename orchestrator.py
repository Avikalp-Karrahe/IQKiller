from typing import Any, Dict, List, Protocol
import asyncio
from text_extractor import extract_batch, JobCore
from micro.patch_missing import patch_missing

class MicroFunction(Protocol):
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...

class Orchestrator:
    def __init__(self, steps: List[MicroFunction]):
        self.steps = steps

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = input_data
        for step in self.steps:
            data = step.run(data)
        return data
    
    def run_from_text(self, raw_jd: str) -> Dict[str, Any]:
        """Process job description text through the pipeline"""
        data = {"raw_input": raw_jd, "input": raw_jd}
        for step in self.steps:
            data = step.run(data)
        return data 

async def analyze(raw: str) -> JobCore:
    """Analyze job description using fast chunked extraction then patch missing data."""
    # Extract using concurrent chunked processing
    job_core = await extract_batch(raw)
    
    # Patch missing data with Google search
    enriched_core = patch_missing(job_core)
    
    return enriched_core 