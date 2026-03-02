from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flask import Blueprint, request

from app.services.alert_service import check_and_generate_alerts
from app.utils.db import get_db_connection
from app.utils.response import error_response, success_response


alerts_bp = Blueprint("alerts", __name__)


def _parse_zone_id(raw_value: Optional[str]) -> Optional[int]:
    if raw_value is None or str(raw_value).strip() == "":
        return None
    if str(raw_value).lower() == "all":
        return None
    return int(raw_value)


def _to_alert_payload(row: Any) -> Dict[str, Any]:
    resolved = bool(row["is_resolved"])
    return {
        "id": row["id"],
        "type": row["type"] or "info",
        "message": row["message"] or "",
        "zone_id": row["zone_id"],
        "is_resolved": resolved,
        "resolved": resolved,
        "created_at": row["created_at"],
        "resolved_at": row["resolved_at"],
        "timestamp": row["created_at"],
    }


@alerts_bp.get("/alerts")
def get_alerts() -> Any:
    try:
        zone_id = _parse_zone_id(request.args.get("zone_id"))
    except (TypeError, ValueError):
        return error_response("zone_id must be an integer or 'all'.", 400)

    try:
        check_and_generate_alerts()
    except Exception:
        # Continue even if alert generation fails; existing alerts can still be returned.
        pass

    conn = get_db_connection()
    cursor = conn.cursor()

    if zone_id is None:
        cursor.execute(
            """
            SELECT id, type, message, zone_id, is_resolved, created_at, resolved_at
            FROM alerts
            ORDER BY created_at DESC, id DESC
            """
        )
    else:
        cursor.execute(
            """
            SELECT id, type, message, zone_id, is_resolved, created_at, resolved_at
            FROM alerts
            WHERE zone_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (zone_id,),
        )

    rows = cursor.fetchall()
    conn.close()

    payload: List[Dict[str, Any]] = [_to_alert_payload(row) for row in rows]
    return success_response(payload, 200)


def _resolve_by_id(alert_id: int) -> Any:
    conn = get_db_connection()
    cursor = conn.cursor()
    resolved_at = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        UPDATE alerts
        SET is_resolved = 1, resolved_at = ?
        WHERE id = ? AND is_resolved = 0
        """,
        (resolved_at, alert_id),
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return error_response("Alert not found or already resolved.", 404)

    cursor.execute(
        """
        SELECT id, type, message, zone_id, is_resolved, created_at, resolved_at
        FROM alerts
        WHERE id = ?
        """,
        (alert_id,),
    )
    row = cursor.fetchone()
    conn.close()

    return success_response(_to_alert_payload(row), 200)


@alerts_bp.post("/alerts/<int:alert_id>/resolve")
def resolve_alert(alert_id: int) -> Any:
    return _resolve_by_id(alert_id)


@alerts_bp.post("/alerts/resolve/<int:alert_id>")
def resolve_alert_legacy(alert_id: int) -> Any:
    # Backward-compatible alias used by older tests/clients.
    return _resolve_by_id(alert_id)

