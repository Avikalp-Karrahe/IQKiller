from typing import Dict, List

def map_facts(facts: Dict[str, str]) -> Dict[str, List[str]]:
    """Map enriched facts into 10 predefined buckets"""
    
    # Initialize all 10 buckets (must exist even if empty)
    buckets = {
        "Team & Manager": [],
        "Tech Stack Snapshot": [],
        "Business Context": [],
        "Comp & Leveling": [],
        "Career Trajectory": [],
        "Culture/WLB": [],
        "Interview Runway": [],
        "Onboarding & Tooling": [],
        "Location/Remote": [],
        "Strategic Risks": []
    }
    
    # Map facts to appropriate buckets
    for key, value in facts.items():
        if not value or value.strip() == "":
            continue
            
        # Team & Manager bucket
        if any(keyword in key.lower() for keyword in ["manager", "team", "hiring"]):
            buckets["Team & Manager"].append(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Tech Stack bucket
        elif any(keyword in key.lower() for keyword in ["stack", "tools", "github", "tech"]):
            buckets["Tech Stack Snapshot"].append(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Business Context bucket
        elif any(keyword in key.lower() for keyword in ["news", "business", "company", "domain"]):
            buckets["Business Context"].append(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Compensation bucket
        elif any(keyword in key.lower() for keyword in ["salary", "comp", "levels", "pay"]):
            buckets["Comp & Leveling"].append(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Culture/WLB bucket  
        elif any(keyword in key.lower() for keyword in ["culture", "blind", "rating", "wlb", "work"]):
            buckets["Culture/WLB"].append(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Location/Remote bucket
        elif any(keyword in key.lower() for keyword in ["location", "remote", "office", "hybrid"]):
            buckets["Location/Remote"].append(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Default to Business Context for unmatched items
        else:
            buckets["Business Context"].append(f"**{key.replace('_', ' ').title()}**: {value}")
    
    # Remove empty buckets to hide them in the UI
    buckets = {k: v for k, v in buckets.items() if v}
    
    return buckets 