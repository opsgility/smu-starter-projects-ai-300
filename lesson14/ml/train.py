"""ETA training script — student refines from the L7 workflow pattern.

This is a scaffold. The actual gradient-boosted regressor + MLflow logging
lives inside the AzureML job you submit with the workflow. Exercise 1 wires
the workflow, not this file. Leave the science out of the container image.
"""

from pathlib import Path


def main() -> None:
    # Placeholder. Real training happens on the AmlCompute cluster via
    # deploy-eta.yml -> az ml job create -f ml/jobs/train-eta.yml
    Path("ml/artifacts").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
