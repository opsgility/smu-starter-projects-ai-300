# AI-300 Lesson 11 — Evaluate and observe Meridian Dispatcher end-to-end

You are the newly promoted MLOps lead at Meridian Freight & Analytics. The
Dispatcher agent — the AI copilot that helps human dispatchers assign carriers
to freight loads — is now shipping traffic in production. In this lab you
close the observability loop: run the four Foundry Evaluation SDK signal
categories (quality, safety, custom-domain, cost/latency) against the
Dispatcher's golden dataset, wire nightly CI evaluation, turn on Foundry
continuous monitoring against the deployed Dispatcher API, and build the
KQL cost + latency dashboards that Meridian's engineering leadership will
watch every morning.

## Scenario

Meridian's Chief Dispatch Officer, Nadia Ortega, has one hard rule after last
year's rate incident: **no Dispatcher response may quote a per-mile rate
above `$4.20 USD/mile`** — the ceiling Meridian's contract legal team locked
in with carriers. The Dispatcher agent must also stay grounded in real
Meridian dispatch policy, not hallucinate rates, refuse violent or self-harm
prompts (drivers on the road have called the line in crisis), and resist
indirect prompt-injection attempts hidden inside carrier email context.

You will encode all of that as evaluators — built-in Foundry evaluators
for the general quality + safety signals, and a `MeridianComplianceEvaluator`
custom class for the domain-specific `$4.20` rule.

## Files

```
ai300_lesson11_dispatcher_eval/
  README.md
  .env.example                 # Filled in from the Environment tab in Exercise 1
  .gitignore
  requirements.txt             # Reference manifest — packages already installed in the lab container
  src/
    verify_env.py              # 30-line smoke test — reads .env, one auth+model round-trip
    evaluate.py                # Scaffold you complete across Exercises 2, 3, 4
    meridian_compliance.py     # Custom evaluator scaffold you complete in Exercise 4
    dispatcher_client.py       # Thin wrapper around DefaultAzureCredential + AIProjectClient
  data/
    golden.jsonl               # 20 Meridian Dispatcher scenarios (query, context, response, ground_truth)
```

`.github/workflows/nightly-eval.yml` is authored in Exercise 5 — that folder
does not yet exist in the starter.

## How to run

1. Confirm you are signed in to the lab's Azure subscription:

   ```bash
   az login --use-device-code
   ```

   Use the lab-issued credentials shown on the Environment tab (paste the
   device code at `https://microsoft.com/devicelogin`).

2. Copy `.env.example` to `.env` and fill each `<...>` placeholder from the
   Environment tab (Foundry project endpoint, model deployment names,
   Application Insights connection string, Dispatcher API URL).

3. Run the smoke test:

   ```bash
   python src/verify_env.py
   ```

   You should see the model name and a short reply. If the script says
   "Missing env var" or "placeholder value," the `.env` file still has a
   `<...>` placeholder in it.

4. Run the evaluation battery (built up across Exercises 2–4):

   ```bash
   python src/evaluate.py
   ```

## Authentication

Every module in this starter authenticates with
[`DefaultAzureCredential`](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential).
The `az login --use-device-code` session on your VS Code container terminal
is what `DefaultAzureCredential` picks up — no API keys, no service
principals, no client secrets end up in code.

The lab-issued Azure account (Environment tab) is a member of the AI-300
`AI-300 Azure Developer` credential — Contributor at the lab's resource
group, plus the `Cognitive Services OpenAI User`, `Cognitive Services User`,
`Application Insights Component Contributor`, and `Log Analytics Contributor`
roles needed to call the Foundry chat + evaluation endpoints and query
App Insights via KQL.

## Notes

- The Dispatcher API is a Container App deployed by the lab's ARM template.
  Its URL is exported as `dispatcherApiUrl` and shown in the Environment
  tab. Exercise 7 hits that URL with `curl` to generate live traffic before
  you inspect telemetry in App Insights.
- `MAX_QUOTE = 4.20` is Meridian's contractual per-mile rate ceiling. Nadia
  Ortega set it. The `MeridianComplianceEvaluator` class you build in
  Exercise 4 enforces it as a numeric score (`0` or `1`) with a plain-text
  `reason`. Nightly CI (Exercise 5) fails the run when the rollup
  `meridian_compliance` score drops below `0.95`.
- Safety evaluators (Violence, SelfHarm, HateUnfairness, IndirectAttack)
  do NOT take a `model_config` — they run against Microsoft's hosted
  Foundry Evaluation Service and take `azure_ai_project` + `credential`
  instead. The quality evaluators (Groundedness, Relevance, Coherence,
  Fluency) do take `model_config` and route the LLM-as-a-judge calls
  through your `gpt-5.1` deployment.
- Do not hardcode model deployment names. Read them from
  `AZURE_AI_CHAT_DEPLOYMENT` / `AZURE_AI_EMBEDDING_DEPLOYMENT` so a future
  model swap is one `.env` change, not a codebase sweep.
