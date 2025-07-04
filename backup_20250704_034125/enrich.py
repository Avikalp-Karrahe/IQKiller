import json
from typing import Any, Dict
from llm_client import llm_client
from prompt_loader import prompt_loader
from metrics import log_metric

class EnrichMicroFunction:
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        scraped_text = data.get("scraped_text", "")
        
        if not scraped_text or scraped_text == "No content found":
            return {**data, "enriched": {"role": "", "company": "", "level": "", "error": "No content to enrich"}}
        
        try:
            # Pre-process to extract obvious info
            company = self._extract_company(scraped_text, data.get("raw_input", ""))
            role = self._extract_role(scraped_text, data.get("raw_input", ""))
            
            # Use LLM to extract structured data
            enrichment_prompt = prompt_loader.get_prompt("enrich_prompt", 
                                                       job_posting=scraped_text,
                                                       pre_company=company,
                                                       pre_role=role)
            
            llm_response = llm_client.call_llm(enrichment_prompt)
            
            # Parse JSON response
            try:
                enriched_data = json.loads(llm_response)
                
                # Override with pre-extracted data if LLM missed it
                if enriched_data.get("company") in ["Unknown", "", None] and company:
                    enriched_data["company"] = company
                if enriched_data.get("role") in ["Unknown", "", None] and role:
                    enriched_data["role"] = role
                    
            except json.JSONDecodeError:
                # Fallback: use pre-extracted data and simple LLM call
                simple_prompt = f"""Extract job information from this text and respond with just the key details:

Job posting: {scraped_text[:1500]}

What is the job title, company, and seniority level?"""
                
                simple_response = llm_client.call_llm(simple_prompt)
                
                enriched_data = {
                    "role": role or "Unknown",
                    "company": company or "Unknown", 
                    "level": self._extract_level(scraped_text, simple_response),
                    "location": "Unknown",
                    "requirements": [],
                    "responsibilities": [],
                    "parsed_response": simple_response
                }
            
            log_metric("enrich_success", {
                "has_role": bool(enriched_data.get("role")),
                "has_company": bool(enriched_data.get("company")),
                "has_requirements": bool(enriched_data.get("requirements"))
            })
            
            return {**data, "enriched": enriched_data}
            
        except Exception as e:
            log_metric("enrich_error", {"error": str(e)})
            return {**data, "enriched": {"error": f"Enrichment failed: {e}"}}
    
    def _extract_company(self, scraped_text: str, raw_input: str) -> str:
        """Extract company name from text or URL"""
        import re
        
        # Check URL for company indicators (expanded list)
        url_company_map = {
            "microsoft.com": "Microsoft",
            "google.com": "Google", 
            "apple.com": "Apple",
            "amazon.com": "Amazon",
            "amazon.jobs": "Amazon",
            # Note: LinkedIn is excluded here because linkedin.com hosts jobs for OTHER companies
            "paypal.com": "PayPal",
            "paypal.eightfold.ai": "PayPal",
            "meta.com": "Meta",
            "facebook.com": "Meta",
            "netflix.com": "Netflix",
            "spotify.com": "Spotify",
            "uber.com": "Uber",
            "airbnb.com": "Airbnb",
            "salesforce.com": "Salesforce",
            "oracle.com": "Oracle",
            "adobe.com": "Adobe",
            "nvidia.com": "NVIDIA",
            "tesla.com": "Tesla",
            "stripe.com": "Stripe",
            "ing.com": "ING"
        }
        
        for domain, company in url_company_map.items():
            if domain in raw_input.lower():
                return company
        
        # Look for company patterns in scraped text (improved patterns)
        company_patterns = [
            # Direct company mentions (case-insensitive)
            r"\b(ING|Microsoft|Google|Apple|Amazon|Meta|Facebook|Netflix|Tesla|Uber|Airbnb|Spotify|PayPal|Salesforce|Oracle|Adobe|NVIDIA|Stripe|Parambil)\b",
            # Company in context patterns
            r"(?:at|with|for|join)\s+([A-Z][a-zA-Z\s&.,-]+(?:Inc|LLC|Corp|Corporation|Ltd|Limited|Bank|Group)?)\b",
            r"The Benefits Of Working With Us At\s+([A-Z][a-zA-Z\s&.-]+)",
            r"About\s+([A-Z][a-zA-Z\s&.-]+)(?:\s+Include|\s*$)",
            # Job posting patterns
            r"Company:\s*([^\n\r]+)",
            r"Company Name:\s*([^\n\r]+)",
            r"Organization:\s*([^\n\r]+)",
            r"Employer:\s*([^\n\r]+)",
            # Common job title patterns with "at Company"
            r"(?:Engineer|Scientist|Manager|Analyst|Developer|Designer|Specialist|Coordinator|Director)\s+at\s+([^\n\r,]+)",
            r"(?:Senior|Junior|Lead|Staff|Principal)\s+\w+\s+at\s+([^\n\r,]+)",
            # First line company extraction (common format)
            r"^([A-Z][a-zA-Z\s&.,-]+(?:Inc|LLC|Corp|Corporation|Ltd|Limited)?)\s*$"
        ]
        
        for pattern in company_patterns:
            matches = re.finditer(pattern, scraped_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                company = match.group(1) if match.lastindex else match.group(0)
                # Clean up formatting
                company = company.strip()
                # Remove markdown formatting
                company = re.sub(r'^\*+\s*', '', company)  # Remove leading asterisks
                company = re.sub(r'\s*\*+$', '', company)  # Remove trailing asterisks
                company = re.sub(r'\s+', ' ', company)  # Normalize whitespace
                
                # Filter out non-company names and LinkedIn
                excluded = ['linkedin', 'linkedin corporation', 'show more', 'about the job', 'about', 'include', 'benefits']
                if (company.lower() not in excluded and 
                    len(company.strip()) >= 2 and 
                    len(company.strip()) <= 50 and
                    not company.lower().startswith('http')):
                    return company
        
        return ""
    
    def _extract_role(self, scraped_text: str, raw_input: str) -> str:
        """Extract job role/title from text or URL"""
        import re
        
        # Look for title patterns in scraped text first (more reliable)
        title_patterns = [
            # Specific title patterns for this job
            r"(Regulatory Engagement and Oversight Specialist[^.\n]*)",
            r"(Financial Risk Specialist[^.\n]*)",
            # Generic title patterns
            r"Title:\s*([^\n\r]+)",
            r"Position:\s*([^\n\r]+)",
            r"Role:\s*([^\n\r]+)",
            r"Job Title:\s*([^\n\r]+)",
            r"Job:\s*([^\n\r]+)",
            # First line of job posting (often the title)
            r"^([A-Z][a-zA-Z\s/-]+(?:Specialist|Engineer|Manager|Analyst|Developer|Designer|Coordinator|Director|Scientist))\s*$",
            # Common job title patterns
            r"\b((?:Senior|Jr|Junior|Lead|Staff|Principal)?\s*(?:Software|Data|Applied|Research|Machine Learning|AI|Product|Marketing|Sales|Business|Regulatory|Financial|Risk)\s*(?:Engineer|Scientist|Manager|Analyst|Developer|Designer|Specialist|Coordinator|Director))\b",
            r"\b((?:Senior|Jr|Junior|Lead|Staff|Principal)?\s*(?:Full Stack|Frontend|Backend|DevOps|Cloud|Security|Mobile|Web)\s*(?:Engineer|Developer))\b"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, scraped_text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip() if match.lastindex else match.group(0).strip()
                # Clean up common formatting issues
                title = re.sub(r'^\*+\s*', '', title)  # Remove leading asterisks
                title = re.sub(r'\s*\*+$', '', title)  # Remove trailing asterisks
                title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
                title = re.sub(r'\s*for\s*$', '', title, flags=re.IGNORECASE)  # Remove trailing "for"
                if 5 <= len(title) <= 100:  # Reasonable length check
                    return title
        
        # Extract from URL if it contains job title (fallback)
        if raw_input and "/" in raw_input:
            url_parts = raw_input.split("/")
            for part in reversed(url_parts):  # Check from end first
                if any(keyword in part.lower() for keyword in ["scientist", "engineer", "developer", "manager", "analyst", "designer", "specialist"]):
                    # Clean up URL formatting
                    role = part.replace("-", " ").replace("_", " ").replace("%20", " ")
                    role = re.sub(r'\([^)]*\)', '', role)  # Remove parentheses content
                    role = re.sub(r'\?.*', '', role)  # Remove query parameters
                    role = " ".join(word.capitalize() for word in role.split() if word)
                    if 10 <= len(role) <= 80:
                        return role.strip()
        
        return ""
    
    def _extract_level(self, scraped_text: str, llm_response: str) -> str:
        """Extract seniority level from text"""
        import re
        
        text_to_check = f"{scraped_text} {llm_response}".lower()
        
        if any(term in text_to_check for term in ["senior", "sr.", "lead", "staff", "principal"]):
            return "Senior"
        elif any(term in text_to_check for term in ["junior", "jr.", "entry", "associate", "grad"]):
            return "Junior"
        elif any(term in text_to_check for term in ["mid", "intermediate", "ii", "2"]):
            return "Mid"
        else:
            return "Mid"  # Default assumption 