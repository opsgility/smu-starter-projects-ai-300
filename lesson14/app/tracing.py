"""OpenTelemetry configuration for the Dispatcher API.

MUST be imported and called BEFORE the FastAPI app is constructed —
`configure_azure_monitor` wires the exporter into the process's
tracer provider, and FastAPI instrumentation later can only pick it
up if the provider was configured first.
"""

import os

from azure.monitor.opentelemetry import configure_azure_monitor


def configure_tracing() -> None:
    conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not conn_str:
        # In dev without App Insights, skip silently; do NOT crash the boot.
        return
    configure_azure_monitor(
        connection_string=conn_str,
        # OTel resource attributes let the workbook filter to this app.
        resource_attributes={"service.name": "meridian-dispatcher"},
    )
