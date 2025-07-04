"""
No-BS Job Brief renderer for IQKiller.
Creates compact, single-card job briefs with essential info only.
"""
from typing import Dict, List, Optional, Any

def skeleton() -> str:
    """Return loading skeleton placeholder."""
    return "<div class='animate-pulse p-4 text-gray-400'>Analyzing…</div>"

def bullets(items: List[str], css_class: str = "text-gray-700") -> str:
    """Convert list to HTML bullet points."""
    if not items:
        return ""
    
    bullet_items = "".join([f"<li class='{css_class} text-sm'>{item}</li>" for item in items])
    return f"<ul class='list-disc list-inside space-y-1 ml-4'>{bullet_items}</ul>"

def hide_if_empty(content: str, wrapper: str = "") -> str:
    """Hide section if content is empty."""
    if not content.strip():
        return ""
    return wrapper.format(content=content) if wrapper else content

def format_title_line(data: Dict[str, Any]) -> str:
    """Format the compact title line."""
    title = data.get("title", "Unknown Role")
    company = data.get("company", "Unknown Company")
    location = data.get("location", "")
    work_type = data.get("work_type", "")
    salary_band = data.get("salary_band", "")
    
    # Build title components
    parts = [f"{title} · {company}"]
    
    if work_type or location:
        location_work = " ".join(filter(None, [work_type, location]))
        parts.append(location_work)
    
    if salary_band:
        parts.append(f"• {salary_band}")
    
    return " — ".join(parts)

def format_mission(mission: str) -> str:
    """Format mission one-liner (≤25 words)."""
    if not mission:
        return ""
    
    # Truncate if too long
    words = mission.split()
    if len(words) > 25:
        mission = " ".join(words[:25]) + "..."
    
    return f"""
    <div class='mb-4'>
        <p class='text-gray-800 text-sm italic'>{mission}</p>
    </div>
    """

def format_must_have(must_have: List[str]) -> str:
    """Format must-have stack (≤6 bullets, <7 words each)."""
    if not must_have:
        return ""
    
    # Limit to 6 items and truncate long items
    limited_items = must_have[:6]
    truncated_items = []
    
    for item in limited_items:
        words = item.split()
        if len(words) > 7:
            item = " ".join(words[:7]) + "..."
        truncated_items.append(item)
    
    bullet_html = bullets(truncated_items, "text-gray-900 font-medium")
    
    return f"""
    <div class='mb-4'>
        <h3 class='text-sm font-semibold text-gray-900 mb-2'>Must-Have Stack</h3>
        {bullet_html}
    </div>
    """

def format_nice_to_have(nice_to_have: List[str]) -> str:
    """Format nice-to-have skills (grey bullets)."""
    if not nice_to_have:
        return ""
    
    # Limit to 6 items
    limited_items = nice_to_have[:6]
    bullet_html = bullets(limited_items, "text-gray-500")
    
    return f"""
    <div class='mb-4'>
        <h3 class='text-sm font-semibold text-gray-600 mb-2'>Nice-to-Haves</h3>
        {bullet_html}
    </div>
    """

def format_why_it_matters(why_it_matters: str) -> str:
    """Format why-it-matters (≤30 words)."""
    if not why_it_matters:
        return ""
    
    # Truncate if too long
    words = why_it_matters.split()
    if len(words) > 30:
        why_it_matters = " ".join(words[:30]) + "..."
    
    return f"""
    <div class='mb-4'>
        <h3 class='text-sm font-semibold text-blue-700 mb-2'>Why It Matters</h3>
        <p class='text-gray-700 text-sm'>{why_it_matters}</p>
    </div>
    """

def format_perks(perks: List[str]) -> str:
    """Format perks as inline list."""
    if not perks:
        return ""
    
    perks_text = " • ".join(perks[:8])  # Limit to avoid overflow
    
    return f"""
    <div class='mb-4'>
        <h3 class='text-sm font-semibold text-green-700 mb-2'>Perks</h3>
        <p class='text-gray-700 text-sm'>{perks_text}</p>
    </div>
    """

