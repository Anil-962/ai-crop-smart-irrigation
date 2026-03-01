from flask import Blueprint, render_template, request
from app.utils.response import error_response

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route("/health")
def health():
    return {"status": "ok"}, 200

@main_bp.route("/<path:path>")
def serve_spa(path):
    if path.startswith("api/"):
        return error_response("Endpoint not found", 404)
    return render_template("index.html")
