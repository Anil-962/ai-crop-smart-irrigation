from __future__ import annotations

from typing import Any

from flask import Blueprint, current_app, request

from app.services.factory import get_disease_predictor, get_irrigation_predictor
from app.utils.errors import ValidationError
from app.utils.images import extract_image_bytes
from app.utils.response import error_response, success_response
from app.utils.validation import validate_irrigation_payload


predict_bp = Blueprint("predict", __name__)


@predict_bp.post("/predict/disease")
def predict_disease() -> Any:
    try:
        image_bytes = extract_image_bytes(request)
        predictor = get_disease_predictor(
            model_path=current_app.config["DISEASE_MODEL_PATH"],
            labels_path=current_app.config["DISEASE_LABELS_PATH"],
        )
        prediction = predictor.predict(image_bytes)
        print("Prediction result:", prediction)
        return success_response(prediction, 200)
    except ValidationError as exc:
        return error_response(str(exc), 400)
    except Exception as exc:
        return error_response(f"Disease prediction failed: {exc}", 500)


@predict_bp.post("/predict/irrigation")
def predict_irrigation() -> Any:
    payload = request.get_json(silent=True) or {}
    try:
        cleaned = validate_irrigation_payload(payload)
        predictor = get_irrigation_predictor(model_path=current_app.config["IRRIGATION_MODEL_PATH"])
        result = predictor.predict(cleaned)
        return success_response(result, 200)
    except ValidationError as exc:
        return error_response(str(exc), 400)
    except Exception as exc:
        return error_response(f"Irrigation prediction failed: {exc}", 500)
