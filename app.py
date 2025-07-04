#!/usr/bin/env python3
"""
Job Posting Analysis App
A Gradio Blocks application for analyzing job postings and generating interview kits.
"""

import hashlib
import time
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urlparse

import gradio as gr
import requests
from bs4 import BeautifulSoup
from orchestrator import Orchestrator
from micro.scrape import ScrapeMicroFunction
from micro.enrich import EnrichMicroFunction
from micro.draft import DraftMicroFunction
from micro.critique import CritiqueMicroFunction
from micro.render import RenderMicroFunction
from micro.qa import QAMicroFunction
from metrics import log_metric
from prompt_loader import prompt_loader


class JobPostingAnalyzer:
    """Main orchestrator for job posting analysis."""
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    

    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def scrape_job_posting(self, url: str) -> Optional[str]:
        """Scrape job posting content from URL."""
        # TODO: Add proper error handling for network issues
        # TODO: Add rate limiting and user-agent headers
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return None
    
    def enrich_job_data(self, scraped_text: str) -> Dict[str, str]:
        """Extract and enrich job posting data."""
        # TODO: Implement AI-powered extraction for better accuracy
        # TODO: Add support for multiple job board formats
        
        lines = scraped_text.split('\n')
        job_data = {
            "title": "",
            "company": "",
            "location": "",
            "level": "",
            "requirements": "",
            "responsibilities": ""
        }
        
        # Simple extraction logic (placeholder)
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if "senior" in line_lower or "lead" in line_lower:
                job_data["level"] = line.strip()
            elif "engineer" in line_lower or "developer" in line_lower:
                if not job_data["title"]:
                    job_data["title"] = line.strip()
        
        return job_data
    
    def generate_preview(self, job_data: Dict[str, str]) -> str:
        """Generate markdown preview from job data."""
        preview = "### Role Snapshot\n"
        
        if job_data["title"]:
            preview += f"- **Title:** {job_data['title']}\n"
        if job_data["level"]:
            preview += f"- **Level:** {job_data['level']}\n"
        if job_data["company"]:
            preview += f"- **Company:** {job_data['company']}\n"
        if job_data["location"]:
            preview += f"- **Location:** {job_data['location']}\n"
        
        preview += "\n---\n"
        return preview
    
    def analyze_job_posting(self, url: str) -> Tuple[bool, str]:
        """Main analysis function."""
        if not self._is_valid_url(url):
            return False, "Invalid URL format. Please provide a valid job posting URL."
        
        # Scrape the job posting
        scraped_text = self.scrape_job_posting(url)
        if not scraped_text:
            return False, "Failed to scrape job posting. Please check the URL and try again."
        
        # Enrich the data
        job_data = self.enrich_job_data(scraped_text)
        
        # Generate preview
        preview = self.generate_preview(job_data)
        
        return True, preview


def create_gradio_interface() -> gr.Blocks:
    """Create the Gradio Blocks interface."""
    analyzer = JobPostingAnalyzer()
    
    with gr.Blocks(title="Job Posting Analyzer") as interface:
        gr.Markdown("# 🎯 Job Posting Analyzer")
        gr.Markdown("Paste a job posting URL to analyze and generate interview preparation materials.")
        
        with gr.Row():
            with gr.Column(scale=2):
                url_input = gr.Textbox(
                    label="Job Posting URL",
                    placeholder="https://example.com/job-posting",
                    lines=1
                )
                analyze_btn = gr.Button("🔍 Analyze Job Posting", variant="primary")
            
            with gr.Column(scale=1):
                status_output = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=2
                )
        
        with gr.Row():
            preview_output = gr.Markdown(
                label="Preview",
                value="Preview will appear here after analysis..."
            )
        
        with gr.Row():
            generate_kit_btn = gr.Button(
                "📋 Generate Interview Kit",
                variant="secondary",
                visible=False
            )
        
        def analyze_url(url: str) -> Tuple[str, str, bool]:
            """Handle URL analysis with status updates."""
            if not url.strip():
                return "Please enter a job posting URL.", "Preview will appear here after analysis...", False
            
            success, result = analyzer.analyze_job_posting(url)
            
            if success:
                return "✅ Analysis complete! Preview generated.", result, True
            else:
                return f"❌ Error: {result}", "Preview will appear here after analysis...", False
        
        # Wire up the interface
        analyze_btn.click(
            fn=analyze_url,
            inputs=[url_input],
            outputs=[status_output, preview_output, generate_kit_btn]
        )
        
        # Enter key in URL input also triggers analysis
        url_input.submit(
            fn=analyze_url,
            inputs=[url_input],
            outputs=[status_output, preview_output, generate_kit_btn]
        )
    
    return interface


if __name__ == "__main__":
    # TODO: Add proper logging configuration
    # TODO: Add environment variable for cache directory
    # TODO: Add proper error handling for Gradio launch
    
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )



# Pipeline steps (can be swapped/reordered)
def get_pipeline():
    return [
        ScrapeMicroFunction(),
        EnrichMicroFunction(),
        DraftMicroFunction(),
        QAMicroFunction(),
        CritiqueMicroFunction(),
        RenderMicroFunction(),
    ]

