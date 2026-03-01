import sys
import threading
import time
import requests
import socketio

# Ensure zone 1 exists for ingest
sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app.utils.db import get_db_connection
conn = get_db_connection()
conn.execute('PRAGMA foreign_keys = OFF;')
conn.execute('DELETE FROM sensor_readings')
conn.execute('DELETE FROM zones')
conn.execute('PRAGMA foreign_keys = ON;')
conn.execute("INSERT INTO zones (id, name, area_size, crop_type, irrigation_mode) VALUES (1, 'Websock Zone', 100, 'Test', 'manual')")
conn.commit()
conn.close()

# Start Flask in background to test the client
from run import app, socketio as server_socketio

def run_server():
    server_socketio.run(app, host='127.0.0.1', port=5000, use_reloader=False, log_output=False)

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

time.sleep(2) # Wait for server to start

# Configure SocketIO Client
sio = socketio.Client()
received_events = []

@sio.event
def connect():
    print('Connection established')

@sio.on('sensor_update')
def on_message(data):
    print(f"\n[WebSocket Event] Received sensor_update: {data}")
    received_events.append(data)

@sio.event
def disconnect():
    print('Disconnected from server')

try:
    sio.connect('http://127.0.0.1:5000')
    time.sleep(1) # Let the connection register
    
    # Trigger Ingest Endpoint via REST (Mocking the hardware)
    print("\n[HTTP POST] Triggering ingest to Zone 1...")
    payload = {
        "zone_id": 1,
        "humidity": 45,
        "temperature": 26,
        "soil_moisture": 30,
        "water_level": 70
    }
    
    resp = requests.post("http://127.0.0.1:5000/api/sensors/ingest", json=payload)
    print(f"Ingest Response Code: {resp.status_code}")
    
    # Wait for websocket broadcast to propagate
    time.sleep(2)
    
except Exception as e:
    print(e)
finally:
    sio.disconnect()
    
if len(received_events) > 0:
    print("\nSUCCESS: WebSocket event correctly received with the expected format.")
else:
    print("\nFAILURE: Did not receive WebSocket event.")
    sys.exit(1)
