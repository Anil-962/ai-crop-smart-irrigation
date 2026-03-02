from __future__ import annotations

from typing import Optional

from flask import Blueprint, request

from app.services.analytics_service import get_analytics_data
from app.utils.response import error_response, success_response


analytics_bp = Blueprint("analytics", __name__)


def _parse_zone_id(raw_value: Optional[str]) -> Optional[int]:
    if raw_value is None or str(raw_value).strip() == "":
        return None
    if str(raw_value).lower() == "all":
        return None
    return int(raw_value)


@analytics_bp.get("/analytics")
def analytics_data():
    try:
        zone_id = _parse_zone_id(request.args.get("zone_id"))
    except (TypeError, ValueError):
        return error_response("zone_id must be an integer or 'all'.", 400)

    try:
        days = int(request.args.get("days", 7))
    except (TypeError, ValueError):
        return error_response("days must be an integer.", 400)

    if days <= 0 or days > 365:
        return error_response("days must be between 1 and 365.", 400)

    try:
        payload = get_analytics_data(zone_id=zone_id, days=days)
        return success_response(payload, 200)
    except Exception as exc:
        return error_response(f"Failed to load analytics data: {exc}", 500)

