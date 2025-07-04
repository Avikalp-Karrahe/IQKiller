#!/usr/bin/env python3
"""
LLM-Powered Job Analysis App
Advanced job posting analysis with comprehensive role previews and interview preparation.
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

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="IQKiller - No-BS Job Brief Generator"
    ) as demo:
        
        gr.HTML("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: bold;'>⚡ IQKiller</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>No-BS Job Brief Generator</p>
            <p style='font-size: 1rem; opacity: 0.8;'>Get the essentials in 30 seconds</p>
        </div>
        """)
        
        with gr.Tab("🎯 Interview Prep"):
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
            <p>🚀 Powered by GPT-4o-mini • ⚡ Fast AI extraction • 🎯 No boilerplate</p>
        </div>
        """)
    
    return demo

def main():
    """Main function to launch the app"""
    print("🚀 Starting IQKiller - Interview Query Killer...")
    
    # Load prompts
    prompts = prompt_loader.prompts
    if not prompts:
        print("⚠️  Warning: No prompts loaded, using defaults")
    
    # Create and launch interface
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7862, show_error=True)

if __name__ == "__main__":
    main() 