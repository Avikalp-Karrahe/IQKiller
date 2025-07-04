import re
import os
from typing import Optional
from text_extractor import JobCore
from llm_client import google_search
from metrics import log_metric


def patch_missing(core: JobCore) -> JobCore:
    """Patch missing fields in JobCore using Google search."""
    
    # Check if Google patching is enabled
    if not os.getenv("GOOGLE_PATCH_ENABLED", "true").lower() in ["true", "1", "yes"]:
        return core
    
    # Only patch if we have basic company info
    if not core.company:
        return core
    
    patches_applied = 0
    
    # Patch salary if missing
    if not core.salary_low and not core.salary_high:
        salary_info = _patch_salary(core.company, core.role)
        if salary_info:
            core.salary_low, core.salary_high = salary_info
            core.source_map["salary"] = "google"
            patches_applied += 1
    
    # Patch funding if missing
    if not core.funding:
        funding_info = _patch_funding(core.company)
        if funding_info:
            core.funding = funding_info
            core.source_map["funding"] = "google"
            patches_applied += 1
    
    # Patch mission if missing
    if not core.mission:
        mission_info = _patch_mission(core.company)
        if mission_info:
            core.mission = mission_info
            core.source_map["mission"] = "google"
            patches_applied += 1
    
    # Patch location if missing
    if not core.location:
        location_info = _patch_location(core.company)
        if location_info:
            core.location = location_info
            core.source_map["location"] = "google"
            patches_applied += 1
    
    log_metric("patch_missing", {
        "company": core.company,
        "patches_applied": patches_applied,
        "source_map": core.source_map
    })
    
    return core


def _patch_salary(company: str, role: str) -> Optional[tuple[int, int]]:
    """Search for salary information and extract range."""
    if not company or not role:
        return None
    
    query = f'"{company}" "{role}" salary range'
    snippets = google_search(query, top=3, timeout=5)
    
    for snippet in snippets:
        # Look for salary patterns like "$120k-$180k", "$150,000-$200,000"
        salary_patterns = [
            r'\$(\d+)k?[-–]\$?(\d+)k?',
            r'\$(\d+),?(\d+)[-–]\$?(\d+),?(\d+)',
            r'(\d+)k?[-–](\d+)k?\s*(?:per|/)?\s*year',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, snippet, re.IGNORECASE)
            if match:
                try:
                    if 'k' in match.group(0).lower():
                        low = int(match.group(1)) * 1000
                        high = int(match.group(2)) * 1000
                    else:
                        low = int(match.group(1))
                        high = int(match.group(2))
                    
                    # Sanity check: reasonable salary range
                    if 30000 <= low <= 500000 and 30000 <= high <= 500000 and low < high:
                        return (low, high)
                except (ValueError, IndexError):
                    continue
    
    return None


def _patch_funding(company: str) -> Optional[str]:
    """Search for funding information."""
    if not company:
        return None
    
    query = f'"{company}" funding round raised'
    snippets = google_search(query, top=3, timeout=5)
    
    for snippet in snippets:
        # Look for funding patterns
        funding_patterns = [
            r'raised \$(\d+(?:\.\d+)?[MB]?)',
            r'Series [A-Z] \$(\d+(?:\.\d+)?[MB]?)',
            r'\$(\d+(?:\.\d+)?[MB]?) (?:Series|round|funding)',
            r'(\$\d+(?:\.\d+)?[MB]? (?:million|billion))',
        ]
        
        for pattern in funding_patterns:
            match = re.search(pattern, snippet, re.IGNORECASE)
            if match:
                return match.group(0)[:50]  # Limit length
    
    return None


def _patch_mission(company: str) -> Optional[str]:
    """Search for company mission/tagline."""
    if not company:
        return None
    
    query = f'"{company}" company mission tagline about'
    snippets = google_search(query, top=3, timeout=5)
    
    for snippet in snippets:
        # Look for mission-like sentences
        sentences = re.split(r'[.!?]+', snippet)
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for sentences that describe what the company does
            if (len(sentence) > 20 and len(sentence) < 200 and 
                any(word in sentence.lower() for word in ['build', 'create', 'develop', 'provide', 'help', 'enable', 'platform'])):
                return sentence
    
    return None


def _patch_location(company: str) -> Optional[str]:
    """Search for company headquarters location."""
    if not company:
        return None
    
    query = f'"{company}" headquarters location'
    snippets = google_search(query, top=3, timeout=5)
    
    for snippet in snippets:
        # Look for location patterns
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2})',  # City City, State
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, snippet)
            if match:
                location = match.group(1).strip()
                # Sanity check for common US locations
                if any(state in location for state in ['CA', 'NY', 'WA', 'TX', 'MA']):
                    return location
    
    return None 