# Meridian ETA predictor — blue/green rollout runbook

Progressive rollout of `meridian-eta-predictor:2` (green) behind the `meridian-eta-endpoint` managed online endpoint. Blue keeps serving until green owns 100% of traffic and has been observed for a full drift-monitor cycle.

## Gates

- `az ml online-endpoint get-logs --deployment-name green` shows no 5xx over the last 30 minutes
- Drift monitor's most recent run is `succeeded` and no signal is above `0.3`
- Latency P95 (Application Insights) within 10% of blue's baseline
- Prediction distribution (green) matches blue's within a Jensen-Shannon distance of `0.15`

## Progression

Each step waits until all gates are green before advancing.

### Step 1 — Deploy green at 0% traffic
```bash
az ml online-deployment create -f deployments/green-deployment.yml \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME
```

### Step 2 — Mirror 100% of blue's traffic to green (no response returned to caller)
```bash
az ml online-endpoint update --name $ENDPOINT_NAME \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME \
  --mirror-traffic green=100
```
Observe for 30 minutes. Green sees production load without affecting callers.

### Step 3 — 90/10 canary
```bash
az ml online-endpoint update --name $ENDPOINT_NAME \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME \
  --traffic "blue=90 green=10" --mirror-traffic ""
```
Observe for 2 hours.

### Step 4 — 50/50
```bash
az ml online-endpoint update --name $ENDPOINT_NAME \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME \
  --traffic "blue=50 green=50"
```
Observe for 2 hours.

### Step 5 — 0/100 (promote green)
```bash
az ml online-endpoint update --name $ENDPOINT_NAME \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME \
  --traffic "blue=0 green=100"
```
Observe for 24 hours (one full drift-monitor cycle).

### Step 6 — Delete blue
```bash
az ml online-deployment delete --name blue --endpoint-name $ENDPOINT_NAME \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME --yes
```

## Rollback

At any step:
```bash
az ml online-endpoint update --name $ENDPOINT_NAME \
  --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME \
  --traffic "blue=100 green=0" --mirror-traffic ""
```
Then investigate green's logs + drift metrics before re-attempting from step 2.
