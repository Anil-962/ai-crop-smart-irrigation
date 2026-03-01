import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


NUMERIC_COLS = [
    "soil_moisture_pct",
    "temperature_c",
    "humidity_pct",
    "rain_forecast_mm_24h",
]
CATEGORICAL_COLS = ["crop_type", "growth_stage"]
TARGET_COL = "water_liters"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline irrigation regressor.")
    parser.add_argument("--csv-path", required=True, help="Path to irrigation CSV file.")
    parser.add_argument("--output-model", default="models/irrigation_model.pkl", help="Output model path.")
    parser.add_argument("--output-metrics", default="models/irrigation_metrics.json", help="Output metrics path.")
    parser.add_argument(
        "--output-importance",
        default="models/irrigation_feature_importance.csv",
        help="Output feature importance CSV path.",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def build_regressor(seed: int):
    try:
        from xgboost import XGBRegressor  # type: ignore

        model = XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=seed,
            objective="reg:squarederror",
        )
        return model, "xgboost"
    except Exception:
        model = RandomForestRegressor(
            n_estimators=300,
            random_state=seed,
            min_samples_leaf=2,
            n_jobs=-1,
        )
        return model, "random_forest"


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    required = set(NUMERIC_COLS + CATEGORICAL_COLS + [TARGET_COL])
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=list(required))
    X = df[NUMERIC_COLS + CATEGORICAL_COLS].copy()
    y = df[TARGET_COL].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUMERIC_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
        ]
    )
    regressor, model_name = build_regressor(seed=args.seed)
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", regressor)])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = r2_score(y_test, preds)

    output_model = Path(args.output_model)
    output_metrics = Path(args.output_metrics)
    output_importance = Path(args.output_importance)
    output_model.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, output_model)

    metrics_payload = {
        "model": model_name,
        "test_samples": int(len(y_test)),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }
    output_metrics.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    reg = pipeline.named_steps["regressor"]
    if hasattr(reg, "feature_importances_"):
        feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
        importance = pd.DataFrame(
            {
                "feature": feature_names,
                "importance": reg.feature_importances_,
            }
        ).sort_values("importance", ascending=False)
        importance.to_csv(output_importance, index=False)

    print("Training completed.")
    print(f"Model: {model_name}")
    print(f"Saved model: {output_model}")
    print(f"Saved metrics: {output_metrics}")
    if output_importance.exists():
        print(f"Saved feature importance: {output_importance}")


if __name__ == "__main__":
    main()
