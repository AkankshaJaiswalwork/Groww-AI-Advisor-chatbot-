import os
import sys
import json
import pytest

# Add phase_1 to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_1"))

from scraper import GrowwScraper
from models import MutualFund

def test_scraper_valid_fund():
    scraper = GrowwScraper()
    test_slug = "nippon-india-small-cap-fund-direct-growth"
    
    # Run the scraper
    result = scraper.scrape_fund(test_slug)
    
    # Assert result structure
    assert result.success is True
    assert result.fund_id == test_slug
    assert isinstance(result.data, MutualFund)
    assert "Nippon India Small Cap" in result.data.fund_name
    
    # Check if the structured JSON file was written
    structured_file_path = os.path.join(scraper.data_dir, f"{test_slug}_structured.json")
    assert os.path.exists(structured_file_path)
    
    # Load structured JSON and assert keys
    with open(structured_file_path, "r") as f:
        data = json.load(f)
        assert data["fund_id"] == test_slug
        assert "Nippon India Small Cap" in data["fund_name"]
        assert len(data["holdings"]) > 0
