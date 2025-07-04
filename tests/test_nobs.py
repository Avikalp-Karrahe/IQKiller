import asyncio
import pytest
from text_extractor import extract_nobs

# StoryPros JD sample for testing
STORYPROS_JD = """
StoryPros logo
StoryPros
Share
Show more options
Artificial Intelligence Engineer
Los Angeles Metropolitan Area · 1 week ago · Over 100 applicants
Promoted by hirer · Actively reviewing applicants

$160K/yr - $190K/yr
Matches your job preferences, minimum pay preference is 80000.

Hybrid
Matches your job preferences, workplace type is Hybrid.

Full-time
Matches your job preferences, job type is Full-time.

About the job
We're looking for an experienced AI Engineer who thrives at the intersection of machine learning, automation, and creative systems. You'll help us design, develop, and optimize AI-powered marketing pipelines that operate with minimal human input.

Key Responsibilities

Build and deploy autonomous AI workflows using LLMs like GPT-4o, Claude, and Mistral
Design automation pipelines for content, video, and campaign execution
Integrate third-party tools and APIs (Zapier, Make, Retool, etc.) into agent stacks
Optimize performance of multi-agent orchestration using frameworks like LangChain, AutoGen, or CrewAI
Collaborate with the creative and strategy teams to ensure alignment between output quality and brand goals
Conduct ongoing testing and iteration to improve reliability, accuracy, and ROI of agent-based systems

Required Qualifications

2+ years experience working with LLMs and generative AI tools
Proficiency in Python and API integrations
Experience with agent frameworks (e.g., LangChain, AutoGen, CrewAI)
Strong understanding of prompt engineering, fine-tuning, and model optimization
Ability to work autonomously in a fast-paced startup environment
Based in the Los Angeles area or available to work Pacific Time hours (remote-friendly)

Preferred Skills

Experience with low-code platforms like Zapier, Notion, Make, or Airtable
Knowledge of AI video, synthetic voice, or content editing tools
Familiarity with marketing automation, lead generation, or creative operations

Compensation and Benefits

Salary: $160,000 – $190,000/year (depending on experience)
Performance bonuses
Equity options
Remote flexibility
Access to cutting-edge AI tools and hardware
Opportunity to help shape the future of AI-driven marketing
"""

@pytest.mark.asyncio
async def test_extract_nobs_storypros():
    """Test that extract_nobs correctly extracts StoryPros data."""
    data = await extract_nobs(STORYPROS_JD)
    
    # Test company extraction
    assert data["company"] == "StoryPros"
    
    # Test title extraction
    assert "AI Engineer" in data.get("title", "") or "Artificial Intelligence Engineer" in data.get("title", "")
    
    # Test salary extraction
    assert "$160" in data.get("salary_band", "") or "160" in str(data.get("salary_band", ""))
    
    # Test location extraction
    assert "Los Angeles" in data.get("location", "")
    
    # Test work type extraction
    assert "Hybrid" in data.get("work_type", "") or "hybrid" in data.get("work_type", "").lower()

@pytest.mark.asyncio
async def test_extract_nobs_must_have_skills():
    """Test extraction of must-have skills from StoryPros JD."""
    data = await extract_nobs(STORYPROS_JD)
    
    # Check if must_have contains relevant skills
    must_have = data.get("must_have", [])
    if isinstance(must_have, str):
        must_have = [must_have]
    
    # Should extract at least some key skills
    skills_text = " ".join(must_have).lower()
    assert any(skill in skills_text for skill in ["python", "llm", "ai", "machine learning", "api"])

@pytest.mark.asyncio
async def test_extract_nobs_mission():
    """Test mission extraction from StoryPros JD."""
    data = await extract_nobs(STORYPROS_JD)
    
    mission = data.get("mission", "")
    # Should extract mission-related content
    assert len(mission) > 0
    # Should be within word limit (≤25 words)
    if mission:
        assert len(mission.split()) <= 26  # Allow slight buffer

