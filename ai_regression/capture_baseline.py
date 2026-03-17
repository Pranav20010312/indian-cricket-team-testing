"""
Part A: Baseline Capture Script
Automatically crawls the running Flask app and records a baseline snapshot
of every route — status codes, response structure, timing, and data counts.
This becomes the "before photo" for regression detection.
"""
import json
import time
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
BASELINE_FILE = os.path.join(os.path.dirname(__file__), "baseline.json")

# Routes to crawl — UI pages and API endpoints
ROUTES = [
    {"path": "/login", "type": "ui", "auth_required": False},
    {"path": "/dashboard", "type": "ui", "auth_required": True},
    {"path": "/players", "type": "ui", "auth_required": True},
    {"path": "/matches", "type": "ui", "auth_required": True},
    {"path": "/api/players", "type": "api", "auth_required": True},
    {"path": "/api/matches", "type": "api", "auth_required": True},
]


def get_authenticated_session():
    """Create an authenticated session by logging in."""
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}/login",
        data={"username": "admin", "password": "admin123"},
        allow_redirects=False,
    )
    if resp.status_code in (302, 200):
        print("[+] Authentication successful")
    else:
        print(f"[!] Authentication may have failed: status {resp.status_code}")
    return session


def capture_ui_page(session, path):
    """Capture baseline data for a UI (HTML) page."""
    url = f"{BASE_URL}{path}"
    start = time.time()
    resp = session.get(url, allow_redirects=True)
    response_time = round(time.time() - start, 4)

    soup = BeautifulSoup(resp.text, "html.parser")

    # Collect structural data
    element_ids = [el.get("id") for el in soup.find_all(id=True)]
    class_names = list(set(
        cls for el in soup.find_all(class_=True) for cls in el.get("class", [])
    ))

    # Count data items (table rows, cards, etc.)
    table_rows = len(soup.select("tbody tr"))
    cards = len(soup.select(".match-card, .nav-card, .stat-card"))

    # Collect text content of key elements
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

    return {
        "url": url,
        "status_code": resp.status_code,
        "response_time_seconds": response_time,
        "page_title": soup.title.string if soup.title else None,
        "element_ids": sorted(element_ids),
        "class_names": sorted(class_names),
        "headings": headings,
        "table_row_count": table_rows,
        "card_count": cards,
        "content_length": len(resp.text),
    }


def capture_api_endpoint(session, path):
    """Capture baseline data for an API (JSON) endpoint."""
    url = f"{BASE_URL}{path}"
    start = time.time()
    resp = session.get(url, allow_redirects=True)
    response_time = round(time.time() - start, 4)

    try:
        data = resp.json()
    except Exception:
        data = None

    result = {
        "url": url,
        "status_code": resp.status_code,
        "response_time_seconds": response_time,
        "content_type": resp.headers.get("Content-Type", ""),
    }

    if data and isinstance(data, dict):
        result["json_keys"] = sorted(data.keys())
        # Record structure of each top-level field
        field_info = {}
        for key, value in data.items():
            if isinstance(value, list):
                field_info[key] = {
                    "type": "array",
                    "count": len(value),
                    "item_keys": sorted(value[0].keys()) if value and isinstance(value[0], dict) else [],
                }
            else:
                field_info[key] = {"type": type(value).__name__, "value": value}
        result["field_structure"] = field_info

    return result


def capture_baseline():
    """Main function: crawl all routes and save baseline."""
    print("=" * 60)
    print("  BASELINE CAPTURE - Indian Cricket Team App")
    print("=" * 60)
    print()

    session = get_authenticated_session()
    baseline = {
        "captured_at": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "routes": {},
    }

    for route in ROUTES:
        path = route["path"]
        print(f"[*] Capturing: {path}")

        if route["type"] == "ui":
            data = capture_ui_page(session, path)
        else:
            data = capture_api_endpoint(session, path)

        data["route_type"] = route["type"]
        data["auth_required"] = route["auth_required"]
        baseline["routes"][path] = data
        print(f"    Status: {data['status_code']} | Time: {data['response_time_seconds']}s")

    # Save baseline
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)

    print()
    print(f"[+] Baseline saved to: {BASELINE_FILE}")
    print(f"[+] Routes captured: {len(baseline['routes'])}")
    return baseline


if __name__ == "__main__":
    capture_baseline()
