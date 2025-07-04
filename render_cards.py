"""
Clean card-based rendering for IQKiller job analysis.
Replaces markdown blob with focused HTML cards.
"""
from typing import Dict, List, Optional, Any
import re


def badge(value: str, field: str, source_map: Dict[str, str]) -> str:
    """Add '(from Google)' badge if field was patched via Google search."""
    if source_map.get(field) == "google":
        return f"{value} <em style='color:#666; font-size:0.9em'>(from Google)</em>"
    return value


def bullets(items: List[str], css_class: str = "text-gray-700") -> str:
    """Convert list to HTML bullet points."""
    if not items:
        return ""
    
    bullet_items = "".join([f"<li class='{css_class}'>{item}</li>" for item in items])
    return f"<ul class='list-disc list-inside space-y-1'>{bullet_items}</ul>"


def at_a_glance_card(job_data: Dict[str, Any], source_map: Dict[str, str]) -> str:
    """Build the main at-a-glance job info card."""
    company = job_data.get("company", "Unknown Company")
    role = job_data.get("role", "Unknown Role")
    level = job_data.get("seniority", job_data.get("level", ""))
    location = job_data.get("location", "")
    posted = job_data.get("posted_days", job_data.get("posted_age", ""))
    
    # Format salary range
    salary_low = job_data.get("salary_low")
    salary_high = job_data.get("salary_high")
    salary_text = ""
    if salary_low or salary_high:
        if salary_low and salary_high:
            salary_text = f"${salary_low:,} - ${salary_high:,}"
        elif salary_low:
            salary_text = f"${salary_low:,}+"
        elif salary_high:
            salary_text = f"Up to ${salary_high:,}"
        salary_text = badge(salary_text, "salary_low", source_map)
    
    # Format posted time
    posted_text = ""
    if posted:
        if isinstance(posted, int):
            if posted == 1:
                posted_text = "1 day ago"
            else:
                posted_text = f"{posted} days ago"
        else:
            posted_text = str(posted)
    
    return f"""
    <div class='bg-white border border-gray-200 rounded-lg p-6 shadow-sm mb-4'>
        <div class='flex items-start justify-between'>
            <div class='flex-1'>
                <h2 class='text-2xl font-bold text-gray-900'>{role}</h2>
                <p class='text-lg text-blue-600 font-semibold mt-1'>{company}</p>
                <div class='flex flex-wrap gap-4 mt-3 text-sm text-gray-600'>
                    {f"<span>📍 {location}</span>" if location else ""}
                    {f"<span>⚡ {level}</span>" if level else ""}
                    {f"<span>🕒 {posted_text}</span>" if posted_text else ""}
                </div>
                {f"<div class='mt-3 text-lg font-semibold text-green-600'>{salary_text}</div>" if salary_text else ""}
            </div>
        </div>
    </div>
    """


def quick_context_card(job_data: Dict[str, Any], source_map: Dict[str, str]) -> str:
    """Build mission and funding context banner."""
    mission = job_data.get("mission", "")
    funding = job_data.get("funding", "")
    
    if not mission and not funding:
        return ""
    
    content = ""
    if mission:
        content += f"<p class='text-gray-800'>{mission}</p>"
    
    if funding:
        funding_text = badge(funding, "funding", source_map)
        content += f"<p class='text-blue-700 font-medium mt-2'>💰 {funding_text}</p>"
    
    return f"""
    <div class='bg-green-50 border border-green-200 rounded-lg p-4 mb-4'>
        <h3 class='text-lg font-semibold text-green-800 mb-2'>Quick Context</h3>
        {content}
    </div>
    """


def skills_section(must_have: List[str], nice_to_have: List[str]) -> str:
    """Build must-have and nice-to-have skills sections."""
    if not must_have and not nice_to_have:
        return ""
    
    content = ""
    
    if must_have:
        content += f"""
        <div class='mb-4'>
            <h4 class='font-semibold text-gray-900 mb-2'>Must-Have Skills</h4>
            {bullets(must_have, "text-gray-700")}
        </div>
        """
    
    if nice_to_have:
        content += f"""
        <div>
            <h4 class='font-semibold text-gray-600 mb-2'>Nice-to-Have Skills</h4>
            {bullets(nice_to_have, "text-gray-500")}
        </div>
        """
    
    return f"""
    <div class='bg-white border border-gray-200 rounded-lg p-6 mb-4'>
        <h3 class='text-lg font-semibold text-gray-900 mb-4'>Skills & Requirements</h3>
        {content}
    </div>
    """


def interview_cheat_sheet(tech_q: List[str], behav_q: List[str]) -> str:
    """Build collapsible interview prep section."""
    if not tech_q and not behav_q:
        return ""
    
    tech_content = bullets(tech_q[:3], "text-gray-700") if tech_q else ""
    behav_content = bullets(behav_q[:3], "text-gray-700") if behav_q else ""
    
    return f"""
    <div class='bg-white border border-gray-200 rounded-lg p-6 mb-4'>
        <details>
            <summary class='text-lg font-semibold text-gray-900 cursor-pointer hover:text-blue-600'>
                Interview Cheat Sheet
            </summary>
            <div class='mt-4 space-y-4'>
                {f"<div><h4 class='font-semibold text-gray-900 mb-2'>Technical Questions</h4>{tech_content}</div>" if tech_content else ""}
                {f"<div><h4 class='font-semibold text-gray-900 mb-2'>Behavioral Questions</h4>{behav_content}</div>" if behav_content else ""}
            </div>
        </details>
    </div>
    """


