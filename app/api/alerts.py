import os
from datetime import datetime

from flask import Blueprint, request
from app.services.alert_service import check_and_generate_alerts
from app.utils.db import get_db_connection
from app.utils.response import success_response, error_response

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.get("/")
@alerts_bp.get("")
def get_alerts():
    # Trigger generating alerts from the latest sensor readings
    check_and_generate_alerts()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, type, message, zone_id, is_resolved, created_at, resolved_at 
        FROM alerts 
        WHERE is_resolved = 0
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            "id": row["id"],
            "type": row["type"],
            "message": row["message"],
            "zone_id": row["zone_id"],
            "is_resolved": bool(row["is_resolved"]),
            "created_at": row["created_at"],
            "resolved_at": row["resolved_at"],
        })
        
    return success_response(alerts, 200)

@alerts_bp.post("/resolve/<int:alert_id>")
def resolve_alert(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if alert exists
    cursor.execute("SELECT id FROM alerts WHERE id = ? AND is_resolved = 0", (alert_id,))
    if cursor.fetchone() is None:
        conn.close()
        return error_response("Alert not found or already resolved", 404)
        
    resolved_time = datetime.now().isoformat()
    cursor.execute("""
        UPDATE alerts 
        SET is_resolved = 1, resolved_at = ? 
        WHERE id = ?
    """, (resolved_time, alert_id))
    
    conn.commit()
    
    # Fetch the updated alert to return
    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    conn.close()
    
    updated_alert = {
        "id": row["id"],
        "type": row["type"],
        "message": row["message"],
        "zone_id": row["zone_id"],
        "is_resolved": bool(row["is_resolved"]),
        "created_at": row["created_at"],
        "resolved_at": row["resolved_at"],
    }
    
    return success_response(updated_alert, 200)

