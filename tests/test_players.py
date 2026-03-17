"""
Players Page Tests
Tests for the players table, search, and sort functionality.
"""
import time
import pytest
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


class TestPlayers:
    def test_players_table_loads_with_data(self, logged_in_browser):
        """Test that players table loads and contains rows."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        rows = logged_in_browser.find_elements(By.CSS_SELECTOR, "#players-body tr")
        assert len(rows) >= 8

    def test_table_has_correct_columns(self, logged_in_browser):
        """Test that table has Name, Role, Matches, Runs, Wickets columns."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        headers = logged_in_browser.find_elements(By.CSS_SELECTOR, "#players-table th")
        header_texts = [h.text.strip().split("\n")[0].strip() for h in headers]
        # Headers contain sort icon character, so use substring matching
        assert any("Name" in h for h in header_texts)
        assert any("Role" in h for h in header_texts)
        assert any("Matches" in h for h in header_texts)
        assert any("Runs" in h for h in header_texts)
        assert any("Wickets" in h for h in header_texts)

    def test_search_filter_by_name(self, logged_in_browser):
        """Test searching for a specific player name filters the table."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        search = logged_in_browser.find_element(By.ID, "search-box")
        search.send_keys("Virat")
        time.sleep(1)
        visible_rows = [
            r for r in logged_in_browser.find_elements(By.CSS_SELECTOR, ".player-row")
            if r.is_displayed()
        ]
        assert len(visible_rows) == 1
        assert "Virat" in visible_rows[0].text

    def test_search_filter_by_role(self, logged_in_browser):
        """Test searching by role filters correctly."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        search = logged_in_browser.find_element(By.ID, "search-box")
        search.send_keys("Bowler")
        time.sleep(1)
        visible_rows = [
            r for r in logged_in_browser.find_elements(By.CSS_SELECTOR, ".player-row")
            if r.is_displayed()
        ]
        assert len(visible_rows) >= 2
        for row in visible_rows:
            assert "Bowler" in row.text

    def test_search_no_results(self, logged_in_browser):
        """Test that searching for non-existent player shows no results message."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        search = logged_in_browser.find_element(By.ID, "search-box")
        search.send_keys("XYZNONEXISTENT")
        time.sleep(1)
        no_results = logged_in_browser.find_element(By.ID, "no-results")
        assert no_results.is_displayed()

    def test_back_to_dashboard_button(self, logged_in_browser):
        """Test that Back to Dashboard button navigates correctly."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)
        btn = logged_in_browser.find_element(By.ID, "back-btn")
        btn.click()
        time.sleep(1)
        assert "/dashboard" in logged_in_browser.current_url

    def test_sort_by_column(self, logged_in_browser):
        """Test that clicking column header sorts the table."""
        logged_in_browser.get(f"{BASE_URL}/players")
        time.sleep(1)

        # Get initial first row name
        first_name_before = logged_in_browser.find_element(
            By.CSS_SELECTOR, "#players-body tr:first-child td:first-child"
        ).text

        # Click Name header to sort
        name_header = logged_in_browser.find_elements(By.CSS_SELECTOR, "#players-table th")[0]
        name_header.click()
        time.sleep(1)

        first_name_after = logged_in_browser.find_element(
            By.CSS_SELECTOR, "#players-body tr:first-child td:first-child"
        ).text

        # Table should have been reordered (alphabetically)
        # We just verify sorting happened by checking order changed or is alphabetical
        rows = logged_in_browser.find_elements(By.CSS_SELECTOR, "#players-body tr")
        names = [r.find_elements(By.TAG_NAME, "td")[0].text for r in rows]
        assert names == sorted(names) or names == sorted(names, reverse=True)
