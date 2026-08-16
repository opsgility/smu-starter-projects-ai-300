# Meridian ETA Predictor — Lesson 5 Starter

This starter backs **AI-300 Lesson 5 — Train, register, and evaluate Meridian's ETA predictor**.

You will train an XGBoost regression model on Meridian Freight & Analytics' driver GPS logs, tune hyperparameters with an Azure Machine Learning sweep job, register the winner as an MLflow model, generate a Responsible AI dashboard, and wire the whole pipeline into GitHub Actions with OpenID Connect.

## What the lab pre-provisions

The lab template deploys these resources into your assigned resource group at start:

| Resource | Name |
|---|---|
| Azure ML workspace | `meridian-mlws-eta` |
| AmlCompute cluster | `cpu-cluster` (Standard_DS3_v2, 0–4 nodes) |
| Registered environment | `eta-training-env:1` (Python 3.11 + xgboost + MLflow) |
| Registered data asset | `driver-gps-logs:1` (500 rows, CSV, `uri_file`) |

You do NOT need to configure any of that — the exercises assume it is already there.

## Files in this starter

| File | Purpose |
|---|---|
| `train.py` | Scaffold with `TODO` markers for you to fill in during Exercise 2. |
| `job.yml` | Command-job spec you submit in Exercise 3. |
| `sweep.yml` | Sweep-job spec you submit in Exercise 4. |
| `rai-job.yml` | Responsible AI pipeline spec you submit in Exercise 6. |
| `data/driver-gps-logs.csv` | The exact dataset that backs the pre-registered `driver-gps-logs:1` data asset — safe to inspect locally. |
| `.github/workflows/train-eta.yml` | CI workflow you push to your fork in Exercise 7. |
| `requirements.txt` | Documentation of what the `python-ai` container already has installed. |

## The dataset

`data/driver-gps-logs.csv` has 500 rows. Columns:

- `trip_id`, `driver_id`, `route_id`
- `distance_km` — trip length
- `stops` — number of scheduled drop-offs
- `weather_score`, `traffic_score` — 0.0 (bad) to 1.0 (perfect)
- `hour_of_day` (0-23), `day_of_week` (0-6)
- `eta_minutes` — the target the model learns to predict

Baseline ground truth: `eta_minutes ≈ 1.2 * distance_km + 3.5 * stops + 25 * traffic_score + 15 * (1 - weather_score) + noise`.

A reasonable XGBoost baseline reaches RMSE around 5–7 minutes on the held-out set.

## What "self-contained" means for this lab

The workspace, compute, environment, and data asset all live in the resource group provisioned by the lab template. When you End Lab, everything is torn down — nothing carries into Lesson 6. This lab is complete on its own.
