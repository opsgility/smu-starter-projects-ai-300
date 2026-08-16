# Observability — one glass for Meridian ops

Exercise 6 builds the Azure Monitor Workbook committed as `workbook.json`.
It is a single-page dashboard with five tiles:

1. **ETA endpoint p95 latency + current accuracy** — line chart from
   `AmlOnlineEndpointRequestLog` in the Log Analytics workspace + single-stat
   accuracy from the last 100 ground-truth callbacks (custom event
   `eta.ground_truth_delta`).
2. **Dispatcher rolling groundedness** — 7-day line chart from the evaluation
   runs (`customEvents | where name == "dispatcher.eval.groundedness"`).
3. **Dispatcher token cost per day** — bar chart from `customMetrics` named
   `dispatcher.cost.usd`.
4. **Search retrieval quality** — average `@search.reranker_score` per query,
   last 24 h, from `customMetrics` `search.reranker_score`.
5. **Business metric — matched/total** — single big number from
   `customEvents` `autodispatch.match_outcome`, computed as
   `count(outcome == "matched") / count(*)` over the last 24 h.

Deploy the workbook via `Microsoft.Insights/workbooks` in
`deploy-autodispatch.yml` (adjacent step to the ACA revision update).
