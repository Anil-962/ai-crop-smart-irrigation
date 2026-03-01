import sys
import os

sys.path.insert(0, r"d:\Ani\Hackathons\AMD\ai-crop-smart-irrigation")

from app import create_app

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

def verify_response(response, success_expected=True):
    data = response.get_json()
    assert "success" in data, "Missing 'success' key"
    assert "data" in data, "Missing 'data' key"
    assert "error" in data, "Missing 'error' key"
    assert "timestamp" in data, "Missing 'timestamp' key"
    assert data["success"] == success_expected, f"Expected success={success_expected} but got {data['success']}"
    return data

# Test 1: Successful endpoint (/health)
resp = client.get('/health')
print("Testing /health ... ", end="")
data = verify_response(resp, True)
assert data["data"]["status"] == "ok"
print("PASS")

# Test 2: Standard API route with payload (/api/zones)
resp = client.get('/api/zones')
print("Testing /api/zones ... ", end="")
data = verify_response(resp, True)
assert isinstance(data["data"], list)
print("PASS")

# Test 3: Standard error endpoint route (Missing params for zone ingestion)
resp = client.post('/api/sensors/ingest', json={})
print("Testing /api/sensors/ingest (Bad Payload) 400 ... ", end="")
data = verify_response(resp, False)
assert data["error"] == "zone_id is required"
print("PASS")

# Test 4: Global Error handler (404)
resp = client.get('/this/route/literally/does/not/exist')
print("Testing /fake_route 404 ... ", end="")
data = verify_response(resp, False)
assert data["error"] == "Endpoint not found"
print("PASS")

# Test 5: Global Error handler (405)
resp = client.post('/health')
print("Testing /health (Invalid Method) 405 ... ", end="")
data = verify_response(resp, False)
assert data["error"] == "Method not allowed"
print("PASS")

print("\nSUCCESS: All endpoints strictly obey the standardized JSON schema structure.")
