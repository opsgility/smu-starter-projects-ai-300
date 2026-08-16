"""
Meridian ETA predictor — training script.

Runs inside an Azure Machine Learning command job. MLflow autologging captures
parameters, metrics, and the trained XGBoost model automatically; the job's
metrics and artifacts show up in the studio without any extra plumbing.

You (the student) fill in the TODOs in Exercise 2. The scaffolding here is
otherwise complete.
"""

import argparse
import os
from pathlib import Path

import mlflow
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


FEATURES = [
    "distance_km",
    "stops",
    "weather_score",
    "traffic_score",
    "hour_of_day",
    "day_of_week",
]
TARGET = "eta_minutes"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--driver_logs",
        type=str,
        required=True,
        help="Path to the driver-gps-logs data asset (CSV file).",
    )
    parser.add_argument("--max_depth", type=int, default=6)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--n_estimators", type=int, default=200)
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--random_state", type=int, default=42)
    return parser.parse_args()


def load_data(driver_logs_path: str) -> pd.DataFrame:
    """Read the CSV asset. AzureML mounts uri_file assets as a local path."""
    path = Path(driver_logs_path)
    # When the data asset is uri_file, driver_logs_path is the file itself.
    # When it is uri_folder, resolve the single .csv inside.
    if path.is_dir():
        csv_files = list(path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV under {path}")
        path = csv_files[0]
    return pd.read_csv(path)


def main() -> None:
    args = parse_args()

    # TODO (Exercise 2, Task 2): Enable MLflow autologging so every XGBoost
    # parameter, metric, and the trained model itself is captured to the run
    # with no further logging calls. One line does it.
    #
    # Hint: the function you need starts with `mlflow.` and ends in `log()`.
    #
    # >>> WRITE THE AUTOLOG CALL BELOW THIS LINE <<<

    # >>> END OF WRITE BLOCK <<<

    df = load_data(args.driver_logs)
    print(f"Loaded {len(df)} rows with columns {list(df.columns)}")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )

    model = XGBRegressor(
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        n_estimators=args.n_estimators,
        objective="reg:squarederror",
        tree_method="hist",
        random_state=args.random_state,
    )

    # TODO (Exercise 2, Task 3): Fit the model on the training split.
    # The call is one line — the same shape you would use in any scikit-learn
    # style API. Once autolog is on (see Task 2), MLflow captures the fit
    # parameters and the trained model automatically.
    #
    # >>> WRITE THE FIT CALL BELOW THIS LINE <<<

    # >>> END OF WRITE BLOCK <<<

    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)

    # Log the held-out RMSE alongside the autologged train metrics.
    mlflow.log_metric("test_rmse", float(rmse))
    print(f"Held-out test RMSE: {rmse:.3f} minutes")

    # Also persist the model under ./outputs so the sweep + registration flow
    # can address it as azureml://jobs/<run>/outputs/artifacts/paths/model.
    output_dir = Path(os.environ.get("AZUREML_MODEL_DIR", "outputs")) / "model"
    output_dir.mkdir(parents=True, exist_ok=True)
    mlflow.xgboost.save_model(model, str(output_dir))
    print(f"Saved MLflow model to {output_dir}")


if __name__ == "__main__":
    main()
