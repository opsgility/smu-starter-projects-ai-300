# AI-300 Lesson 13 — Optimize Meridian's Contract Summarizer (`ai300_lesson13_contract_optimizer`)

Scenario: **Meridian Freight & Analytics** ships a Contract Summarizer that turns
carrier-contract PDFs into a structured JSON of key terms (parties, effective
dates, rate tables, indemnity limits, termination clauses). The v1 baseline
uses `gpt-4.1-mini` with retrieval from an Azure AI Search index.

Legal reports that the summaries occasionally hallucinate section numbers and
skip named-entity clauses (e.g. "Section 4.2"). Your job is to systematically
lift groundedness on a golden 15-scenario dataset by working the RAG lever
hierarchy — chunk size, retrieval strategy, top-k, threshold — and only then
reach for fine-tuning to correct the style bias.

Nova coaches you through it in the left pane.

## Files

```
ai300_lesson13_contract_optimizer/
├── app/
│   ├── __init__.py
│   ├── config.py            # Loads env vars from ARM outputs
│   ├── retrieval.py         # search_vector / search_hybrid / search_semantic_hybrid
│   ├── baseline_rag.py      # Ex 1: baseline vector RAG on gpt-4.1-mini
│   ├── reindex.py           # Ex 2: reindex the corpus at a different chunk size
│   ├── hybrid_rag.py        # Ex 3: hybrid + semantic ranker variant
│   ├── synthesize.py        # Ex 4: gpt-5.1 → labeled training pairs + groundedness gate
│   ├── finetune.py          # Ex 5: submit + poll the fine-tune job
│   ├── dispatcher.py        # Ex 6: 90/10 A/B routing between baseline + ft-v1
│   ├── ab_evaluate.py       # Ex 7: side-by-side eval of both variants
│   └── evaluate.py          # Shared azure-ai-evaluation harness (Groundedness + Relevance)
├── data/
│   └── golden.jsonl         # 15 golden (question, context, ground_truth) rows
├── scripts/
│   └── deploy_ft.sh         # Ex 6: az CLI scaffold for deploying the fine-tuned model
├── requirements.txt         # Packages already installed in the python-ai container
├── .env.example
├── .gitignore
└── README.md
```

## Infrastructure

The lab's ARM template pre-provisions every Azure resource into your lab
resource group. You do **not** deploy Bicep or ARM yourself. Allow up to
**12 minutes** for the environment to become ready before beginning
Exercise 1 — the deployment script that seeds the `contracts-v3` index is
the slow step.

- Foundry AI Services account + project
- `gpt-5.1` GlobalStandard deployment (synthetic-label generation only)
- `gpt-4.1-mini` GlobalStandard deployment (baseline + fine-tune base)
- `text-embedding-3-large` GlobalStandard deployment (3072-dim embeddings)
- Azure AI Search — Standard tier, semantic ranker Free plan enabled
- Pre-seeded `contracts-v3` index (15 chunks of Meridian carrier-contract text)
- App Insights + Log Analytics workspace

## Setup

Every package in `requirements.txt` is preinstalled in the `python-ai`
VS Code container the lab runs in. Do **not** run `pip install` at lab time.

```bash
cp .env.example .env
# Values are pre-filled from the ARM template outputs — inspect them:
cat .env
```

## Model & fine-tuning choice — why `gpt-4.1-mini` and not `gpt-5-mini`?

Azure OpenAI supports Supervised Fine-Tuning (SFT) on `gpt-4o-mini`,
`gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, and `gpt-4.1-nano` as of the current
model catalog. GPT-5 family models are inference-only in Foundry today.
`gpt-4.1-mini` is the cost-optimized SFT-supported base that most closely
matches the "small, fast, style-tunable" role in Meridian's stack.

## Exercise walkthrough

1. **Verify the Search index + baseline RAG** — inspect `contracts-v3`,
   run `python -m app.baseline_rag`, record baseline groundedness.
2. **Vary chunk size and re-evaluate** — reindex at 256 and 1024 via
   `python -m app.reindex 256` / `1024`, compare scores.
3. **Enable hybrid search + semantic ranker** — swap to `search_semantic_hybrid`
   in `hybrid_rag.py` and re-evaluate on entity-named queries.
4. **Synthesize 200 labeled training examples** — `python -m app.synthesize`
   produces `training.jsonl`, gates each pair on a groundedness check.
5. **Submit a Foundry fine-tune job on `gpt-4.1-mini`** — `python -m app.finetune`.
6. **Deploy the fine-tuned model + 10% traffic split** — `bash scripts/deploy_ft.sh`
   then run the dispatcher.
7. **A/B evaluate + promote** — `python -m app.ab_evaluate`, decide, promote.

## MS Learn references (agent will re-query these at runtime)

- Hybrid search — https://learn.microsoft.com/azure/search/hybrid-search-overview
- Semantic ranker — https://learn.microsoft.com/azure/search/semantic-search-overview
- Foundry fine-tuning — https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning
- Fine-tuning considerations — https://learn.microsoft.com/azure/ai-foundry/openai/concepts/fine-tuning-considerations
- RAG evaluators — https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rag-evaluators
