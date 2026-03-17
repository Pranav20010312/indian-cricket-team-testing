"""
API Endpoint Tests
Tests for the JSON API endpoints using the requests library.
"""
import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


class TestAPI:
    def test_get_players_returns_200(self, session_cookies):
        """Test GET /api/players returns 200 status and valid JSON."""
        resp = session_cookies.get(f"{BASE_URL}/api/players")
        assert resp.status_code == 200
        data = resp.json()
        assert "players" in data

    def test_get_matches_returns_200(self, session_cookies):
        """Test GET /api/matches returns 200 status and valid JSON."""
        resp = session_cookies.get(f"{BASE_URL}/api/matches")
        assert resp.status_code == 200
        data = resp.json()
        assert "matches" in data

    def test_players_api_data_structure(self, session_cookies):
        """Test that /api/players returns correct data structure."""
        resp = session_cookies.get(f"{BASE_URL}/api/players")
        data = resp.json()
        assert "players" in data
        assert "count" in data
        assert isinstance(data["players"], list)
        assert data["count"] >= 8

        # Check each player has required fields
        for player in data["players"]:
            assert "name" in player
            assert "role" in player
            assert "matches" in player
            assert "runs" in player
            assert "wickets" in player

    def test_matches_api_data_structure(self, session_cookies):
        """Test that /api/matches returns correct data structure."""
        resp = session_cookies.get(f"{BASE_URL}/api/matches")
        data = resp.json()
        assert "matches" in data
        assert "count" in data
        assert isinstance(data["matches"], list)
        assert data["count"] >= 5

        # Check each match has required fields
        for match in data["matches"]:
            assert "opponent" in match
            assert "date" in match
            assert "venue" in match
            assert "result" in match
            assert "score" in match

    def test_api_without_login_redirects(self, app):
        """Test that API returns redirect (302) when not authenticated."""
        resp = requests.get(f"{BASE_URL}/api/players", allow_redirects=False)
        assert resp.status_code == 302

    def test_api_matches_without_login_redirects(self, app):
        """Test that matches API returns redirect when not authenticated."""
        resp = requests.get(f"{BASE_URL}/api/matches", allow_redirects=False)
        assert resp.status_code == 302
