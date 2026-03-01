from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.services.dashboard_service import FALLBACK_METRICS_BY_ZONE, FALLBACK_ZONE_LOCATIONS
from app.utils.db import get_db_connection


def _fallback_seed_for_zone(zone_id: Optional[int]) -> Dict[str, float]:
    if zone_id is None:
        values = list(FALLBACK_METRICS_BY_ZONE.values())
        return {
            "soil_moisture": round(sum(v["soil_moisture"] for v in values) / len(values), 1),
            "temperature": round(sum(v["temperature"] for v in values) / len(values), 1),
        }
    return FALLBACK_METRICS_BY_ZONE.get(zone_id, FALLBACK_METRICS_BY_ZONE[1])


def _build_chart_dataset(label: str, labels: List[str], values: List[float], color: str) -> Dict[str, Any]:
    return {
        "labels": labels,
        "datasets": [
            {
                "label": label,
                "data": values,
                "borderColor": color,
                "backgroundColor": color,
                "tension": 0.35,
                "fill": False,
                "pointRadius": 3,
            }
        ],
    }


def _generate_fallback_series(days: int, zone_id: Optional[int]) -> Tuple[List[str], List[float], List[float]]:
    seed = _fallback_seed_for_zone(zone_id)
    today = datetime.now().date()
    labels: List[str] = []
    moisture_values: List[float] = []
    temp_values: List[float] = []

    for index in range(days - 1, -1, -1):
        day = today - timedelta(days=index)
        labels.append(day.strftime("%b %d"))

        # Deterministic wave without random imports.
        wave = ((days - index) % 4) - 1.5
        moisture_values.append(round(max(0.0, min(100.0, seed["soil_moisture"] + wave * 1.7)), 2))
        temp_values.append(round(max(0.0, seed["temperature"] + wave * 0.6), 2))

    return labels, moisture_values, temp_values


def _zone_label(zone_id: Optional[int]) -> str:
    if zone_id is None:
        return "All Zones"
    fallback = FALLBACK_ZONE_LOCATIONS.get(zone_id, {})
    return fallback.get("name", f"Zone {zone_id}")


def get_analytics_data(zone_id: Optional[int], days: int) -> Dict[str, Any]:
    threshold_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    if zone_id is None:
        query = """
            SELECT
                date(created_at) AS day,
                ROUND(AVG(temperature), 2) AS temperature,
                ROUND(AVG(soil_moisture), 2) AS soil_moisture
            FROM sensor_readings
            WHERE date(created_at) >= ?
            GROUP BY day
            ORDER BY day ASC
        """
        cursor.execute(query, (threshold_date,))
    else:
        query = """
            SELECT
                date(created_at) AS day,
                ROUND(AVG(temperature), 2) AS temperature,
                ROUND(AVG(soil_moisture), 2) AS soil_moisture
            FROM sensor_readings
            WHERE zone_id = ? AND date(created_at) >= ?
            GROUP BY day
            ORDER BY day ASC
        """
        cursor.execute(query, (zone_id, threshold_date))

    rows = cursor.fetchall()
    conn.close()

    labels: List[str] = []
    moisture_values: List[float] = []
    temperature_values: List[float] = []
    raw_data: List[Dict[str, Any]] = []

    for row in rows:
        day_obj = datetime.strptime(row["day"], "%Y-%m-%d")
        day_label = day_obj.strftime("%b %d")
        labels.append(day_label)
        soil = float(row["soil_moisture"] or 0.0)
        temp = float(row["temperature"] or 0.0)
        moisture_values.append(round(soil, 2))
        temperature_values.append(round(temp, 2))
        raw_data.append({"date": row["day"], "soil_moisture": soil, "temperature": temp})

    if not labels:
        labels, moisture_values, temperature_values = _generate_fallback_series(days=days, zone_id=zone_id)

    return {
        "zone_id": "all" if zone_id is None else zone_id,
        "zone_name": _zone_label(zone_id),
        "period_days": days,
        "moisture": _build_chart_dataset(
            label="Soil Moisture (%)",
            labels=labels,
            values=moisture_values,
            color="#16A34A",
        ),
        "temperature": _build_chart_dataset(
            label="Temperature (C)",
            labels=labels,
            values=temperature_values,
            color="#0EA5E9",
        ),
        "raw": raw_data,
    }
