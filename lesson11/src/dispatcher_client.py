# Thin wrapper: builds the AzureOpenAIModelConfiguration dict the built-in
# quality evaluators need, and the (subscription_id, resource_group_name,
# project_name) dict the safety evaluators need. Both are read from the
# same .env values; keep this module the one place that knows the shape.
from __future__ import annotations

import os
from typing import Dict


def azure_openai_model_config() -> Dict[str, str]:
    """Model config for the quality evaluators (Groundedness, Relevance,
    Coherence, Fluency). They call `gpt-5.1` as the LLM-as-a-judge model.
    """
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    # Foundry project endpoints look like:
    #   https://<account>.services.ai.azure.com/api/projects/<project>
    # The quality evaluators want the account-level endpoint:
    #   https://<account>.services.ai.azure.com
    account_endpoint = endpoint.split("/api/projects/")[0]

    return {
        "azure_endpoint": account_endpoint,
        "azure_deployment": os.environ["AZURE_AI_CHAT_DEPLOYMENT"],
        "api_version": "2024-08-01-preview",
    }


def azure_ai_project() -> Dict[str, str]:
    """Project reference for the safety evaluators (Violence, SelfHarm,
    HateUnfairness, IndirectAttack). They call Microsoft's hosted Foundry
    Evaluation Service — no `model_config`, no LLM-as-a-judge.
    """
    return {
        "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
        "resource_group_name": os.environ["AZURE_RESOURCE_GROUP"],
        "project_name": os.environ["AZURE_PROJECT_NAME"],
    }
