"""predict_eta — agent tool that calls meridian-eta-endpoint.

Exercise 3. The tool MUST return a JSON-serializable dict so agent-framework
can hand it back to gpt-5.1 as tool output. On endpoint 5xx, return an
{"error": "eta_unavailable"} payload — do NOT return None or raise, or the
model will confabulate an ETA.
"""

# TODO Exercise 3:
# 1. Decorate a `predict_eta(origin: str, destination: str, pickup_iso: str,
#    carrier_tier: Literal["standard","premium"]) -> dict` function so
#    agent-framework picks it up as a tool.
# 2. Inside, call the online endpoint. Two options:
#    a) az ml online-endpoint invoke via subprocess (simpler, requires az CLI in image).
#    b) Direct REST POST to the scoring URI with a Bearer token from
#       DefaultAzureCredential().get_token("https://ml.azure.com/.default").
#    Nova will hint at which is more production-shaped.
# 3. Return {"predicted_hours": float, "confidence": float, "model_version": str}
#    on success; {"error": "eta_unavailable"} on any failure.
