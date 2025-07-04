#!/usr/bin/env python3
"""
Simple test script for job posting analysis functionality.
"""

import time
from typing import Dict, Any, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import gradio as gr
import asyncio
import pytest


class JobPostingAnalyzer:
    """Simplified analyzer for testing without caching."""
    
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
        
        # Simple extraction logic
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
        """Main analysis function with caching."""
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


def main():
    """Test the job posting analyzer."""
    analyzer = JobPostingAnalyzer()
    
    # Test with a sample job posting URL
    test_url = "https://jobs.lever.co/example/senior-data-engineer"
    
    print("Testing Job Posting Analyzer...")
    print(f"URL: {test_url}")
    
    success, result = analyzer.analyze_job_posting(test_url)
    
    if success:
        print("✅ Analysis successful!")
        print("\nPreview:")
        print(result)
    else:
        print(f"❌ Analysis failed: {result}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    main() 