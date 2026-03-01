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

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('DELETE FROM sensor_readings')

# Insert known data:
# Soil Moisture = 60 (score = 100 * 0.4 = 40)
# Water Level = 80 (score = 80 * 0.25 = 20)
# Temperature = 25 (score = 100 * 0.20 = 20)
# IE = 85 (score = 85 * 0.15 = 12.75)
# Expected total: 40 + 20 + 20 + 12.75 = 92.75 -> 93 (Good)
cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', (1, 50.0, 25.0, 60.0, 80.0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

conn.commit()
conn.close()

app = create_app()
client = app.test_client()

print("=== GET /api/health-score ===")
response = client.get('/api/health-score')
print(f"Status Code: {response.status_code}")
print(json.dumps(response.get_json(), indent=2))
