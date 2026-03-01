import sys
import os
import json
import time

sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app import create_app
from app.utils.db import get_db_connection, init_db

init_db()

conn = get_db_connection()
cursor = conn.cursor()

# Start clean
cursor.execute('PRAGMA foreign_keys = OFF;')
cursor.execute('DELETE FROM sensor_readings')
cursor.execute('DELETE FROM zones')
cursor.execute('PRAGMA foreign_keys = ON;')

# Create a zone
cursor.execute("INSERT INTO zones (name, area_size, crop_type, irrigation_mode) VALUES ('Trend Zone', 100, 'Test', 'manual')")
zone_id = cursor.lastrowid
conn.commit()

# Testing 1 Reading (Trend should be 0)
cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level)
    VALUES (?, ?, ?, ?, ?)
''', (zone_id, 61.0, 25.0, 45.0, 80.0))
conn.commit()

app = create_app()
client = app.test_client()

print("=== GET metrics (1 Reading) ===")
res1 = client.get(f'/api/zones/{zone_id}/metrics')
print(json.dumps(res1.get_json(), indent=2))

# Testing 2 Readings (Should calculate differences)
time.sleep(1) # Ensure difference in created_at timestamp
cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level)
    VALUES (?, ?, ?, ?, ?)
''', (zone_id, 64.0, 24.5, 40.0, 85.0))
# Humidity goes 61 -> 64 (+3)
# Temp goes 25 -> 24.5 (-0.5)
# Soil goes 45 -> 40 (-5)
# Water goes 80 -> 85 (+5)
conn.commit()

print("\n=== GET metrics (2+ Readings) ===")
res2 = client.get(f'/api/zones/{zone_id}/metrics')
print(json.dumps(res2.get_json(), indent=2))

conn.close()
