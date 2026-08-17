# AI-300 Lesson 9 — Dispatcher Foundry stack + versioned prompts

Meridian Freight's AI copilot for freight dispatchers — the **Dispatcher** — moves from notebook prototype to production service in this lesson. You wire the Foundry stack the lab pre-provisions (project, `gpt-5.1` deployment, `text-embedding-3-large` deployment, Container Apps environment, ACR, App Insights) into a Python service, land the very first versioned prompt in git, gate every prompt PR with a smoke evaluation, and ship the Dispatcher API to Container Apps.

## What ships in this starter

```
lesson9/
├── README.md              (this file)
├── .env.example
├── .gitignore
└── src/
    ├── verify_stack.py    ← Ex 1 asks you to fill this in
    └── api/
        ├── main.py        ← Ex 4 asks you to read this
        ├── Dockerfile
        └── requirements.txt
```

Two things you create yourself during the lesson (they are not in this starter):

- `lesson9/prompts/dispatcher_v1.md` — Ex 2 authors the first versioned prompt.
- `lesson9/eval/smoke.py` + `lesson9/eval/golden_scenarios.json` + `.github/workflows/l9-promote-prompt.yml` — Ex 3 wires the PR-time smoke evaluation.
- `.github/workflows/l9-deploy-dispatcher.yml` — Ex 4 wires the deploy pipeline.

Workflows live at the **repo root** under `.github/workflows/` with an `l9-` prefix (see the top-level `README.md` for the multi-lesson layout convention). Each workflow's `paths:` filter is scoped to `lesson9/…` so a push that touches `lesson3/` or `lesson5/` never fires L9's workflows.

## Prerequisites (the lab pre-provisions these for you)

- Foundry AIServices account with `allowProjectManagement: true` and a `dispatcher` project.
- `gpt-5.1` model deployment (v `2025-11-13`, `GlobalStandard`, capacity 100).
- `text-embedding-3-large` deployment (v `1`, `GlobalStandard`, capacity 50).
- Container Apps managed environment `meridian-aca-env` (Consumption workload profile).
- Azure Container Registry (`meridianacr<uniq>`).
- Application Insights instance wired to the Foundry project.
- Managed identity + role assignments so `DefaultAzureCredential()` in the container gets a token for the Foundry project without any client secret.

The `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_CHAT_DEPLOYMENT`, `AZURE_RESOURCE_GROUP`, and `APPLICATIONINSIGHTS_CONNECTION_STRING` env vars are injected into the VS Code container at start.

## Student workflow

1. Ex 1: verify the pre-provisioned Foundry stack with `az` + `azure-ai-projects`.
2. Ex 2: author `lesson9/prompts/dispatcher_v1.md` as a versioned prompt with front-matter and open a PR.
3. Ex 3: wire `.github/workflows/l9-promote-prompt.yml` so every prompt PR runs a smoke evaluation.
4. Ex 4: merge the PR, wire `.github/workflows/l9-deploy-dispatcher.yml`, watch the Dispatcher API deploy to Container Apps.
5. Ex 5: call the deployed API and inspect the Foundry trace end-to-end.

## Notes

- **No client secrets anywhere.** The container's managed identity + `DefaultAzureCredential()` resolves the Foundry token. The deploy workflow uses OIDC federation via the pre-provisioned UAMI (same pattern as Lesson 3).
- **Prompts are code.** Every field in the front-matter is read by a real consumer — the eval workflow, the deploy pipeline, or the runtime. See `prompts/dispatcher_v1.md` after Ex 2 for the full front-matter shape.
- **Model version pin.** `gpt-5.1 @ 2025-11-13` is the current GA — verify at authoring time via MS Learn if you fork this into a different course release.
