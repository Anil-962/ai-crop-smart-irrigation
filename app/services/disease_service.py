import io
import json
import os
from typing import Any

import numpy as np
from PIL import Image


DISEASE_LABELS = [
    "Healthy",
    "Early Blight",
    "Late Blight",
    "Leaf Spot",
    "Powdery Mildew",
    "Bacterial Head Rot",
    "Yellow Leaf Curl",
]

TREATMENT_MAP = {
    "Healthy": "No disease symptoms detected.",
    "Early Blight": "Apply copper-based fungicide and remove infected leaves.",
    "Late Blight": "Use systemic fungicide and avoid overhead irrigation.",
    "Leaf Spot": "Remove damaged leaves and improve field air circulation.",
    "Powdery Mildew": "Use sulfur-based treatment and monitor humidity closely.",
    "Bacterial Head Rot": "Apply bactericide and reduce overhead water application.",
    "Yellow Leaf Curl": "Control whiteflies and use resistant crop varieties.",
}


class DiseasePredictor:
    def __init__(self, model_path: str, labels_path: str):
        self.model_path = model_path
        self.labels_path = labels_path
        self.model: Any = None
        self.labels = DISEASE_LABELS
        self.backend = "mobilenetv2_stub"
        self._load_labels_if_available()
        self._load_model_if_available()

    def _load_labels_if_available(self) -> None:
        if not os.path.exists(self.labels_path):
            return
        try:
            with open(self.labels_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            labels = payload.get("classes", [])
            if isinstance(labels, list) and labels:
                self.labels = [str(x) for x in labels]
        except Exception:
            self.labels = DISEASE_LABELS

    def _load_model_if_available(self) -> None:
        if not os.path.exists(self.model_path):
            return
        try:
            import tensorflow as tf  # type: ignore

            self.model = tf.keras.models.load_model(self.model_path)
            self.backend = "mobilenetv2_loaded"
        except Exception:
            self.model = None
            self.backend = "mobilenetv2_stub"

    @staticmethod
    def _read_image(image_bytes: bytes) -> Image.Image:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image

    def _predict_stub(self, image: Image.Image) -> tuple[str, float]:
        arr = np.asarray(image.resize((224, 224)), dtype=np.float32)
        red_mean = float(arr[:, :, 0].mean())
        green_mean = float(arr[:, :, 1].mean())
        blue_mean = float(arr[:, :, 2].mean())

        # Improved heuristic for leaf conditions
        if green_mean > red_mean + 10 and green_mean > blue_mean + 10:
            return "Healthy", 0.88
        if red_mean > 160 and green_mean < 120:
            return "Late Blight", 0.76
        if red_mean > 140 and green_mean > 140 and blue_mean < 100:
            return "Yellow Leaf Curl", 0.72
        if red_mean > green_mean + 15:
            return "Leaf Spot", 0.71
        if blue_mean > green_mean + 15:
            return "Bacterial Head Rot", 0.68
        if abs(red_mean - green_mean) < 10 and abs(green_mean - blue_mean) < 10:
            return "Powdery Mildew", 0.62
        return "Early Blight", 0.65

    def _predict_model(self, image: Image.Image) -> tuple[str, float]:
        arr = np.asarray(image.resize((224, 224)), dtype=np.float32) / 255.0
        batch = np.expand_dims(arr, axis=0)
        probs = self.model.predict(batch, verbose=0)[0]
        idx = int(np.argmax(probs))
        if idx >= len(self.labels):
            return "Unknown", float(probs[idx])
        return self.labels[idx], float(probs[idx])

    def predict(self, image_bytes: bytes) -> dict:
        if not image_bytes:
            raise ValueError("Empty image payload.")

        image = self._read_image(image_bytes)

        if self.model is not None:
            disease_name, confidence = self._predict_model(image)
        else:
            disease_name, confidence = self._predict_stub(image)

        return {
            "prediction": disease_name,
            "confidence": round(confidence, 4),
            "treatment_suggestion": TREATMENT_MAP.get(disease_name, "Consult local agronomist."),
            "model": self.backend,
        }
