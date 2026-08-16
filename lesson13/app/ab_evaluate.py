"""Exercise 7 — side-by-side A/B evaluation of baseline vs fine-tuned variants.

Runs the golden 15-scenario dataset against BOTH deployments (bypassing the
90/10 traffic split so every scenario hits each variant). Writes ab_results.json
with per-variant aggregate groundedness + relevance, plus a delta and a
promotion recommendation.
"""
from __future__ import annotations

import json
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from app.config import load
from app.retrieval import search_semantic_hybrid
from app.evaluate import run_eval

_SETTINGS = load()
_CRED = DefaultAzureCredential()

PROMOTION_MARGIN = 0.25  # groundedness_mean delta required to recommend promotion

SYSTEM_PROMPT = (
    "You are Meridian's contract-summarizer agent. Given a user question and a set of "
    "carrier-contract clauses, produce a valid JSON object with the fields the question asks "
    "for. Cite every fact by the clause id."
)


def _run_variant(deployment: str, questions: list[str]) -> list[dict]:
    rows = []
    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            for question in questions:
                hits = search_semantic_hybrid(question, top_k=5)
                context = "\n\n".join(f"[{h['id']}] {h['chunk']}" for h in hits)
                completion = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"CLAUSES:\n{context}\n\nQUESTION:\n{question}"},
                    ],
                    response_format={"type": "json_object"},
                )
                rows.append({
                    "question": question,
                    "response": completion.choices[0].message.content,
                    "context": context,
                })
    return rows


def run_ab() -> dict:
    golden = [json.loads(line) for line in Path("data/golden.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    questions = [row["question"] for row in golden]

    baseline_rows = _run_variant(_SETTINGS.baseline_deployment, questions)
    ft_rows = _run_variant(_SETTINGS.fine_tuned_deployment, questions)

    baseline = run_eval(baseline_rows)
    ft = run_eval(ft_rows)

    delta = round(
        ft["aggregate"]["groundedness_mean"] - baseline["aggregate"]["groundedness_mean"],
        3,
    )
    recommendation = (
        f"Promote {_SETTINGS.fine_tuned_deployment} to 100%."
        if delta >= PROMOTION_MARGIN
        else f"Keep {_SETTINGS.baseline_deployment} at 100% and investigate."
    )

    result = {
        "baseline": {"deployment": _SETTINGS.baseline_deployment, **baseline["aggregate"]},
        "fine_tuned": {"deployment": _SETTINGS.fine_tuned_deployment, **ft["aggregate"]},
        "groundedness_delta": delta,
        "promotion_margin": PROMOTION_MARGIN,
        "recommendation": recommendation,
    }
    Path("ab_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run_ab()
