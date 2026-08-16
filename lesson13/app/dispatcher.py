"""Exercise 6 — application-layer A/B dispatcher.

Routes 10% of chat traffic to `gpt-4.1-mini-ft-v1` and 90% to the baseline
`gpt-4.1-mini`. Deterministic per-question hash so a given question always
lands on the same variant across replays. Used by the ab_evaluate module
and can be smoke-tested via `python -m app.dispatcher smoke`.
"""
from __future__ import annotations

import hashlib
import sys

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from app.config import load
from app.retrieval import search_semantic_hybrid

_SETTINGS = load()
_CRED = DefaultAzureCredential()

FT_TRAFFIC_PCT = 10

SYSTEM_PROMPT = (
    "You are Meridian's contract-summarizer agent. Given a user question and a set of "
    "carrier-contract clauses, produce a valid JSON object with the fields the question asks "
    "for. Cite every fact by the clause id."
)


def route(question: str) -> str:
    """Return the deployment name to route this question to."""
    h = int(hashlib.sha256(question.encode("utf-8")).hexdigest(), 16) % 100
    if h < FT_TRAFFIC_PCT:
        return _SETTINGS.fine_tuned_deployment
    return _SETTINGS.baseline_deployment


def summarize(question: str, top_k: int = 5) -> dict:
    deployment = route(question)
    hits = search_semantic_hybrid(question, top_k=top_k)
    context = "\n\n".join(f"[{h['id']}] {h['chunk']}" for h in hits)
    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            completion = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"CLAUSES:\n{context}\n\nQUESTION:\n{question}"},
                ],
                response_format={"type": "json_object"},
            )
    return {
        "question": question,
        "deployment": deployment,
        "response": completion.choices[0].message.content,
        "context": context,
    }


def smoke() -> None:
    for q in ["What is the detention rate in MSA-Cascadia?", "Summarize the termination clauses in every MSA."]:
        result = summarize(q)
        print(f"\n[{result['deployment']}] {q}\n{result['response']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        smoke()
    else:
        print("usage: python -m app.dispatcher smoke")
