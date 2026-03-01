import sys
import os
import json
from datetime import datetime, timedelta

# Add the project root to sys.path so we can import app
sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app import create_app
from app.utils.db import get_db_connection, init_db

# Initialize DB
init_db()

# Insert mock data
conn = get_db_connection()
cursor = conn.cursor()

# Clear existing data for clear tests
cursor.execute('DELETE FROM sensor_readings')

base_date = datetime.now()
zone_id = 1
for i in range(10):
    date = base_date - timedelta(days=i)
    # Insert a few readings per day to test grouping/averaging
    for j in range(3):
        cursor.execute('''
            INSERT INTO sensor_readings 
            (zone_id, humidity, temperature, soil_moisture, water_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            zone_id, 
            60.0 + j, 
            27.0 + j, 
            45.0 + j, 
            80.0 + j, 
            date.strftime('%Y-%m-%d %H:%M:%S')
        ))
conn.commit()
conn.close()

app = create_app()
client = app.test_client()

response = client.get('/api/analytics?zone_id=1&days=7')
print(f"Status Code: {response.status_code}")
print(json.dumps(response.get_json(), indent=2))
