def build_recommendations(disease_name: str, crop_type: str, rain_forecast_mm_24h: float) -> dict:
    fertilizer = _fertilizer_suggestion(crop_type, disease_name)
    weather_alert = _weather_alert(rain_forecast_mm_24h)
    return {
        "fertilizer_suggestion": fertilizer,
        "weather_alert": weather_alert,
    }


def _fertilizer_suggestion(crop_type: str, disease_name: str) -> str:
    crop = (crop_type or "").lower()
    disease = (disease_name or "").lower()

    if "blight" in disease or "spot" in disease or "mildew" in disease:
        return "Pause heavy nitrogen use and prioritize disease management."

    if crop in {"tomato", "potato"}:
        return "Apply balanced NPK in split doses."
    if crop in {"rice", "wheat", "maize", "corn"}:
        return "Apply nitrogen in two splits and monitor leaf color."
    if crop in {"strawberry", "grape"}:
        return "Use potassium-rich fertilizer during fruiting phase."
    if crop in {"coffee", "cucumber"}:
        return "Maintain regular micronutrient supply and organic mulch."
    return "Use soil-test-based fertilizer plan."


def _weather_alert(rain_forecast_mm_24h: float) -> str:
    if rain_forecast_mm_24h is None:
        return "Weather data unavailable. Use local forecast for planning."
    if rain_forecast_mm_24h >= 10.0:
        return "Moderate to heavy rain expected in next 24h."
    if rain_forecast_mm_24h >= 1.0:
        return "Light rain expected in next 24h."
    return "No significant rain expected in next 24h."
