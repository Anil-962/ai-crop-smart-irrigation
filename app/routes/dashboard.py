from __future__ import annotations

from typing import Optional

from flask import Blueprint, current_app, request

from app.services.dashboard_service import get_dashboard_data
from app.utils.response import error_response, success_response


dashboard_bp = Blueprint("dashboard", __name__)


def _parse_zone_id(raw_value: Optional[str]) -> Optional[int]:
    if raw_value is None or str(raw_value).strip() == "":
        return None
    if str(raw_value).lower() == "all":
        return None
    return int(raw_value)


@dashboard_bp.get("/dashboard")
def dashboard_data():
    try:
        zone_id = _parse_zone_id(request.args.get("zone_id"))
    except (TypeError, ValueError):
        return error_response("zone_id must be an integer or 'all'.", 400)

    weather_config = {
        "base_url": current_app.config.get("WEATHER_API_BASE_URL", ""),
        "timeout_seconds": current_app.config.get("WEATHER_TIMEOUT_SECONDS", 5),
    }

    try:
        payload = get_dashboard_data(zone_id=zone_id, weather_config=weather_config)
        return success_response(payload, 200)
    except Exception as exc:
        return error_response(f"Failed to load dashboard data: {exc}", 500)

