#!/usr/bin/env python3
"""
IQKiller: AI-Powered Job Analysis Platform
Advanced job posting analysis with comprehensive role previews and interview preparation.
Now with JWT authentication and production-ready features.
"""

import gradio as gr
import time
from orchestrator import Orchestrator, analyze
from micro.scrape import ScrapeMicroFunction
from micro.enrich import EnrichMicroFunction
from micro.draft import DraftMicroFunction
from micro.critique import CritiqueMicroFunction
from micro.render import RenderMicroFunction
from micro.qa import QAMicroFunction
from metrics import log_metric
from prompt_loader import prompt_loader
from typing import Any, Dict, Tuple, AsyncGenerator
import os
import render_cards
import renderer_nobs
import asyncio
from text_extractor import extract_nobs
from auth import create_login_interface, create_authenticated_wrapper, health_check
import flask
from flask import Flask
from enhanced_interview_orchestrator import EnhancedInterviewOrchestrator

async def fetch_raw(raw_text: str, raw_url: str) -> str:
    """Fetch raw job description from text input or URL."""
    # Priority: URL first, then text
    input_source = raw_url.strip() if raw_url.strip() else raw_text.strip()
    
    if not input_source:
        raise ValueError("No input provided")
    
    # If it's a URL, fetch content
    if input_source.startswith(('http://', 'https://')):
        # Check for LinkedIn detection
        if "linkedin.com/jobs" in input_source:
            import requests
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                response = requests.get(input_source, headers=headers, timeout=10)
                if len(response.text) < 1000 or "authwall" in response.text.lower():
                    return f"⚠️ LinkedIn requires login. Please copy-paste the job description text instead.\n\nURL attempted: {input_source}"
                return response.text
            except Exception as e:
                return f"❌ Failed to fetch URL: {str(e)}\n\nPlease copy-paste the job description text instead."
        
        # For other URLs, try to fetch
        try:
            import requests
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            response = requests.get(input_source, headers=headers, timeout=10)
            return response.text
        except Exception as e:
            return f"❌ Failed to fetch URL: {str(e)}\n\nPlease copy-paste the job description text instead."
    
    # Return raw text
    return input_source

async def run_job(raw_text: str, raw_url: str):
    """No-BS job analysis with streaming."""
    try:
        # Show skeleton immediately
        yield renderer_nobs.skeleton()
        
        # Fetch raw content
        raw = await fetch_raw(raw_text, raw_url)
        
        # Check for error messages
        if raw.startswith(('❌', '⚠️')):
            yield f"<div class='p-4 text-red-600'>{raw}</div>"
            return
        
        # Extract using No-BS format
        data = await extract_nobs(raw)
        
        # Generate final HTML
        final_html = renderer_nobs.to_html(data)
        yield final_html
        
    except Exception as e:
        yield f"<div class='p-4 text-red-600'>❌ Analysis failed: {str(e)}</div>"

def get_pipeline():
    """Create the analysis pipeline with all micro-functions"""
    from micro.scrape import ScrapeMicroFunction
    from micro.enrich import EnrichMicroFunction
    from micro.draft import DraftMicroFunction
    from micro.qa import QAMicroFunction
    from micro.critique import CritiqueMicroFunction
    from micro.bucket_enrich import BucketEnrichMicroFunction
    from micro.render import RenderMicroFunction
    
    return [
        ScrapeMicroFunction(),
        EnrichMicroFunction(),
        DraftMicroFunction(),
        QAMicroFunction(),
        CritiqueMicroFunction(),
        BucketEnrichMicroFunction(),
        RenderMicroFunction(),
    ]

