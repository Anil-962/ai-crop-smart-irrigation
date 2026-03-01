from datetime import datetime
from app.utils.db import get_db_connection

def calculate_farm_health_score():
    """
    Calculates the overall farm health score based on the latest sensor readings.
    Score calculation formula:
    - Soil moisture weight: 40% (Optimal around 60%. Deviation lowers score)
    - Water level weight: 25% (Higher is better, max 100)
    - Temperature deviation weight: 20% (Optimal 25C. Deviation lowers score)
    - Irrigation efficiency weight: 15% (Mocked as 85%)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the latest reading for each zone to average them out
    query_latest = """
        SELECT humidity, temperature, soil_moisture, water_level
        FROM sensor_readings
        WHERE id IN (
            SELECT MAX(id)
            FROM sensor_readings
            GROUP BY zone_id
        )
    """
    cursor.execute(query_latest)
    latest_readings = cursor.fetchall()
    conn.close()

    if not latest_readings:
        # Fallback if no data
        return _format_health_response(50)

    # Calculate farm-wide averages
    avg_soil_moisture = sum([r["soil_moisture"] for r in latest_readings]) / len(latest_readings)
    avg_water_level = sum([r["water_level"] for r in latest_readings]) / len(latest_readings)
    avg_temperature = sum([r["temperature"] for r in latest_readings]) / len(latest_readings)

    # 1. Soil Moisture Subscore (0-100)
    # Assume 60% is perfect. If it's 20% away (e.g. 40 or 80), it's bad.
    sm_deviation = abs(avg_soil_moisture - 60)
    sm_subscore = max(0, 100 - (sm_deviation * 2.5))  # e.g., 40 deviates by 20 -> 50 score
    
    # 2. Water Level Subscore (0-100)
    # Directly linear, capping at 100
    wl_subscore = min(100, max(0, avg_water_level))

    # 3. Temperature Deviation Subscore (0-100)
    # Assume 25C is perfect.
    temp_deviation = abs(avg_temperature - 25)
    temp_subscore = max(0, 100 - (temp_deviation * 5))  # e.g., 5 degrees off loses 25 points

    # 4. Irrigation Efficiency Subscore (0-100)
    ie_subscore = 85.0

    # Compute Final Weighted Score
    final_score = (sm_subscore * 0.40) + (wl_subscore * 0.25) + (temp_subscore * 0.20) + (ie_subscore * 0.15)
    
    # Bound between 0 and 100
    final_score = max(0, min(100, int(round(final_score))))

    return _format_health_response(final_score)

def _format_health_response(score: int):
    if score >= 80:
        status = "Good"
        recommendation = "Irrigation optimal. Monitor tank level."
    elif score >= 50:
        status = "Warning"
        recommendation = "Sub-optimal conditions detected. Check soil moisture delivery in affected zones."
    else:
        status = "Critical"
        recommendation = "Critical systemic failure. Immediate manual intervention required for water delivery."

    return {
        "health_score": score,
        "status": status,
        "recommendation": recommendation,
        "last_updated": datetime.now().isoformat()
    }