def format_red_flags(red_flags: List[str]) -> str:
    """Format red flags (red, only if any)."""
    if not red_flags:
        return ""
    
    bullet_html = bullets(red_flags, "text-red-700")
    
    return f"""
    <div class='mb-4 bg-red-50 border border-red-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-red-800 mb-2'>🚩 Red Flags</h3>
        {bullet_html}
    </div>
    """

def format_technical_questions(technical_questions: List[str]) -> str:
    """Format likely technical interview questions."""
    if not technical_questions:
        return ""
    
    bullet_html = bullets(technical_questions[:6], "text-red-700")
    
    return f"""
    <div class='mb-4 bg-red-50 border border-red-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-red-800 mb-2'>🔧 Technical Questions</h3>
        <p class='text-xs text-red-600 mb-2'>Likely technical questions they'll ask:</p>
        {bullet_html}
    </div>
    """

def format_behavioral_questions(behavioral_questions: List[str]) -> str:
    """Format likely behavioral interview questions."""
    if not behavioral_questions:
        return ""
    
    bullet_html = bullets(behavioral_questions[:6], "text-purple-700")
    
    return f"""
    <div class='mb-4 bg-purple-50 border border-purple-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-purple-800 mb-2'>💬 Behavioral Questions</h3>
        <p class='text-xs text-purple-600 mb-2'>Behavioral questions to prepare for:</p>
        {bullet_html}
    </div>
    """

def format_talking_points(talking_points: List[str]) -> str:
    """Format key talking points to emphasize."""
    if not talking_points:
        return ""
    
    bullet_html = bullets(talking_points[:6], "text-indigo-700")
    
    return f"""
    <div class='mb-4 bg-indigo-50 border border-indigo-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-indigo-800 mb-2'>🎯 Talking Points</h3>
        <p class='text-xs text-indigo-600 mb-2'>Highlight these experiences/achievements:</p>
        {bullet_html}
    </div>
    """

def format_company_intel(company_intel: List[str]) -> str:
    """Format key company intelligence for interview research."""
    if not company_intel:
        return ""
    
    bullet_html = bullets(company_intel[:3], "text-blue-700")
    
    return f"""
    <div class='mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-blue-800 mb-2'>🏢 Company Intel</h3>
        <p class='text-xs text-blue-600 mb-2'>Key facts to mention:</p>
        {bullet_html}
    </div>
    """

def format_smart_questions(smart_questions: List[str]) -> str:
    """Format smart questions for the applicant to ask."""
    if not smart_questions:
        return ""
    
    bullet_html = bullets(smart_questions[:5], "text-green-700")
    
    return f"""
    <div class='mb-4 bg-green-50 border border-green-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-green-800 mb-2'>❓ Smart Questions</h3>
        <p class='text-xs text-green-600 mb-2'>Ask these to show strategic thinking:</p>
        {bullet_html}
    </div>
    """

def format_role_challenges(role_challenges: List[str]) -> str:
    """Format main challenges this role will solve."""
    if not role_challenges:
        return ""
    
    bullet_html = bullets(role_challenges[:5], "text-orange-700")
    
    return f"""
    <div class='mb-4 bg-orange-50 border border-orange-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-orange-800 mb-2'>⚡ Role Challenges</h3>
        <p class='text-xs text-orange-600 mb-2'>Key problems you'll solve:</p>
        {bullet_html}
    </div>
    """

def format_success_metrics(success_metrics: List[str]) -> str:
    """Format how success is measured in this role."""
    if not success_metrics:
        return ""
    
    bullet_html = bullets(success_metrics[:5], "text-teal-700")
    
    return f"""
    <div class='mb-4 bg-teal-50 border border-teal-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-teal-800 mb-2'>📊 Success Metrics</h3>
        <p class='text-xs text-teal-600 mb-2'>How success is measured:</p>
        {bullet_html}
    </div>
    """