async def analyze_job_stream(url_input: str, jd_input: str, progress=gr.Progress()):
    """Streaming job analysis with progress updates"""
    
    # Determine input type and text
    input_text = url_input.strip() if url_input.strip() else jd_input.strip()
    if not input_text:
        yield "❌ Please provide either a URL or job description text.", "❌ No input provided", "", ""
        return
        
    banner_html = ""
    
    try:
        # Initialize progress
        progress(0, desc="🚀 Starting analysis...")
        
        # Check for LinkedIn detection
        if "linkedin.com/jobs" in input_text:
            import requests
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                response = requests.get(input_text, headers=headers, timeout=10)
                if len(response.text) < 1000 or "authwall" in response.text.lower():
                    banner_html = """
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <div style='display: flex; align-items: center; gap: 0.5rem;'>
                            <span style='font-size: 1.2rem;'>⚠️</span>
                            <strong>LinkedIn Detection:</strong> Please copy-paste the job description text instead.
                        </div>
                    </div>
                    """
                    input_text = jd_input.strip()
                    if not input_text:
                        yield banner_html + "❌ No job description text provided.", "❌ LinkedIn blocked", "", ""
                        return
                else:
                    input_text = response.text
            except Exception as e:
                banner_html = f"""
                <div style='background: #fee; color: #c33; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <strong>URL Fetch Failed:</strong> {str(e)}<br>
                    Please copy-paste the job description text instead.
                </div>
                """
                input_text = jd_input.strip()
                if not input_text:
                    yield banner_html + "❌ No job description text provided.", "❌ URL fetch failed", "", ""
                    return
        
        progress(0.1, desc="⚡ Fast AI extraction...")
        
        # Use fast extraction
        job_core = await analyze(input_text)
        
        progress(0.3, desc="🏗️ Building analysis pipeline...")
        
        # Create orchestrator and run pipeline
        orchestrator = Orchestrator(get_pipeline())
        
        progress(0.5, desc="🎯 Running comprehensive analysis...")
        
        # Run analysis
        result = orchestrator.run({
            "raw": input_text,
            "role": job_core.role or "Unknown Role",
            "company": job_core.company or "Unknown Company"
        })
        
        progress(0.8, desc="🎨 Generating final report...")
        
        # Generate HTML using card renderer
        final_html = render_cards.to_html(result)
        
        progress(1.0, desc="✅ Analysis complete!")
        
        # Final result
        yield banner_html + final_html, f"Analysis complete for {job_core.company or 'Unknown Company'}", "", ""
        
    except Exception as e:
        log_metric("analysis_error", {"error": str(e)})
        yield f"❌ Analysis failed: {str(e)}", "❌ Error occurred", "", ""

# Sync wrapper for Gradio compatibility
def analyze_job_wrapper(url_input: str, jd_input: str, progress=gr.Progress()):
    """Sync wrapper for the async analysis function"""
    
    async def run_analysis():
        final_result = None
        async for result in analyze_job_stream(url_input, jd_input, progress):
            final_result = result
        return final_result
    
    return asyncio.run(run_analysis())

# No-BS wrapper for gradio compatibility
def run_job_wrapper(raw_text: str, raw_url: str):
    """Sync wrapper for No-BS job analysis"""
    
    async def run_analysis():
        final_result = None
        async for result in run_job(raw_text, raw_url):
            final_result = result
        return final_result
    
    return asyncio.run(run_analysis())

