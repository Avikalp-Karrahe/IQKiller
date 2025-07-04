"""
Enhanced Interview Orchestrator - Coordinates the complete enhanced pipeline
"""
import logging
from typing import Dict, Any, Union
from dataclasses import dataclass
import time

from llm_client import LLMClient
from read_pdf import read_pdf_with_pdfplumber as extract_text_from_pdf
from micro.enhanced_resume_parser import EnhancedResumeParser
from micro.enhanced_job_parser import EnhancedJobParser
from micro.advanced_gap_analysis import AdvancedGapAnalysis
from micro.personalized_interview_guide import PersonalizedInterviewGuideGenerator
from micro.enhanced_guide_renderer import EnhancedGuideRenderer


@dataclass
class EnhancedInterviewResult:
    """Complete result from enhanced interview pipeline"""
    success: bool
    interview_guide: str
    resume_data: Dict[str, Any]
    job_data: Dict[str, Any]
    gap_analysis: Dict[str, Any]
    match_score: float
    processing_time: float
    error_message: str = ""


class EnhancedInterviewOrchestrator:
    """Orchestrates the complete enhanced interview guide pipeline"""

    def __init__(self):
        self.llm_client = LLMClient()
        self.resume_parser = EnhancedResumeParser()
        self.job_parser = EnhancedJobParser()
        self.gap_analyzer = AdvancedGapAnalysis()
        self.guide_generator = PersonalizedInterviewGuideGenerator()
        self.guide_renderer = EnhancedGuideRenderer()
        self.logger = logging.getLogger(__name__)

    async def create_enhanced_interview_guide(
        self,
        resume_input: Union[str, Dict[str, Any]],
        job_input: Union[str, Dict[str, Any]],
        input_type: str = "text"
    ) -> EnhancedInterviewResult:
        """
        Create a comprehensive personalized interview guide

        Args:
            resume_input: Resume text, file path, or parsed data
            job_input: Job description text, URL, or parsed data
            input_type: 'text', 'file_path', 'pdf_path', or 'url'

        Returns:
            EnhancedInterviewResult with complete analysis and guide
        """
        start_time = time.time()

        try:
            # Step 1: Parse Resume
            self.logger.info("Starting enhanced resume parsing...")
            if isinstance(resume_input, dict):
                resume_data = resume_input
            else:
                if input_type == "pdf_path":
                    resume_text = extract_text_from_pdf(resume_input)
                else:
                    resume_text = resume_input

                resume_result = await self.resume_parser.run(
                    {"resume_text": resume_text})
                resume_data = resume_result.get("resume_data_enhanced", {})

            # Step 2: Parse Job Description
            self.logger.info("Starting enhanced job parsing...")
            if isinstance(job_input, dict):
                job_data = job_input
            else:
                job_result = await self.job_parser.run({
                    "scraped": {"content": job_input},
                    "enriched": {}
                })
                job_data = job_result.get("job_data_enhanced", {})

            # Step 3: Perform Advanced Gap Analysis
            self.logger.info("Performing advanced gap analysis...")
            gap_result = await self.gap_analyzer.run({
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data
            })
            gap_analysis = gap_result.get("gap_analysis_advanced", {})

            # Step 4: Generate Personalized Interview Guide
            self.logger.info("Generating personalized interview guide...")
            guide_result = await self.guide_generator.run({
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data,
                **gap_result
            })
            interview_guide_data = guide_result.get("personalized_guide", {})

            # Step 5: Render Final Guide
            self.logger.info("Rendering final interview guide...")
            render_result = self.guide_renderer.run({
                "personalized_guide": interview_guide_data,
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data,
                **gap_result
            })
            rendered_guide = render_result.get("rendered_guide", "")

            processing_time = time.time() - start_time
            match_score = gap_analysis.get('overall_match_score', 0)

            return EnhancedInterviewResult(
                success=True,
                interview_guide=rendered_guide,
                resume_data=resume_data,
                job_data=job_data,
                gap_analysis=gap_analysis,
                match_score=match_score,
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"Enhanced interview guide generation failed: {e}")
            processing_time = time.time() - start_time

            return EnhancedInterviewResult(
                success=False,
                interview_guide="",
                resume_data={},
                job_data={},
                gap_analysis={},
                match_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )

    async def analyze_compatibility_async(
        self,
        resume_input: Union[str, Dict[str, Any]],
        job_input: Union[str, Dict[str, Any]],
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """Async compatibility analysis"""
        try:
            # Parse inputs
            if isinstance(resume_input, dict):
                resume_data = resume_input
            else:
                if input_type == "pdf_path":
                    resume_text = extract_text_from_pdf(resume_input)
                else:
                    resume_text = resume_input
                resume_result = await self.resume_parser.run(
                    {"resume_text": resume_text})
                resume_data = resume_result.get("resume_data_enhanced", {})

            if isinstance(job_input, dict):
                job_data = job_input
            else:
                job_result = await self.job_parser.run({
                    "scraped": {"content": job_input},
                    "enriched": {}
                })
                job_data = job_result.get("job_data_enhanced", {})

            # Perform gap analysis
            gap_result = await self.gap_analyzer.run({
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data
            })
            gap_analysis = gap_result.get("gap_analysis_advanced", {})

            return {
                "compatibility_score": gap_analysis.get('overall_match_score', 0),
                "strong_matches": gap_analysis.get('strong_matches', []),
                "key_gaps": gap_analysis.get('gaps', []),
                "recommendations": gap_analysis.get('recommendations', []),
                "competitive_advantages": gap_analysis.get('competitive_advantages', [])
            }

        except Exception as e:
            return {
                "error": f"Compatibility analysis failed: {e}",
                "compatibility_score": 0,
                "strong_matches": [],
                "key_gaps": [],
                "recommendations": [],
                "competitive_advantages": []
            }

    async def generate_skills_table_async(
        self,
        resume_input: Union[str, Dict[str, Any]],
        job_input: Union[str, Dict[str, Any]],
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """Async skills table generation"""
        try:
            # Parse inputs
            if isinstance(resume_input, dict):
                resume_data = resume_input
            else:
                if input_type == "pdf_path":
                    resume_text = extract_text_from_pdf(resume_input)
                else:
                    resume_text = resume_input
                resume_result = await self.resume_parser.run(
                    {"resume_text": resume_text})
                resume_data = resume_result.get("resume_data_enhanced", {})

            if isinstance(job_input, dict):
                job_data = job_input
            else:
                job_result = await self.job_parser.run({
                    "scraped": {"content": job_input},
                    "enriched": {}
                })
                job_data = job_result.get("job_data_enhanced", {})

            # Perform gap analysis
            gap_result = await self.gap_analyzer.run({
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data
            })
            gap_analysis = gap_result.get("gap_analysis_advanced", {})

            return {
                "skills_matches": gap_analysis.get('skill_matches', []),
                "summary": {
                    "total_requirements": len(gap_analysis.get('all_requirements', [])),
                    "strong_matches": len(gap_analysis.get('strong_matches', [])),
                    "partial_matches": len(gap_analysis.get('partial_matches', [])),
                    "gaps": len(gap_analysis.get('gaps', []))
                },
                "overall_score": gap_analysis.get('overall_match_score', 0)
            }

        except Exception as e:
            return {
                "error": f"Skills table generation failed: {e}",
                "skills_matches": [],
                "summary": {"total_requirements": 0, "strong_matches": 0, "partial_matches": 0, "gaps": 0},
                "overall_score": 0
            }


def analyze_resume_job_compatibility(
    resume_input: Union[str, Dict[str, Any]],
    job_input: Union[str, Dict[str, Any]],
    input_type: str = "text"
) -> Dict[str, Any]:
    """
    Quick compatibility analysis between resume and job

    Returns compatibility score and high-level recommendations
    """
    import asyncio

    async def async_analyze():
        orchestrator = EnhancedInterviewOrchestrator()

        try:
            # Parse inputs
            if isinstance(resume_input, dict):
                resume_data = resume_input
            else:
                if input_type == "pdf_path":
                    resume_text = extract_text_from_pdf(resume_input)
                else:
                    resume_text = resume_input
                resume_result = await orchestrator.resume_parser.run(
                    {"resume_text": resume_text})
                resume_data = resume_result.get("resume_data_enhanced", {})

            if isinstance(job_input, dict):
                job_data = job_input
            else:
                job_result = await orchestrator.job_parser.run({
                    "scraped": {"content": job_input},
                    "enriched": {}
                })
                job_data = job_result.get("job_data_enhanced", {})

            # Perform gap analysis
            gap_result = await orchestrator.gap_analyzer.run({
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data
            })
            gap_analysis = gap_result.get("gap_analysis_advanced", {})

            return {
                "compatibility_score": gap_analysis.get(
                    'overall_match_score', 0),
                "strong_matches": gap_analysis.get('strong_matches', []),
                "key_gaps": gap_analysis.get('gaps', []),
                "recommendations": gap_analysis.get('recommendations', []),
                "competitive_advantages": gap_analysis.get(
                    'competitive_advantages', [])
            }

        except Exception as e:
            return {
                "error": f"Compatibility analysis failed: {e}",
                "compatibility_score": 0,
                "strong_matches": [],
                "key_gaps": [],
                "recommendations": [],
                "competitive_advantages": []
            }

    return asyncio.run(async_analyze())


def generate_skills_match_table(
    resume_input: Union[str, Dict[str, Any]],
    job_input: Union[str, Dict[str, Any]],
    input_type: str = "text"
) -> Dict[str, Any]:
    """
    Generate detailed skills matching table with scores

    Returns structured table showing match details for each requirement
    """
    import asyncio

    async def async_generate():
        orchestrator = EnhancedInterviewOrchestrator()

        try:
            # Parse inputs
            if isinstance(resume_input, dict):
                resume_data = resume_input
            else:
                if input_type == "pdf_path":
                    resume_text = extract_text_from_pdf(resume_input)
                else:
                    resume_text = resume_input
                resume_result = await orchestrator.resume_parser.run(
                    {"resume_text": resume_text})
                resume_data = resume_result.get("resume_data_enhanced", {})

            if isinstance(job_input, dict):
                job_data = job_input
            else:
                job_result = await orchestrator.job_parser.run({
                    "scraped": {"content": job_input},
                    "enriched": {}
                })
                job_data = job_result.get("job_data_enhanced", {})

            # Get detailed skill matches from gap analysis
            gap_result = await orchestrator.gap_analyzer.run({
                "resume_data_enhanced": resume_data,
                "job_data_enhanced": job_data
            })
            gap_analysis = gap_result.get("gap_analysis_advanced", {})

            # Extract skill matches
            skill_matches = gap_analysis.get("detailed_matches", [])

            return {
                "skill_matches": skill_matches,
                "summary": {
                    "total_requirements": len(skill_matches),
                    "strong_matches": len([m for m in skill_matches
                                         if m.get('match_score', 0) > 0.8]),
                    "partial_matches": len([m for m in skill_matches
                                          if 0.4 <= m.get('match_score', 0) <= 0.8]),
                    "gaps": len([m for m in skill_matches
                               if m.get('match_score', 0) < 0.4])
                }
            }

        except Exception as e:
            return {
                "error": f"Skills matching failed: {e}",
                "skill_matches": [],
                "summary": {
                    "total_requirements": 0,
                    "strong_matches": 0,
                    "partial_matches": 0,
                    "gaps": 0
                }
            }

    return asyncio.run(async_generate()) 