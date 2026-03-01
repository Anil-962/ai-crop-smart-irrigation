import os
from typing import Any

import joblib
import numpy as np


CROP_MAP = {
    "tomato": 0,
    "potato": 1,
    "rice": 2,
    "wheat": 3,
    "maize": 4,
    "cotton": 5,
    "chili": 6,
    "corn": 7,
    "strawberry": 8,
    "grape": 9,
    "coffee": 10,
    "cucumber": 11,
}

STAGE_MAP = {
    "seedling": 0,
    "vegetative": 1,
    "flowering": 2,
    "fruiting": 3,
    "maturity": 4,
}


class IrrigationPredictor:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model: Any = None
        self.backend = "xgboost_stub"
        self._load_model_if_available()

    def _load_model_if_available(self) -> None:
        if not os.path.exists(self.model_path):
            return
        try:
            self.model = joblib.load(self.model_path)
            self.backend = "xgboost_loaded"
        except Exception:
            self.model = None
            self.backend = "xgboost_stub"

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(value, high))

    def _encode(self, payload: dict) -> np.ndarray:
        crop_id = CROP_MAP.get(payload["crop_type"].lower(), -1)
        stage_id = STAGE_MAP.get(payload["growth_stage"].lower(), -1)

        features = np.array(
            [
                payload["soil_moisture_pct"],
                payload["temperature_c"],
                payload["humidity_pct"],
                payload["rain_forecast_mm_24h"],
                crop_id,
                stage_id,
            ],
            dtype=np.float32,
        )
        return features.reshape(1, -1)

    def _predict_stub(self, payload: dict) -> float:
        soil = payload["soil_moisture_pct"]
        temp = payload["temperature_c"]
        humidity = payload["humidity_pct"]
        rain = payload["rain_forecast_mm_24h"]

        dryness_score = (100.0 - soil) * 0.35 + temp * 0.45 - humidity * 0.15 - rain * 0.8
        liters = dryness_score / 2.5
        return self._clamp(liters, 0.0, 40.0)

    def _predict_model(self, payload: dict) -> float:
        features = self._encode(payload)
        pred = float(self.model.predict(features)[0])
        return self._clamp(pred, 0.0, 60.0)

    def predict(self, payload: dict) -> dict:
        liters = self._predict_model(payload) if self.model is not None else self._predict_stub(payload)
        irrigate_now = liters >= 2.0

        return {
            "irrigate_now": bool(irrigate_now),
            "recommended_liters": round(liters, 2),
            "model": self.backend,
        }
