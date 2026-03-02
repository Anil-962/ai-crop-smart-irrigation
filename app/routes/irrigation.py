from __future__ import annotations

from typing import Any

from flask import Blueprint, request

from app.utils.db import get_db_connection
from app.utils.response import error_response, success_response


irrigation_bp = Blueprint("irrigation", __name__)


@irrigation_bp.post("/irrigation/control")
def control_irrigation() -> Any:
    payload = request.get_json(silent=True) or {}

    try:
        zone_id = int(payload.get("zone_id"))
    except (TypeError, ValueError):
        return error_response("zone_id is required and must be an integer.", 400)

    action = str(payload.get("action", "")).strip().lower()
    if action not in {"start", "stop"}:
        return error_response("action must be either 'start' or 'stop'.", 400)

    mode = str(payload.get("mode", "")).strip().lower()
    if mode not in {"auto", "manual"}:
        return error_response("mode must be either 'auto' or 'manual'.", 400)

    try:
        flow_rate = float(payload.get("flow_rate", 0))
    except (TypeError, ValueError):
        return error_response("flow_rate must be numeric.", 400)

    flow_rate = max(0.0, min(100.0, flow_rate))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM zones WHERE id = ?", (zone_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return error_response(f"Zone {zone_id} not found.", 404)

    cursor.execute("UPDATE zones SET irrigation_mode = ? WHERE id = ?", (mode, zone_id))
    conn.commit()
    conn.close()

    response = {
        "status": "success",
        "zone_id": zone_id,
        "zone_status": "active" if action == "start" else "idle",
        "action": action,
        "current_mode": mode,
        "flow_rate": round(flow_rate, 1),
        "message": f"Zone {zone_id} irrigation {action}ed in {mode} mode.",
    }
    return success_response(response, 200)

