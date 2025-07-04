#!/usr/bin/env python3
"""Test job description text extraction workflow"""

import pytest
from micro.scrape import ScrapeMicroFunction


def test_shields_group_extraction():
    """Test extraction from the provided Shields Group JD sample"""
    
    sample_jd = """Shields Group Search logo
Shields Group Search
Share
Show more options
Junior Machine Learning Engineer
New York, NY · Reposted 2 weeks ago · Over 100 applicants
Promoted by hirer · Actively reviewing applicants


 $130K/yr - $170K/yr
Matches your job preferences, minimum pay preference is 80000.

 On-site
Matches your job preferences, workplace type is On-site.

 Full-time
Matches your job preferences, job type is Full-time.

Easy Apply

Save
Save Junior Machine Learning Engineer at Shields Group Search
Junior Machine Learning Engineer
Shields Group Search · New York, NY (On-site)

Easy Apply

Save
Save Junior Machine Learning Engineer at Shields Group Search
Show more options
Your AI-powered job assessment


Am I a good fit?

Tailor my resume

How can I best position myself?

Meet the hiring team
Thomas Shields
Thomas Shields  
 3rd
Executive Search | Investor | Strategic Advisor
Job poster

Message
About the job
Junior Machine Learning / Computer Vision Engineer



About the Company:

Our client is a pre-seed startup that is ready to bring on a Junior Machine Learning engineer to supercharge their core product. They are building the next-generation operating system for commercial HVAC suppliers and contractors. In just five months, they've launched V1 of their first product and grown revenue 10x. Backed by top US VCs and top HVAC industry angels, their goal is to perfect our first product and continue scaling rapidly through 2025.


Location Requirements:

This position requires a full-time in office work arrangement in New York City. Candidates must be based in NYC.



Required Qualifications

Bachelor's or Master's degree in Computer Science, Electrical Engineering, or other relevant field with focus on machine learning.
0-3 years experience as an ML focused engineer
Coding experience with Python.
Experience developing and adapting model architectures with PyTorch.
Experience with deep learning for computer vision applications, especially semantic segmentation or object detection.
Experience with production-level code development and optimization.
Experience with distributed/parallel training.
Experience with deployment and monitoring pipelines for ML systems.
Experience with model development on a major cloud platform (GCP, AWS etc.)
Experience constructing and maintaining quality datasets (experiences with data cleaning, data reformatting, bootstrapping synthetic datasets, and creating annotation tasks are all valued).
Experience with OpenCV or equivalent libraries.
Proven ability to implement and adapt techniques or architectures from academic or industry literature.


Nice to Have

Experience building continual learning or periodic retraining pipelines for production CV applications.
Experience with active learning setups.
Experience using OCR libraries or APIs.
Ability to implement CV algorithms in a low-level language (C).
Experience writing CUDA kernel programs.
Strong understanding of traditional CV techniques - (component analysis, template matching, key point matching, etc.)
Published research developing SOTA computer vision models.


Compensation and Benefits

Salary: $130-170K, dependent on experience
Equity: Meaningful equity package, commensurate with experience
Benefits: Comprehensive medical, dental, and vision coverage
Perks: Free lunches and dinners provided


This is a salaried, onsite role located in New York City's beautiful Flatiron district, just minutes away from Madison Square Park and Union Square. Working onsite offers invaluable opportunities for real-time collaboration, creative problem-solving, and building strong connections within their talented and dynamic team. You'll be at the heart of fast-paced operations, actively contributing to a culture that values engagement, growth, and teamwork.


This is a unique opportunity to join a high-potential startup in a specialized industry and make a real impact on product and company direction. If you're passionate about using technology to streamline and modernize the construction sales process and are based in NYC, we'd love to hear from you!
"""

    # Test the extraction
    result = ScrapeMicroFunction.from_text(sample_jd)
    
    # Assert company extraction
    assert result['company'] == "Shields Group Search", f"Expected 'Shields Group Search', got '{result['company']}'"
    
    # Assert role extraction
    assert result['role'] == "Junior Machine Learning Engineer", f"Expected 'Junior Machine Learning Engineer', got '{result['role']}'"
    
    # Assert location extraction
    assert "New York" in result['location'], f"Expected location to contain 'New York', got '{result['location']}'"


def test_scrape_microfunction_text_processing():
    """Test the ScrapeMicroFunction handles text input correctly"""
    
    scraper = ScrapeMicroFunction()
    
    test_text = "Software Engineer at TechCorp\nSan Francisco, CA\nWe are looking for a software engineer..."
    
    result = scraper.run({"raw_input": test_text})
    
    # Should succeed with text input
    assert result['success'] is True
    assert result['content'] == test_text
    assert result['scraped_text'] == test_text
    assert 'preview' in result
    

def test_url_canonicalization():
    """Test URL canonicalization for LinkedIn URLs"""
    from micro.scrape import canonicalise
    
    # Test currentJobId conversion
    linkedin_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=1234567890"
    canonical = canonicalise(linkedin_url)
    assert canonical == "https://www.linkedin.com/jobs/view/1234567890"
    
    # Test /jobs/view/ URLs remain unchanged
    view_url = "https://www.linkedin.com/jobs/view/1234567890"
    canonical = canonicalise(view_url)
    assert canonical == "https://www.linkedin.com/jobs/view/1234567890"
    
    # Test non-LinkedIn URLs remain unchanged
    other_url = "https://jobs.microsoft.com/job/123456"
    canonical = canonicalise(other_url)
    assert canonical == other_url


if __name__ == "__main__":
    test_shields_group_extraction()
    test_scrape_microfunction_text_processing()
    test_url_canonicalization()
    print("✅ All tests passed!") 