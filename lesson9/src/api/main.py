"""
Meridian Dispatcher API — FastAPI service that wraps the Foundry gpt-5.1
deployment behind /dispatch, exposes /healthz, and streams OpenTelemetry
spans to App Insights so the Foundry portal's tracing view lights up.

Ex 4 asks you to read this file and understand the three moving parts:

1. configure_azure_monitor()      — turns on OTel export to App Insights.
2. AIProjectClient(...)           — resolves a Foundry token via managed identity.
3. The prompt is loaded from disk — /app/prompts/dispatcher_v1.md is copied
   into the image at Dockerfile build time. Every prompt change ships as a
   new image and a new Container App revision.

Environment variables (Container App env-vars, set by the deploy workflow):
    FOUNDRY_PROJECT_ENDPOINT               — e.g. https://<acct>.services.ai.azure.com/api/projects/dispatcher
    APPLICATIONINSIGHTS_CONNECTION_STRING  — pre-provisioned App Insights connection string
"""
import os
import pathlib

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI
from pydantic import BaseModel

# Turn on OpenTelemetry exporter -> App Insights BEFORE the app starts serving
# so the FastAPI HTTP server span and the openai chat span both land in the
# same trace tree in Foundry portal.
configure_azure_monitor()

PROMPT_PATH = pathlib.Path("/app/prompts/dispatcher_v1.md")
_prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
SYSTEM_MSG = _prompt_text.split("## System message", 1)[1].strip()

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai = project.inference.get_azure_openai_client(
    api_version="2025-11-13-preview",
)

app = FastAPI(title="Meridian Dispatcher API")


class DispatchRequest(BaseModel):
    load: str


@app.post("/dispatch")
def dispatch(req: DispatchRequest) -> dict[str, str]:
    resp = openai.chat.completions.create(
        model="gpt-5.1",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": req.load},
        ],
    )
    return {"answer": resp.choices[0].message.content}


@app.get("/healthz")
def healthz() -> dict[str, bool]:
    return {"ok": True}
