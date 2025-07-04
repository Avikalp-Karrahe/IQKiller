import asyncio
import pytest
from text_extractor import extract_batch

@pytest.mark.asyncio
async def test_extract_batch_storypros():
    """Test that extract_batch correctly extracts StoryPros data."""
    storypros_jd = """
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
    
    # Run extraction
    job_core = await extract_batch(storypros_jd)
    
    # Verify expected data
    assert job_core.company == "StoryPros"
    assert job_core.salary_low == 160000  # $160K in the JD
    assert job_core.role is not None  # Should extract some role
    assert "AI" in job_core.role or "Engineer" in job_core.role  # Should be AI Engineer
    
    # Additional checks
    assert job_core.location is not None
    assert "Los Angeles" in job_core.location or "LA" in job_core.location

if __name__ == "__main__":
    asyncio.run(test_extract_batch_storypros()) 