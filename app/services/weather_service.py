from typing import Optional

import requests


def fetch_rain_forecast_mm_24h(
    lat: float,
    lon: float,
    base_url: str,
    timeout_seconds: float,
) -> Optional[float]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation",
        "forecast_days": 1,
    }
    try:
        response = requests.get(base_url, params=params, timeout=timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        hourly = payload.get("hourly", {})
        precip = hourly.get("precipitation", [])
        if not precip:
            return 0.0
        return round(float(sum(precip[:24])), 2)
    except Exception:
        return None
