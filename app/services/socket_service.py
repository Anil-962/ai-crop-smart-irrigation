from app import socketio
from app.utils.db import get_db_connection

def emit_sensor_update(zone_id):
    """
    Fetches the latest two metrics for a zone, calculates the trend,
    and broadcasts the structured payload via WebSocket.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the latest two metrics
    cursor.execute("""
        SELECT id, humidity, temperature, soil_moisture, water_level, created_at
        FROM sensor_readings
        WHERE zone_id = ?
        ORDER BY created_at DESC
        LIMIT 2
    """, (zone_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) == 0:
        return
        
    current = rows[0]
    previous = rows[1] if len(rows) > 1 else None

    def get_trend(metric_name):
        curr_val = current[metric_name]
        if previous is None or previous[metric_name] is None or curr_val is None:
            return 0
        return round(curr_val - previous[metric_name], 2)

    payload = {
        "id": current["id"],
        "zone_id": zone_id,
        "created_at": current["created_at"],
        "humidity": {
            "value": current["humidity"],
            "trend": get_trend("humidity")
        },
        "temperature": {
            "value": current["temperature"],
            "trend": get_trend("temperature")
        },
        "soil_moisture": {
            "value": current["soil_moisture"],
            "trend": get_trend("soil_moisture")
        },
        "water_level": {
            "value": current["water_level"],
            "trend": get_trend("water_level")
        }
    }
    
    socketio.emit('sensor_update', payload)
    
@socketio.on('connect')
def handle_connect():
    print("Client connected to WebSocket")
    
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected from WebSocket")
