#!/usr/bin/env python3
"""
Debug script to see what content we're scraping from job postings.
"""

import requests
from bs4 import BeautifulSoup

def debug_scrape(url: str):
    """Debug scraping of a job posting URL."""
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
        
        print("=== SCRAPED CONTENT ===")
        print(text[:2000])  # First 2000 characters
        print("\n=== END SCRAPED CONTENT ===")
        
        # Look for specific elements that might contain job info
        print("\n=== LOOKING FOR JOB TITLE ===")
        title_elements = soup.find_all(['h1', 'h2', 'h3', 'title'])
        for elem in title_elements[:10]:  # First 10 title elements
            if elem.get_text().strip():
                print(f"Tag: {elem.name}, Text: {elem.get_text().strip()}")
        
        print("\n=== LOOKING FOR COMPANY INFO ===")
        company_elements = soup.find_all(text=lambda text: text and 'microsoft' in text.lower())
        for elem in company_elements[:5]:
            print(f"Company text: {elem.strip()}")
            
    except Exception as e:
        print(f"Error scraping URL: {e}")

if __name__ == "__main__":
    url = "https://jobs.careers.microsoft.com/global/en/job/1829758/Applied-Scientist-II-and-Senior-Applied-Scientist-(Multiple-Positions)---Office-AI-Platform-team"
    debug_scrape(url) 