async def generate_interview_guide_wrapper(resume_text: str, resume_file, job_url: str, job_text: str, progress=gr.Progress()):
    """Generate personalized interview guide with progress updates"""
    
    try:
        # Progress updates
        progress(0, desc="🔍 Validating inputs...")
        
        # Handle resume input (text or file)
        final_resume_text = ""
        if resume_file is not None:
            # Read uploaded file
            try:
                if resume_file.name.endswith('.pdf'):
                    # Try to read PDF
                    import PyPDF2
                    with open(resume_file.name, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        text_parts = []
                        for page in pdf_reader.pages:
                            text_parts.append(page.extract_text())
                        final_resume_text = "\n".join(text_parts)
                else:
                    # Read as text file
                    with open(resume_file.name, 'r', encoding='utf-8') as file:
                        final_resume_text = file.read()
            except Exception as e:
                return f"❌ Failed to read resume file: {str(e)}", ""
        else:
            final_resume_text = resume_text.strip()
        
        # Handle job input (URL or text)
        final_job_input = job_url.strip() if job_url.strip() else job_text.strip()
        
        # Validate inputs
        if not final_resume_text:
            return "❌ Please provide a resume (text or file upload)", ""
        
        if not final_job_input:
            return "❌ Please provide a job posting (URL or text)", ""
        
        if len(final_resume_text) < 100:
            return "❌ Resume text is too short. Please provide a complete resume.", ""
        
        if len(final_job_input) < 50:
            return "❌ Job posting is too short. Please provide a complete job description.", ""
        
        progress(0.2, desc="🤖 Processing resume...")
        progress(0.4, desc="🎯 Analyzing job requirements...")
        progress(0.6, desc="📊 Performing gap analysis...")
        progress(0.8, desc="📝 Generating personalized guide...")
        
        # Generate interview guide using enhanced orchestrator
        orchestrator = EnhancedInterviewOrchestrator()
        result = await orchestrator.create_enhanced_interview_guide(final_resume_text, final_job_input)
        
        if not result.success:
            error_msg = result.error_message or "Unknown error occurred"
            return f"❌ Guide generation failed: {error_msg}", ""
        
        progress(1.0, desc="✅ Interview guide complete!")
        
        # Extract key metrics for status
        match_score = result.match_score
        processing_time = result.processing_time
        
        status_msg = f"✅ Generated personalized interview guide • Match Score: {match_score:.1f}% • Time: {processing_time:.1f}s"
        
        return result.interview_guide, status_msg
        
    except Exception as e:
        log_metric("interview_guide_error", {"error": str(e)})
        return f"❌ Guide generation failed: {str(e)}", "❌ Error occurred"

def generate_interview_guide_sync_wrapper(resume_text: str, resume_file, job_url: str, job_text: str, progress=gr.Progress()):
    """Sync wrapper for the async interview guide generation"""
    
    async def run_generation():
        result = await generate_interview_guide_wrapper(resume_text, resume_file, job_url, job_text, progress)
        return result
    
    return asyncio.run(run_generation())

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="IQKiller - No-BS Job Brief Generator"
    ) as demo:
        
        gr.HTML("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: bold;'>⚡ IQKiller</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>Personalized Interview Guide Generator</p>
            <p style='font-size: 1rem; opacity: 0.8;'>Resume + Job → Custom Interview Strategy</p>
        </div>
        """)
        
        with gr.Tab("🎯 Personalized Interview Guide"):
            gr.Markdown("### Get a personalized interview guide based on your resume and target job")
            gr.Markdown("Upload your resume and the target job posting to receive gap analysis, tailored questions, and strategic advice.")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Your Resume")
                    resume_text_input = gr.Textbox(
                        label="📝 Paste your resume text",
                        placeholder="Copy and paste your complete resume here...",
                        lines=8,
                        max_lines=15
                    )
                    resume_file_input = gr.File(
                        label="📎 Or upload resume file",
                        file_types=[".pdf", ".txt", ".docx"],
                        type="filepath"
                    )
                    
                    gr.Markdown("#### Target Job")
                    job_url_input = gr.Textbox(
                        label="🔗 Job posting URL (optional)",
                        placeholder="https://company.com/jobs/role-id",
                        lines=1
                    )
                    job_text_input = gr.Textbox(
                        label="📝 Or paste job description",
                        placeholder="Copy the complete job posting here...",
                        lines=6,
                        max_lines=10
                    )
                    
                    generate_guide_btn = gr.Button("🚀 Generate Interview Guide", variant="primary", size="lg")
                
                with gr.Column():
                    guide_output = gr.Markdown(label="Personalized Interview Guide")
                    guide_status = gr.Textbox(label="Status", interactive=False)
            
            generate_guide_btn.click(
                fn=generate_interview_guide_sync_wrapper,
                inputs=[resume_text_input, resume_file_input, job_url_input, job_text_input],
                outputs=[guide_output, guide_status]
            )
        
        with gr.Tab("⚡ Quick Job Brief"):
            gr.Markdown("### Get personalized interview prep guide with technical questions, talking points, and company intel")
            
            with gr.Row():
                with gr.Column():
                    nobs_url_input = gr.Textbox(
                        label="🔗 Job URL (optional)",
                        placeholder="https://company.com/jobs/role-id",
                        lines=1
                    )
                    nobs_text_input = gr.Textbox(
                        label="📝 Or paste job description text",
                        placeholder="Paste the complete job posting here...",
                        lines=8
                    )
                    nobs_analyze_btn = gr.Button("⚡ Generate Brief", variant="primary")
                
                with gr.Column():
                    nobs_output = gr.HTML(label="Job Brief")
            
            nobs_analyze_btn.click(
                fn=run_job_wrapper,
                inputs=[nobs_text_input, nobs_url_input],
                outputs=nobs_output
            )
        
        with gr.Tab("📊 Full Analysis"):
            gr.Markdown("### Complete job analysis with interview prep and detailed insights")
            
            with gr.Row():
                with gr.Column():
                    url_input = gr.Textbox(
                        label="🔗 Job URL (optional)",
                        placeholder="https://company.com/jobs/role-id",
                        lines=1
                    )
                    jd_input = gr.Textbox(
                        label="📝 Or paste job description text",
                        placeholder="Paste the complete job posting here...",
                        lines=8
                    )
                    analyze_btn = gr.Button("🚀 Analyze Job", variant="primary")
                
                with gr.Column():
                    output = gr.HTML(label="Analysis Results")
                    status = gr.Textbox(label="Status", interactive=False)
                    debug = gr.Textbox(label="Debug", visible=False)
                    timing = gr.Textbox(label="Timing", visible=False)
            
            analyze_btn.click(
                fn=analyze_job_wrapper,
                inputs=[url_input, jd_input],
                outputs=[output, status, debug, timing]
            )
        
        gr.HTML("""
        <div style='text-align: center; padding: 1rem; margin-top: 2rem; border-top: 1px solid #eee; color: #666;'>
            <p>🚀 Powered by GPT-4o-mini • 🎯 Personalized gap analysis • 📊 Interview Query style guides</p>
        </div>
        """)
    
    return demo

def create_health_check_server():
    """Create Flask server for health checks"""
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return health_check()
    
    @app.route('/login')
    def login_page():
        return "Please use the Gradio login interface at /login"
    
    return app

def main():
    """Main function to launch the app with authentication"""
    print("🚀 Starting IQKiller No-BS Job Brief Generator...")
    
    # Environment setup
    auth_mode = os.getenv("AUTH_ENABLED", "true").lower() == "true"
    run_mode = os.getenv("RUN_MODE", "app")  # "app", "login", or "both"
    
    # Load prompts
    prompts = prompt_loader.prompts
    if not prompts:
        print("⚠️  Warning: No prompts loaded, using defaults")
    
    if run_mode == "login":
        # Launch only login interface
        print("🔐 Launching login interface...")
        login_demo = create_login_interface()
        login_demo.launch(
            server_name="0.0.0.0", 
            server_port=7863,  # Different port for login
            show_error=True
        )
    
    elif run_mode == "app" and not auth_mode:
        # Launch app without authentication (development mode)
        print("⚠️  Authentication disabled - development mode")
        demo = create_interface()
        demo.launch(server_name="0.0.0.0", server_port=7862, show_error=True)
    
    elif run_mode == "app" and auth_mode:
        # Launch app with authentication (production mode)
        print("🔒 Launching authenticated app...")
        auth_wrapper = create_authenticated_wrapper(create_interface)
        demo = auth_wrapper()
        demo.launch(server_name="0.0.0.0", server_port=7862, show_error=True)
    
    elif run_mode == "both":
        # Launch both login and app interfaces (demo mode)
        print("🚀 Launching both login and app interfaces...")
        import threading
        
        # Start login interface in background
        def start_login():
            login_demo = create_login_interface()
            login_demo.launch(
                server_name="0.0.0.0",
                server_port=7863,
                show_error=True,
                prevent_thread_lock=True
            )
        
        login_thread = threading.Thread(target=start_login)
        login_thread.start()
        
        # Start main app with auth
        auth_wrapper = create_authenticated_wrapper(create_interface)
        demo = auth_wrapper()
        demo.launch(server_name="0.0.0.0", server_port=7862, show_error=True)
    
    else:
        print(f"❌ Invalid RUN_MODE: {run_mode}. Use 'app', 'login', or 'both'")
        return
        
    # Start health check server on different port
    try:
        health_app = create_health_check_server()
        health_thread = threading.Thread(
            target=lambda: health_app.run(host="0.0.0.0", port=8080, debug=False)
        )
        health_thread.daemon = True
        health_thread.start()
        print("🏥 Health check server running on port 8080")
    except Exception as e:
        print(f"⚠️  Health check server failed to start: {e}")

if __name__ == "__main__":
    main() 