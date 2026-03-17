"""
Protected Routes / Security Tests
Tests that unauthenticated users cannot access protected pages.
"""
import time
import pytest
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


class TestSecurity:
    def test_dashboard_redirects_to_login_without_auth(self, browser):
        """Test that /dashboard redirects to login when not logged in."""
        browser.get(f"{BASE_URL}/dashboard")
        time.sleep(1)
        assert "/login" in browser.current_url

    def test_players_redirects_to_login_without_auth(self, browser):
        """Test that /players redirects to login when not logged in."""
        browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        assert "/login" in browser.current_url

    def test_matches_redirects_to_login_without_auth(self, browser):
        """Test that /matches redirects to login when not logged in."""
        browser.get(f"{BASE_URL}/matches")
        time.sleep(1)
        assert "/login" in browser.current_url

    def test_after_logout_dashboard_redirects(self, logged_in_browser):
        """Test that after logout, accessing dashboard redirects to login."""
        # First verify we are on dashboard
        assert "/dashboard" in logged_in_browser.current_url

        # Logout
        logged_in_browser.get(f"{BASE_URL}/logout")
        time.sleep(1)

        # Try accessing dashboard again
        logged_in_browser.get(f"{BASE_URL}/dashboard")
        time.sleep(1)
        assert "/login" in logged_in_browser.current_url
