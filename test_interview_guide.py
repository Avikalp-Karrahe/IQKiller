#!/usr/bin/env python3
"""
Test script for the personalized interview guide functionality.
Demonstrates the complete pipeline: Resume + Job → Gap Analysis → Personalized Guide
"""

import asyncio
import json
from interview_orchestrator import create_personalized_interview_guide

# Sample resume data
SAMPLE_RESUME = """
John Smith
Software Engineer
john.smith@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johnsmith | GitHub: github.com/johnsmith

PROFESSIONAL SUMMARY
Experienced full-stack software engineer with 3+ years developing web applications using Python, JavaScript, and cloud technologies. Strong background in API development, database design, and agile methodologies.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, SQL, HTML/CSS
Frameworks: Django, React, Node.js, Express
Databases: PostgreSQL, MongoDB, Redis
Cloud/DevOps: AWS (EC2, S3, RDS), Docker, Git, CI/CD
Tools: VS Code, Postman, Jira, Slack

PROFESSIONAL EXPERIENCE

Software Engineer | TechCorp | Jan 2021 - Present
• Developed and maintained 5+ web applications serving 10,000+ users daily
• Built RESTful APIs using Python/Django with 99.9% uptime
• Implemented responsive front-end components using React and modern JavaScript
• Collaborated with cross-functional teams in Agile/Scrum environment
• Reduced database query time by 40% through optimization and indexing

Junior Developer | StartupXYZ | Jun 2020 - Dec 2020
• Created feature-rich web application using MERN stack
• Integrated third-party APIs and payment processing systems
• Participated in code reviews and maintained coding standards
• Deployed applications to AWS cloud infrastructure

PROJECTS

E-commerce Platform (2023)
• Built full-stack e-commerce solution with Django backend and React frontend
• Implemented user authentication, shopping cart, and payment integration
• Technologies: Python, Django, React, PostgreSQL, Stripe API

Task Management App (2022)
• Developed collaborative task management application
• Features include real-time updates, file uploads, and team collaboration
• Technologies: Node.js, Express, MongoDB, Socket.io

EDUCATION
Bachelor of Science in Computer Science
State University | 2020
GPA: 3.7/4.0
Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering
"""

# Sample job posting
SAMPLE_JOB = """
Senior Full Stack Engineer
DataFlow Inc.
San Francisco, CA | Remote

About DataFlow Inc.
We're a fast-growing fintech startup building next-generation data analytics tools for financial institutions. Our platform processes billions of transactions daily and helps banks make better decisions through AI-powered insights.

Role Overview
We're seeking a Senior Full Stack Engineer to join our engineering team and help scale our platform to handle growing demand. You'll work on both frontend and backend systems, collaborate with data scientists, and contribute to architectural decisions.

Key Responsibilities
• Design and implement scalable web applications using modern technologies
• Build robust APIs and microservices to support our data platform
• Collaborate with product and design teams to deliver exceptional user experiences
• Optimize application performance and ensure high availability
• Mentor junior developers and contribute to engineering best practices
• Work with data engineering team to build data visualization tools

Required Qualifications
• 4+ years of experience in full-stack web development
• Strong proficiency in Python and modern JavaScript frameworks
• Experience with cloud platforms (AWS, GCP, or Azure)
• Knowledge of relational databases and SQL optimization
• Familiarity with containerization (Docker) and CI/CD pipelines
• Experience with agile development methodologies
• Bachelor's degree in Computer Science or related field

Preferred Qualifications
• Experience with financial/fintech applications
• Knowledge of data visualization libraries (D3.js, Chart.js)
• Familiarity with machine learning concepts
• Experience with Kubernetes and microservices architecture
• Previous experience at a startup or high-growth company

Technical Stack
• Backend: Python, Django/Flask, PostgreSQL, Redis
• Frontend: React, TypeScript, Next.js
• Infrastructure: AWS, Docker, Kubernetes
• Data: Apache Airflow, Spark, Snowflake

Compensation & Benefits
• Competitive salary: $140,000 - $180,000
• Equity package
• Comprehensive health, dental, and vision insurance
• Flexible PTO policy
• $2,000 annual learning and development budget
• Remote-first culture with optional office access

Why Join DataFlow?
• Work on cutting-edge fintech technology
• High-impact role in a fast-growing company
• Collaborative and learning-focused culture
• Opportunity to shape product direction
• Competitive compensation and equity upside
"""

