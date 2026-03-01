import sqlite3
import os
from datetime import datetime

# Path for SQLite fallback
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sensor_readings.db")

def get_db_connection():
    from app.config import Config
    db_url = Config.DATABASE_URL
    
    if db_url.startswith("sqlite:///"):
        # Handle SQLite (remove the prefix)
        path = db_url.replace("sqlite:///", "")
        # Ensure path is absolute relative to project root if it starts with 'data/'
        if path.startswith("data/"):
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), path)
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Generic fallback or Postgres logic (would require psycopg2 and different SQL syntax)
    # For now, we stick to SQLite as the primary engine but log the attempt
    print(f"Warning: Attempting to use non-SQLite database URL: {db_url}")
    print("Defaulting to SQLite as the application logic is currently SQLite-specific.")
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON;')

    # Create the zones table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            area_size REAL,
            crop_type TEXT,
            irrigation_mode TEXT CHECK(irrigation_mode IN ('auto', 'manual')) DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create the sensor_readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            humidity REAL,
            temperature REAL,
            soil_moisture REAL,
            water_level REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
        )
    ''')
    
    # Create the index on created_at for fast querying
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_created_at
        ON sensor_readings(created_at)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_zone_id
        ON sensor_readings(zone_id)
    ''')
    
    # Create the daily summaries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_sensor_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            summary_date DATE,
            avg_humidity REAL,
            avg_temperature REAL,
            avg_soil_moisture REAL,
            avg_water_level REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(zone_id, summary_date),
            FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
        )
    ''')

    # Create the alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('info', 'warning', 'critical')),
            message TEXT,
            zone_id INTEGER NULL,
            is_resolved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP NULL
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_alerts_type
        ON alerts(type)
    ''')
    
    conn.commit()
    conn.close()