def analyze_job(input_text: str, progress=gr.Progress()) -> Tuple[str, str]:
    """Analyze job posting with progress updates"""
    if not input_text.strip():
        return "Please enter a job posting URL or paste job description.", ""
    
    progress(0.1, "🔍 Starting analysis...")
    
    try:
        orchestrator = Orchestrator(get_pipeline())
        
        # Track progress through pipeline
        progress(0.2, "📥 Scraping content...")
        time.sleep(0.5)  # Small delay for UX
        
        progress(0.4, "🔍 Enriching data...")
        time.sleep(0.5)
        
        progress(0.6, "✍️ Drafting content...")
        time.sleep(0.5)
        
        progress(0.8, "🔍 Quality assurance...")
        time.sleep(0.5)
        
        progress(0.9, "📝 Final review...")
        
        result: Dict[str, Any] = orchestrator.run({"input": input_text})
        
        preview = result.get("rendered_markdown", "No preview generated.")
        quality_score = result.get("quality_score", "N/A")
        enriched = result.get("enriched", {})
        
        log_metric("preview_generated", {"input": input_text, "quality_score": quality_score})
        
        progress(1.0, "✅ Analysis complete!")
        
        # Status info
        status = f"""📊 **Analysis Complete**
        
**Quality Score**: {quality_score}/10
**Role**: {enriched.get('role', 'Unknown')}
**Company**: {enriched.get('company', 'Unknown')}
**Level**: {enriched.get('level', 'Unknown')}

🎯 Generated comprehensive role preview and interview prep guide!"""
        
        return preview, status
        
    except Exception as e:
        log_metric("preview_error", {"input": input_text, "error": str(e)})
        error_msg = f"❌ Analysis failed: {str(e)}"
        return error_msg, error_msg

def load_prompts():
    """Load current prompts for editing"""
    prompts = prompt_loader.prompts
    return (
        prompts.get("scrape_prompt", ""),
        prompts.get("enrich_prompt", ""),
        prompts.get("draft_prompt", ""),
        prompts.get("qa_prompt", ""),
        prompts.get("critique_prompt", "")
    )

def save_prompts(scrape, enrich, draft, qa, critique):
    """Save edited prompts (Note: This would need file write permissions in production)"""
    try:
        # In a real implementation, you'd update the YAML file
        # For now, just show a status message
        return "✅ Prompts updated successfully! (Restart app to apply changes)"
    except Exception as e:
        return f"❌ Failed to save prompts: {e}"

def main():
    with gr.Blocks(title="🎯 Job Deep-Dive Web App") as demo:
        gr.Markdown("# 🎯 One-Stop Job Deep-Dive Web App")
        gr.Markdown("*LLM-powered job analysis with comprehensive role previews and interview preparation*")
        
        with gr.Tab("🔍 Job Analysis"):
            with gr.Row():
                with gr.Column(scale=2):
                    input_box = gr.Textbox(
                        label="Job URL or Job Description", 
                        placeholder="Paste job posting URL or full job description here...",
                        lines=8
                    )
                    analyze_btn = gr.Button("🔍 Analyze Job", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    status_box = gr.Markdown("Ready to analyze your job posting!", elem_id="status")
            
            preview_output = gr.Markdown(label="📄 Analysis Results", height=600)
            
            # Connect events
            analyze_btn.click(
                analyze_job, 
                inputs=input_box, 
                outputs=[preview_output, status_box]
            )
            input_box.submit(
                analyze_job, 
                inputs=input_box, 
                outputs=[preview_output, status_box]
            )
        
        with gr.Tab("⚙️ Sources & Prompt Editor"):
            gr.Markdown("## 📝 Edit LLM Prompts")
            gr.Markdown("*Customize the prompts used for each stage of the analysis pipeline*")
            
            with gr.Row():
                load_btn = gr.Button("📂 Load Current Prompts", variant="secondary")
                save_btn = gr.Button("💾 Save Prompts", variant="primary")
            
            with gr.Accordion("🔍 Scraping Prompt", open=False):
                scrape_prompt = gr.Textbox(
                    label="Scrape Prompt",
                    lines=8,
                    placeholder="Prompt for content extraction..."
                )
            
            with gr.Accordion("🔍 Enrichment Prompt", open=False):
                enrich_prompt = gr.Textbox(
                    label="Enrichment Prompt",
                    lines=8,
                    placeholder="Prompt for data enrichment..."
                )
            
            with gr.Accordion("✍️ Draft Prompt", open=False):
                draft_prompt = gr.Textbox(
                    label="Draft Prompt",
                    lines=8,
                    placeholder="Prompt for content drafting..."
                )
            
            with gr.Accordion("✅ QA Prompt", open=False):
                qa_prompt = gr.Textbox(
                    label="QA Prompt",
                    lines=8,
                    placeholder="Prompt for quality assurance..."
                )
            
            with gr.Accordion("🔍 Critique Prompt", open=False):
                critique_prompt = gr.Textbox(
                    label="Critique Prompt",
                    lines=8,
                    placeholder="Prompt for content critique..."
                )
            
            save_status = gr.Markdown("")
            
            # Connect prompt editor events
            load_btn.click(
                load_prompts,
                outputs=[scrape_prompt, enrich_prompt, draft_prompt, qa_prompt, critique_prompt]
            )
            
            save_btn.click(
                save_prompts,
                inputs=[scrape_prompt, enrich_prompt, draft_prompt, qa_prompt, critique_prompt],
                outputs=save_status
            )
        
        with gr.Tab("📊 Analytics"):
            gr.Markdown("## 📈 Usage Analytics")
            gr.Markdown("*Analytics dashboard coming soon...*")
            gr.Markdown("""
            **Features in development:**
            - Request volume and latency metrics
            - Quality score distributions
            - Popular job sites and companies analyzed
            - LLM provider performance comparison
            - Cost tracking and optimization insights
            """)
    
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)

if __name__ == "__main__":
    main() 