async def test_interview_guide_generation():
    """Test the complete interview guide generation pipeline"""
    
    print("🚀 Testing Personalized Interview Guide Generation")
    print("=" * 60)
    
    print("\n📝 Resume Summary:")
    print(f"- Length: {len(SAMPLE_RESUME)} characters")
    print("- Skills: Python, JavaScript, React, Django, AWS")
    print("- Experience: 3+ years full-stack development")
    
    print("\n🎯 Job Summary:")
    print("- Role: Senior Full Stack Engineer at DataFlow Inc.")
    print("- Requirements: 4+ years, Python, JavaScript, Cloud, Fintech")
    print("- Salary: $140k-$180k")
    
    print("\n⚡ Generating Interview Guide...")
    print("-" * 40)
    
    # Generate the guide
    result = create_personalized_interview_guide(SAMPLE_RESUME, SAMPLE_JOB)
    
    if result.get("success"):
        print("✅ Guide generation successful!")
        
        # Display metrics
        gap_analysis = result.get("gap_analysis", {})
        match_score = gap_analysis.get("match_score", 0)
        processing_time = result.get("processing_time", 0)
        guide_length = len(result.get("rendered_guide", ""))
        
        print(f"\n📊 Results:")
        print(f"- Match Score: {match_score}%")
        print(f"- Processing Time: {processing_time:.2f} seconds")
        print(f"- Guide Length: {guide_length} characters")
        
        # Display gap analysis summary
        summary = gap_analysis.get("summary", "")
        if summary:
            print(f"\n🎯 Gap Analysis: {summary}")
        
        # Display skills breakdown
        skills_map = gap_analysis.get("skills_map", {})
        if skills_map:
            print(f"\n💪 Strengths: {skills_map.get('strong', [])[:3]}")
            print(f"📚 Areas to Study: {skills_map.get('gaps', [])[:3]}")
        
        # Show first part of rendered guide
        rendered_guide = result.get("rendered_guide", "")
        if rendered_guide:
            print(f"\n📄 Generated Guide Preview:")
            print("-" * 40)
            preview = rendered_guide[:500] + "..." if len(rendered_guide) > 500 else rendered_guide
            print(preview)
            print("-" * 40)
        
        # Save full guide to file
        with open("sample_interview_guide.md", "w") as f:
            f.write(rendered_guide)
        print(f"\n💾 Full guide saved to: sample_interview_guide.md")
        
    else:
        print("❌ Guide generation failed!")
        error_msg = result.get("error", "Unknown error")
        print(f"Error: {error_msg}")
        
        # Show debug info if available
        if "data" in result:
            print("\n🔍 Debug Information:")
            print(json.dumps(result["data"], indent=2))

def test_validation():
    """Test input validation"""
    
    print("\n🧪 Testing Input Validation")
    print("-" * 30)
    
    # Test empty inputs
    result1 = create_personalized_interview_guide("", SAMPLE_JOB)
    print(f"Empty resume: {'✅ Caught' if not result1.get('success') else '❌ Missed'}")
    
    result2 = create_personalized_interview_guide(SAMPLE_RESUME, "")
    print(f"Empty job: {'✅ Caught' if not result2.get('success') else '❌ Missed'}")
    
    # Test short inputs
    result3 = create_personalized_interview_guide("Short resume", SAMPLE_JOB)
    print(f"Short resume: {'✅ Caught' if not result3.get('success') else '❌ Missed'}")
    
    result4 = create_personalized_interview_guide(SAMPLE_RESUME, "Short job")
    print(f"Short job: {'✅ Caught' if not result4.get('success') else '❌ Missed'}")

async def main():
    """Main test function"""
    
    print("🎯 IQKiller Personalized Interview Guide Test Suite")
    print("=" * 60)
    
    # Run main test
    await test_interview_guide_generation()
    
    # Run validation tests
    test_validation()
    
    print("\n🎉 Test suite completed!")
    print("\nTo view the full generated guide, open: sample_interview_guide.md")

if __name__ == "__main__":
    asyncio.run(main()) 