# Twenty-day validation of frozen proposals

These measurements use the five proposals saved in the production experiment `20261014T091653Z`. Plans were frozen before testing new seeds. Each scenario has 20 synthetic days; together this is 100 paired comparisons (200 simulations). These are not 100 observed campus days.

| Scenario | Mean extra completed journeys | 95% bootstrap interval for mean | Mean wait change (min) | Service wins | Transfer regression days | Candidate violations |
|---|---:|---|---:|---:|---:|---:|
| normal | 80.90 | 74.30 to 86.90 | -7.30 | 20/20 | 7/20 | 0 |
| rush | 149.80 | 143.55 to 155.85 | -7.38 | 20/20 | 13/20 | 0 |
| breakdown | 163.40 | 157.05 to 170.25 | -11.28 | 20/20 | 19/20 | 0 |
| traffic | 73.75 | 70.90 to 76.55 | -4.58 | 20/20 | 1/20 | 0 |
| event | 113.50 | 110.65 to 116.40 | -6.23 | 20/20 | 12/20 | 0 |

## Interpretation

Completed journeys improved in every tested pair, but transfer regressions occur in all five scenarios and are particularly frequent during breakdown recovery. Service-first optimization does not promise transfer improvement. The interface retains these regressions and shows service and mean wait by passenger origin; aggregate gains are insufficient to establish fairness.

No optimizer tuning was performed using these results. The existing plans were evaluated unchanged. Once the suite is used to tune a future model, new held-out data or a new prespecified seed suite is necessary for independent evaluation.

## Protocol and limits

- Freeze the saved network, published plan, candidate plan and scenario, identified by SHA-256 of canonical JSON.
- Use seeds 70001–70020, skipping any original planning or evaluation seed that overlaps and continuing through the reserved range. The exact list is saved. Historical forecast seeds 110–121 and planning seed 809 are excluded.
- For each day, generate one passenger list. Run both plans against that same list and the same keyed exogenous traffic field. Save all 13 metrics for both plans and a SHA-256 demand hash.
- Report candidate minus baseline. Positive completed-journey differences are improvements; negative waits and missed-connection differences are improvements. Operating minutes are a resource trade-off.
- Resample the 20 paired differences with replacement 2,000 times using bootstrap seed 91023. The 2.5th and 97.5th percentiles give a descriptive 95% interval for the mean under this simulator. This is not a prediction interval for a single day, real-world confidence, or a simultaneous guarantee over multiple metrics.
- Origin-level outcomes pool passenger journeys across all 20 days; they are passenger-weighted. Zero-demand origins are omitted. Mean wait includes waiting passengers at the horizon.
- Changes in demand and stochastic travel are tested within each scenario. Structural model errors, unknown outages, changed routes, actual driver rules and real-world distribution shift are not covered.

## Reproduce

```bash
PYTHONPATH=services/api .venv/bin/python scripts/validate_plan.py data/experiments/20261014T091653Z/rush-validation-v1.json
# Evaluate another exported optimization (output must not already exist):
PYTHONPATH=services/api .venv/bin/python scripts/validate_plan.py exported-optimization.json --output validation.json
```

Replay asserts every daily metric, demand hash, origin result and summary interval. The API exposes GET/POST `/api/v1/optimizations/{id}/validation`; repeated POST requests return the saved report for that run and protocol. JSON exports include snapshots; CSV exports contain daily deltas. No plan is accepted by evaluating it.
