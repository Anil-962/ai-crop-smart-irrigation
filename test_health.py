import sys
import os
import json
from datetime import datetime

sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app import create_app

app = create_app()
client = app.test_client()

print("=== Testing /api/health ===")
resp = client.get('/api/health')
print(f"Status: {resp.status_code}")
data = resp.get_json()
print(json.dumps(data, indent=2))

# Basic Assertions
assert resp.status_code == 200
assert data["status"] == "ok"
assert data["database"] in ["connected", "disconnected"]
assert "timestamp" in data

print("\nPASS: /api/health returns the expected structure.")