def format_salary_context(salary_context: str) -> str:
    """Format salary negotiation context."""
    if not salary_context:
        return ""
    
    return f"""
    <div class='mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3'>
        <h3 class='text-sm font-semibold text-yellow-800 mb-2'>💰 Salary Context</h3>
        <p class='text-yellow-700 text-sm'>{salary_context}</p>
    </div>
    """

def format_next_actions(apply_link: str = "") -> str:
    """Format next actions with apply and copy buttons."""
    apply_button = ""
    if apply_link:
        apply_button = f"""
        <a href="{apply_link}" target="_blank" 
           class='inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors mr-2'>
            ▶ Apply
        </a>
        """
    
    return f"""
    <div class='pt-4 border-t border-gray-200'>
        <div class='flex items-center gap-2'>
            {apply_button}
            <button onclick="copySummary()" 
                    class='inline-flex items-center px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors'>
                📋 Copy summary
            </button>
        </div>
    </div>
    """

def create_copy_script() -> str:
    """Create JavaScript for copy functionality."""
    return """
    <script>
    function copySummary(){
        navigator.clipboard.writeText(document.getElementById("iq-summary").innerText);
    }
    </script>
    """

def create_summary_text(data: Dict[str, Any]) -> str:
    """Create plain text summary for copying."""
    lines = []
    
    # Title line
    lines.append(format_title_line(data))
    
    # Mission
    mission = data.get("mission", "")
    if mission:
        lines.append(f"Mission: {mission}")
    
    # Must-have
    must_have = data.get("must_have", [])
    if must_have:
        lines.append("Must-Have Stack:")
        for item in must_have[:6]:
            lines.append(f"  • {item}")
    
    # Nice-to-have
    nice_to_have = data.get("nice_to_have", [])
    if nice_to_have:
        lines.append("Nice-to-Haves:")
        for item in nice_to_have[:6]:
            lines.append(f"  • {item}")
    
    # Why it matters
    why_it_matters = data.get("why_it_matters", "")
    if why_it_matters:
        lines.append(f"Why It Matters: {why_it_matters}")
    
    # Technical questions
    technical_questions = data.get("technical_questions", [])
    if technical_questions:
        lines.append("Technical Questions:")
        for item in technical_questions[:6]:
            lines.append(f"  • {item}")
    
    # Behavioral questions
    behavioral_questions = data.get("behavioral_questions", [])
    if behavioral_questions:
        lines.append("Behavioral Questions:")
        for item in behavioral_questions[:6]:
            lines.append(f"  • {item}")
    
    # Talking points
    talking_points = data.get("talking_points", [])
    if talking_points:
        lines.append("Talking Points:")
        for item in talking_points[:6]:
            lines.append(f"  • {item}")
    
    # Company intel
    company_intel = data.get("company_intel", [])
    if company_intel:
        lines.append("Company Intel:")
        for item in company_intel[:3]:
            lines.append(f"  • {item}")
    
    # Smart questions
    smart_questions = data.get("smart_questions", [])
    if smart_questions:
        lines.append("Smart Questions:")
        for item in smart_questions[:5]:
            lines.append(f"  • {item}")
    
    # Role challenges
    role_challenges = data.get("role_challenges", [])
    if role_challenges:
        lines.append("Role Challenges:")
        for item in role_challenges[:5]:
            lines.append(f"  • {item}")
    
    # Success metrics
    success_metrics = data.get("success_metrics", [])
    if success_metrics:
        lines.append("Success Metrics:")
        for item in success_metrics[:5]:
            lines.append(f"  • {item}")
    
    # Salary context
    salary_context = data.get("salary_context", "")
    if salary_context:
        lines.append(f"Salary Context: {salary_context}")
    
    # Perks
    perks = data.get("perks", [])
    if perks:
        lines.append(f"Perks: {' • '.join(perks)}")
    
    return "\n\n".join(lines)

