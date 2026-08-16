# AI-300 Lesson 3 — MLOps Foundation starter

Meridian Freight is standing up its **first production Azure ML workspace** — `meridian-mlws-<suffix>` — and this repo is the GitOps entry point. The lab has already pre-provisioned Storage, Key Vault, Container Registry, Application Insights, and a User-Assigned Managed Identity (UAMI) in your resource group. Your job is to author the workspace Bicep, wire GitHub Actions to Azure via OIDC federation on the pre-provisioned UAMI, push, and watch the workflow deploy the workspace end-to-end.

## What you will build

- **`project/main.bicep`** — declares `Microsoft.MachineLearningServices/workspaces` and binds it to the four pre-provisioned dependent resources.
- **`.github/workflows/deploy-workspace.yml`** (repo root) — a GitHub Actions pipeline that authenticates via workload identity (no secrets), then runs `az deployment group create --template-file project/main.bicep` against your resource group.
- **`project/docs/oidc-federation.md`** — walkthrough for creating the OIDC federated credential on the pre-provisioned UAMI so GitHub can assume it.

## Repo layout

```
smu-starter-projects-ai-300/
├── .github/
│   └── workflows/
│       └── deploy-workspace.yml     ← GitHub Actions reads workflows from repo root
└── project/                         ← everything else lives here
    ├── main.bicep
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── docs/
        └── oidc-federation.md
```

**Why the split?** GitHub Actions only reads workflows from `.github/workflows/*.yml` at the repo root — moving that file into `project/.github/` would silently disable it. Everything else (`main.bicep`, docs, env template) stays in `project/` so the working directory the exercises assume is one clean folder.

## Prerequisites (the lab pre-provisions these for you)

- Resource group (`AZURE_RESOURCE_GROUP`)
- User-Assigned Managed Identity (UAMI) with Contributor on the RG
- Storage account, Key Vault, Container Registry, Application Insights, Log Analytics workspace

## Student workflow

1. **Fork this starter** into your own GitHub account.
2. **Clone your fork** to the lab VS Code environment.
3. **Configure the OIDC federated credential** on the pre-provisioned UAMI (see `project/docs/oidc-federation.md`). This lets GitHub Actions exchange its OIDC token for an Azure access token *without any client secret*.
4. **Set the three GitHub Actions secrets** on your fork (Settings → Secrets and variables → Actions):
   - `AZURE_CLIENT_ID` — the UAMI's client ID
   - `AZURE_TENANT_ID` — the Azure AD tenant ID
   - `AZURE_SUBSCRIPTION_ID` — the lab subscription ID
5. **Edit `project/.env.example`** if you want to run `az deployment group create` locally too (copy to `project/.env`, fill in real values).
6. **Push to `main`** — the workflow fires automatically on changes under `project/main.bicep` or to the workflow file itself.
7. **Watch the workflow** in the Actions tab. It logs in via OIDC, then deploys `project/main.bicep` to your resource group.
8. **Verify** the workspace `meridian-mlws-<suffix>` exists in the Azure portal and that its Overview blade shows Storage + KV + ACR + App Insights bound correctly.

## Files

| File | Purpose |
|------|---------|
| `project/main.bicep` | Workspace + parameter wiring |
| `.github/workflows/deploy-workspace.yml` | OIDC login + `az deployment group create` (repo root) |
| `project/.env.example` | Local dev / manual-deploy variables |
| `project/docs/oidc-federation.md` | UAMI OIDC federated credential setup |
| `project/.gitignore` | Bicep / Python / Node ignores |

## Notes

- **No client secrets.** The whole point of OIDC federation is that GitHub proves its identity to Entra ID with a short-lived JWT — you never store an Azure password anywhere.
- **`workspaceNameSuffix`** — the lab generates a per-instance suffix (e.g. `a1b2`) and injects it as a parameter. The workspace name becomes `meridian-mlws-a1b2` so it is unique across concurrent students.
- **API version.** The Bicep pins `Microsoft.MachineLearningServices/workspaces@2026-05-01` — the current GA API version.
