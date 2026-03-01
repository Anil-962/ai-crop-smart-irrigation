import logging
import traceback
from flask import Blueprint, current_app, request
from app.services.dashboard_service import get_dashboard_data
from app.utils.response import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.get("/", strict_slashes=False)
def dashboard_status():
    try:
        logger.debug("Fetching dashboard data")
        zone_raw = (request.args.get("zone_id") or "all").strip().lower()
        zone_id = None
        if zone_raw and zone_raw != "all":
            try:
                zone_id = int(zone_raw)
            except ValueError:
                return error_response("zone_id must be an integer or 'all'", 400)

        weather_config = {
            "base_url": current_app.config.get("WEATHER_API_BASE_URL", ""),
            "timeout_seconds": current_app.config.get("WEATHER_TIMEOUT_SECONDS", 5),
        }
        data = get_dashboard_data(zone_id=zone_id, weather_config=weather_config)
        return success_response(data, 200)
    except Exception as e:
        logger.error("Error in dashboard_status: %s", traceback.format_exc())
        return error_response(f"Failed to fetch dashboard data: {str(e)}", 500)
