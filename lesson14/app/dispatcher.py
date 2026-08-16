"""Dispatcher — Foundry gpt-5.1 orchestration.

Exercise 2 finishes /dispatch. Exercise 3 registers the predict_eta tool
and updates the system prompt to force tool invocation for ETA questions.

The scaffolding here is intentionally minimal. Nova will hint; do NOT ask
her to paste the completed file.
"""

import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_system_prompt() -> str:
    # Exercise 7 flips this to dispatcher_v4.md. Keep the filename resolvable at runtime.
    prompt_name = os.environ.get("DISPATCHER_PROMPT", "dispatcher_v3.md")
    return (PROMPTS_DIR / prompt_name).read_text(encoding="utf-8")


def _project_client() -> AIProjectClient:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


async def health() -> dict:
    return {
        "status": "ok",
        "chat_deployment": os.environ.get("CHAT_DEPLOYMENT", "unset"),
    }


async def dispatch(body: dict) -> dict:
    """POST /dispatch — student implements the agent orchestration here."""
    # TODO Exercise 2: construct the chat client, load the system prompt,
    # send the user query, return the response body.
    # TODO Exercise 3: register the predict_eta tool on the agent, and
    # update dispatcher_v3.md so gpt-5.1 MUST call predict_eta when asked
    # for ETAs / arrival times.
    raise NotImplementedError("Exercise 2 — finish /dispatch")
