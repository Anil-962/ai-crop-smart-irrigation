from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.weather_service import fetch_rain_forecast_mm_24h
from app.utils.db import get_db_connection


FALLBACK_ZONE_LOCATIONS: Dict[int, Dict[str, Any]] = {
    1: {"name": "Zone 1 (North)", "location": "North Field", "latitude": 17.5204, "longitude": 78.4080},
    2: {"name": "Zone 2 (East)", "location": "East Field", "latitude": 17.5161, "longitude": 78.4472},
    3: {"name": "Zone 3 (South)", "location": "South Field", "latitude": 17.4842, "longitude": 78.4312},
    4: {"name": "Zone 4 (West)", "location": "West Field", "latitude": 17.5068, "longitude": 78.3892},
    5: {"name": "Zone 5 (Center)", "location": "Central Hub", "latitude": 17.5023, "longitude": 78.4197},
}

FALLBACK_METRICS_BY_ZONE: Dict[int, Dict[str, float]] = {
    1: {"humidity": 66.0, "temperature": 28.6, "soil_moisture": 48.0, "water_level": 74.0},
    2: {"humidity": 62.0, "temperature": 29.1, "soil_moisture": 41.0, "water_level": 71.0},
    3: {"humidity": 64.0, "temperature": 27.8, "soil_moisture": 52.0, "water_level": 76.0},
    4: {"humidity": 59.0, "temperature": 31.0, "soil_moisture": 33.0, "water_level": 65.0},
    5: {"humidity": 63.0, "temperature": 28.2, "soil_moisture": 45.0, "water_level": 69.0},
}


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _metric_status(metric: str, value: float) -> str:
    if metric == "temperature":
        if value >= 36 or value <= 10:
            return "critical"
        if value >= 32 or value <= 15:
            return "warning"
        if 22 <= value <= 30:
            return "optimal"
        return "normal"
    if metric == "humidity":
        if value < 30 or value > 85:
            return "warning"
        if 45 <= value <= 75:
            return "optimal"
        return "normal"
    if metric == "soil_moisture":
        if value < 25:
            return "critical"
        if value < 40:
            return "warning"
        if 45 <= value <= 70:
            return "optimal"
        return "normal"
    if metric == "water_level":
        if value < 20:
            return "critical"
        if value < 35:
            return "warning"
        if value >= 60:
            return "good"
        return "normal"
    return "normal"


