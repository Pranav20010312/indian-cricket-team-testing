"""
Dashboard Tests
Tests for the main dashboard page after login.
"""
import time
import pytest
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


class TestDashboard:
    def test_dashboard_loads_after_login(self, logged_in_browser):
        """Test that dashboard page loads successfully after login."""
        assert "/dashboard" in logged_in_browser.current_url

    def test_welcome_message_shows_username(self, logged_in_browser):
        """Test that welcome message displays the correct username."""
        welcome = logged_in_browser.find_element(By.ID, "welcome-message")
        assert "admin" in welcome.text.lower()

    def test_view_players_button_exists(self, logged_in_browser):
        """Test that View Players button exists and is clickable."""
        btn = logged_in_browser.find_element(By.ID, "view-players-btn")
        assert btn.is_displayed()
        assert btn.is_enabled()

    def test_view_matches_button_exists(self, logged_in_browser):
        """Test that View Match Scores button exists and is clickable."""
        btn = logged_in_browser.find_element(By.ID, "view-matches-btn")
        assert btn.is_displayed()
        assert btn.is_enabled()

    def test_view_stats_button_exists(self, logged_in_browser):
        """Test that View Team Stats button exists and is clickable."""
        btn = logged_in_browser.find_element(By.ID, "view-stats-btn")
        assert btn.is_displayed()
        assert btn.is_enabled()

    def test_logout_button_exists_and_works(self, logged_in_browser):
        """Test that Logout button exists and signs the user out."""
        btn = logged_in_browser.find_element(By.ID, "logout-btn")
        assert btn.is_displayed()
        btn.click()
        time.sleep(1)
        assert "/login" in logged_in_browser.current_url

    def test_players_button_navigates(self, logged_in_browser):
        """Test clicking View Players navigates to players page."""
        logged_in_browser.find_element(By.ID, "view-players-btn").click()
        time.sleep(1)
        assert "/players" in logged_in_browser.current_url

    def test_matches_button_navigates(self, logged_in_browser):
        """Test clicking View Match Scores navigates to matches page."""
        logged_in_browser.find_element(By.ID, "view-matches-btn").click()
        time.sleep(1)
        assert "/matches" in logged_in_browser.current_url
