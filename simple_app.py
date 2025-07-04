#!/usr/bin/env python3
"""
Simple Flask-based Job Posting Analysis App
"""

import hashlib
import os
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify
import pdfplumber
import re
import gradio as gr
import asyncio

app = Flask(__name__)


class JobPostingAnalyzer:
    """Simplified analyzer without caching."""
    
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
    
    def _is_pdf_file(self, path: str) -> bool:
        """Check if the path is a PDF file."""
        return path.lower().endswith('.pdf') or os.path.exists(path)
    
    def scrape_pdf_content(self, pdf_path: str) -> Optional[str]:
        """Scrape content from PDF file."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    
    def scrape_job_posting(self, url: str) -> Optional[str]:
        """Scrape job posting content from URL or PDF file."""
        # Check if it's a PDF file
        if self._is_pdf_file(url):
            return self.scrape_pdf_content(url)
        
        # Otherwise treat as URL
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
        lines = scraped_text.split('\n')
        job_data = {
            "title": "",
            "company": "",
            "location": "",
            "level": "",
            "requirements": "",
            "responsibilities": ""
        }
        
        # Enhanced extraction logic for JRD content
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Look for project title
            if "project:" in line_lower and not job_data["title"]:
                job_data["title"] = line.strip()
            elif "joint requirements document" in line_lower and not job_data["title"]:
                job_data["title"] = "Joint Requirements Document (JRD)"
            
            # Look for company info
            if "microsoft" in line_lower and not job_data["company"]:
                job_data["company"] = "Microsoft"
            
            # Look for level/position info
            if any(level in line_lower for level in ["senior", "lead", "principal", "staff"]):
                job_data["level"] = line.strip()
            
            # Look for requirements
            if "requirements" in line_lower or "functional" in line_lower:
                # Get next few lines as requirements
                req_lines = []
                for j in range(i, min(i + 10, len(lines))):
                    if lines[j].strip():
                        req_lines.append(lines[j].strip())
                job_data["requirements"] = " ".join(req_lines)
                break
        
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
        if job_data["requirements"]:
            preview += f"- **Requirements:** {job_data['requirements'][:200]}...\n"
        
        preview += "\n---\n"
        return preview
    
    def analyze_job_posting(self, url: str) -> Tuple[bool, str]:
        """Main analysis function with caching."""
        # Check if it's a PDF file first
        if self._is_pdf_file(url):
            # For PDFs, don't validate URL format
            pass
        elif not self._is_valid_url(url):
            return False, "Invalid URL format. Please provide a valid job posting URL or PDF file path."
        
        # Scrape the content (URL or PDF)
        scraped_text = self.scrape_job_posting(url)
        if not scraped_text:
            return False, "Failed to scrape content. Please check the file path or URL."
        
        # Enrich the data
        job_data = self.enrich_job_data(scraped_text)
        
        # Generate preview
        preview = self.generate_preview(job_data)
        
        return True, preview


# Initialize analyzer
analyzer = JobPostingAnalyzer()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Posting Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; }
        .preview { background: white; padding: 15px; border-radius: 4px; margin-top: 10px; }
        .info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Job Posting Analyzer</h1>
        <p>Paste a job posting URL or PDF file path to analyze and generate interview preparation materials.</p>
        
        <div class="info">
            <strong>Supported inputs:</strong><br>
            • URLs: https://example.com/job-posting<br>
            • PDF files: JRD_v1.1.pdf (local files)
        </div>
        
        <form method="POST">
            <input type="text" name="url" placeholder="https://example.com/job-posting or JRD_v1.1.pdf" value="{{ url or '' }}" required>
            <button type="submit">🔍 Analyze Job Posting</button>
        </form>
        
        {% if result %}
        <div class="result {% if success %}success{% else %}error{% endif %}">
            <strong>{{ status }}</strong>
            {% if success and preview %}
            <div class="preview">
                <h3>Preview:</h3>
                <pre>{{ preview }}</pre>
            </div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with form and results."""
    url = ""
    result = ""
    success = False
    status = ""
    preview = ""
    
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            success, result = analyzer.analyze_job_posting(url)
            if success:
                status = "✅ Analysis complete! Preview generated."
                preview = result
            else:
                status = f"❌ Error: {result}"
    
    return render_template_string(HTML_TEMPLATE, 
                                url=url, 
                                result=result, 
                                success=success, 
                                status=status, 
                                preview=preview)


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for job posting analysis."""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'})
    
    success, result = analyzer.analyze_job_posting(url)
    
    return jsonify({
        'success': success,
        'result': result if success else None,
        'error': result if not success else None
    })


if __name__ == '__main__':
    print("🚀 Starting Job Posting Analyzer...")
    print("📱 Web interface available at: http://localhost:5000")
    print("🔌 API endpoint available at: http://localhost:5000/api/analyze")
    app.run(debug=True, host='0.0.0.0', port=5000) 