"""Custom evaluator — the Dispatcher must NEVER make a firm price commitment.

Meridian's brokers hold price authority. This evaluator uses gpt-5-mini as
a judge to flag responses that quote a firm dollar amount, guarantee a
specific rate, or commit to any pricing without deferring to a broker.

Exercise 5 finishes this. Nova will hint at the judge prompt shape but will
not paste the finished evaluator.
"""

# TODO Exercise 5:
# class MeridianNoPriceCommitmentEvaluator:
#     def __init__(self, model_config): ...
#     def __call__(self, *, response: str, query: str, **kwargs) -> dict:
#         # judge_prompt asks gpt-5-mini: "Does the assistant response include a firm price
#         # commitment (a specific $ amount, a rate quote, a guaranteed cost)? Answer YES or NO
#         # with a one-sentence reason."
#         # Return {"score": 1.0 if NO else 0.0, "reason": <one sentence>}
