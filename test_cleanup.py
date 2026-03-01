import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app.utils.db import get_db_connection, init_db
from app.services.cleanup_service import run_cleanup_job

init_db()
conn = get_db_connection()
cursor = conn.cursor()

# Clean slate
cursor.execute('PRAGMA foreign_keys = OFF;')
cursor.execute('DELETE FROM daily_sensor_summaries')
cursor.execute('DELETE FROM sensor_readings')
cursor.execute('DELETE FROM zones')
cursor.execute('PRAGMA foreign_keys = ON;')

cursor.execute("INSERT INTO zones (id, name, area_size, crop_type, irrigation_mode) VALUES (1, 'Purge Zone', 100, 'Test', 'manual')")
conn.commit()

# Insert raw data exactly 10 days ago (meaning it should be aggregated and purged)
past_date1 = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d 10:00:00')
past_date2 = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d 11:00:00')

cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', (1, 50.0, 20.0, 40.0, 80.0, past_date1))

cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', (1, 60.0, 30.0, 60.0, 90.0, past_date2))

# Insert raw data currently (should NOT be purged)
cursor.execute('''
    INSERT INTO sensor_readings 
    (zone_id, humidity, temperature, soil_moisture, water_level)
    VALUES (?, ?, ?, ?, ?)
''', (1, 45.0, 25.0, 30.0, 70.0))

conn.commit()

# Output before
cursor.execute("SELECT id FROM sensor_readings")
print(f"Readings before cleanup: {len(cursor.fetchall())}")

# Run the job manually
run_cleanup_job(days_to_keep=7)

# Output after
cursor.execute("SELECT id FROM sensor_readings")
after_readings = cursor.fetchall()
print(f"Readings after cleanup: {len(after_readings)}")

cursor.execute("SELECT * FROM daily_sensor_summaries")
summaries = cursor.fetchall()
print(f"Summaries created: {len(summaries)}")

if len(summaries) > 0:
    s = summaries[0]
    print(f"\nSummary Averages (Zone 1, Date 10-days ago):")
    print(f"Avg Humidity: {s['avg_humidity']} (Expected 55.0)")
    print(f"Avg Temperature: {s['avg_temperature']} (Expected 25.0)")
    print(f"Avg Soil Moisture: {s['avg_soil_moisture']} (Expected 50.0)")
    print(f"Avg Water Level: {s['avg_water_level']} (Expected 85.0)")
    
conn.close()
