# Training Guide

This folder contains baseline training pipelines for both AI modules.

## 1) Disease Model (MobileNetV2)

Script: `train/train_disease.py`

Expected dataset layout:

```text
train/data/disease_images/
  healthy/
    img1.jpg
    img2.jpg
  early_blight/
    img3.jpg
  late_blight/
    img4.jpg
```

Run:

```bash
pip install -r train/requirements-train.txt
python train/train_disease.py --dataset-dir train/data/disease_images
```

Outputs:

- `models/disease_model.h5`
- `models/disease_labels.json`
- `models/disease_metrics.json`

## 2) Irrigation Model (XGBoost baseline, RF fallback)

Script: `train/train_irrigation.py`

Expected CSV columns:

- `soil_moisture_pct`
- `temperature_c`
- `humidity_pct`
- `rain_forecast_mm_24h`
- `crop_type`
- `growth_stage`
- `water_liters` (target)

Run:

```bash
pip install -r train/requirements-train.txt
python train/train_irrigation.py --csv-path train/data/irrigation.csv
```

Outputs:

- `models/irrigation_model.pkl`
- `models/irrigation_metrics.json`
- `models/irrigation_feature_importance.csv`
