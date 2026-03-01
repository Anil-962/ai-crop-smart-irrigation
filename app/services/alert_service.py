from datetime import datetime
from app.utils.db import get_db_connection

def check_and_generate_alerts():
    """
    Evaluates the latest sensor reading for each zone and generates alerts according to rules:
    - If water_level < 30 -> warning alert
    - If soil_moisture < 25 -> critical alert
    - If temperature > 40 -> warning alert
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the latest reading for each zone
    query_latest = """
        SELECT zone_id, humidity, temperature, soil_moisture, water_level
        FROM sensor_readings
        WHERE id IN (
            SELECT MAX(id)
            FROM sensor_readings
            GROUP BY zone_id
        )
    """
    cursor.execute(query_latest)
    latest_readings = cursor.fetchall()

    for reading in latest_readings:
        zone_id = reading["zone_id"]
        water_level = reading["water_level"]
        soil_moisture = reading["soil_moisture"]
        temperature = reading["temperature"]
        
        # Check water_level
        if water_level is not None and water_level < 30:
            _create_alert_if_not_exists(cursor, "warning", f"Water level low in Zone {zone_id}", zone_id)
            
        # Check soil_moisture
        if soil_moisture is not None and soil_moisture < 25:
            _create_alert_if_not_exists(cursor, "critical", f"Soil moisture critically low in Zone {zone_id}", zone_id)
            
        # Check temperature
        if temperature is not None and temperature > 40:
            _create_alert_if_not_exists(cursor, "warning", f"Temperature too high in Zone {zone_id}", zone_id)
            
    conn.commit()
    conn.close()

def _create_alert_if_not_exists(cursor, alert_type, message, zone_id):
    # Check if an unresolved alert with the same message and zone already exists
    cursor.execute("""
        SELECT id FROM alerts 
        WHERE message = ? AND zone_id = ? AND is_resolved = 0
    """, (message, zone_id))
    
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO alerts (type, message, zone_id, is_resolved)
            VALUES (?, ?, ?, 0)
        """, (alert_type, message, zone_id))
