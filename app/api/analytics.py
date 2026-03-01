import logging
import traceback
from flask import Blueprint, request
from app.services.analytics_service import get_analytics_data
from app.utils.response import success_response, error_response

analytics_bp = Blueprint("analytics", __name__)
logger = logging.getLogger(__name__)

@analytics_bp.get("")
@analytics_bp.get("/")
def analytics_status():
    try:
        zone_raw = (request.args.get("zone_id") or "all").strip().lower()
        zone_id = None
        if zone_raw and zone_raw != "all":
            try:
                zone_id = int(zone_raw)
            except ValueError:
                return error_response("zone_id must be an integer or 'all'", 400)

        days = request.args.get("days", default=7, type=int)
        if days <= 0:
            return error_response("days must be a positive integer", 400)
        
        logger.debug("Fetching analytics data for zone %s over %s days", zone_raw, days)
        data = get_analytics_data(zone_id, days)
        return success_response(data, 200)
    except Exception as e:
        logger.error("Error in analytics_status: %s", traceback.format_exc())
        return error_response(f"Failed to fetch analytics data: {str(e)}", 500)

