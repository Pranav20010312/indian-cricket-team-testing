"""
Part B: Regression Detector Script
Re-crawls the app after a code change and compares every response
against the saved baseline. Flags differences as REGRESSION, WARNING,
or EXPECTED, and generates a detailed report.
"""
import json
import time
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
BASELINE_FILE = os.path.join(os.path.dirname(__file__), "baseline.json")
REPORT_JSON = os.path.join(os.path.dirname(__file__), "regression_report.json")
REPORT_TXT = os.path.join(os.path.dirname(__file__), "regression_report.txt")

# Expected changes can be listed here (developer marks them before running)
EXPECTED_CHANGES = []
# Example: EXPECTED_CHANGES = ["/api/players:field_structure", "/players:table_row_count"]


def load_baseline():
    """Load the previously captured baseline."""
    with open(BASELINE_FILE, "r") as f:
        return json.load(f)


def get_authenticated_session():
    session = requests.Session()
    session.post(
        f"{BASE_URL}/login",
        data={"username": "admin", "password": "admin123"},
        allow_redirects=False,
    )
    return session


def capture_current_state(session, route_path, route_data):
    """Capture the current state of a route (same logic as baseline capture)."""
    url = f"{BASE_URL}{route_path}"
    start = time.time()
    resp = session.get(url, allow_redirects=True)
    response_time = round(time.time() - start, 4)

    result = {
        "status_code": resp.status_code,
        "response_time_seconds": response_time,
    }

    if route_data.get("route_type") == "api":
        try:
            data = resp.json()
            result["json_keys"] = sorted(data.keys()) if isinstance(data, dict) else []
            if isinstance(data, dict):
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
        except Exception:
            result["json_keys"] = []
            result["field_structure"] = {}
        result["content_type"] = resp.headers.get("Content-Type", "")
    else:
        soup = BeautifulSoup(resp.text, "html.parser")
        result["element_ids"] = sorted([el.get("id") for el in soup.find_all(id=True)])
        result["class_names"] = sorted(list(set(
            cls for el in soup.find_all(class_=True) for cls in el.get("class", [])
        )))
        result["headings"] = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
        result["table_row_count"] = len(soup.select("tbody tr"))
        result["card_count"] = len(soup.select(".match-card, .nav-card, .stat-card"))
        result["content_length"] = len(resp.text)
        result["page_title"] = soup.title.string if soup.title else None

    return result


def classify_finding(route_path, field_name):
    """Classify a finding as EXPECTED, REGRESSION, or WARNING."""
    key = f"{route_path}:{field_name}"
    if key in EXPECTED_CHANGES:
        return "EXPECTED"
    return "REGRESSION"


def compare_route(route_path, baseline_data, current_data):
    """Compare baseline vs current for a single route and return findings."""
    findings = []

    # 1. Status code change
    if baseline_data.get("status_code") != current_data.get("status_code"):
        findings.append({
            "field": "status_code",
            "severity": "CRITICAL",
            "classification": classify_finding(route_path, "status_code"),
            "baseline": baseline_data.get("status_code"),
            "current": current_data.get("status_code"),
            "description": f"Status code changed from {baseline_data.get('status_code')} to {current_data.get('status_code')}",
        })

    # 2. Response time regression (more than 2x slower)
    baseline_time = baseline_data.get("response_time_seconds", 0)
    current_time = current_data.get("response_time_seconds", 0)
    if baseline_time > 0 and current_time > baseline_time * 2:
        findings.append({
            "field": "response_time",
            "severity": "HIGH",
            "classification": "WARNING",
            "baseline": baseline_time,
            "current": current_time,
            "description": f"Response time increased from {baseline_time}s to {current_time}s (>{2*baseline_time}s threshold)",
        })

    # 3. UI-specific checks
    if baseline_data.get("route_type") == "ui":
        # Missing element IDs
        baseline_ids = set(baseline_data.get("element_ids", []))
        current_ids = set(current_data.get("element_ids", []))
        missing_ids = baseline_ids - current_ids
        new_ids = current_ids - baseline_ids

        if missing_ids:
            findings.append({
                "field": "element_ids",
                "severity": "HIGH",
                "classification": classify_finding(route_path, "element_ids"),
                "baseline": sorted(missing_ids),
                "current": "MISSING",
                "description": f"Missing HTML element IDs: {sorted(missing_ids)}",
            })
        if new_ids:
            findings.append({
                "field": "element_ids_new",
                "severity": "LOW",
                "classification": "WARNING",
                "baseline": "N/A",
                "current": sorted(new_ids),
                "description": f"New HTML element IDs found: {sorted(new_ids)}",
            })

        # Data count changes
        for count_field in ["table_row_count", "card_count"]:
            baseline_count = baseline_data.get(count_field, 0)
            current_count = current_data.get(count_field, 0)
            if baseline_count != current_count and baseline_count > 0:
                findings.append({
                    "field": count_field,
                    "severity": "MEDIUM",
                    "classification": classify_finding(route_path, count_field),
                    "baseline": baseline_count,
                    "current": current_count,
                    "description": f"{count_field} changed from {baseline_count} to {current_count}",
                })

    # 4. API-specific checks
    if baseline_data.get("route_type") == "api":
        # JSON key changes
        baseline_keys = set(baseline_data.get("json_keys", []))
        current_keys = set(current_data.get("json_keys", []))
        missing_keys = baseline_keys - current_keys
        new_keys = current_keys - baseline_keys

        if missing_keys:
            findings.append({
                "field": "json_keys",
                "severity": "CRITICAL",
                "classification": classify_finding(route_path, "json_keys"),
                "baseline": sorted(missing_keys),
                "current": "MISSING",
                "description": f"Missing JSON fields: {sorted(missing_keys)}",
            })
        if new_keys:
            findings.append({
                "field": "json_keys_new",
                "severity": "LOW",
                "classification": "WARNING",
                "baseline": "N/A",
                "current": sorted(new_keys),
                "description": f"New JSON fields found: {sorted(new_keys)}",
            })

        # Nested field structure changes (item keys in arrays)
        baseline_struct = baseline_data.get("field_structure", {})
        current_struct = current_data.get("field_structure", {})

        for key in baseline_struct:
            if key in current_struct:
                b_info = baseline_struct[key]
                c_info = current_struct[key]

                if b_info.get("type") == "array" and c_info.get("type") == "array":
                    # Check item count
                    if b_info.get("count") != c_info.get("count"):
                        findings.append({
                            "field": f"field_structure.{key}.count",
                            "severity": "MEDIUM",
                            "classification": classify_finding(route_path, f"field_structure.{key}.count"),
                            "baseline": b_info.get("count"),
                            "current": c_info.get("count"),
                            "description": f"Array '{key}' count changed from {b_info.get('count')} to {c_info.get('count')}",
                        })

                    # Check item keys (schema)
                    b_item_keys = set(b_info.get("item_keys", []))
                    c_item_keys = set(c_info.get("item_keys", []))
                    missing_item_keys = b_item_keys - c_item_keys

                    if missing_item_keys:
                        findings.append({
                            "field": f"field_structure.{key}.item_keys",
                            "severity": "CRITICAL",
                            "classification": classify_finding(route_path, "field_structure"),
                            "baseline": sorted(missing_item_keys),
                            "current": "MISSING",
                            "description": f"Missing fields in '{key}' items: {sorted(missing_item_keys)}",
                        })

    return findings


