# AGROGUARD AI - Backend Starter

Flask starter backend for:

- Crop disease detection (image -> disease/confidence/treatment)
- Smart irrigation recommendation (features -> irrigate_now/recommended_liters)
- Combined decision endpoint for app integration

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Server runs on `http://127.0.0.1:5000`.

## API Contract

See `docs/API_CONTRACT.md`.

## Project Structure

See `docs/FOLDER_STRUCTURE.md`.

## Endpoints

- `GET /health`
- `POST /predict/disease`
- `POST /predict/irrigation`
- `POST /decision/combined`

## Model Training

Install training dependencies:

```bash
pip install -r train/requirements-train.txt
```

Train disease model (MobileNetV2):

```bash
python train/train_disease.py --dataset-dir train/data/disease_images
```

Train irrigation model (XGBoost baseline):

```bash
python train/train_irrigation.py --csv-path train/data/irrigation.csv
```

Detailed training guide: `train/README.md`.

## Docker Deployment

One-command local deployment:

```bash
copy .env.example .env
docker compose up --build
```

Backend will be available at `http://127.0.0.1:5000`.

## Example Requests

Disease (base64 JSON):

```bash
curl -X POST http://127.0.0.1:5000/predict/disease ^
  -H "Content-Type: application/json" ^
  -d "{\"image_base64\":\"<BASE64_IMAGE>\"}"
```

Irrigation:

```bash
curl -X POST http://127.0.0.1:5000/predict/irrigation ^
  -H "Content-Type: application/json" ^
  -d "{\"soil_moisture_pct\":29.5,\"temperature_c\":34.2,\"humidity_pct\":52.0,\"rain_forecast_mm_24h\":1.5,\"crop_type\":\"tomato\",\"growth_stage\":\"vegetative\"}"
```

## Notes

- Model files are expected in `models/` by default.
- Current predictors are stubs if model artifacts are missing, so UI integration can proceed immediately.
- To use real CNN inference, install TensorFlow and place `models/disease_model.h5`.
- Disease class names are loaded from `models/disease_labels.json` if available.
