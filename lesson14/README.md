# AI-300 L14 Capstone — Meridian Auto-Dispatch

End-to-end MLOps + GenAIOps capstone for Meridian Freight & Analytics. You will finish an Auto-Dispatch service that combines:

- **ETA predictor** — classical ML model on an Azure ML managed online endpoint (`meridian-eta-endpoint`).
- **Dispatcher API** — Foundry `gpt-5.1` copilot on Azure Container Apps, calls the ETA endpoint as a tool.
- **Contract Summarizer** — RAG over `meridian-contracts` index in Azure AI Search (semantic ranker).
- **Evaluation gate** — quality + safety + Meridian compliance evaluators as a CI gate.
- **Observability workbook** — one glass showing every KPI ops cares about.
- **Progressive rollout** — Container Apps revisions with staged traffic weights.

## What the lab pre-provisions

Every resource named below is created by the ARM template attached to the lab, in the resource group assigned to your lab instance. **Do not redeploy the platform** — the exercises assume it is there.

- Azure ML workspace + `cpu-cluster` AmlCompute (Standard_DS3_v2, 0-2 nodes)
- Azure AI Foundry account + project (`meridian-autodispatch`) + three GlobalStandard deployments:
  - `gpt-5-1` (v `2025-11-13`, 200 capacity)
  - `gpt-5-mini` (v `2025-08-07`, 100 capacity)
  - `text-embedding-3-large` (v `1`, 50 capacity)
- Azure AI Search Standard tier with semantic ranker enabled
- Container Apps managed environment
- ACR Standard, Storage, Key Vault
- Log Analytics + workspace-based Application Insights
- User-Assigned Managed Identity `meridian-oidc-uami` with a GitHub OIDC federated credential (subject `repo:opsgility/smu-starter-projects:ref:refs/heads/main`)

Read every name at the start of the lab:

```bash
az deployment group list --resource-group "$RG_NAME" --query "[0].properties.outputs" -o json
```

## Layout

```
ai300_lesson14_capstone_autodispatch/
├── README.md                            # this file
├── requirements.txt                     # documentation only — every package is preinstalled in python-ai
├── .env.example                         # names to export at the start of the lab
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app entry — wires /health, /dispatch
│   ├── dispatcher.py                    # AIProjectClient + agent-framework — Exercise 2 + 3
│   ├── tracing.py                       # configure_azure_monitor() — call BEFORE FastAPI()
│   └── tools/
│       ├── __init__.py
│       └── eta_tool.py                  # predict_eta agent tool — Exercise 3
├── ml/
│   ├── train.py                         # ETA training script — student refines from L7 workflow
│   ├── endpoints/
│   │   ├── eta-endpoint.yml             # managed online endpoint (v2 CLI schema)
│   │   └── eta-deployment-blue.yml      # blue deployment (100% traffic)
│   └── samples/
│       └── eta_request.json             # sample scoring request
├── evaluation/
│   ├── evaluate.py                      # Exercise 5 — quality + safety + custom evaluators
│   ├── golden.jsonl                     # 30 auto-dispatch scenarios with retrieval context
│   ├── thresholds.yml                   # per-evaluator pass thresholds
│   └── evaluators/
│       └── meridian_no_price_commitment.py  # custom compliance evaluator
├── prompts/
│   ├── dispatcher_v1.md                 # baseline system prompt
│   ├── dispatcher_v2.md
│   ├── dispatcher_v3.md                 # current prod baseline for this lab
│   └── dispatcher_v4.md.NOT-YET         # Exercise 7 — student writes this from v3
├── observability/
│   ├── workbook.json                    # Exercise 6 — Azure Monitor Workbook
│   └── README.md                        # tile-by-tile description
├── config/
│   └── traffic-weights.yml              # Exercise 4 — progressive rollout stages
├── infra/
│   └── main.bicep                       # reference-only mirror of the attached ARM template
├── .github/workflows/
│   ├── deploy-eta.yml                   # Exercise 1 — train + deploy ETA endpoint
│   ├── deploy-dispatcher.yml            # Exercise 2 — build image + deploy ACA
│   ├── deploy-autodispatch.yml          # Exercise 4 — top-level release workflow
│   └── nightly-eval.yml                 # Exercise 5 — evaluation battery + gate
└── Dockerfile                           # Dispatcher API image (multi-stage python:3.11-slim)
```

## The container environment

You are running in the SkillMeUp `python-ai` VS Code container. Every SDK the exercises reference is **preinstalled** — do NOT run `pip install`.

- Python 3.11
- `azure-ai-ml==1.34.1`, `azure-ai-projects`, `azure-ai-evaluation==1.18.3`
- `agent-framework` (Microsoft Agent Framework, replaces `azure-ai-agents`)
- `azure-identity`, `azure-monitor-opentelemetry`, `opentelemetry-instrumentation-fastapi`
- `azure-search-documents`, `azure-storage-blob`, `azure-keyvault-secrets`
- `fastapi`, `uvicorn[standard]`, `pydantic`, `httpx`
- `az` CLI, `gh` CLI, `jq`, `sqlite3`

## Sign-in

The container is headless. Always use device-code:

```bash
az login --use-device-code
```

The device-code prompt sends you to `https://microsoft.com/devicelogin`.

## Env vars to export

Copy `.env.example` to `.env`. Fill in the names from the ARM outputs:

```bash
export RG_NAME=$(az group list --query "[?tags.LabInstanceId].name" -o tsv | head -1)
az deployment group list -g "$RG_NAME" --query "[0].properties.outputs" -o json > infra/outputs.json

export WORKSPACE_NAME=$(jq -r .workspaceName.value infra/outputs.json)
export FOUNDRY_PROJECT_ENDPOINT=$(jq -r .foundryProjectEndpoint.value infra/outputs.json)
export CHAT_DEPLOYMENT=$(jq -r .chatDeploymentName.value infra/outputs.json)
export CHAT_MINI_DEPLOYMENT=$(jq -r .chatMiniDeploymentName.value infra/outputs.json)
export EMBEDDING_DEPLOYMENT=$(jq -r .embeddingDeploymentName.value infra/outputs.json)
export SEARCH_ENDPOINT=$(jq -r .searchServiceEndpoint.value infra/outputs.json)
export ACA_ENV_NAME=$(jq -r .acaEnvName.value infra/outputs.json)
export ACR_NAME=$(jq -r .acrName.value infra/outputs.json)
export ACR_LOGIN_SERVER=$(jq -r .acrLoginServer.value infra/outputs.json)
export APP_INSIGHTS_CONNECTION_STRING=$(jq -r .appInsightsConnectionString.value infra/outputs.json)
export UAMI_CLIENT_ID=$(jq -r .uamiClientId.value infra/outputs.json)
export UAMI_RESOURCE_ID=$(jq -r .uamiResourceId.value infra/outputs.json)
```

## Where to start

Exercise 1 in the right pane. Nova is on the left. She will hint, not solve.
