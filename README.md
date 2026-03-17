# Indian Cricket Team - Web Application & AI Regression Testing

A complete demonstration project showcasing a Flask web application with automated testing and an AI-powered regression testing system.

**Built for:** Qrvey Assessment
**Author:** Pranav

---

## Project Structure

```
├── app.py                          # Flask web application
├── requirements.txt                # Python dependencies
├── templates/                      # HTML templates (Jinja2)
│   ├── login.html
│   ├── dashboard.html
│   ├── players.html
│   └── matches.html
├── static/css/style.css            # Styling (blue & orange cricket theme)
├── tests/                          # Automated test suite (Selenium + pytest)
│   ├── conftest.py                 # Shared fixtures & setup
│   ├── test_login.py               # Login page tests (8 tests)
│   ├── test_dashboard.py           # Dashboard tests (8 tests)
│   ├── test_players.py             # Players page tests (7 tests)
│   ├── test_matches.py             # Match scores tests (4 tests)
│   ├── test_security.py            # Protected routes tests (4 tests)
│   └── test_api.py                 # API endpoint tests (6 tests)
└── ai_regression/                  # AI-powered regression testing system
    ├── capture_baseline.py         # Part A: Capture app baseline
    ├── detect_regression.py        # Part B: Detect regressions
    ├── ai_analyzer.py              # Part C: AI analysis with Claude
    └── simulate_change.py          # Part D: Simulate regressions for demo
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

You also need **Google Chrome** and **ChromeDriver** installed for Selenium tests.

### 2. Run the Web Application

```bash
python app.py
```

The app runs at `http://127.0.0.1:5000`. Login with:
- **Username:** `admin`
- **Password:** `admin123`

### 3. Run Automated Tests

```bash
# Run all tests
pytest tests/ -v

# Run with HTML report
pytest tests/ -v --html=report.html --self-contained-html
```

### 4. Run the AI Regression Testing System

This is the **key differentiator** — demonstrates how AI can automate regression testing without manually written test cases.

#### Step 1: Capture Baseline (while app is running)
```bash
python ai_regression/capture_baseline.py
```
This creates `ai_regression/baseline.json` — a snapshot of the entire app.

#### Step 2: Simulate a Code Change
```bash
python ai_regression/simulate_change.py --apply
```
This introduces intentional regressions:
- Removes a player from the data
- Drops a field from the API schema
- Adds a performance delay to an endpoint

#### Step 3: Detect Regressions
```bash
python ai_regression/detect_regression.py
```
Compares the changed app against the baseline and generates reports.

#### Step 4: AI Analysis
```bash
# Set your API key first
export ANTHROPIC_API_KEY="your-key-here"

python ai_regression/ai_analyzer.py
```
Claude analyzes the findings and provides:
- Plain English explanations
- Severity classifications
- Root cause analysis
- Fix recommendations

> **Note:** If no API key is set, the script falls back to rule-based analysis.

#### Step 5: Revert Changes
```bash
python ai_regression/simulate_change.py --revert
```

---

## Complete Demo Flow (End-to-End)

```bash
# Terminal 1: Start the app
python app.py

# Terminal 2: Run the full demo
python ai_regression/capture_baseline.py          # Take the "before photo"
python ai_regression/simulate_change.py --apply    # Break something
python ai_regression/detect_regression.py          # Catch the regressions
python ai_regression/ai_analyzer.py                # AI explains what broke
python ai_regression/simulate_change.py --revert   # Restore the app
```

---

## Deliverables

### Deliverable 1: Web Application
- Flask backend with session-based authentication
- Indian cricket theme (blue & orange)
- Pages: Login, Dashboard, Players (with search & sort), Match Scores (with filters)
- All routes protected behind login
- JSON API endpoints: `/api/players`, `/api/matches`

### Deliverable 2: Automated Tests (37 tests)
- Login flow tests (8)
- Dashboard navigation tests (8)
- Players page tests (7)
- Match scores tests (4)
- Security / protected routes tests (4)
- API endpoint tests (6)

### Deliverable 3: AI Regression Testing System
- **Baseline Capture:** Crawls app and records status codes, HTML structure, JSON schemas, response times, data counts
- **Regression Detection:** Compares current state vs baseline, classifies findings as REGRESSION / WARNING / EXPECTED
- **AI Analysis:** Claude reads the report and explains findings in plain English with severity, root cause, and fix recommendations
- **Simulation Script:** Introduces intentional regressions for live demonstration

### Deliverable 4: Documentation
- This README with complete setup and demo instructions

---

## Key Design Decisions

1. **No manual test cases for regression testing** — The AI system auto-discovers changes by comparing structural baselines, aligning with Qrvey's challenge of eliminating manual regression test maintenance.

2. **Fallback analysis** — The AI analyzer works with or without an API key (rule-based fallback), ensuring the demo always runs.

3. **Classification system** — Findings are automatically classified (REGRESSION vs WARNING vs EXPECTED) so developers know what to fix vs what to review.

4. **Realistic data** — All cricket data uses real Indian cricket team players and plausible statistics.

---

## Login Credentials

| Username | Password |
|----------|----------|
| admin    | admin123 |