def comp_perks_section(job_data: Dict[str, Any], perks: List[str]) -> str:
    """Build compensation and perks section."""
    salary_low = job_data.get("salary_low")
    salary_high = job_data.get("salary_high")
    
    if not salary_low and not salary_high and not perks:
        return ""
    
    content = ""
    
    if perks:
        content += f"""
        <div>
            <h4 class='font-semibold text-gray-900 mb-2'>Perks & Benefits</h4>
            {bullets(perks, "text-gray-700")}
        </div>
        """
    
    return f"""
    <div class='bg-white border border-gray-200 rounded-lg p-6 mb-4'>
        <h3 class='text-lg font-semibold text-gray-900 mb-4'>Compensation & Perks</h3>
        {content}
    </div>
    """


def red_flags_section(red_flags: List[str]) -> str:
    """Build red flags warning section."""
    if not red_flags:
        return ""
    
    return f"""
    <div class='bg-red-50 border border-red-200 rounded-lg p-4 mb-4'>
        <h3 class='text-lg font-semibold text-red-800 mb-2'>🚩 Red Flag Watchlist</h3>
        {bullets(red_flags, "text-red-700")}
    </div>
    """


def next_actions_section(apply_link: str = "") -> str:
    """Build action buttons section."""
    apply_button = ""
    if apply_link:
        apply_button = f"""
        <a href="{apply_link}" target="_blank" 
           class='inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors'>
            Apply Now
        </a>
        """
    
    return f"""
    <div class='bg-gray-50 border border-gray-200 rounded-lg p-6'>
        <h3 class='text-lg font-semibold text-gray-900 mb-4'>Next Actions</h3>
        <div class='flex gap-3 flex-wrap'>
            <button onclick='copyToClipboard()' 
                    class='bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors'>
                📋 Copy Summary
            </button>
            <button onclick='downloadPDF()' 
                    class='bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors'>
                📥 Download PDF
            </button>
            {apply_button}
        </div>
    </div>
    """


def extract_qa_data(qa_content: str) -> Dict[str, List[str]]:
    """Extract structured data from QA content."""
    data = {
        "must_have": [],
        "nice_to_have": [],
        "tech_q": [],
        "behav_q": [],
        "perks": [],
        "red_flags": []
    }
    
    # Simple regex patterns to extract lists from QA content
    patterns = {
        "must_have": r"(?:must.?have|required|essential).*?(?:\n|$)((?:\s*[-•]\s*.+(?:\n|$))*)",
        "nice_to_have": r"(?:nice.?to.?have|preferred|bonus).*?(?:\n|$)((?:\s*[-•]\s*.+(?:\n|$))*)",
        "tech_q": r"(?:technical|tech).*?question.*?(?:\n|$)((?:\s*[-•]\s*.+(?:\n|$))*)",
        "behav_q": r"(?:behavioral|behaviour).*?question.*?(?:\n|$)((?:\s*[-•]\s*.+(?:\n|$))*)",
        "perks": r"(?:perks|benefits).*?(?:\n|$)((?:\s*[-•]\s*.+(?:\n|$))*)",
        "red_flags": r"(?:red.?flag|warning|concern).*?(?:\n|$)((?:\s*[-•]\s*.+(?:\n|$))*)"
    }
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, qa_content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            items = re.findall(r"[-•]\s*(.+)", match)
            data[key].extend([item.strip() for item in items if item.strip()])
    
    return data


def to_html(result_data: Dict[str, Any]) -> str:
    """Convert job analysis result to clean HTML cards."""
    # Extract job core data
    enriched = result_data.get("enriched", {})
    source_map = enriched.get("source_map", {})
    
    # Extract QA-derived data (using correct orchestrator keys)
    qa_content = result_data.get("qa_result", "")
    critique_content = result_data.get("critique", "")
    draft_content = result_data.get("draft", "")
    
    qa_data = extract_qa_data(qa_content + "\n" + critique_content + "\n" + draft_content)
    
    # Apply link from enriched data
    apply_link = enriched.get("apply_link", "")
    
    # Build HTML sections
    html_parts = [
        at_a_glance_card(enriched, source_map),
        quick_context_card(enriched, source_map),
        skills_section(qa_data["must_have"], qa_data["nice_to_have"]),
        interview_cheat_sheet(qa_data["tech_q"], qa_data["behav_q"]),
        comp_perks_section(enriched, qa_data["perks"]),
        red_flags_section(qa_data["red_flags"]),
        next_actions_section(apply_link)
    ]
    
    # JavaScript for copy functionality
    role = enriched.get('role', 'Unknown')
    company = enriched.get('company', 'Unknown')
    location = enriched.get('location', 'N/A')
    seniority = enriched.get('seniority', 'N/A')
    mission = enriched.get('mission', '')
    
    js_script = f"""
    <script>
    window.__IQ_SUMMARY__ = `Job: {role} at {company}
Location: {location}
Level: {seniority}
{mission}`;
    
    function copyToClipboard() {{
        navigator.clipboard.writeText(window.__IQ_SUMMARY__).then(() => {{
            alert('Summary copied to clipboard!');
        }});
    }}
    
    function downloadPDF() {{
        alert('PDF download coming soon!');
    }}
    </script>
    """
    
    # Combine all sections
    return "\n".join([part for part in html_parts if part.strip()]) + js_script 


def skeleton() -> str:
    """Return loading skeleton placeholder."""
    return "<div class='animate-pulse p-6 text-gray-400'>Analyzing JD…</div>" 