import sys
import os
import json
from datetime import datetime

sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app import create_app
from app.utils.db import get_db_connection, init_db

init_db()

conn = get_db_connection()
cursor = conn.cursor()

# Start clean
cursor.execute('PRAGMA foreign_keys = OFF;')
cursor.execute('DELETE FROM sensor_readings')
cursor.execute('DELETE FROM alerts')
cursor.execute('DELETE FROM zones')
cursor.execute('PRAGMA foreign_keys = ON;')
conn.commit()
conn.close()

app = create_app()
client = app.test_client()

print("=== POST /api/zones (Zone A) ===")
res_a = client.post('/api/zones', json={
    "name": "Zone A",
    "area_size": 150.5,
    "crop_type": "Wheat",
    "irrigation_mode": "auto"
})
zone_a = res_a.get_json()
print(f"Status: {res_a.status_code}")
print(json.dumps(zone_a, indent=2))

print("\n=== POST /api/zones (Zone B) ===")
res_b = client.post('/api/zones', json={
    "name": "Zone B",
    "area_size": 200.0,
    "crop_type": "Corn",
    "irrigation_mode": "manual"
})
zone_b = res_b.get_json()
print(f"Status: {res_b.status_code}")
print(json.dumps(zone_b, indent=2))


print("\n=== GET /api/zones ===")
res_list = client.get('/api/zones')
print(f"Status: {res_list.status_code}")
print(json.dumps(res_list.get_json(), indent=2))

# Insert mock reading for Zone A
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level)
    VALUES (?, ?, ?, ?, ?)
''', (zone_a["data"]["id"], 65.5, 22.0, 55.0, 85.0))
conn.commit()
conn.close()

print(f"\n=== GET /api/zones/{zone_a['data']['id']}/metrics ===")
res_metrics = client.get(f"/api/zones/{zone_a['data']['id']}/metrics")
print(f"Status: {res_metrics.status_code}")
print(json.dumps(res_metrics.get_json(), indent=2))

print(f"\n=== GET /api/zones/{zone_b['data']['id']}/metrics ===")
res_empty_metrics = client.get(f"/api/zones/{zone_b['data']['id']}/metrics")
print(f"Status: {res_empty_metrics.status_code}")
print(json.dumps(res_empty_metrics.get_json(), indent=2))
