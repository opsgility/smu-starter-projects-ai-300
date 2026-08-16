"""Exercise 3 — hybrid + semantic-ranker RAG variant.

Same summarize() shape as baseline_rag.py, but uses `search_semantic_hybrid`
(BM25 + vector + L2 semantic reranker). Re-evaluates on the golden 15
scenarios and writes hybrid_scores.json.

Entity-named queries such as "What does Section 4.2 of MSA-Cascadia say?"
benefit the most — BM25 nails the exact section token that vector search
tends to smear across synonyms.
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

SYSTEM_PROMPT = (
    "You are Meridian's contract-summarizer agent. Given a user question and a set of "
    "carrier-contract clauses, produce a valid JSON object with the fields the question asks "
    "for. Cite every fact by the clause id. If the clauses do not contain the answer, return "
    '{"answer": null, "reason": "not found in retrieved clauses"}.'
)


def summarize(question: str, top_k: int = 5) -> dict:
    hits = search_semantic_hybrid(question, top_k=top_k)
    context = "\n\n".join(f"[{h['id']}] {h['chunk']}" for h in hits)
    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            completion = client.chat.completions.create(
                model=_SETTINGS.baseline_deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"CLAUSES:\n{context}\n\nQUESTION:\n{question}"},
                ],
                response_format={"type": "json_object"},
            )
    return {
        "question": question,
        "response": completion.choices[0].message.content,
        "context": context,
    }


def run_hybrid() -> None:
    golden = [json.loads(line) for line in Path("data/golden.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [summarize(row["question"]) for row in golden]
    scores = run_eval(rows)
    print(json.dumps(scores, indent=2))
    Path("hybrid_scores.json").write_text(json.dumps(scores, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run_hybrid()
