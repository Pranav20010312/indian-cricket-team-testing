"""
Shared fixtures for all test modules.
Starts the Flask app in a background thread and provides a Selenium WebDriver.
"""
import pytest
import threading
import time
import sys
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Add project root to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="session")
def app():
    """Start Flask app in a background thread for the entire test session."""
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test_secret"

    server = threading.Thread(
        target=lambda: flask_app.run(port=5000, use_reloader=False, debug=False)
    )
    server.daemon = True
    server.start()

    # Wait for server to be ready
    time.sleep(2)
    yield flask_app


@pytest.fixture(scope="function")
def browser(app):
    """Provide a fresh Chrome WebDriver for each test function."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def logged_in_browser(browser):
    """Provide a browser that is already logged in."""
    browser.get(f"{BASE_URL}/login")
    browser.find_element("id", "username").send_keys("admin")
    browser.find_element("id", "password").send_keys("admin123")
    browser.find_element("id", "login-btn").click()
    time.sleep(1)
    return browser


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def session_cookies(app):
    """Get session cookies via requests for API testing."""
    import requests

    s = requests.Session()
    s.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin123"})
    return s
