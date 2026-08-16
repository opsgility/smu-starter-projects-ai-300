"""Exercise 4 — synthesize labeled training examples with a groundedness gate.

Iterates through every chunk in `contracts-v3`, asks gpt-5.1 to produce a
(clause, JSON_of_key_terms) pair, then runs a groundedness check with a
second gpt-5.1 call. Rows that do not ground back to their source clause
are dropped. Emits `training.jsonl` in Foundry chat-completion SFT format.
"""
from __future__ import annotations

import json
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.search.documents import SearchClient

from app.config import load

_SETTINGS = load()
_CRED = DefaultAzureCredential()

TARGET_ROWS = 200

LABEL_PROMPT = (
    "You extract structured key terms from carrier-contract clauses. Return a JSON object "
    "with keys: parties, effective_date, rate_table, detention, indemnity_cap, termination. "
    "Use null for fields the clause does not mention. Do NOT invent values."
)

GATE_PROMPT = (
    "You are a groundedness judge. Given a CLAUSE and a JSON_OUTPUT, answer 'YES' if every "
    "non-null field in JSON_OUTPUT can be verified verbatim (or as a direct paraphrase) from "
    "the CLAUSE. Otherwise answer 'NO'. Respond with only YES or NO."
)


def _iter_chunks(client: SearchClient):
    # `search_text=*` streams every document. In production you would page.
    for r in client.search(search_text="*", select=["id", "source", "chunk"], top=1000):
        yield {"id": r["id"], "source": r["source"], "chunk": r["chunk"]}


def synthesize(target: int = TARGET_ROWS) -> Path:
    raw_out = Path("training.raw.jsonl")
    curated_out = Path("training.jsonl")
    raw = []
    curated = []
    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            with SearchClient(
                endpoint=_SETTINGS.search_endpoint,
                index_name=_SETTINGS.search_index,
                credential=_CRED,
            ) as search:
                # Cycle through the corpus repeatedly until we hit the target.
                chunks = list(_iter_chunks(search))
                if not chunks:
                    raise RuntimeError("contracts-v3 is empty — check the ARM deployment script.")
                i = 0
                while len(curated) < target and i < target * 3:
                    chunk = chunks[i % len(chunks)]
                    i += 1
                    # Vary temperature slightly so repeats don't collapse to the same output.
                    completion = client.chat.completions.create(
                        model=_SETTINGS.synth_deployment,
                        messages=[
                            {"role": "system", "content": LABEL_PROMPT},
                            {"role": "user", "content": chunk["chunk"]},
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.7,
                    )
                    label = completion.choices[0].message.content
                    raw.append({"chunk_id": chunk["id"], "chunk": chunk["chunk"], "label": label})

                    gate = client.chat.completions.create(
                        model=_SETTINGS.synth_deployment,
                        messages=[
                            {"role": "system", "content": GATE_PROMPT},
                            {"role": "user", "content": f"CLAUSE:\n{chunk['chunk']}\n\nJSON_OUTPUT:\n{label}"},
                        ],
                        temperature=0,
                    )
                    verdict = (gate.choices[0].message.content or "").strip().upper()
                    if verdict.startswith("YES"):
                        curated.append({
                            "messages": [
                                {"role": "system", "content": "You extract structured key terms from carrier-contract clauses."},
                                {"role": "user", "content": chunk["chunk"]},
                                {"role": "assistant", "content": label},
                            ]
                        })

    raw_out.write_text("\n".join(json.dumps(r) for r in raw), encoding="utf-8")
    curated_out.write_text("\n".join(json.dumps(r) for r in curated), encoding="utf-8")
    print(json.dumps({"raw": len(raw), "curated": len(curated)}, indent=2))
    return curated_out


if __name__ == "__main__":
    synthesize()
