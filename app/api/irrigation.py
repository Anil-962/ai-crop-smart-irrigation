from flask import Blueprint, request
from app.utils.errors import ValidationError
from app.utils.response import success_response, error_response

irrigation_bp = Blueprint("irrigation", __name__)

@irrigation_bp.post("/control")
def control_irrigation():
    try:
        data = request.get_json(silent=True) or {}
        
        # Validation
        zone_id = data.get("zone_id")
        mode = data.get("mode")
        action = data.get("action")
        flow_rate = data.get("flow_rate")

        if zone_id is None:
            raise ValidationError("zone_id is required")
        if mode not in ["auto", "manual"]:
            raise ValidationError("mode must be 'auto' or 'manual'")
        if action not in ["start", "stop"]:
            raise ValidationError("action must be 'start' or 'stop'")
        if not isinstance(flow_rate, (int, float)) or not (0 <= flow_rate <= 100):
            raise ValidationError("flow_rate must be a number between 0 and 100")

        # Mock logic to simulate success
        # In a real scenario, this would interface with hardware/IoT services
        return success_response({
            "status": "success",
            "current_mode": mode,
            "zone_status": "active" if action == "start" else "idle"
        }, 200)

    except ValidationError as err:
        return error_response(str(err), 400)
    except Exception as err:
        return error_response(f"Internal server error: {err}", 500)
