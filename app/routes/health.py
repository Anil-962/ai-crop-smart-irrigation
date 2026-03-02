from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, current_app

from app.services.health_service import calculate_farm_health_score
from app.utils.db import get_db_connection
from app.utils.response import error_response, success_response


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def api_health():
    db_status = "disconnected"
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    payload = {
        "status": "ok",
        "service": current_app.config.get("APP_NAME", "agroguard-ai-backend"),
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return success_response(payload, 200)


@health_bp.get("/health/score")
def get_health_score():
    try:
        return success_response(calculate_farm_health_score(), 200)
    except Exception as exc:
        return error_response(f"Failed to calculate health score: {exc}", 500)


@health_bp.get("/health-score")
def get_health_score_legacy():
    # Backward-compatible alias used by older tests/clients.
    return get_health_score()

