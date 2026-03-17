# AI-Powered Regression Testing System

This system automatically detects regressions in the Flask application by comparing the current state against a known-good baseline. No manually written test cases needed.

## Files

| File | Purpose |
|------|---------|
| `capture_baseline.py` | Crawls the app and saves a snapshot (baseline.json) |
| `detect_regression.py` | Compares current state against baseline, flags differences |
| `ai_analyzer.py` | Sends findings to Claude for plain-English analysis |
| `simulate_change.py` | Introduces intentional regressions for demo purposes |

## Prerequisites

- The Flask app must be running on `http://127.0.0.1:5000`
- Python packages: `requests`, `beautifulsoup4`, `anthropic` (install via `pip install -r requirements.txt` from the project root)
- For AI analysis: set the `ANTHROPIC_API_KEY` environment variable (optional — falls back to rule-based analysis without it)

## How to Run Each Step

**Make sure the Flask app is running first:**
```bash
python app.py
```

### Step 1: Capture Baseline

```bash
python ai_regression/capture_baseline.py
```

This crawls all routes (`/login`, `/dashboard`, `/players`, `/matches`, `/api/players`, `/api/matches`) and records:
- HTTP status codes
- HTML element IDs and class names
- JSON schema and field names (for API endpoints)
- Response times
- Data counts (table rows, cards, array items)

Output: `ai_regression/baseline.json`

### Step 2: Simulate a Code Change (for demo)

```bash
python ai_regression/simulate_change.py --apply
```

This introduces three intentional regressions:
1. Removes a player from the data (row count + API count change)
2. Drops the `wickets` field from one player (API schema change)
3. Adds a 3-second delay to `/api/matches` (performance regression)

### Step 3: Detect Regressions

```bash
python ai_regression/detect_regression.py
```

Compares the current app state against the baseline and classifies each difference:
- **REGRESSION**: Unexpected change — something broke
- **WARNING**: Minor difference needing review
- **EXPECTED**: Known change (developer can mark these in the script)

Output:
- `ai_regression/regression_report.json` (machine-readable)
- `ai_regression/regression_report.txt` (human-readable)

### Step 4: AI Analysis

```bash
# Set API key (optional)
export ANTHROPIC_API_KEY="your-key-here"

python ai_regression/ai_analyzer.py
```

Claude analyzes each finding and provides:
- Plain English explanation
- Severity classification (Critical / High / Medium / Low)
- Probable root cause
- Recommended fix
- Whether it is likely expected or an actual regression

Output: `ai_regression/ai_analysis_report.txt`

If no API key is set, the script generates a rule-based analysis instead.

### Step 5: Revert Changes

```bash
python ai_regression/simulate_change.py --revert
```

Restores `app.py` to its original state from the backup.

## Complete Demo (copy-paste)

```bash
# In a separate terminal, start the app:
python app.py

# Then run the full demo:
python ai_regression/capture_baseline.py
python ai_regression/simulate_change.py --apply
python ai_regression/detect_regression.py
python ai_regression/ai_analyzer.py
python ai_regression/simulate_change.py --revert
```

## Generated Files

After a full run, you will have:
- `baseline.json` — The app snapshot before changes
- `regression_report.json` — Detected differences (machine-readable)
- `regression_report.txt` — Detected differences (human-readable)
- `ai_analysis_report.txt` — AI-powered analysis of findings
