"""Shared evaluation harness — Groundedness + Relevance via azure-ai-evaluation.

Each caller passes a list of {question, response, context} rows plus a parallel
list of ground_truth strings. `run_eval` returns aggregate mean pass rates.
"""
from __future__ import annotations

from statistics import mean
from typing import Sequence

from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
)

from app.config import load

_SETTINGS = load()


def _model_config() -> dict:
    # azure-ai-evaluation reads a model config dict; Foundry endpoint + deployment
    # name are sufficient. Uses managed identity when azure_ad_token is omitted.
    return {
        "azure_endpoint": _SETTINGS.openai_endpoint,
        "azure_deployment": _SETTINGS.baseline_deployment,
        "api_version": "2024-10-21",
    }


def run_eval(rows: Sequence[dict], ground_truths: Sequence[str] | None = None) -> dict:
    groundedness = GroundednessEvaluator(model_config=_model_config())
    relevance = RelevanceEvaluator(model_config=_model_config())

    g_scores: list[float] = []
    r_scores: list[float] = []
    per_row = []
    for row in rows:
        g = groundedness(
            query=row["question"],
            response=row["response"],
            context=row["context"],
        )
        r = relevance(
            query=row["question"],
            response=row["response"],
            context=row["context"],
        )
        g_scores.append(float(g.get("groundedness", 0)))
        r_scores.append(float(r.get("relevance", 0)))
        per_row.append({
            "question": row["question"],
            "groundedness": g.get("groundedness"),
            "relevance": r.get("relevance"),
        })

    return {
        "aggregate": {
            "groundedness_mean": round(mean(g_scores), 3) if g_scores else 0,
            "relevance_mean": round(mean(r_scores), 3) if r_scores else 0,
            "n": len(rows),
        },
        "per_row": per_row,
    }