def _avg(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _fallback_zone(zone_id: int) -> Dict[str, Any]:
    loc = FALLBACK_ZONE_LOCATIONS.get(zone_id, {})
    defaults = FALLBACK_METRICS_BY_ZONE.get(zone_id, FALLBACK_METRICS_BY_ZONE[1])
    return {
        "id": zone_id,
        "name": loc.get("name", f"Zone {zone_id}"),
        "location": loc.get("location", f"Field {zone_id}"),
        "irrigation_mode": "auto" if zone_id % 2 == 1 else "manual",
        "humidity": defaults["humidity"],
        "temperature": defaults["temperature"],
        "soil_moisture": defaults["soil_moisture"],
        "water_level": defaults["water_level"],
        "created_at": None,
        "latitude": loc.get("latitude"),
        "longitude": loc.get("longitude"),
    }


def _fetch_zone_snapshots(zone_id: Optional[int]) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if zone_id is None:
        cursor.execute(
            """
            SELECT
                z.id,
                z.name,
                z.irrigation_mode,
                lr.humidity,
                lr.temperature,
                lr.soil_moisture,
                lr.water_level,
                lr.created_at
            FROM zones z
            LEFT JOIN sensor_readings lr ON lr.id = (
                SELECT sr.id
                FROM sensor_readings sr
                WHERE sr.zone_id = z.id
                ORDER BY sr.created_at DESC, sr.id DESC
                LIMIT 1
            )
            ORDER BY z.id
            """
        )
    else:
        cursor.execute(
            """
            SELECT
                z.id,
                z.name,
                z.irrigation_mode,
                lr.humidity,
                lr.temperature,
                lr.soil_moisture,
                lr.water_level,
                lr.created_at
            FROM zones z
            LEFT JOIN sensor_readings lr ON lr.id = (
                SELECT sr.id
                FROM sensor_readings sr
                WHERE sr.zone_id = z.id
                ORDER BY sr.created_at DESC, sr.id DESC
                LIMIT 1
            )
            WHERE z.id = ?
            ORDER BY z.id
            """,
            (zone_id,),
        )
    rows = cursor.fetchall()
    conn.close()

    snapshots: List[Dict[str, Any]] = []
    for row in rows:
        loc = FALLBACK_ZONE_LOCATIONS.get(row["id"], {})
        defaults = FALLBACK_METRICS_BY_ZONE.get(row["id"], FALLBACK_METRICS_BY_ZONE[1])
        snapshots.append(
            {
                "id": row["id"],
                "name": row["name"] or loc.get("name", f"Zone {row['id']}"),
                "location": loc.get("location", f"Field {row['id']}"),
                "irrigation_mode": row["irrigation_mode"] or "manual",
                "humidity": _safe_float(row["humidity"], defaults["humidity"]),
                "temperature": _safe_float(row["temperature"], defaults["temperature"]),
                "soil_moisture": _safe_float(row["soil_moisture"], defaults["soil_moisture"]),
                "water_level": _safe_float(row["water_level"], defaults["water_level"]),
                "created_at": row["created_at"],
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
            }
        )

    if not snapshots:
        if zone_id is not None:
            return [_fallback_zone(zone_id)]
        return [_fallback_zone(i) for i in sorted(FALLBACK_ZONE_LOCATIONS.keys())]
    return snapshots


def _compute_trend(zone_id: Optional[int], metric: str) -> float:
    conn = get_db_connection()
    cursor = conn.cursor()
    if zone_id is None:
        delta_values: List[float] = []
        cursor.execute("SELECT id FROM zones ORDER BY id")
        zone_rows = cursor.fetchall()
        for z in zone_rows:
            cursor.execute(
                f"""
                SELECT {metric}
                FROM sensor_readings
                WHERE zone_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT 2
                """,
                (z["id"],),
            )
            readings = cursor.fetchall()
            if len(readings) == 2 and readings[0][metric] is not None and readings[1][metric] is not None:
                delta_values.append(float(readings[0][metric]) - float(readings[1][metric]))
        conn.close()
        return round(_avg(delta_values), 1) if delta_values else 0.0

    cursor.execute(
        f"""
        SELECT {metric}
        FROM sensor_readings
        WHERE zone_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 2
        """,
        (zone_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    if len(rows) < 2:
        return 0.0
    current = rows[0][metric]
    previous = rows[1][metric]
    if current is None or previous is None:
        return 0.0
    return round(float(current) - float(previous), 1)


def _alerts_count(zone_id: Optional[int]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    if zone_id is None:
        cursor.execute("SELECT COUNT(*) AS c FROM alerts WHERE is_resolved = 0")
    else:
        cursor.execute("SELECT COUNT(*) AS c FROM alerts WHERE is_resolved = 0 AND zone_id = ?", (zone_id,))
    row = cursor.fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def _build_weather(
    zone_id: Optional[int],
    snapshots: List[Dict[str, Any]],
    weather_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if zone_id is not None:
        anchor = snapshots[0]
        location_label = anchor["location"]
        temp = round(anchor["temperature"], 1)
        humidity = int(round(anchor["humidity"]))
        lat = anchor.get("latitude")
        lon = anchor.get("longitude")
    else:
        location_label = "All Locations"
        temp = round(_avg([z["temperature"] for z in snapshots]), 1)
        humidity = int(round(_avg([z["humidity"] for z in snapshots])))
        lat = _avg([z.get("latitude") for z in snapshots if z.get("latitude") is not None])
        lon = _avg([z.get("longitude") for z in snapshots if z.get("longitude") is not None])

    wind = round(7.5 + (temp - 20) * 0.25, 1)
    rain_forecast = None
    source = "sensor-estimate"

    if weather_config and lat and lon:
        rain_forecast = fetch_rain_forecast_mm_24h(
            lat=lat,
            lon=lon,
            base_url=weather_config.get("base_url", ""),
            timeout_seconds=float(weather_config.get("timeout_seconds", 5)),
        )
        if rain_forecast is not None:
            source = "open-meteo"

    return {
        "location": location_label,
        "temp": temp,
        "humidity": humidity,
        "wind": wind,
        "rain_forecast_mm_24h": 0.0 if rain_forecast is None else rain_forecast,
        "source": source,
    }


def get_dashboard_data(
    zone_id: Optional[int] = None,
    weather_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    all_snapshots = _fetch_zone_snapshots(zone_id=None)
    active_snapshots = all_snapshots
    if zone_id is not None:
        filtered = [zone for zone in all_snapshots if zone["id"] == zone_id]
        if filtered:
            active_snapshots = filtered

    humidity = round(_avg([z["humidity"] for z in active_snapshots]), 1)
    temperature = round(_avg([z["temperature"] for z in active_snapshots]), 1)
    soil_moisture = round(_avg([z["soil_moisture"] for z in active_snapshots]), 1)
    water_level = round(_avg([z["water_level"] for z in active_snapshots]), 1)

    response_zones: List[Dict[str, Any]] = []
    for zone in all_snapshots:
        soil_value = round(zone["soil_moisture"], 1)
        response_zones.append(
            {
                "id": zone["id"],
                "name": zone["name"],
                "location": zone["location"],
                "status": _metric_status("soil_moisture", soil_value),
                "mode": "Auto" if zone["irrigation_mode"] == "auto" else "Manual",
                "moisture": soil_value,
                "last_updated": zone["created_at"],
            }
        )

    selected_zone = None
    if zone_id is not None and active_snapshots:
        selected_zone = {
            "id": active_snapshots[0]["id"],
            "name": active_snapshots[0]["name"],
            "location": active_snapshots[0]["location"],
        }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_status": "online",
        "selected_zone": selected_zone or {"id": "all", "name": "All Zones", "location": "Farm-wide"},
        "metrics": {
            "humidity": {
                "value": humidity,
                "unit": "%",
                "trend": _compute_trend(zone_id, "humidity"),
                "status": _metric_status("humidity", humidity),
            },
            "temperature": {
                "value": temperature,
                "unit": "°C",
                "trend": _compute_trend(zone_id, "temperature"),
                "status": _metric_status("temperature", temperature),
            },
            "soil_moisture": {
                "value": soil_moisture,
                "unit": "%",
                "trend": _compute_trend(zone_id, "soil_moisture"),
                "status": _metric_status("soil_moisture", soil_moisture),
            },
            "water_level": {
                "value": water_level,
                "unit": "%",
                "trend": _compute_trend(zone_id, "water_level"),
                "status": _metric_status("water_level", water_level),
            },
        },
        "weather": _build_weather(zone_id=zone_id, snapshots=active_snapshots, weather_config=weather_config),
        "zones": response_zones,
        "alerts_count": _alerts_count(zone_id),
    }
