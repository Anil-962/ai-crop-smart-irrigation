from flask import Blueprint, current_app, request

from app.services.decision_service import build_recommendations
from app.services.factory import get_disease_predictor, get_irrigation_predictor
from app.services.weather_service import fetch_rain_forecast_mm_24h
from app.utils.errors import ValidationError
from app.utils.images import decode_base64_image
from app.utils.validation import validate_irrigation_payload
from app.utils.response import success_response, error_response

decision_bp = Blueprint("decision", __name__)


@decision_bp.post("/combined")
def combined_decision():
    try:
        payload = request.get_json(silent=True) or {}
        sensor_data = payload.get("sensor_data", {})
        location = payload.get("location", {})
        image_base64 = payload.get("image_base64")

        if "rain_forecast_mm_24h" not in sensor_data:
            lat = location.get("latitude")
            lon = location.get("longitude")
            if lat is not None and lon is not None:
                sensor_data["rain_forecast_mm_24h"] = fetch_rain_forecast_mm_24h(
                    lat=lat,
                    lon=lon,
                    base_url=current_app.config["WEATHER_API_BASE_URL"],
                    timeout_seconds=current_app.config["WEATHER_TIMEOUT_SECONDS"],
                )
            else:
                sensor_data["rain_forecast_mm_24h"] = 0.0

        cleaned = validate_irrigation_payload(sensor_data)

        if image_base64:
            image_bytes = decode_base64_image(image_base64)
            disease = get_disease_predictor(
                current_app.config["DISEASE_MODEL_PATH"],
                current_app.config["DISEASE_LABELS_PATH"],
            ).predict(image_bytes)
        else:
            disease = {
                "disease_name": "Unknown",
                "confidence": 0.0,
                "suggested_treatment": "Upload leaf image for disease diagnosis.",
                "model": "none",
            }

        irrigation = get_irrigation_predictor(current_app.config["IRRIGATION_MODEL_PATH"]).predict(cleaned)
        recommendations = build_recommendations(
            disease_name=disease["disease_name"],
            crop_type=cleaned["crop_type"],
            rain_forecast_mm_24h=cleaned["rain_forecast_mm_24h"],
        )

        return success_response(
            {
                "disease": disease,
                "irrigation": irrigation,
                "recommendations": recommendations,
            },
            200
        )
    except ValidationError as err:
        return error_response(str(err), 400)
    except Exception as err:
        return error_response(f"Unexpected server error: {err}", 500)
