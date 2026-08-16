"""Evaluation battery — Exercise 5.

Runs quality + safety + custom Meridian compliance evaluators against
`golden.jsonl` and enforces thresholds from `thresholds.yml`. Exits
non-zero on any threshold breach so the workflow fails the PR.

Nova will hint at the shape; she will NOT paste the finished file.
"""

import json
import os
import sys
from pathlib import Path

import yaml

# TODO Exercise 5:
# from azure.ai.evaluation import (
#     evaluate,
#     GroundednessEvaluator,
#     RelevanceEvaluator,
#     CoherenceEvaluator,
#     FluencyEvaluator,
#     ViolenceEvaluator,
#     SelfHarmEvaluator,
#     HateUnfairnessEvaluator,
#     AzureOpenAIModelConfiguration,
# )
# from evaluation.evaluators.meridian_no_price_commitment import MeridianNoPriceCommitmentEvaluator


THIS_DIR = Path(__file__).parent


def load_thresholds() -> dict:
    return yaml.safe_load((THIS_DIR / "thresholds.yml").read_text())


def main() -> int:
    thresholds = load_thresholds()
    # TODO: build model_config from FOUNDRY_PROJECT_ENDPOINT + CHAT_MINI_DEPLOYMENT.
    # TODO: build evaluators dict with all 7 built-ins + meridian_no_price_commitment.
    # TODO: call evaluate(data=str(THIS_DIR / "golden.jsonl"), evaluators=evaluators, ...).
    # TODO: iterate over metrics, compare against thresholds, print a per-evaluator table,
    #       and return non-zero if any evaluator dropped below its threshold.
    raise NotImplementedError("Exercise 5 — finish evaluate.py")


if __name__ == "__main__":
    sys.exit(main())
