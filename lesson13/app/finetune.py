"""Exercise 5 — submit + poll an Azure OpenAI fine-tune job on gpt-4.1-mini.

Uploads `training.jsonl` as a purpose='fine-tune' file, kicks off the job
using the OpenAI-shaped fine_tuning.jobs API against the Foundry account,
and polls for completion. Prints the resulting `fine_tuned_model` id so
you can plug it into `scripts/deploy_ft.sh`.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from app.config import load

_SETTINGS = load()
_CRED = DefaultAzureCredential()

TRAINING_FILE = Path("training.jsonl")

TERMINAL_STATES = {"succeeded", "failed", "cancelled"}


def submit_and_wait(poll_seconds: int = 60) -> str:
    if not TRAINING_FILE.exists():
        raise SystemExit("training.jsonl missing — run `python -m app.synthesize` first.")

    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            print(f"Uploading {TRAINING_FILE}...")
            with TRAINING_FILE.open("rb") as fh:
                training = client.files.create(file=fh, purpose="fine-tune")
            print(json.dumps({"file_id": training.id, "status": training.status}, indent=2))

            print(f"Submitting fine-tune job on base model gpt-4.1-mini (2025-04-14)...")
            job = client.fine_tuning.jobs.create(
                model="gpt-4.1-mini-2025-04-14",
                training_file=training.id,
            )
            print(json.dumps({"job_id": job.id, "status": job.status}, indent=2))

            while True:
                job = client.fine_tuning.jobs.retrieve(job.id)
                print(f"[{time.strftime('%H:%M:%S')}] status={job.status}")
                if job.status in TERMINAL_STATES:
                    break
                time.sleep(poll_seconds)

            if job.status != "succeeded":
                raise SystemExit(f"Fine-tune ended in state {job.status}.")

            print(json.dumps({"fine_tuned_model": job.fine_tuned_model}, indent=2))
            Path("fine_tuned_model.txt").write_text(job.fine_tuned_model, encoding="utf-8")
            return job.fine_tuned_model


if __name__ == "__main__":
    submit_and_wait()
