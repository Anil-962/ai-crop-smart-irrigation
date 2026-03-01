from flask import Blueprint, current_app, request

from app.services.factory import get_disease_predictor, get_irrigation_predictor
from app.utils.errors import ValidationError
from app.utils.images import extract_image_bytes
from app.utils.validation import validate_irrigation_payload
from app.utils.response import success_response, error_response

predict_bp = Blueprint("predict", __name__)


@predict_bp.post("/disease")
def predict_disease():
    try:
        image_bytes = extract_image_bytes(request)
        predictor = get_disease_predictor(
            current_app.config["DISEASE_MODEL_PATH"],
            current_app.config["DISEASE_LABELS_PATH"],
        )
        result = predictor.predict(image_bytes)
        return success_response(result, 200)
    except ValidationError as err:
        return error_response(str(err), 400)
    except Exception as err:
        return error_response(f"Unexpected server error: {err}", 500)


@predict_bp.post("/irrigation")
def predict_irrigation():
    try:
        payload = request.get_json(silent=True) or {}
        cleaned = validate_irrigation_payload(payload)
        predictor = get_irrigation_predictor(current_app.config["IRRIGATION_MODEL_PATH"])
        result = predictor.predict(cleaned)
        return success_response(result, 200)
    except ValidationError as err:
        return error_response(str(err), 400)
    except Exception as err:
        return error_response(f"Unexpected server error: {err}", 500)
