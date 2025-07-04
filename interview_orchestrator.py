import asyncio
import time
from typing import Dict, Any, Optional
from metrics import log_metric

# Import all micro-functions
from micro.scrape import ScrapeMicroFunction
from micro.enrich import EnrichMicroFunction
from micro.resume_parser import ResumeParserMicroFunction
from micro.gap_analysis import GapAnalysisMicroFunction
from micro.interview_guide import InterviewGuideMicroFunction
from micro.guide_render import GuideRenderMicroFunction

class InterviewGuideOrchestrator:
    """
    Orchestrates the complete personalized interview guide generation pipeline.
    
    Pipeline: Resume + Job Posting → Gap Analysis → Personalized Interview Guide
    """
    
    def __init__(self):
        self.scrape = ScrapeMicroFunction()
        self.enrich = EnrichMicroFunction()
        self.resume_parser = ResumeParserMicroFunction()
        self.gap_analysis = GapAnalysisMicroFunction()
        self.interview_guide = InterviewGuideMicroFunction()
        self.guide_render = GuideRenderMicroFunction()
    
    async def generate_interview_guide(self, resume_text: str, job_input: str) -> Dict[str, Any]:
        """
        Generate a personalized interview guide from resume and job posting.
        
        Args:
            resume_text: Raw resume text or file content
            job_input: Job posting URL or raw text
            
        Returns:
            Dict containing the complete interview guide and analysis
        """
        start_time = time.time()
        
        try:
            # Initialize data pipeline
            data = {
                "resume_text": resume_text,
                "raw_input": job_input,
                "timestamp": start_time
            }
            
            # Step 1: Process job posting (scrape if URL, otherwise use direct text)
            log_metric("pipeline_start", {"stage": "job_processing"})
            data = self.scrape.run(data)
            
            if not data.get("success", False):
                return {"error": "Failed to process job posting", "data": data}
            
            # Step 2: Enrich job data (extract structured information)
            log_metric("pipeline_start", {"stage": "job_enrichment"})
            data = self.enrich.run(data)
            
            if data.get("enriched", {}).get("error"):
                return {"error": "Failed to extract job data", "data": data}
            
            # Step 3: Parse resume (extract structured information)
            log_metric("pipeline_start", {"stage": "resume_parsing"})
            data = await self.resume_parser.run(data)
            
            if data.get("resume_data", {}).get("error"):
                return {"error": "Failed to parse resume", "data": data}
            
            # Step 4: Perform gap analysis (compare resume vs job requirements)
            log_metric("pipeline_start", {"stage": "gap_analysis"})
            data = self.gap_analysis.run(data)
            
            if data.get("gap_analysis", {}).get("error"):
                return {"error": "Failed to perform gap analysis", "data": data}
            
            # Step 5: Generate personalized interview guide
            log_metric("pipeline_start", {"stage": "guide_generation"})
            data = self.interview_guide.run(data)
            
            if data.get("interview_guide", {}).get("error"):
                return {"error": "Failed to generate interview guide", "data": data}
            
            # Step 6: Render final markdown guide
            log_metric("pipeline_start", {"stage": "guide_rendering"})
            data = self.guide_render.run(data)
            
            # Calculate total pipeline time
            total_time = time.time() - start_time
            
            log_metric("interview_guide_pipeline_complete", {
                "total_seconds": total_time,
                "match_score": data.get("gap_analysis", {}).get("match_score", 0),
                "guide_length": len(data.get("rendered_guide", "")),
                "success": True
            })
            
            return {
                "success": True,
                "rendered_guide": data.get("rendered_guide", ""),
                "gap_analysis": data.get("gap_analysis", {}),
                "interview_guide": data.get("interview_guide", {}),
                "job_data": data.get("enriched", {}),
                "resume_data": data.get("resume_data", {}),
                "processing_time": total_time
            }
            
        except Exception as e:
            log_metric("interview_guide_pipeline_error", {"error": str(e)})
            return {"error": f"Pipeline failed: {e}", "success": False}
    
    def generate_interview_guide_sync(self, resume_text: str, job_input: str) -> Dict[str, Any]:
        """Synchronous wrapper for the async interview guide generation"""
        try:
            return asyncio.run(self.generate_interview_guide(resume_text, job_input))
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                # We're already in an event loop, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        self.generate_interview_guide(resume_text, job_input)
                    )
                    return future.result()
            else:
                raise e

# Convenience function for direct usage
def create_personalized_interview_guide(resume_text: str, job_input: str) -> Dict[str, Any]:
    """
    Convenience function to generate a personalized interview guide.
    
    Args:
        resume_text: Resume content (text or parsed from PDF)
        job_input: Job posting URL or raw text
        
    Returns:
        Complete interview guide with analysis
    """
    orchestrator = InterviewGuideOrchestrator()
    return orchestrator.generate_interview_guide_sync(resume_text, job_input) 