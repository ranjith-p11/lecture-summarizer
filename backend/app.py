"""
app.py – Main Flask API server for Lecture Summarizer
"""
import os
import tempfile
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from transcriber import transcribe_file, transcribe_youtube, transcribe_text_passthrough
from summarizer import summarize_text
from firestore_client import verify_id_token, save_record, get_user_records, delete_record

# ─── App Setup ───────────────────────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

ALLOWED_EXTENSIONS = {
    "mp3", "mp4", "wav", "m4a", "ogg", "webm", "flac", "mpeg", "mpga"
}

MAX_FILE_SIZE_MB = 200
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024


# ─── Helpers ─────────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Auth Middleware ──────────────────────────────────────────────────────────

def require_auth(f):
    """Decorator: verify Firebase ID token from Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header."}), 401
        id_token = auth_header.split("Bearer ")[1].strip()
        try:
            decoded = verify_id_token(id_token)
            request.user = decoded          # expose uid, email, etc.
        except Exception as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Lecture Summarizer API is running."})


@app.route("/api/transcribe", methods=["POST"])
@require_auth
def api_transcribe():
    """
    Accepts a multipart file OR a JSON body with { url, source_type:'url' }.
    Returns: { transcript }
    """
    source_type = request.form.get("source_type") or (
        request.json.get("source_type") if request.is_json else None
    )

    try:
        # ── 1. Paste Text ──────────────────────────────────────────────────
        if source_type == "text":
            data = request.get_json(force=True)
            raw_text = data.get("text", "").strip()
            if not raw_text:
                return jsonify({"error": "No text provided."}), 400
            transcript = transcribe_text_passthrough(raw_text)
            return jsonify({"transcript": transcript, "source_type": "text"})

        # ── 2. YouTube / URL ───────────────────────────────────────────────
        if source_type == "url":
            data = request.get_json(force=True)
            url = data.get("url", "").strip()
            if not url:
                return jsonify({"error": "No URL provided."}), 400
            transcript = transcribe_youtube(url)
            return jsonify({"transcript": transcript, "source_type": "url"})

        # ── 3. File Upload ─────────────────────────────────────────────────
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400
        uploaded_file = request.files["file"]
        if not uploaded_file.filename:
            return jsonify({"error": "Empty filename."}), 400
        if not allowed_file(uploaded_file.filename):
            return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            uploaded_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            transcript = transcribe_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        return jsonify({
            "transcript": transcript,
            "source_type": "file",
            "filename": uploaded_file.filename,
        })

    except Exception as e:
        print(f"[/api/transcribe] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/summarize", methods=["POST"])
@require_auth
def api_summarize():
    """
    Body: { transcript, summary_length, source_type, source_name }
    Saves record to Firestore and returns { summary, record_id }
    """
    try:
        data = request.get_json(force=True)
        transcript    = data.get("transcript", "").strip()
        summary_length = data.get("summary_length", "medium")
        source_type   = data.get("source_type", "text")
        source_name   = data.get("source_name", "")

        if not transcript:
            return jsonify({"error": "No transcript provided."}), 400
        if summary_length not in ("short", "medium", "long"):
            summary_length = "medium"

        summary = summarize_text(transcript, summary_length)

        user_uid   = request.user.get("uid", "")
        user_email = request.user.get("email", "")

        record_id = save_record(
            user_uid=user_uid,
            user_email=user_email,
            transcript=transcript,
            summary=summary,
            source_type=source_type,
            source_name=source_name,
            summary_length=summary_length,
        )

        return jsonify({"summary": summary, "record_id": record_id})

    except Exception as e:
        print(f"[/api/summarize] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/records", methods=["GET"])
@require_auth
def api_records():
    """Return all records for the authenticated user."""
    try:
        user_uid = request.user.get("uid", "")
        records  = get_user_records(user_uid)
        return jsonify({"records": records})
    except Exception as e:
        print(f"[/api/records] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/records/<record_id>", methods=["DELETE"])
@require_auth
def api_delete_record(record_id):
    """Delete a record by ID (must belong to the authenticated user)."""
    try:
        user_uid = request.user.get("uid", "")
        success  = delete_record(record_id, user_uid)
        if not success:
            return jsonify({"error": "Record not found or unauthorized."}), 404
        return jsonify({"success": True})
    except Exception as e:
        print(f"[/api/records DELETE] Error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── Serve Frontend ───────────────────────────────────────────────────────────

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/dashboard")
def serve_dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "1") == "1"
    print(f"[App] Starting Lecture Summarizer on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
