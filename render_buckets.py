from typing import Dict, List
import re

def render_buckets(bucket_facts: Dict[str, str], buckets: Dict[str, List[str]]) -> str:
    """Render markdown for intelligence buckets, hiding empty ones"""
    
    # Predefined bucket order and emojis
    bucket_order = [
        ("Team & Manager", "👥"),
        ("Tech Stack Snapshot", "⚡"),
        ("Business Context", "🏢"),
        ("Comp & Leveling", "💰"),
        ("Career Trajectory", "📈"),
        ("Culture/WLB", "🌟"),
        ("Interview Runway", "🎯"),
        ("Onboarding & Tooling", "🛠️"),
        ("Location/Remote", "🌍"),
        ("Strategic Risks", "⚠️")
    ]
    
    rendered_sections = []
    empty_bucket_count = 0
    
    for bucket_name, emoji in bucket_order:
        facts = buckets.get(bucket_name, [])
        
        # Skip empty buckets
        if not facts or all(not fact.strip() for fact in facts):
            empty_bucket_count += 1
            continue
        
        # Render bucket with limited bullets
        section = f"## {emoji} {bucket_name}\n\n"
        
        # Limit to 6 bullets per bucket
        limited_facts = facts[:6]
        
        for fact in limited_facts:
            if fact.strip():
                # Ensure fact ends with source link
                fact = fact.strip()
                if not fact.endswith('🔗'):
                    # Add generic source link if missing
                    if 'http' not in fact:
                        fact += " 🔗"
                
                section += f"- {fact}\n"
        
        section += "\n"
        rendered_sections.append(section)
    
    # Log empty buckets for metrics
    if empty_bucket_count > 0:
        from metrics import log_metric
        log_metric("bucket_missing", {"empty_buckets": empty_bucket_count})
    
    # Only return content if we have non-empty buckets
    if rendered_sections:
        header = "# 🧠 Deep Intelligence Analysis\n\n"
        return header + "".join(rendered_sections)
    else:
        return ""

def format_bullet_with_source(text: str, source_url: str = "") -> str:
    """Format a bullet point with proper source link"""
    text = text.strip()
    
    # If already has source link, return as-is
    if '🔗' in text:
        return text
    
    # Add source link
    if source_url:
        return f"{text} 🔗 {source_url}"
    else:
        return f"{text} 🔗"

def _format_bullet(item: str) -> str:
    """Format individual bullet with emoji and source links"""
    
    # Extract URLs and add link emoji
    if "🔗" in item:
        return item
    elif "http" in item:
        # Add link emoji for URLs
        item = re.sub(r'(https?://[^\s]+)', r'🔗 \1', item)
    
    # Add context emoji based on content
    if any(keyword in item.lower() for keyword in ["manager", "team", "hiring"]):
        return f"👥 {item}"
    elif any(keyword in item.lower() for keyword in ["salary", "comp", "pay"]):
        return f"💰 {item}"
    elif any(keyword in item.lower() for keyword in ["culture", "rating"]):
        return f"🏢 {item}"
    elif any(keyword in item.lower() for keyword in ["stack", "tech", "tools"]):
        return f"⚙️ {item}"
    elif any(keyword in item.lower() for keyword in ["news", "business"]):
        return f"📈 {item}"
    else:
        return f"📋 {item}" 