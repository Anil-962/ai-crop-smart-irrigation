# API Contract - AGROGUARD AI

Base URL: `http://127.0.0.1:5000`
Content type: `application/json` unless noted.

## 1) Health Check

Endpoint: `GET /health`

Response:

```json
{
  "status": "ok",
  "service": "agroguard-ai-backend"
}
```

## 2) Disease Prediction

Endpoint: `POST /predict/disease`

Accepted request formats:

1. JSON with base64 image:

```json
{
  "image_base64": "<base64-encoded-image>"
}
```

2. Multipart form data:
`image` file field containing image bytes.

Success response:

```json
{
  "disease_name": "Early Blight",
  "confidence": 0.84,
  "suggested_treatment": "Apply copper-based fungicide and remove infected leaves.",
  "model": "mobilenetv2_stub"
}
```

Error response:

```json
{
  "error": "image_base64 is required for JSON requests."
}
```

## 3) Irrigation Prediction

Endpoint: `POST /predict/irrigation`

Request:

```json
{
  "soil_moisture_pct": 29.5,
  "temperature_c": 34.2,
  "humidity_pct": 52.0,
  "rain_forecast_mm_24h": 1.5,
  "crop_type": "tomato",
  "growth_stage": "vegetative"
}
```

Success response:

```json
{
  "irrigate_now": true,
  "recommended_liters": 19.4,
  "model": "xgboost_stub"
}
```

Error response:

```json
{
  "error": "Missing required field: soil_moisture_pct"
}
```

## 4) Combined Decision Endpoint

Endpoint: `POST /decision/combined`

Request:

```json
{
  "image_base64": "<base64-encoded-image>",
  "sensor_data": {
    "soil_moisture_pct": 29.5,
    "temperature_c": 34.2,
    "humidity_pct": 52.0,
    "crop_type": "tomato",
    "growth_stage": "vegetative",
    "rain_forecast_mm_24h": 0.0
  },
  "location": {
    "latitude": 17.385,
    "longitude": 78.4867
  }
}
```

Notes:

- If `sensor_data.rain_forecast_mm_24h` is missing and location is provided, backend fetches rain forecast from Open-Meteo.
- `image_base64` is optional. If omitted, disease output is marked as `Unknown`.

Success response:

```json
{
  "disease": {
    "disease_name": "Healthy",
    "confidence": 0.91,
    "suggested_treatment": "No disease symptoms detected."
  },
  "irrigation": {
    "irrigate_now": true,
    "recommended_liters": 16.2
  },
  "recommendations": {
    "fertilizer_suggestion": "Apply balanced NPK in split doses.",
    "weather_alert": "Light rain expected in next 24h."
  }
}
```

## HTTP Status Codes

- `200` success
- `400` client validation error
- `500` unexpected server error
