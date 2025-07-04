"""
Tests for render_cards module.
"""
import pytest
from render_cards import at_a_glance_card, badge, bullets, to_html


def test_badge_adds_google_source():
    """Test that badge adds '(from Google)' when field is in source_map."""
    source_map = {"salary_low": "google"}
    result = badge("$120,000", "salary_low", source_map)
    assert "(from Google)" in result
    assert "120,000" in result


def test_badge_no_source():
    """Test that badge doesn't add annotation when field not in source_map."""
    source_map = {}
    result = badge("$120,000", "salary_low", source_map)
    assert "(from Google)" not in result
    assert result == "$120,000"


def test_bullets_creates_list():
    """Test that bullets creates proper HTML list."""
    items = ["Python", "Machine Learning", "SQL"]
    result = bullets(items)
    assert "<ul" in result
    assert "<li" in result
    assert "Python" in result
    assert "SQL" in result


def test_at_a_glance_card_basic():
    """Test at-a-glance card contains key job info."""
    job_data = {
        "company": "TechCorp",
        "role": "Senior Engineer",
        "location": "San Francisco",
        "seniority": "Senior"
    }
    source_map = {}
    
    result = at_a_glance_card(job_data, source_map)
    
    assert "TechCorp" in result
    assert "Senior Engineer" in result
    assert "San Francisco" in result
    assert "Senior" in result
    assert "bg-white" in result  # Tailwind class


def test_to_html_complete():
    """Test full HTML generation with sample data."""
    result_data = {
        "enriched": {
            "company": "TestCorp",
            "role": "Software Engineer",
            "location": "Remote",
            "mission": "Building the future",
            "source_map": {}
        },
        "qa_content": "Must-have skills:\n- Python\n- SQL",
        "critique_content": "Red flags:\n- Long hours mentioned"
    }
    
    html = to_html(result_data)
    
    assert "TestCorp" in html
    assert "Software Engineer" in html
    assert "Building the future" in html
    assert "<script>" in html  # JavaScript included
    assert "copyToClipboard" in html


def test_empty_data_handling():
    """Test handling of missing or empty data."""
    result_data = {"enriched": {}, "qa_content": "", "critique_content": ""}
    
    html = to_html(result_data)
    
    # Should still generate basic structure without errors
    assert "Unknown" in html  # Fallback values
    assert "<script>" in html 