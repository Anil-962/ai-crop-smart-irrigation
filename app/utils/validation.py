from app.utils.errors import ValidationError


REQUIRED_FIELDS = [
    "soil_moisture_pct",
    "temperature_c",
    "humidity_pct",
    "crop_type",
    "growth_stage",
]


def _to_float(payload: dict, key: str, default=None) -> float:
    value = payload.get(key, default)
    if value is None:
        raise ValidationError(f"Missing required field: {key}")
    try:
        return float(value)
    except (TypeError, ValueError) as err:
        raise ValidationError(f"Field '{key}' must be numeric.") from err


def _to_str(payload: dict, key: str) -> str:
    value = payload.get(key)
    if value is None or str(value).strip() == "":
        raise ValidationError(f"Missing required field: {key}")
    return str(value).strip()


def validate_irrigation_payload(payload: dict) -> dict:
    for field in REQUIRED_FIELDS:
        if field not in payload:
            raise ValidationError(f"Missing required field: {field}")

    cleaned = {
        "soil_moisture_pct": _to_float(payload, "soil_moisture_pct"),
        "temperature_c": _to_float(payload, "temperature_c"),
        "humidity_pct": _to_float(payload, "humidity_pct"),
        "crop_type": _to_str(payload, "crop_type"),
        "growth_stage": _to_str(payload, "growth_stage"),
    }

    rain = payload.get("rain_forecast_mm_24h", 0.0)
    try:
        cleaned["rain_forecast_mm_24h"] = 0.0 if rain is None else float(rain)
    except (TypeError, ValueError) as err:
        raise ValidationError("Field 'rain_forecast_mm_24h' must be numeric.") from err

    _validate_ranges(cleaned)
    return cleaned


def _validate_ranges(cleaned: dict) -> None:
    if not (0 <= cleaned["soil_moisture_pct"] <= 100):
        raise ValidationError("soil_moisture_pct must be between 0 and 100.")
    if not (-20 <= cleaned["temperature_c"] <= 70):
        raise ValidationError("temperature_c must be between -20 and 70.")
    if not (0 <= cleaned["humidity_pct"] <= 100):
        raise ValidationError("humidity_pct must be between 0 and 100.")
    if not (0 <= cleaned["rain_forecast_mm_24h"] <= 500):
        raise ValidationError("rain_forecast_mm_24h must be between 0 and 500.")
