from functools import lru_cache

from app.services.disease_service import DiseasePredictor
from app.services.irrigation_service import IrrigationPredictor


@lru_cache(maxsize=1)
def get_disease_predictor(model_path: str, labels_path: str) -> DiseasePredictor:
    return DiseasePredictor(model_path=model_path, labels_path=labels_path)


@lru_cache(maxsize=1)
def get_irrigation_predictor(model_path: str) -> IrrigationPredictor:
    return IrrigationPredictor(model_path=model_path)
