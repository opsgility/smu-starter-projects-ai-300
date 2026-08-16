"""Dispatcher API entry — student refines dispatcher.py; this file wires the app."""

from app.tracing import configure_tracing

# Configure tracing BEFORE FastAPI is constructed. Reordering these lines breaks
# telemetry — App Insights will not receive dependency spans.
configure_tracing()

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.dispatcher import dispatch, health

app = FastAPI(title="Meridian Auto-Dispatch")
FastAPIInstrumentor.instrument_app(app)

app.get("/health")(health)
app.post("/dispatch")(dispatch)
