import logging
import traceback
import sqlite3
from flask import Blueprint, request
from datetime import datetime
from app.utils.db import get_db_connection
from app.utils.response import success_response, error_response

zones_bp = Blueprint('zones', __name__)
logger = logging.getLogger(__name__)

@zones_bp.get("")
@zones_bp.get("/")
def get_zones():
    try:
        logger.debug("Fetching all zones")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, area_size, crop_type, irrigation_mode, created_at
            FROM zones
        """)
        rows = cursor.fetchall()
        conn.close()
        
        zones = []
        for row in rows:
            zones.append({
                "id": row["id"],
                "name": row["name"],
                "area_size": row["area_size"],
                "crop_type": row["crop_type"],
                "irrigation_mode": row["irrigation_mode"],
                "created_at": row["created_at"]
            })
            
        return success_response(zones, 200)
    except sqlite3.Error as e:
        logger.error("Database error in get_zones: %s", traceback.format_exc())
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        logger.error("Unexpected error in get_zones: %s", traceback.format_exc())
        return error_response(f"An unexpected error occurred: {str(e)}", 500)


@zones_bp.post("")
@zones_bp.post("/")
def create_zone():
    try:
        data = request.get_json()
        if not data or not data.get("name"):
            return error_response("name is required", 400)
            
        name = data["name"]
        area_size = data.get("area_size")
        crop_type = data.get("crop_type")
        irrigation_mode = data.get("irrigation_mode", "manual")
        
        if irrigation_mode not in ["auto", "manual"]:
            return error_response("irrigation_mode must be 'auto' or 'manual'", 400)
            
        logger.debug("Creating zone: %s", name)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO zones (name, area_size, crop_type, irrigation_mode)
            VALUES (?, ?, ?, ?)
        """, (name, area_size, crop_type, irrigation_mode))
        
        conn.commit()
        new_zone_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM zones WHERE id = ?", (new_zone_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return error_response("Failed to retrieve created zone", 500)
            
        zone = {
            "id": row["id"],
            "name": row["name"],
            "area_size": row["area_size"],
            "crop_type": row["crop_type"],
            "irrigation_mode": row["irrigation_mode"],
            "created_at": row["created_at"]
        }
        
        return success_response(zone, 201)
    except sqlite3.Error as e:
        logger.error("Database error in create_zone: %s", traceback.format_exc())
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        logger.error("Unexpected error in create_zone: %s", traceback.format_exc())
        return error_response(f"An unexpected error occurred: {str(e)}", 500)


@zones_bp.get("/<int:zone_id>/metrics")
def get_zone_metrics(zone_id):
    try:
        logger.debug("Fetching metrics for zone: %s", zone_id)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, verify zone exists
        cursor.execute("SELECT id FROM zones WHERE id = ?", (zone_id,))
        if cursor.fetchone() is None:
            conn.close()
            return success_response([], 200)
            
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
            return success_response([], 200)
            
        current = rows[0]
        previous = rows[1] if len(rows) > 1 else None

        def get_trend(metric_name):
            curr_val = current[metric_name]
            if previous is None or previous[metric_name] is None or curr_val is None:
                return 0
            return round(curr_val - previous[metric_name], 2)

        metrics = {
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
        
        return success_response(metrics, 200)
    except sqlite3.Error as e:
        logger.error("Database error in get_zone_metrics: %s", traceback.format_exc())
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        logger.error("Unexpected error in get_zone_metrics: %s", traceback.format_exc())
        return error_response(f"An unexpected error occurred: {str(e)}", 500)
