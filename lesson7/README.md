# AI-300 Lesson 7 — ETA Predictor Deploy Starter

Starter project for the Meridian Logistics ETA predictor **blue/green rollout + drift monitor + retrain-on-drift** workflow.

## What's inside

```
ai300_lesson7_eta_deploy/
├── deployments/
│   ├── blue-deployment.yml     # current production deployment (model v1)
│   └── green-deployment.yml    # candidate deployment (model v2)
├── monitoring/
│   └── monitoring.yml          # Azure ML monitor definition (data drift, threshold 0.3)
├── training/
│   └── train-eta-job.yml       # placeholder training job spec used by retrain workflow
├── .github/workflows/
│   └── retrain-on-drift.yml    # manual + drift-triggered retrain pipeline
└── docs/
    └── rollout-runbook.md      # blue → mirror → 90/10 → 50/50 → 100/0 → delete-blue runbook
```

## Story

Meridian Logistics ships an ETA prediction service behind a single **Azure ML managed online endpoint**. Two deployments live behind that endpoint:

- `blue` — the currently-serving model (`meridian-eta-predictor:1`, 100% traffic at steady-state)
- `green` — the candidate model (`meridian-eta-predictor:2`, 0% traffic until the promotion runbook widens it)

A **data drift monitor** watches inbound driver-GPS features against a captured baseline (`driver-gps-baseline:1`). When the drift signal exceeds `0.3`, the monitor emits an alert, and the retrain GitHub Actions workflow is fired manually (or later, from an event grid subscription) to submit a new training job that produces `meridian-eta-predictor:3`.

## Prerequisites

- Azure ML workspace with a managed online endpoint already provisioned by the lab ARM template
- The registered model `azureml:meridian-eta-predictor:1` (and `:2` after lesson 6)
- The registered dataset `azureml:driver-gps-baseline:1` captured from a prior week of production traffic
- Azure CLI `az` with the `ml` extension: `az extension add -n ml`
- `az login` completed with the lab credential

Copy `.env.example` to `.env` and fill in your workspace + endpoint + resource group names.

## Quick start

```bash
# Load env
set -a && source .env && set +a

# Deploy blue (production model)
az ml online-deployment create \
  -f deployments/blue-deployment.yml \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $WORKSPACE_NAME \
  --all-traffic

# Deploy green (candidate)
az ml online-deployment create \
  -f deployments/green-deployment.yml \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $WORKSPACE_NAME

# Attach the drift monitor
az ml schedule create \
  -f monitoring/monitoring.yml \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $WORKSPACE_NAME
```

Then follow `docs/rollout-runbook.md` for the traffic-split progression.

## Retrain workflow

`.github/workflows/retrain-on-drift.yml` supports `workflow_dispatch` for manual retrain. It authenticates via **OIDC** (`azure/login@v2`) — no client secrets in the repo — and submits `training/train-eta-job.yml` as the training job. The job's output model is registered as a new version of `meridian-eta-predictor`, which then becomes the next `green` candidate.
