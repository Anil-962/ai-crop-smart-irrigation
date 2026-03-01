import logging
import traceback
from flask import Blueprint, current_app, jsonify
from datetime import datetime, timezone
from app.utils.db import get_db_connection
from app.utils.response import success_response, error_response
from app.services.health_service import calculate_farm_health_score

health_bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)

@health_bp.get("/status")
def health_check():
    return success_response({"status": "ok", "service": current_app.config.get("APP_NAME", "agroguard-ai-backend")}, 200)


@health_bp.get("", strict_slashes=False)
@health_bp.get("/", strict_slashes=False)
def api_health():
    """
    Detailed health check including database connectivity.
    """
    db_status = "disconnected"
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        logger.error("Database health check failed: %s", traceback.format_exc())
    
    return jsonify({
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@health_bp.get("/index")
def index():
    return success_response(
        {
            "app": current_app.config.get("APP_NAME", "AgriPulse AI"),
            "status": "online",
            "endpoints": ["/api/health", "/api/predict/disease", "/api/predict/irrigation", "/api/health/score"],
        }, 
        200
    )


@health_bp.get("/score", strict_slashes=False)
def get_health_score():
    try:
        logger.debug("Calculating farm health score")
        response = calculate_farm_health_score()
        return success_response(response, 200)
    except Exception as e:
        logger.error("Error in get_health_score: %s", traceback.format_exc())
        return error_response(f"Failed to calculate health score: {str(e)}", 500)
