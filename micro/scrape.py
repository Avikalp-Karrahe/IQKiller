import requests
import time
import re
from typing import Dict, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime


class LinkedInAuthError(Exception):
    """Raised when LinkedIn requires authentication"""
    pass


def canonicalise(url: str) -> str:
    """Convert URL to canonical form for better caching"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Handle LinkedIn URLs
    if 'linkedin.com' in url:
        # Extract job ID from currentJobId parameter
        job_id_match = re.search(r'currentJobId=(\d+)', url)
        if job_id_match:
            job_id = job_id_match.group(1)
            return f"https://www.linkedin.com/jobs/view/{job_id}"
        
        # Extract job ID from /jobs/view/ URLs
        view_match = re.search(r'/jobs/view/(\d+)', url)
        if view_match:
            job_id = view_match.group(1)
            return f"https://www.linkedin.com/jobs/view/{job_id}"
    
    return url


def extract_preview_from_html(html: str, url: str) -> Dict[str, str]:
    """Extract preview info from HTML for immediate display"""
    preview = {
        'company': 'Not specified',
        'role': 'Not specified', 
        'location': 'Not specified',
        'posted_days': 'Recently'
    }
    
    if not html:
        return preview
    
    # LinkedIn job page patterns
    if 'linkedin.com' in url:
        # Company name patterns
        company_patterns = [
            r'<span[^>]*class="[^"]*job-details-jobs-unified-top-card__company-name[^"]*"[^>]*>([^<]+)</span>',
            r'<a[^>]*class="[^"]*job-details-jobs-unified-top-card__company-name[^"]*"[^>]*>([^<]+)</a>',
            r'"hiringCompany":\s*{\s*"name":\s*"([^"]+)"',
            r'<h4[^>]*class="[^"]*job-details-jobs-unified-top-card__company-name[^"]*"[^>]*>([^<]+)</h4>'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                preview['company'] = match.group(1).strip()
                break
        
        # Job title patterns
        title_patterns = [
            r'<h1[^>]*class="[^"]*job-details-jobs-unified-top-card__job-title[^"]*"[^>]*>([^<]+)</h1>',
            r'"jobTitle":\s*"([^"]+)"',
            r'<title>([^|]+)\s*\|[^<]*</title>'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                preview['role'] = match.group(1).strip()
                break
        
        # Location patterns
        location_patterns = [
            r'<span[^>]*class="[^"]*job-details-jobs-unified-top-card__bullet[^"]*"[^>]*>([^<]+)</span>',
            r'"jobLocation":\s*{\s*"displayName":\s*"([^"]+)"',
            r'<div[^>]*class="[^"]*job-details-jobs-unified-top-card__primary-description-container[^"]*"[^>]*>.*?<span[^>]*>([^<]+)</span>'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                location = match.group(1).strip()
                if location and not any(x in location.lower() for x in ['applicant', 'employee', 'easy apply']):
                    preview['location'] = location
                    break
    
    # Microsoft careers patterns
    elif 'microsoft.com' in url:
        company_match = re.search(r'<title>([^|]+)\s*\|\s*Microsoft\s*Careers', html, re.IGNORECASE)
        if company_match:
            preview['role'] = company_match.group(1).strip()
            preview['company'] = 'Microsoft'
        
        location_match = re.search(r'"jobLocation":\s*"([^"]+)"', html)
        if location_match:
            preview['location'] = location_match.group(1).strip()
    
    # Google careers patterns  
    elif 'google.com' in url:
        preview['company'] = 'Google'
        title_match = re.search(r'<title>([^|]+)\s*\|\s*Google\s*Careers', html, re.IGNORECASE)
        if title_match:
            preview['role'] = title_match.group(1).strip()
    
    # Amazon jobs patterns
    elif 'amazon.jobs' in url:
        preview['company'] = 'Amazon'
        title_match = re.search(r'<h1[^>]*class="[^"]*job-title[^"]*"[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
        if title_match:
            preview['role'] = title_match.group(1).strip()
    
    # PayPal patterns
    elif 'paypal.eightfold.ai' in url:
        preview['company'] = 'PayPal'
        title_match = re.search(r'"jobTitle":\s*"([^"]+)"', html)
        if title_match:
            preview['role'] = title_match.group(1).strip()
    
    # Clean up extracted text
    for key in preview:
        if isinstance(preview[key], str):
            preview[key] = re.sub(r'\s+', ' ', preview[key]).strip()
            if len(preview[key]) > 100:
                preview[key] = preview[key][:97] + '...'
    
    return preview


class ScrapeMicroFunction:
    """Micro-function for web scraping with enhanced preview extraction"""
    
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    def run(self, data: dict) -> dict:
        """Main scraping function returning preview and full content"""
        raw_input = data.get('raw_input', '') or data.get('input', '')
        
        if not raw_input:
            return {
                'success': False,
                'error': 'No input provided',
                'preview': {'company': 'Error', 'role': 'No input', 'location': '', 'posted_days': ''},
                'content': '',
                'scraped_text': ''
            }
        
        # If it's a URL, scrape it
        if raw_input.startswith(('http://', 'https://', 'www.')):
            canonical_url = canonicalise(raw_input)
            result = self._scrape_url(canonical_url)
            
            # Add scraped_text for backward compatibility
            result['scraped_text'] = result.get('content', '')
            return {**data, **result, 'raw_input': raw_input}
        else:
            # Direct text input - use text_extractor
            from text_extractor import extract_entities
            from micro.patch_missing import patch_missing
            
            job_core = extract_entities(raw_input)
            # Apply Google patching for missing fields
            job_core = patch_missing(job_core)
            
            # Convert JobCore to preview format
            preview = {
                'company': job_core.company or 'Not specified',
                'role': job_core.role or 'Not specified',
                'location': job_core.location or 'Not specified',
                'posted_days': str(job_core.posted_days) if job_core.posted_days else 'Recently'
            }
            
            return {
                **data,
                'success': True,
                'content': raw_input,
                'preview': preview,
                'url': None,
                'scraped_text': raw_input,
                'raw_input': raw_input,
                'job_core': job_core  # Add extracted entities for downstream use
            }
    
    def _scrape_url(self, url: str) -> dict:
        """Scrape URL and extract both preview and full content"""
        try:
            # Try LinkedIn-specific scraping first
            if 'linkedin.com' in url:
                return self._scrape_linkedin(url)
            else:
                return self._scrape_generic(url)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'preview': {'company': 'Error', 'role': str(e)[:50], 'location': '', 'posted_days': ''},
                'content': ''
            }
    
    def _scrape_linkedin(self, url: str) -> dict:
        """LinkedIn-specific scraping with auth detection"""
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            driver.set_page_load_timeout(10)
            
            driver.get(url)
            
            # Wait briefly and check for auth redirect
            time.sleep(2)
            current_url = driver.current_url
            
            if 'authwall' in current_url or 'login' in current_url or 'challenge' in current_url:
                raise LinkedInAuthError("LinkedIn requires authentication")
            
            # Wait for job content to load
            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
            except TimeoutException:
                pass
            
            html = driver.page_source
            preview = extract_preview_from_html(html, url)
            
            return {
                'success': True,
                'content': html,
                'preview': preview,
                'url': url
            }
            
        except LinkedInAuthError:
            raise
        except Exception as e:
            return {
                'success': False,
                'error': f"LinkedIn scraping failed: {str(e)}",
                'preview': {'company': 'LinkedIn', 'role': 'Auth Required', 'location': '', 'posted_days': ''},
                'content': ''
            }
        finally:
            if driver:
                driver.quit()
    
    def _scrape_generic(self, url: str) -> dict:
        """Generic scraping for non-LinkedIn URLs"""
        try:
            # Try requests first (faster)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            html = response.text
            preview = extract_preview_from_html(html, url)
            
            return {
                'success': True,
                'content': html,
                'preview': preview,
                'url': url
            }
            
        except Exception as e:
            # Fallback to Selenium
            return self._scrape_with_selenium(url)
    
    def _scrape_with_selenium(self, url: str) -> dict:
        """Selenium fallback for sites that block requests"""
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            driver.set_page_load_timeout(15)
            
            driver.get(url)
            time.sleep(3)
            
            html = driver.page_source
            preview = extract_preview_from_html(html, url)
            
            return {
                'success': True,
                'content': html,
                'preview': preview,
                'url': url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Selenium scraping failed: {str(e)}",
                'preview': {'company': 'Error', 'role': 'Scraping failed', 'location': '', 'posted_days': ''},
                'content': ''
            }
        finally:
            if driver:
                driver.quit()
    
    def _extract_preview_from_text(self, text: str) -> Dict[str, str]:
        """Extract preview info from pasted text"""
        preview = {
            'company': 'Not specified',
            'role': 'Not specified',
            'location': 'Not specified', 
            'posted_days': 'Recently'
        }
        
        lines = text.split('\n')
        
        # Enhanced extraction patterns for better accuracy
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            if len(line) < 3 or len(line) > 150:
                continue
                
            # Pattern: "Company · Role · Location"
            if '·' in line and preview['company'] == 'Not specified':
                parts = [p.strip() for p in line.split('·')]
                if len(parts) >= 3:
                    preview['company'] = parts[0]
                    preview['role'] = parts[1]
                    preview['location'] = parts[2]
                    continue
            
            # Pattern: "Role at Company"
            if ' at ' in line and any(word in line.lower() for word in ['engineer', 'developer', 'analyst', 'manager', 'scientist', 'designer']):
                parts = line.split(' at ')
                if len(parts) == 2:
                    preview['role'] = parts[0].strip()
                    preview['company'] = parts[1].strip()
                    continue
            
            # Look for standalone role titles
            if preview['role'] == 'Not specified' and any(word in line.lower() for word in ['engineer', 'developer', 'analyst', 'manager', 'scientist', 'designer', 'specialist']):
                # Check if it's likely a job title (not part of description)
                if i < 5 and not line.lower().startswith(('we', 'the', 'our', 'about', 'job', 'position')):
                    preview['role'] = line
            
            # Look for company names (common patterns)
            if preview['company'] == 'Not specified':
                if any(word in line.lower() for word in ['group', 'search', 'inc', 'corp', 'company', 'technologies', 'systems', 'solutions']):
                    # Avoid generic descriptions and clean up
                    if not any(word in line.lower() for word in ['the', 'our', 'we', 'about', 'job', 'position', 'looking', 'seeking', 'logo']):
                        # Clean up common suffixes
                        clean_company = line.replace(' logo', '').replace(' Logo', '').strip()
                        preview['company'] = clean_company
            
            # Look for location patterns
            if preview['location'] == 'Not specified':
                # Extract location from patterns like "New York, NY · other text"
                location_match = re.search(r'([^·•]+(?:, [A-Z]{2}|New York|California|Remote))[·•\s]', line)
                if location_match:
                    preview['location'] = location_match.group(1).strip()
                # Fallback to simple patterns
                elif any(pattern in line for pattern in [', NY', ', CA', ', TX', ', FL', 'New York', 'California', 'Remote']):
                    if not any(word in line.lower() for word in ['we', 'the', 'our', 'about', 'job']):
                        # Try to extract just the location part
                        for pattern in [', NY', ', CA', ', TX', ', FL']:
                            if pattern in line:
                                parts = line.split(pattern)
                                if len(parts) >= 2:
                                    location_part = parts[0].split()[-1] + pattern
                                    preview['location'] = location_part
                                    break
                        if preview['location'] == 'Not specified' and 'New York' in line:
                            preview['location'] = 'New York, NY'
                        elif preview['location'] == 'Not specified':
                            preview['location'] = line
        
        return preview
    
    @staticmethod
    def from_text(raw: str) -> Dict[str, str]:
        """Static method to extract company/role/location from plain text"""
        scraper = ScrapeMicroFunction()
        return scraper._extract_preview_from_text(raw) 