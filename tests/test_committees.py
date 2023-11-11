from philadelphia_scraper.committees import repair_names
import pytest

def test_repair_names():
    assert repair_names(["Joe James", "Sally Smith"]) == ["Joe James", "Sally Smith"] 
    assert repair_names(["Joe James, Jr.", "Sally Smith"]) == ["Joe James, Jr.", "Sally Smith"] 

