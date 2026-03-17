"""
Match Scores Page Tests
Tests for match results display and filtering.
"""
import time
import pytest
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


class TestMatches:
    def test_match_results_load(self, logged_in_browser):
        """Test that match results load with data."""
        logged_in_browser.get(f"{BASE_URL}/matches")
        time.sleep(1)
        cards = logged_in_browser.find_elements(By.CSS_SELECTOR, ".match-card")
        assert len(cards) >= 5

    def test_filter_wins_only(self, logged_in_browser):
        """Test that Wins filter shows only won matches."""
        logged_in_browser.get(f"{BASE_URL}/matches")
        time.sleep(1)
        logged_in_browser.find_element(By.ID, "filter-wins").click()
        time.sleep(1)
        visible_cards = [
            c for c in logged_in_browser.find_elements(By.CSS_SELECTOR, ".match-card")
            if c.is_displayed()
        ]
        assert len(visible_cards) >= 1
        for card in visible_cards:
            assert card.get_attribute("data-result") == "won"

    def test_filter_losses_only(self, logged_in_browser):
        """Test that Losses filter shows only lost matches."""
        logged_in_browser.get(f"{BASE_URL}/matches")
        time.sleep(1)
        logged_in_browser.find_element(By.ID, "filter-losses").click()
        time.sleep(1)
        visible_cards = [
            c for c in logged_in_browser.find_elements(By.CSS_SELECTOR, ".match-card")
            if c.is_displayed()
        ]
        assert len(visible_cards) >= 1
        for card in visible_cards:
            assert card.get_attribute("data-result") == "lost"

    def test_back_to_dashboard_button(self, logged_in_browser):
        """Test that Back to Dashboard button works."""
        logged_in_browser.get(f"{BASE_URL}/matches")
        time.sleep(1)
        btn = logged_in_browser.find_element(By.ID, "back-btn")
        btn.click()
        time.sleep(1)
        assert "/dashboard" in logged_in_browser.current_url
