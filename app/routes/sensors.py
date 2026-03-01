from flask import Blueprint, request
from app.utils.db import get_db_connection
from app.services.socket_service import emit_sensor_update
from app.utils.response import success_response, error_response

sensors_bp = Blueprint('sensors', __name__)

@sensors_bp.post("/ingest")
def ingest_sensor_data():
    """
    Simulates a hardware sensor sending data to the backend.
    Saves to the database and implicitly broadcasts to WebSockets.
    """
    data = request.get_json()
    if not data or not data.get("zone_id"):
        return error_response("zone_id is required", 400)
        
    zone_id = data["zone_id"]
    humidity = data.get("humidity", 0)
    temperature = data.get("temperature", 0)
    soil_moisture = data.get("soil_moisture", 0)
    water_level = data.get("water_level", 0)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure zone exists to prevent constraint failures
    cursor.execute("SELECT id FROM zones WHERE id = ?", (zone_id,))
    if cursor.fetchone() is None:
        conn.close()
        return error_response(f"Zone {zone_id} does not exist", 404)
        
    cursor.execute('''
        INSERT INTO sensor_readings 
        (zone_id, humidity, temperature, soil_moisture, water_level)
        VALUES (?, ?, ?, ?, ?)
    ''', (zone_id, humidity, temperature, soil_moisture, water_level))
    
    conn.commit()
    conn.close()
    
    # Broadcast the real-time websocket event
    emit_sensor_update(zone_id)
    
    return success_response({"message": "Data ingested and broadcasted successfully"}, 201)