@pytest.mark.asyncio
async def test_extract_nobs_perks():
    """Test perks extraction from StoryPros JD."""
    data = await extract_nobs(STORYPROS_JD)
    
    perks = data.get("perks", [])
    if isinstance(perks, str):
        perks = [perks]
    
    # Should extract compensation and benefits
    perks_text = " ".join(perks).lower()
    if perks_text:
        assert any(perk in perks_text for perk in ["equity", "bonus", "remote", "tools", "hardware"])

@pytest.mark.asyncio
async def test_extract_nobs_empty_input():
    """Test extract_nobs with empty input."""
    data = await extract_nobs("")
    
    # Should return fallback data
    assert "company" in data
    assert "title" in data

@pytest.mark.asyncio
async def test_extract_nobs_array_limits():
    """Test that arrays are limited to ≤6 items."""
    data = await extract_nobs(STORYPROS_JD)
    
    # Check array field limits
    for field in ["must_have", "nice_to_have", "perks"]:
        field_data = data.get(field, [])
        if isinstance(field_data, list):
            assert len(field_data) <= 6, f"{field} has {len(field_data)} items, should be ≤6"

@pytest.mark.asyncio
async def test_extract_nobs_interview_query_fields():
    """Test extraction of Interview Query-style fields."""
    data = await extract_nobs(STORYPROS_JD)
    
    # Test technical_questions field
    technical_questions = data.get("technical_questions", [])
    if technical_questions:
        if isinstance(technical_questions, list):
            assert len(technical_questions) <= 6, f"technical_questions has {len(technical_questions)} items, should be ≤6"
        else:
            assert isinstance(technical_questions, str), "technical_questions should be string or list"
    
    # Test behavioral_questions field
    behavioral_questions = data.get("behavioral_questions", [])
    if behavioral_questions:
        if isinstance(behavioral_questions, list):
            assert len(behavioral_questions) <= 6, f"behavioral_questions has {len(behavioral_questions)} items, should be ≤6"
        else:
            assert isinstance(behavioral_questions, str), "behavioral_questions should be string or list"
    
    # Test talking_points field
    talking_points = data.get("talking_points", [])
    if talking_points:
        if isinstance(talking_points, list):
            assert len(talking_points) <= 6, f"talking_points has {len(talking_points)} items, should be ≤6"
        else:
            assert isinstance(talking_points, str), "talking_points should be string or list"
    
    # Test company_intel field
    company_intel = data.get("company_intel", [])
    if company_intel:
        if isinstance(company_intel, list):
            assert len(company_intel) <= 6, f"company_intel has {len(company_intel)} items, should be ≤6"
        else:
            assert isinstance(company_intel, str), "company_intel should be string or list"
    
    # Test smart_questions field
    smart_questions = data.get("smart_questions", [])
    if smart_questions:
        if isinstance(smart_questions, list):
            assert len(smart_questions) <= 6, f"smart_questions has {len(smart_questions)} items, should be ≤6"
        else:
            assert isinstance(smart_questions, str), "smart_questions should be string or list"
    
    # Test role_challenges field
    role_challenges = data.get("role_challenges", [])
    if role_challenges:
        if isinstance(role_challenges, list):
            assert len(role_challenges) <= 6, f"role_challenges has {len(role_challenges)} items, should be ≤6"
        else:
            assert isinstance(role_challenges, str), "role_challenges should be string or list"
    
    # Test success_metrics field
    success_metrics = data.get("success_metrics", [])
    if success_metrics:
        if isinstance(success_metrics, list):
            assert len(success_metrics) <= 6, f"success_metrics has {len(success_metrics)} items, should be ≤6"
        else:
            assert isinstance(success_metrics, str), "success_metrics should be string or list"
    
    # Test salary_context field
    salary_context = data.get("salary_context", "")
    if salary_context:
        assert isinstance(salary_context, str), "salary_context should be string"
        assert len(salary_context) > 0, "salary_context should not be empty if present" 