#!/usr/bin/env python3
"""
Test script to analyze the JRD PDF file using our job posting analyzer.
"""

import hashlib
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import time
import requests
from bs4 import BeautifulSoup
import PyPDF2
import pdfplumber
import re
from urllib.parse import urljoin
import gradio as gr
import asyncio


class JobPostingAnalyzer:
    """Test analyzer without caching."""
    
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
    
    def scrape_pdf_content(self, pdf_path: str) -> Optional[str]:
        """Scrape content from PDF file."""
        try:
            # Try pdfplumber first for better text extraction
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
        # Check if it's a local file path
        if url.startswith('/') or url.startswith('./') or url.endswith('.pdf'):
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
        cache_key = self._get_cache_key(url)
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return True, cached_result
        
        # Scrape the content (URL or PDF)
        scraped_text = self.scrape_job_posting(url)
        if not scraped_text:
            return False, "Failed to scrape content. Please check the file path or URL."
        
        # Enrich the data
        job_data = self.enrich_job_data(scraped_text)
        
        # Generate preview
        preview = self.generate_preview(job_data)
        
        # Cache the result
        self.cache.set(cache_key, preview, expire=self.cache_timeout)
        
        return True, preview


def main():
    """Test the job posting analyzer with the JRD PDF."""
    analyzer = JobPostingAnalyzer()
    
    # Test with the JRD PDF file
    pdf_path = "JRD_v1.1.pdf"
    
    print("Testing Job Posting Analyzer with JRD PDF...")
    print(f"File: {pdf_path}")
    print("=" * 60)
    
    success, result = analyzer.analyze_job_posting(pdf_path)
    
    if success:
        print("✅ Analysis successful!")
        print("\nPreview:")
        print(result)
    else:
        print(f"❌ Analysis failed: {result}")
    
    print("\n" + "=" * 60)
    print("Test completed!")


if __name__ == "__main__":
    main() 