def detect_regressions():
    """Main function: compare current app state against baseline."""
    print("=" * 60)
    print("  REGRESSION DETECTION - Indian Cricket Team App")
    print("=" * 60)
    print()

    baseline = load_baseline()
    session = get_authenticated_session()

    report = {
        "detection_time": datetime.now().isoformat(),
        "baseline_captured_at": baseline["captured_at"],
        "total_routes": len(baseline["routes"]),
        "findings": {},
        "summary": {
            "total_findings": 0,
            "regressions": 0,
            "warnings": 0,
            "expected": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
    }

    all_findings = []

    for route_path, baseline_data in baseline["routes"].items():
        print(f"[*] Checking: {route_path}")
        current_data = capture_current_state(session, route_path, baseline_data)
        findings = compare_route(route_path, baseline_data, current_data)

        if findings:
            report["findings"][route_path] = findings
            all_findings.extend(findings)
            for f in findings:
                print(f"    [{f['severity']}] {f['classification']}: {f['description']}")
        else:
            print(f"    [OK] No changes detected")

    # Build summary
    for f in all_findings:
        report["summary"]["total_findings"] += 1
        report["summary"][f["classification"].lower() + "s"] += 1
        report["summary"][f["severity"].lower()] += 1

    # Save JSON report
    with open(REPORT_JSON, "w") as f:
        json.dump(report, f, indent=2)

    # Save human-readable text report
    with open(REPORT_TXT, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  REGRESSION DETECTION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Detection Time:     {report['detection_time']}\n")
        f.write(f"Baseline From:      {report['baseline_captured_at']}\n")
        f.write(f"Total Routes:       {report['total_routes']}\n\n")

        f.write("--- SUMMARY ---\n")
        s = report["summary"]
        f.write(f"Total Findings:     {s['total_findings']}\n")
        f.write(f"  Regressions:      {s['regressions']}\n")
        f.write(f"  Warnings:         {s['warnings']}\n")
        f.write(f"  Expected:         {s['expected']}\n")
        f.write(f"  Critical:         {s['critical']}\n")
        f.write(f"  High:             {s['high']}\n")
        f.write(f"  Medium:           {s['medium']}\n")
        f.write(f"  Low:              {s['low']}\n\n")

        if all_findings:
            f.write("--- DETAILED FINDINGS ---\n\n")
            for route_path, findings in report["findings"].items():
                f.write(f"Route: {route_path}\n")
                f.write("-" * 40 + "\n")
                for finding in findings:
                    f.write(f"  [{finding['severity']}] {finding['classification']}\n")
                    f.write(f"  {finding['description']}\n")
                    f.write(f"  Baseline: {finding['baseline']}\n")
                    f.write(f"  Current:  {finding['current']}\n\n")
        else:
            f.write("No regressions detected. All routes match baseline.\n")

    print()
    print(f"[+] Report saved: {REPORT_JSON}")
    print(f"[+] Report saved: {REPORT_TXT}")
    print()
    print(f"=== SUMMARY: {report['summary']['total_findings']} findings "
          f"({report['summary']['regressions']} regressions, "
          f"{report['summary']['warnings']} warnings) ===")

    return report


if __name__ == "__main__":
    detect_regressions()
