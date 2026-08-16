"""Exercise 1 — baseline RAG pipeline.

Retrieves the top-5 chunks via pure vector search, formats them into a system
prompt, calls `gpt-4.1-mini` for a JSON summary, and returns the result. The
evaluate module scores groundedness of every summary against its retrieved
context.
"""
from __future__ import annotations

import json
from pathlib import Path

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient

from app.config import load
from app.retrieval import search_vector
from app.evaluate import run_eval

_SETTINGS = load()
_CRED = DefaultAzureCredential()

SYSTEM_PROMPT = (
    "You are Meridian's contract-summarizer agent. Given a user question and a set of "
    "carrier-contract clauses, produce a valid JSON object with the fields the question asks "
    "for. Cite every fact by the clause id. If the clauses do not contain the answer, return "
    '{"answer": null, "reason": "not found in retrieved clauses"}.'
)


def summarize(question: str, top_k: int = 5, index: str | None = None) -> dict:
    hits = search_vector(question, top_k=top_k, index=index)
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


def run_baseline() -> None:
    golden = [json.loads(line) for line in Path("data/golden.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [summarize(row["question"]) for row in golden]
    ground_truths = [row.get("ground_truth", "") for row in golden]
    scores = run_eval(rows, ground_truths)
    print(json.dumps(scores, indent=2))
    Path("baseline_scores.json").write_text(json.dumps(scores, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run_baseline()
