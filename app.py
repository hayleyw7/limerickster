import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from ai import generate_kit

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.environ.get("RATE_LIMIT_DEFAULT", "120 per hour")],
    storage_uri="memory://",
)

GENERATE_LIMIT = os.environ.get("RATE_LIMIT_GENERATE", "10 per minute")

VALID_PRONOUNS = {"he/him", "she/her", "they/them"}

_MINOR_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "by", "with",
}


def _cap_segment(segment: str, force: bool) -> str:
    if not segment:
        return segment
    if not force and segment.lower() in _MINOR_WORDS:
        return segment.lower()
    return segment[:1].upper() + segment[1:].lower()


def capitalize_proper(text: str, *, title_style: bool = False) -> str:
    """Capitalize proper nouns even when the user typed lowercase."""
    text = text.strip()
    if not text:
        return text
    words = text.split()
    out = []
    for i, word in enumerate(words):
        force = not title_style or i == 0 or i == len(words) - 1
        parts = word.split("-")
        out.append("-".join(_cap_segment(p, force or j == 0) for j, p in enumerate(parts)))
    return " ".join(out)


def _normalize_field(value: str, *, title_style: bool = False) -> str:
    value = (value or "").strip()
    return capitalize_proper(value, title_style=title_style) if value else ""


@limiter.request_filter
def _exempt_static_assets():
    return request.path.startswith("/static/") or request.path == "/favicon.ico"


@limiter.request_filter
def _exempt_localhost():
    """Skip rate limits for local dev (macOS AirPlay also fights for :5000)."""
    if os.environ.get("RATE_LIMIT_LOCAL_EXEMPT", "true").lower() not in (
        "1",
        "true",
        "yes",
    ):
        return False
    return request.remote_addr in ("127.0.0.1", "::1")

SITE_DESCRIPTION = "Easily create a personalized limerick from a few details."
# Bump when og-image.jpg changes so crawlers (Discord, preview tools) refetch.
OG_IMAGE_VERSION = "ibm-plex"


def _public_site_url() -> str:
    """Absolute HTTPS origin for OG tags — match the URL being shared."""
    if request:
        scheme = request.headers.get("X-Forwarded-Proto", request.scheme)
        host = request.headers.get("X-Forwarded-Host", request.host)
        return f"{scheme}://{host}".rstrip("/")
    return os.environ.get("SITE_URL", "").strip().rstrip("/")


@app.context_processor
def inject_site_meta():
    site_url = _public_site_url()
    if site_url:
        return {
            "site_description": SITE_DESCRIPTION,
            "site_og_image": f"{site_url}/static/og-image.jpg?v={OG_IMAGE_VERSION}",
            "site_canonical_url": f"{site_url}/",
        }
    return {
        "site_description": SITE_DESCRIPTION,
        "site_og_image": None,
        "site_canonical_url": None,
    }


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(
        {"error": "Too many requests. Please wait a moment and try again."}
    ), 429


@app.route("/")
@limiter.limit("60 per minute")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
@limiter.limit(GENERATE_LIMIT)
def api_generate():
    data = request.get_json(silent=True) or {}

    name = _normalize_field(data.get("name"))
    if not name:
        return jsonify({"error": "Name is required."}), 400

    location = _normalize_field(data.get("location"), title_style=True)
    if not location:
        return jsonify({"error": "Location is required."}), 400

    pronouns = (data.get("pronouns") or "they/them").strip()
    if pronouns not in VALID_PRONOUNS:
        return jsonify({"error": "Pronouns are required."}), 400

    hobby_1 = (data.get("hobby_1") or "").strip()
    hobby_2 = (data.get("hobby_2") or "").strip()
    hobby_3 = (data.get("hobby_3") or "").strip()
    if not hobby_1 or not hobby_2 or not hobby_3:
        return jsonify({"error": "All three hobbies are required."}), 400

    profile = {
        "name": name,
        "location": location,
        "pronouns": pronouns,
        "hobby_1": hobby_1,
        "hobby_2": hobby_2,
        "hobby_3": hobby_3,
        "job": (data.get("job") or "").strip(),
        "pets": (data.get("pets") or "").strip(),
        "favorite_food": (data.get("favorite_food") or "").strip(),
        "physical_trait": (data.get("physical_trait") or "").strip(),
        "other_notes": (data.get("other_notes") or "").strip(),
        "tone": data.get("tone", "cheerful"),
    }

    try:
        kit = generate_kit(profile)
        return jsonify({"profile": profile, "kit": kit})
    except ValueError as e:
        msg = str(e)
        status = 503 if "quota" in msg.lower() or "billing" in msg.lower() else 500
        return jsonify({"error": msg}), status
    except Exception as e:
        return jsonify({"error": f"Generation failed: {e}"}), 500


if __name__ == "__main__":
    # Default 8080 — macOS AirPlay Receiver often binds port 5000 and returns 403.
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="127.0.0.1", port=port)
