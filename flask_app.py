"""
flask_app.py
────────────
Flask web version of the Password Generator.

Run
───
    pip install flask
    python flask_app.py

Then open http://127.0.0.1:5000 in your browser.

Routes
──────
GET  /               → Landing page with the generator UI.
POST /generate       → JSON API: receive options, return password + metadata.
GET  /static/...     → Served automatically by Flask.
"""

from flask import Flask, render_template, request, jsonify
from password_generator import PasswordOptions, generate_password, check_strength

app = Flask(__name__)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the single-page generator UI."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def api_generate():
    """
    Generate a password from JSON body options.

    Expected JSON body
    ------------------
    {
        "length":      16,
        "use_upper":   true,
        "use_lower":   true,
        "use_digits":  true,
        "use_symbols": true
    }

    Response JSON
    -------------
    {
        "password": "...",
        "entropy":  95.4,
        "strength": "Strong",
        "score":    3
    }
    """
    data = request.get_json(force=True, silent=True) or {}

    opts = PasswordOptions(
        length=int(data.get("length", 16)),
        use_upper=bool(data.get("use_upper", True)),
        use_lower=bool(data.get("use_lower", True)),
        use_digits=bool(data.get("use_digits", True)),
        use_symbols=bool(data.get("use_symbols", True)),
    )

    try:
        result = generate_password(opts)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "password": result.password,
        "entropy":  result.entropy,
        "strength": result.strength,
        "score":    result.score,
    })


@app.route("/check", methods=["POST"])
def api_check():
    """
    Evaluate the strength of a manually-entered password.

    Expected JSON body
    ------------------
    { "password": "MyP@ssw0rd" }

    Response JSON
    -------------
    { "strength": "Strong", "score": 3, "entropy": 78.4 }
    """
    data     = request.get_json(force=True, silent=True) or {}
    password = data.get("password", "")
    strength, score, entropy = check_strength(password)
    return jsonify({"strength": strength, "score": score, "entropy": entropy})


# ─── Dev server ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
