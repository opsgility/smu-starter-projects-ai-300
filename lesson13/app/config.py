"""Environment loader shared across the lab's Python modules.

Every exercise reads its configuration from `.env`, which is populated from
the ARM template outputs at lab start. Do NOT hard-code values — the
subscription and endpoints are re-issued on every lab launch.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_endpoint: str
    openai_endpoint: str
    baseline_deployment: str
    synth_deployment: str
    embedding_deployment: str
    search_endpoint: str
    search_index: str
    fine_tuned_deployment: str
    subscription_id: str
    resource_group: str
    openai_account_name: str


def load() -> Settings:
    def _get(name: str, default: str = "") -> str:
        return os.environ.get(name, default)

    return Settings(
        project_endpoint=_get("AZURE_AI_PROJECT_ENDPOINT"),
        openai_endpoint=_get("AZURE_OPENAI_ENDPOINT"),
        baseline_deployment=_get("BASELINE_DEPLOYMENT", "gpt-4.1-mini"),
        synth_deployment=_get("SYNTH_DEPLOYMENT", "gpt-5.1"),
        embedding_deployment=_get("EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
        search_endpoint=_get("AZURE_SEARCH_ENDPOINT"),
        search_index=_get("AZURE_SEARCH_INDEX", "contracts-v3"),
        fine_tuned_deployment=_get("FINE_TUNED_DEPLOYMENT", "gpt-4.1-mini-ft-v1"),
        subscription_id=_get("AZURE_SUBSCRIPTION_ID"),
        resource_group=_get("AZURE_RESOURCE_GROUP"),
        openai_account_name=_get("AZURE_OPENAI_ACCOUNT_NAME"),
    )
