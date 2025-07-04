import pytest
from micro.scrape import ScrapeMicroFunction, extract_preview_from_html, canonicalise


def test_canonicalise_linkedin_url():
    """Test URL canonicalization for LinkedIn"""
    url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4237922966"
    canonical = canonicalise(url)
    assert canonical == "https://www.linkedin.com/jobs/view/4237922966"


def test_extract_preview_from_microsoft_url():
    """Test preview extraction from Microsoft careers HTML"""
    html = """
    <html>
    <head>
        <title>Applied Scientist II | Microsoft Careers</title>
    </head>
    <body>
        <script>{"jobLocation": "Redmond, WA"}</script>
    </body>
    </html>
    """
    url = "https://jobs.careers.microsoft.com/global/en/job/1829758/"
    
    preview = extract_preview_from_html(html, url)
    
    assert preview['company'] == 'Microsoft'
    assert preview['role'] == 'Applied Scientist II'
    assert preview['location'] == 'Redmond, WA'


def test_extract_preview_from_linkedin_html():
    """Test preview extraction from LinkedIn job HTML"""
    html = """
    <html>
    <head>
        <title>Software Engineer | LinkedIn Jobs</title>
    </head>
    <body>
        <h1 class="job-details-jobs-unified-top-card__job-title">Software Engineer</h1>
        <span class="job-details-jobs-unified-top-card__company-name">Parambil Technologies</span>
        <span class="job-details-jobs-unified-top-card__bullet">San Francisco, CA</span>
    </body>
    </html>
    """
    url = "https://www.linkedin.com/jobs/view/4237922966"
    
    preview = extract_preview_from_html(html, url)
    
    assert preview['company'] == 'Parambil Technologies'
    assert preview['role'] == 'Software Engineer'
    assert preview['location'] == 'San Francisco, CA'


def test_scrape_micro_function_with_text_input():
    """Test scraping micro function with direct text input"""
    scraper = ScrapeMicroFunction()
    
    text_input = """
    Senior Data Scientist
    Netflix Inc.
    Los Angeles, CA
    
    We are looking for a senior data scientist to join our team...
    """
    
    result = scraper.run({'raw_input': text_input})
    
    assert result['success'] is True
    assert 'preview' in result
    assert result['preview']['company'] != 'Not specified'  # Should extract Netflix
    assert 'scientist' in result['preview']['role'].lower()


def test_scrape_micro_function_error_handling():
    """Test error handling for invalid inputs"""
    scraper = ScrapeMicroFunction()
    
    # Test empty input
    result = scraper.run({'raw_input': ''})
    assert result['success'] is False
    assert 'error' in result
    
    # Test invalid URL
    result = scraper.run({'raw_input': 'https://invalid-domain-that-does-not-exist.com'})
    assert result['success'] is False or 'error' in result


def test_preview_card_parambil_link():
    """Assert preview card can be parsed for Parambil company link"""
    html = """
    <html>
    <body>
        <span class="job-details-jobs-unified-top-card__company-name">Parambil Technologies</span>
        <h1 class="job-details-jobs-unified-top-card__job-title">Senior Software Engineer</h1>
        <span class="job-details-jobs-unified-top-card__bullet">Remote</span>
    </body>
    </html>
    """
    
    url = "https://www.linkedin.com/jobs/view/123456"
    preview = extract_preview_from_html(html, url)
    
    # Verify Parambil company is extracted correctly
    assert 'Parambil' in preview['company']
    assert preview['role'] == 'Senior Software Engineer'
    assert preview['location'] == 'Remote'


def test_linkedin_auth_error_detection():
    """Test LinkedIn authentication error detection"""
    from micro.scrape import LinkedInAuthError
    
    # This would be tested in integration with actual LinkedIn URLs
    # For now, just ensure the exception class exists and can be imported
    assert LinkedInAuthError is not None


if __name__ == "__main__":
    pytest.main([__file__]) 