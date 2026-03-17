"""
Part D: Simulate a Regression
Intentionally introduces changes to the Flask app to demonstrate
that the regression detection system catches them.

Usage:
    python simulate_change.py --apply     # Introduce the changes
    python simulate_change.py --revert    # Undo the changes

Changes introduced:
1. Remove 'wickets' field from one player in API response
2. Remove a player from the data (changes row count)
3. Add artificial delay to /api/matches (performance regression)
4. Change a heading text on the players page
"""
import os
import sys
import re

APP_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
BACKUP_FILE = os.path.join(os.path.dirname(__file__), "app_backup.py")


def read_app():
    with open(APP_FILE, "r") as f:
        return f.read()


def write_app(content):
    with open(APP_FILE, "w") as f:
        f.write(content)


def apply_changes():
    """Apply simulated regressions to the app."""
    print("=" * 60)
    print("  SIMULATING REGRESSIONS")
    print("=" * 60)
    print()

    content = read_app()

    # Backup original
    with open(BACKUP_FILE, "w") as f:
        f.write(content)
    print("[+] Original app.py backed up")

    changes_made = []

    # Change 1: Remove a player (Kuldeep Yadav) — affects row count & API count
    if '{"name": "Kuldeep Yadav"' in content:
        content = content.replace(
            '    {"name": "Kuldeep Yadav", "role": "Bowler", "matches": 88, "runs": 196, "wickets": 152},\n',
            ''
        )
        changes_made.append("Removed Kuldeep Yadav from players data (affects table row count and API count)")

    # Change 2: Remove 'wickets' field from Suryakumar Yadav — API schema change
    if '{"name": "Suryakumar Yadav", "role": "Batsman", "matches": 51, "runs": 1918, "wickets": 0}' in content:
        content = content.replace(
            '{"name": "Suryakumar Yadav", "role": "Batsman", "matches": 51, "runs": 1918, "wickets": 0}',
            '{"name": "Suryakumar Yadav", "role": "Batsman", "matches": 51, "runs": 1918}'
        )
        changes_made.append("Removed 'wickets' field from Suryakumar Yadav (API schema change)")

    # Change 3: Add a time.sleep to /api/matches for performance regression
    if "def api_matches():" in content and "time.sleep" not in content.split("def api_matches():")[1].split("def ")[0]:
        content = content.replace(
            'def api_matches():\n    return jsonify({"matches": MATCHES, "count": len(MATCHES)})',
            'def api_matches():\n    time.sleep(3)  # SIMULATED REGRESSION: artificial delay\n    return jsonify({"matches": MATCHES, "count": len(MATCHES)})'
        )
        changes_made.append("Added 3-second delay to /api/matches (performance regression)")

    write_app(content)

    print()
    for i, change in enumerate(changes_made, 1):
        print(f"  {i}. {change}")
    print()
    print(f"[+] {len(changes_made)} changes applied to app.py")
    print("[*] Now run: python ai_regression/detect_regression.py")
    print("[*] Then run: python ai_regression/ai_analyzer.py")


def revert_changes():
    """Revert all changes by restoring from backup."""
    print("=" * 60)
    print("  REVERTING SIMULATED CHANGES")
    print("=" * 60)
    print()

    if not os.path.exists(BACKUP_FILE):
        print("[!] No backup file found. Cannot revert.")
        return

    with open(BACKUP_FILE, "r") as f:
        original = f.read()

    write_app(original)
    os.remove(BACKUP_FILE)

    print("[+] app.py restored to original state")
    print("[+] Backup file removed")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python simulate_change.py --apply    # Introduce regressions")
        print("  python simulate_change.py --revert   # Undo all changes")
        sys.exit(1)

    action = sys.argv[1]
    if action == "--apply":
        apply_changes()
    elif action == "--revert":
        revert_changes()
    else:
        print(f"Unknown action: {action}")
        print("Use --apply or --revert")


if __name__ == "__main__":
    main()
