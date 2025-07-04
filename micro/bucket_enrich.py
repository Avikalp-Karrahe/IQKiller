import asyncio
import time
import re
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from metrics import log_metric

class BucketEnrichMicroFunction:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main enrichment pipeline with async parallel execution"""
        start_time = time.time()
        enriched_data = data.get("enriched", {})
        
        company = enriched_data.get("company", "Unknown")
        location = enriched_data.get("location", "Unknown") 
        raw_input = data.get("raw_input", "")
        
        # Skip if no company identified
        if company in ["Unknown", "", None, "Not specified"]:
            log_metric("bucket_enrich_skip", {"reason": "no_company"})
            return {**data, "bucket_facts": {}}
        
        try:
            # Run enrichments in parallel using asyncio
            bucket_facts = asyncio.run(self._async_enrich_all(company, location, raw_input))
            
            # Log enrichment latency
            total_time = time.time() - start_time
            log_metric("enrich_latency", {
                "company": company,
                "total_seconds": total_time,
                "facts_count": len(bucket_facts)
            })
            log_metric("enrich_parallel_seconds", {"value": total_time})
            
            return {**data, "bucket_facts": bucket_facts}
            
        except Exception as e:
            log_metric("bucket_enrich_error", {"company": company, "error": str(e)})
            return {**data, "bucket_facts": {}}
    
    async def _async_enrich_all(self, company: str, location: str, raw_input: str) -> Dict[str, str]:
        """Run all enrichments in parallel"""
        # Prepare tasks for parallel execution
        tasks = []
        
        # Manager & Team enrichment (LinkedIn-based)
        if "linkedin.com" in raw_input:
            tasks.append(self._async_manager_enrich(raw_input))
        else:
            tasks.append(self._async_empty_result())
        
        # Company-based enrichments
        if company not in ["Unknown", "", None, "Not specified"]:
            tasks.extend([
                self._async_stack_enrich(company),
                self._async_biz_enrich(company),
                self._async_comp_enrich(company, location),
                self._async_culture_enrich(company)
            ])
        else:
            tasks.extend([
                self._async_empty_result(),
                self._async_empty_result(),
                self._async_empty_result(),
                self._async_empty_result()
            ])
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        bucket_facts = {}
        for result in results:
            if isinstance(result, dict):
                bucket_facts.update(result)
            elif isinstance(result, Exception):
                log_metric("async_enrich_error", {"error": str(result)})
        
        return bucket_facts
    
    async def _async_empty_result(self) -> Dict[str, str]:
        """Return empty result for skipped enrichments"""
        return {}
    
    async def _async_manager_enrich(self, linkedin_url: str) -> Dict[str, str]:
        """Async wrapper for manager enrichment"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.manager_enrich, linkedin_url
        )
    
    async def _async_stack_enrich(self, company: str) -> Dict[str, str]:
        """Async wrapper for stack enrichment"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.stack_enrich, company
        )
    
    async def _async_biz_enrich(self, company: str) -> Dict[str, str]:
        """Async wrapper for business enrichment"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.biz_enrich, company
        )
    
    async def _async_comp_enrich(self, company: str, location: str) -> Dict[str, str]:
        """Async wrapper for compensation enrichment"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.comp_enrich, company, location
        )
    
    async def _async_culture_enrich(self, company: str) -> Dict[str, str]:
        """Async wrapper for culture enrichment"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.culture_enrich, company
        )
    
    def manager_enrich(self, linkedin_url: str) -> Dict[str, str]:
        """Extract hiring manager and team info from LinkedIn job page"""
        facts = {}
            
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--user-data-dir=/tmp/chrome_user_data")
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            driver.get(linkedin_url)
            time.sleep(2)
            
            # Look for hiring manager info
            try:
                manager_element = driver.find_element(By.CSS_SELECTOR, '[data-test-id="hiring-manager"]')
                if manager_element:
                    facts["hiring_manager"] = manager_element.text.strip()
            except:
                pass
            
            # Look for team size indicators
            try:
                team_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'team') or contains(text(), 'employees')]")
                for element in team_elements[:2]:
                    text = element.text.lower()
                    if any(keyword in text for keyword in ["team of", "team size", "employees"]):
                        facts["team_info"] = element.text.strip()
                        break
            except:
                pass
                
            driver.quit()
            
        except Exception as e:
            log_metric("manager_enrich_error", {"url": linkedin_url, "error": str(e)})
            facts["manager_error"] = f"Failed to extract manager info: {str(e)}"
        
        return facts
    
    def stack_enrich(self, company: str) -> Dict[str, str]:
        """Get tech stack info from StackShare and GitHub"""
        facts = {}
        
        try:
            # StackShare lookup (2s timeout)
            stackshare_url = f"https://stackshare.io/{company.lower().replace(' ', '-')}"
            response = requests.get(stackshare_url, timeout=2)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract popular tools
                tool_elements = soup.find_all(class_=re.compile("tool|stack"))
                tools = []
                for elem in tool_elements[:10]:
                    text = elem.get_text().strip()
                    if text and len(text) < 50:
                        tools.append(text)
                
                if tools:
                    facts["tech_stack"] = f"Popular tools: {', '.join(tools[:5])}"
        
        except Exception as e:
            log_metric("stack_enrich_error", {"company": company, "error": str(e)})
        
        return facts
    
    def biz_enrich(self, company: str) -> Dict[str, str]:
        """Get business context from recent news and company info"""
        facts = {}
        
        try:
            # Recent news search (2s timeout)
            search_query = f"{company} news site:techcrunch.com OR site:bloomberg.com OR site:reuters.com"
            search_url = f"https://www.google.com/search?q={search_query}&tbm=nws&tbs=qdr:m2"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=2)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract recent headlines
                headlines = []
                for elem in soup.find_all(['h3', 'h4'], limit=3):
                    if elem.text.strip():
                        headlines.append(elem.text.strip())
                
                if headlines:
                    facts["recent_news"] = " | ".join(headlines[:2])
                    
        except Exception:
            pass
        
        # Basic company info
        try:
            # Simple company lookup
            facts["company_domain"] = f"{company.lower().replace(' ', '')}.com"
            
        except Exception:
            pass
        
        return facts
    
    def comp_enrich(self, company: str, location: str) -> Dict[str, str]:
        """Get compensation data from levels.fyi"""
        facts = {}
        
        try:
            # Levels.fyi lookup (2s timeout)
            levels_url = f"https://www.levels.fyi/companies/{company.lower().replace(' ', '-')}"
            response = requests.get(levels_url, timeout=2)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for salary ranges
                salary_elements = soup.find_all(text=re.compile(r'\$\d{2,3}[kK]'))
                if salary_elements:
                    salaries = [elem.strip() for elem in salary_elements[:3]]
                    facts["salary_range_levels"] = " - ".join(salaries)
                    facts["levels_url"] = f"🔗 {levels_url}"
                    
        except Exception:
            pass
        
        return facts
    
    def culture_enrich(self, company: str) -> Dict[str, str]:
        """Get culture and work-life balance info from Blind"""
        facts = {}
        
        try:
            # Blind company lookup (2s timeout)
            blind_url = f"https://www.teamblind.com/company/{company.lower().replace(' ', '-')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(blind_url, headers=headers, timeout=2)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for ratings
                rating_elements = soup.find_all(text=re.compile(r'\d\.\d'))
                if rating_elements:
                    facts["blind_rating"] = rating_elements[0].strip()
                    facts["blind_url"] = f"🔗 {blind_url}"
                    
                # Look for culture keywords
                culture_keywords = soup.find_all(text=re.compile(r'work.?life|culture|benefits|remote'))
                if culture_keywords:
                    facts["culture_mentions"] = " | ".join([kw.strip() for kw in culture_keywords[:2]])
                    
        except Exception:
            pass
        
        return facts 