from flask import jsonify
from datetime import datetime, timezone

def success_response(data=None, status_code=200):
    """
    Returns a standardized JSON success response.
    """
    payload = {
        "success": True,
        "data": data,
        "error": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(payload), status_code

def error_response(message="An error occurred", status_code=400):
    """
    Returns a standardized JSON error response.
    """
    payload = {
        "success": False,
        "data": None,
        "error": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(payload), status_code