def to_html(data: Dict[str, Any]) -> str:
    """Build the complete No-BS job brief card."""
    
    # Handle data normalization
    if isinstance(data.get("must_have"), str):
        data["must_have"] = [data["must_have"]]
    if isinstance(data.get("nice_to_have"), str):
        data["nice_to_have"] = [data["nice_to_have"]]
    if isinstance(data.get("perks"), str):
        data["perks"] = [data["perks"]]
    if isinstance(data.get("red_flags"), str):
        data["red_flags"] = [data["red_flags"]]
    if isinstance(data.get("technical_questions"), str):
        data["technical_questions"] = [data["technical_questions"]]
    if isinstance(data.get("behavioral_questions"), str):
        data["behavioral_questions"] = [data["behavioral_questions"]]
    if isinstance(data.get("talking_points"), str):
        data["talking_points"] = [data["talking_points"]]
    if isinstance(data.get("company_intel"), str):
        data["company_intel"] = [data["company_intel"]]
    if isinstance(data.get("smart_questions"), str):
        data["smart_questions"] = [data["smart_questions"]]
    if isinstance(data.get("role_challenges"), str):
        data["role_challenges"] = [data["role_challenges"]]
    if isinstance(data.get("success_metrics"), str):
        data["success_metrics"] = [data["success_metrics"]]
    
    # Build sections
    title_line = format_title_line(data)
    mission_section = format_mission(data.get("mission", ""))
    must_have_section = format_must_have(data.get("must_have", []))
    nice_to_have_section = format_nice_to_have(data.get("nice_to_have", []))
    why_it_matters_section = format_why_it_matters(data.get("why_it_matters", ""))
    perks_section = format_perks(data.get("perks", []))
    red_flags_section = format_red_flags(data.get("red_flags", []))
    
    # Interview Query-style sections
    technical_questions_section = format_technical_questions(data.get("technical_questions", []))
    behavioral_questions_section = format_behavioral_questions(data.get("behavioral_questions", []))
    talking_points_section = format_talking_points(data.get("talking_points", []))
    company_intel_section = format_company_intel(data.get("company_intel", []))
    smart_questions_section = format_smart_questions(data.get("smart_questions", []))
    role_challenges_section = format_role_challenges(data.get("role_challenges", []))
    success_metrics_section = format_success_metrics(data.get("success_metrics", []))
    salary_context_section = format_salary_context(data.get("salary_context", ""))
    
    next_actions_section = format_next_actions(data.get("apply_link", ""))
    
    # Create plain text summary for copying
    summary_text = create_summary_text(data)
    
    # Build complete HTML
    html = f"""
    <div class='max-w-2xl mx-auto'>
        <div class='bg-white border border-gray-200 rounded-lg p-6 shadow-sm'>
            <h1 class='text-lg font-bold text-gray-900 mb-4'>{title_line}</h1>
            
            {hide_if_empty(mission_section)}
            {hide_if_empty(must_have_section)}
            {hide_if_empty(nice_to_have_section)}
            {hide_if_empty(why_it_matters_section)}
            {hide_if_empty(perks_section)}
            {hide_if_empty(red_flags_section)}
            
            {hide_if_empty(technical_questions_section)}
            {hide_if_empty(behavioral_questions_section)}
            {hide_if_empty(talking_points_section)}
            {hide_if_empty(company_intel_section)}
            {hide_if_empty(smart_questions_section)}
            {hide_if_empty(role_challenges_section)}
            {hide_if_empty(success_metrics_section)}
            {hide_if_empty(salary_context_section)}
            
            {next_actions_section}
        </div>
        
        <pre id="iq-summary" style="display: none;">{summary_text}</pre>
    </div>
    
    {create_copy_script()}
    """
    
    return html 