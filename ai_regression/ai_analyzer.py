"""
Part C: AI Analysis Script
Takes the regression report and uses the Anthropic API (Claude) to
provide plain-English explanations, severity classifications,
root cause analysis, and fix recommendations.
"""
import json
import os
from datetime import datetime

REPORT_JSON = os.path.join(os.path.dirname(__file__), "regression_report.json")
AI_REPORT_FILE = os.path.join(os.path.dirname(__file__), "ai_analysis_report.txt")


def load_regression_report():
    """Load the regression detection report."""
    with open(REPORT_JSON, "r") as f:
        return json.load(f)


def build_prompt(report):
    """Build the prompt for Claude to analyze the regression report."""
    report_text = json.dumps(report, indent=2)

    prompt = f"""You are a senior QA engineer analyzing a regression test report for a web application
(Indian Cricket Team portal built with Python Flask).

The regression detection system compared the current state of the application against a known-good
baseline and found the following differences:

--- REGRESSION REPORT ---
{report_text}
--- END REPORT ---

Please analyze each finding and provide:

1. **Plain English Explanation**: What changed and what it means for the user
2. **Severity Classification**: Critical / High / Medium / Low — with reasoning
3. **Probable Root Cause**: What code change likely caused this
4. **Recommended Fix**: What the developer should do to fix it
5. **Expected vs Regression**: Is this likely an intentional change or an actual regression?

At the end, provide:
- An **Executive Summary** (2-3 sentences for a non-technical stakeholder)
- A **Priority Action List** (ordered by severity, what to fix first)

Format your response clearly with headers and bullet points."""

    return prompt


def analyze_with_ai(report):
    """Send the report to Claude for analysis."""
    try:
        import anthropic
    except ImportError:
        print("[!] anthropic package not installed. Run: pip install anthropic")
        print("[*] Generating fallback analysis without AI...")
        return generate_fallback_analysis(report)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[!] ANTHROPIC_API_KEY environment variable not set.")
        print("[*] Generating fallback analysis without AI...")
        return generate_fallback_analysis(report)

    print("[*] Sending regression report to Claude for analysis...")
    client = anthropic.Anthropic(api_key=api_key)

    prompt = build_prompt(report)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def generate_fallback_analysis(report):
    """Generate a rule-based analysis when the AI API is not available."""
    lines = []
    lines.append("=" * 60)
    lines.append("  AI REGRESSION ANALYSIS (Rule-Based Fallback)")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Note: Anthropic API key not configured. Using rule-based analysis.")
    lines.append("Set ANTHROPIC_API_KEY environment variable for AI-powered analysis.")
    lines.append("")

    findings = report.get("findings", {})
    if not findings:
        lines.append("No findings to analyze. Application matches baseline.")
        return "\n".join(lines)

    finding_num = 0
    for route_path, route_findings in findings.items():
        lines.append(f"Route: {route_path}")
        lines.append("-" * 40)

        for f in route_findings:
            finding_num += 1
            lines.append(f"\nFinding #{finding_num}: {f['description']}")
            lines.append(f"  Severity: {f['severity']}")
            lines.append(f"  Classification: {f['classification']}")

            # Rule-based analysis
            if f["field"] == "status_code":
                lines.append("  Analysis: A status code change is critical — it means the route")
                lines.append("    is returning a completely different response type. This could")
                lines.append("    indicate a broken route, missing authentication, or server error.")
                lines.append("  Recommended Fix: Check the route handler and middleware for errors.")

            elif "element_ids" in f["field"] and "MISSING" in str(f.get("current", "")):
                lines.append("  Analysis: Missing HTML element IDs suggest that UI elements were")
                lines.append("    removed or renamed. This will break any automated tests or")
                lines.append("    scripts that reference these IDs.")
                lines.append("  Recommended Fix: Restore the missing elements or update all")
                lines.append("    references to use the new IDs.")

            elif "json_keys" in f["field"] and "MISSING" in str(f.get("current", "")):
                lines.append("  Analysis: Missing JSON fields in the API response is a breaking")
                lines.append("    change. Any client consuming this API will fail if it expects")
                lines.append("    these fields.")
                lines.append("  Recommended Fix: Restore the missing fields or version the API.")

            elif "count" in f["field"]:
                lines.append("  Analysis: A change in data count could mean records were added")
                lines.append("    or removed. If unintentional, it may indicate a data corruption")
                lines.append("    or a query change.")
                lines.append("  Recommended Fix: Verify the data source and check recent changes.")

            elif f["field"] == "response_time":
                lines.append("  Analysis: A significant response time increase suggests a")
                lines.append("    performance regression — possibly a new database query,")
                lines.append("    added middleware, or inefficient code.")
                lines.append("  Recommended Fix: Profile the route and check for new bottlenecks.")

            else:
                lines.append("  Analysis: This change should be reviewed to determine if it")
                lines.append("    was intentional or accidental.")
                lines.append("  Recommended Fix: Compare the code diff for this route.")

            lines.append("")

    # Summary
    s = report.get("summary", {})
    lines.append("=" * 60)
    lines.append("EXECUTIVE SUMMARY")
    lines.append("=" * 60)
    lines.append(f"The regression scan detected {s.get('total_findings', 0)} differences")
    lines.append(f"between the baseline and current application state.")
    lines.append(f"Of these, {s.get('regressions', 0)} are classified as regressions")
    lines.append(f"and {s.get('warnings', 0)} as warnings requiring review.")
    lines.append("")
    lines.append("PRIORITY ACTION LIST:")
    lines.append("1. Fix all CRITICAL severity findings immediately")
    lines.append("2. Review HIGH severity findings before the next release")
    lines.append("3. Investigate MEDIUM findings for unintended side effects")
    lines.append("4. Document LOW/WARNING findings for tracking")

    return "\n".join(lines)


def run_analysis():
    """Main function: load report, analyze, and save results."""
    print("=" * 60)
    print("  AI REGRESSION ANALYSIS - Indian Cricket Team App")
    print("=" * 60)
    print()

    if not os.path.exists(REPORT_JSON):
        print("[!] No regression report found. Run detect_regression.py first.")
        return

    report = load_regression_report()

    if report["summary"]["total_findings"] == 0:
        analysis = "No regressions detected. The application matches the baseline perfectly."
        print("[+] " + analysis)
    else:
        print(f"[*] Analyzing {report['summary']['total_findings']} findings...")
        analysis = analyze_with_ai(report)

    # Save the analysis report
    with open(AI_REPORT_FILE, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  AI-POWERED REGRESSION ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Baseline:  {report['baseline_captured_at']}\n")
        f.write(f"Detection: {report['detection_time']}\n\n")
        f.write(analysis)
        f.write("\n")

    print()
    print(f"[+] AI analysis saved to: {AI_REPORT_FILE}")


if __name__ == "__main__":
    run_analysis()
