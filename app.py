"""
Indian Cricket Team Web Application
Built with Flask for Qrvey assessment
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import time

app = Flask(__name__)
app.secret_key = "cricket_secret_key_2024"

# Hardcoded credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

# Indian cricket players data
PLAYERS = [
    {"name": "Virat Kohli", "role": "Batsman", "matches": 292, "runs": 13906, "wickets": 4},
    {"name": "Rohit Sharma", "role": "Batsman", "matches": 264, "runs": 10709, "wickets": 8},
    {"name": "Jasprit Bumrah", "role": "Bowler", "matches": 89, "runs": 241, "wickets": 149},
    {"name": "Ravindra Jadeja", "role": "All-rounder", "matches": 197, "runs": 2756, "wickets": 220},
    {"name": "KL Rahul", "role": "Batsman", "matches": 72, "runs": 2981, "wickets": 0},
    {"name": "Mohammed Shami", "role": "Bowler", "matches": 101, "runs": 254, "wickets": 195},
    {"name": "Hardik Pandya", "role": "All-rounder", "matches": 92, "runs": 1769, "wickets": 72},
    {"name": "Shubman Gill", "role": "Batsman", "matches": 45, "runs": 2291, "wickets": 0},
    {"name": "Kuldeep Yadav", "role": "Bowler", "matches": 88, "runs": 196, "wickets": 152},
    {"name": "Suryakumar Yadav", "role": "Batsman", "matches": 51, "runs": 1918, "wickets": 0},
]

# Recent match results
MATCHES = [
    {"opponent": "Australia", "date": "2024-11-15", "venue": "Mumbai", "result": "Won", "score": "India 326/5 - Australia 289/10"},
    {"opponent": "England", "date": "2024-10-28", "venue": "Kolkata", "result": "Won", "score": "India 281/7 - England 245/10"},
    {"opponent": "South Africa", "date": "2024-10-10", "venue": "Delhi", "result": "Lost", "score": "India 212/10 - South Africa 298/6"},
    {"opponent": "New Zealand", "date": "2024-09-22", "venue": "Bangalore", "result": "Won", "score": "India 345/4 - New Zealand 302/10"},
    {"opponent": "Pakistan", "date": "2024-09-05", "venue": "Ahmedabad", "result": "Won", "score": "India 298/6 - Pakistan 276/10"},
    {"opponent": "Sri Lanka", "date": "2024-08-18", "venue": "Chennai", "result": "Lost", "score": "India 189/10 - Sri Lanka 245/8"},
]

# Team statistics
TEAM_STATS = {
    "total_matches": 1000,
    "wins": 540,
    "losses": 420,
    "draws": 40,
    "win_percentage": "54.0%",
    "highest_score": "418/5 vs West Indies (2011)",
    "captain": "Rohit Sharma",
    "coach": "Gautam Gambhir",
    "icc_ranking": 2,
}


def login_required(f):
    """Decorator to protect routes behind login."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username and not password:
            error = "Please enter both username and password"
        elif not username:
            error = "Please enter your username"
        elif not password:
            error = "Please enter your password"
        elif username == VALID_USERNAME and password == VALID_PASSWORD:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"], stats=TEAM_STATS)


@app.route("/players")
@login_required
def players():
    return render_template("players.html", players=PLAYERS)


@app.route("/matches")
@login_required
def matches():
    return render_template("matches.html", matches=MATCHES)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- API Endpoints ---

@app.route("/api/players")
@login_required
def api_players():
    return jsonify({"players": PLAYERS, "count": len(PLAYERS)})


@app.route("/api/matches")
@login_required
def api_matches():
    return jsonify({"matches": MATCHES, "count": len(MATCHES)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
