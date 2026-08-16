# Meridian Dispatcher evaluation harness — you build this out across
# Exercises 2 (quality), 3 (safety), and 4 (custom Meridian compliance).
#
# Start of Exercise 2:
#   Uncomment the QUALITY block below, run `python src/evaluate.py`, and
#   inspect the per-row output + rollup scores.
#
# Exercise 3:
#   Uncomment the SAFETY block. Safety evaluators do NOT take a model_config;
#   they hit Microsoft's hosted Foundry Evaluation Service.
#
# Exercise 4:
#   Uncomment the CUSTOM block. Your MeridianComplianceEvaluator enforces
#   the Meridian per-mile rate ceiling.
from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import evaluate

# Built-in quality evaluators — Exercise 2
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
)

# Built-in safety evaluators — Exercise 3
# (uncomment as you add them)
# from azure.ai.evaluation import (
#     ViolenceEvaluator,
#     SelfHarmEvaluator,
#     HateUnfairnessEvaluator,
#     IndirectAttackEvaluator,
# )

# Custom evaluator — Exercise 4
# from meridian_compliance import MeridianComplianceEvaluator

from dispatcher_client import azure_openai_model_config, azure_ai_project


DATA_PATH = str(Path(__file__).resolve().parent.parent / "data" / "golden.jsonl")


def main() -> None:
    load_dotenv()

    model_config = azure_openai_model_config()

    evaluators = {
        # ---- Exercise 2: quality (LLM-as-a-judge via gpt-5.1) ----
        "groundedness": GroundednessEvaluator(model_config=model_config),
        "relevance": RelevanceEvaluator(model_config=model_config),
        "coherence": CoherenceEvaluator(model_config=model_config),
        "fluency": FluencyEvaluator(model_config=model_config),

        # ---- Exercise 3: safety (hosted Foundry Evaluation Service) ----
        # project = azure_ai_project()
        # credential = DefaultAzureCredential()
        # "violence": ViolenceEvaluator(azure_ai_project=project, credential=credential),
        # "self_harm": SelfHarmEvaluator(azure_ai_project=project, credential=credential),
        # "hate_unfairness": HateUnfairnessEvaluator(azure_ai_project=project, credential=credential),
        # "indirect_attack": IndirectAttackEvaluator(azure_ai_project=project, credential=credential),

        # ---- Exercise 4: custom Meridian compliance ----
        # "meridian_compliance": MeridianComplianceEvaluator(),
    }

    result = evaluate(
        data=DATA_PATH,
        evaluators=evaluators,
    )

    print("\n=== Rollup ===")
    print(json.dumps(result.get("metrics", {}), indent=2))
    print(f"\n=== Per-row results written to: {result.get('studio_url', 'local run')} ===")


if __name__ == "__main__":
    main()
