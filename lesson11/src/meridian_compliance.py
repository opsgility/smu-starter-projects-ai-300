# Custom domain evaluator: enforces Meridian Freight's contractual per-mile
# rate ceiling. Called from evaluate.py alongside the built-in Groundedness/
# Relevance/Coherence/Fluency + safety evaluators.
#
# Contract: __call__(query: str, response: str) -> dict with keys "score" and
# "reason". `score` is 0 or 1 (float); `reason` is a short human-readable
# explanation. The evaluate() harness rolls per-row scores into a mean and
# prints it as `meridian_compliance.mean` in the summary.
from __future__ import annotations

import os
import re
from typing import Any, Dict


class MeridianComplianceEvaluator:
    """Returns 1.0 when the Dispatcher response does NOT quote a per-mile
    rate above Meridian's contractual ceiling, 0.0 when it does.

    The ceiling is read from the env at construction time so a policy
    change (contract renegotiation, seasonal peak-rate window) is a
    single .env edit — no code change needed.
    """

    # Matches a USD-per-mile rate like "$4.75/mile", "$5.10 per mile",
    # "$3.90/mi", "USD 4.50 per mile". Greedy enough to catch common
    # phrasings, strict enough to avoid matching "$4.20 total".
    _RATE_RE = re.compile(
        r"\$?\s*(\d+\.\d{1,2})\s*(?:USD)?\s*(?:/|per\s+)\s*mi(?:le)?",
        flags=re.IGNORECASE,
    )

    def __init__(self, max_quote_usd_per_mile: float | None = None) -> None:
        if max_quote_usd_per_mile is None:
            max_quote_usd_per_mile = float(
                os.environ.get("MAX_QUOTE_USD_PER_MILE", "4.20")
            )
        self.max_quote = float(max_quote_usd_per_mile)

    # The evaluate() harness invokes evaluators as callables. Keyword args
    # are mapped from the JSONL columns via evaluate()'s built-in mapping —
    # the JSONL rows in data/golden.jsonl use "query" and "response" keys.
    def __call__(self, *, query: str, response: str, **kwargs: Any) -> Dict[str, Any]:
        matches = self._RATE_RE.findall(response or "")

        if not matches:
            return {
                "score": 1.0,
                "reason": (
                    f"No per-mile rate quoted; ceiling ${self.max_quote:.2f}/mile not breached."
                ),
            }

        quotes = [float(m) for m in matches]
        breaches = [q for q in quotes if q > self.max_quote]

        if not breaches:
            return {
                "score": 1.0,
                "reason": (
                    f"Quoted rates {quotes} all at or below Meridian ceiling "
                    f"${self.max_quote:.2f}/mile."
                ),
            }

        return {
            "score": 0.0,
            "reason": (
                f"Quoted rate(s) {breaches} exceed Meridian ceiling "
                f"${self.max_quote:.2f}/mile — response violates Nadia Ortega's "
                "post-incident rate policy."
            ),
        }
