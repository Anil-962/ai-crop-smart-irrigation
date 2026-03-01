import sys
import os
import json
from datetime import datetime

# Add the project root to sys.path so we can import app
sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app import create_app
from app.utils.db import get_db_connection, init_db

# Initialize DB
init_db()

# Insert mock data that drops triggers
conn = get_db_connection()
cursor = conn.cursor()

# Clear existing alerts
cursor.execute('DELETE FROM alerts')

# Insert conditions that trace out to warnings and critical errors
alert_conditions = [
    # Normal reading
    (1, 60.0, 27.0, 45.0, 80.0),
    # Water level low (warning)
    (2, 60.0, 27.0, 45.0, 20.0),
    # Soil moisture low (critical)
    (3, 60.0, 27.0, 20.0, 80.0),
    # Temperature high (warning)
    (4, 60.0, 45.0, 45.0, 80.0)
]

for zone, h, t, sm, wl in alert_conditions:
    cursor.execute('''
        INSERT INTO sensor_readings 
        (zone_id, humidity, temperature, soil_moisture, water_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (zone, h, t, sm, wl, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

conn.commit()
conn.close()

app = create_app()
client = app.test_client()

# Fetch Alerts (which should generate them)
print("=== GET /api/alerts ===")
response = client.get('/api/alerts')
alerts = response.get_json()
print(f"Status Code: {response.status_code}")
print(json.dumps(alerts, indent=2))

if alerts:
    first_alert_id = alerts[0]["id"]
    # Resolve the first alert
    print(f"\n=== POST /api/alerts/resolve/{first_alert_id} ===")
    res_response = client.post(f'/api/alerts/resolve/{first_alert_id}')
    print(f"Status Code: {res_response.status_code}")
    print(json.dumps(res_response.get_json(), indent=2))
    
    # Fetch remaining active alerts
    print("\n=== GET /api/alerts (after resolve) ===")
    final_response = client.get('/api/alerts')
    print(json.dumps(final_response.get_json(), indent=2))
