import time
from datetime import datetime, timedelta
from app.utils.db import get_db_connection

def run_cleanup_job(days_to_keep=7):
    """
    Aggregates sensor readins older than `days_to_keep` into daily_sensor_summaries
    and then deletes the raw readings to optimize the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    threshold_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Select the aggregations for data older than threshold
    cursor.execute("""
        SELECT 
            zone_id,
            date(created_at) as summary_date,
            AVG(humidity) as avg_hum,
            AVG(temperature) as avg_temp,
            AVG(soil_moisture) as avg_soil,
            AVG(water_level) as avg_water
        FROM sensor_readings
        WHERE created_at < ?
        GROUP BY zone_id, date(created_at)
    """, (threshold_date,))
    
    aggregations = cursor.fetchall()
    
    # 2. Insert into daily_sensor_summaries
    for agg in aggregations:
        cursor.execute("""
            INSERT OR IGNORE INTO daily_sensor_summaries 
            (zone_id, summary_date, avg_humidity, avg_temperature, avg_soil_moisture, avg_water_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            agg["zone_id"],
            agg["summary_date"],
            round(agg["avg_hum"], 2),
            round(agg["avg_temp"], 2),
            round(agg["avg_soil"], 2),
            round(agg["avg_water"], 2)
        ))
        
    # 3. Delete raw data
    cursor.execute("DELETE FROM sensor_readings WHERE created_at < ?", (threshold_date,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    print(f"[Cleanup Job] Aggregated {len(aggregations)} daily summaries and deleted {deleted_count} raw sensor records.")

def schedule_cleanup_job(interval_hours=24):
    """
    Runs `run_cleanup_job` immediately, then loops every `interval_hours`.
    Intended to be executed in a background thread.
    """
    while True:
        try:
            run_cleanup_job(days_to_keep=7)
        except Exception as e:
            print(f"[Cleanup Job] Error: {e}")
        time.sleep(interval_hours * 3600)
