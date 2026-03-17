"""
Login Page Tests
Tests for authentication flow including success, failure, and validation.
"""
import time
import pytest
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


class TestLogin:
    def test_successful_login(self, browser):
        """Test login with correct credentials redirects to dashboard."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "username").send_keys("admin")
        browser.find_element(By.ID, "password").send_keys("admin123")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        assert "/dashboard" in browser.current_url

    def test_failed_login_wrong_password(self, browser):
        """Test login fails with wrong password."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "username").send_keys("admin")
        browser.find_element(By.ID, "password").send_keys("wrongpass")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        error = browser.find_element(By.ID, "error-message")
        assert "Invalid username or password" in error.text

    def test_failed_login_wrong_username(self, browser):
        """Test login fails with wrong username."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "username").send_keys("wronguser")
        browser.find_element(By.ID, "password").send_keys("admin123")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        error = browser.find_element(By.ID, "error-message")
        assert "Invalid username or password" in error.text

    def test_failed_login_empty_username(self, browser):
        """Test login fails when username is empty."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "password").send_keys("admin123")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        error = browser.find_element(By.ID, "error-message")
        assert "username" in error.text.lower()

    def test_failed_login_empty_password(self, browser):
        """Test login fails when password is empty."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "username").send_keys("admin")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        error = browser.find_element(By.ID, "error-message")
        assert "password" in error.text.lower()

    def test_failed_login_both_empty(self, browser):
        """Test login fails when both fields are empty."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        error = browser.find_element(By.ID, "error-message")
        assert "both" in error.text.lower() or "username" in error.text.lower()

    def test_error_message_appears_on_failed_login(self, browser):
        """Test that the error message element appears on failed login."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "username").send_keys("bad")
        browser.find_element(By.ID, "password").send_keys("bad")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        error = browser.find_element(By.ID, "error-message")
        assert error.is_displayed()

    def test_redirect_to_dashboard_after_login(self, browser):
        """Test that user lands on dashboard after successful login."""
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.ID, "username").send_keys("admin")
        browser.find_element(By.ID, "password").send_keys("admin123")
        browser.find_element(By.ID, "login-btn").click()
        time.sleep(1)
        assert "dashboard" in browser.current_url
        welcome = browser.find_element(By.ID, "welcome-message")
        assert "admin" in welcome.text.lower()
