# Evaluation protocol

Run `PYTHONPATH=services/api .venv/bin/python scripts/experiments.py` to produce all five scenario experiments under a new UTC-timestamped directory in `data/experiments`. `summary.json` is the compact measured evidence. Full JSON files include inputs, plans, passenger outcomes, GPS, events, search history, uncertainty calibration and forecast errors. No improvement claim is hardcoded.

## Baseline and controls

The published plan has departures every 15 minutes on each route, with two alternating vehicles per route and one reserve. Offsets between routes are two minutes. This is a plausible fixed small-campus service, not an intentionally broken normal-operation baseline. Demand/traffic/breakdown scenarios can make that fixed baseline inadequate or infeasible; this is reported before recovery planning.

Evaluation seeds are 4101 normal, 4102 rush, 4103 breakdown, 4104 traffic and 4105 event. Historical forecasting uses 110–121, planning uses 809 and ETA prior training uses 151–154 and residual calibration uses 201–204. Baseline and candidate share the exact evaluation passenger list and exogenous edge/time-bucket traffic field. Different departure times may encounter different time buckets, representing a legitimate change in operating conditions at a different clock time.

| Metric | Definition |
|---|---|
| Passengers | Number of generated people arriving before 09:40 |
| Served | People who reach their final destination by 10:00 |
| Unserved | Demand minus completed journeys, including unfinished onboard journeys |
| Service rate | 100 × served / demand, zero for zero demand |
| Average wait | Sum of all passengers' queue waiting, including unfinished waiting to cutoff, divided by demand |
| P95 wait | Linearly interpolated 95th percentile of those per-person queue waits |
| Missed connections | Completed-first-leg passengers who take a later intended service or remain incomplete |
| Successful connections | Completed transfer journeys that did not miss the intended connection |
| Fleet utilization | 100 × in-window route operating minutes / (7 inventory vehicles × 120 minutes); reserve remains in denominator |
| Operating minutes | Route runtime overlapping the evaluation window, including dwell; excludes deadhead/turnaround |
| Total trip delay | Sum of positive terminal delays versus published uncongested timetable; can include terminal times after cutoff |
| Capacity violations | Count of stop observations above physical capacity; must be zero |
| Feasibility violations | Number of validator violations, which can include multiple categories for one duty |

CSV includes baseline, candidate, absolute delta, beneficial percentage when meaningful, and direction. Beneficial percentage reverses for higher-is-better service metrics. A zero denominator produces null, not a fabricated percentage. Utilization and operating minutes are neutral trade-offs. Incomplete optimization returns unchanged comparison values with an explicit no-improvement status.

## ETA

Observations newer than the prediction instant are removed before sorting or map matching. Segment priors are learned from four independent historical journeys (seeds 151–154), normalized for known congestion. GPS is projected onto a route segment; upcoming stop times blend 70% segment-time prior and 30% smoothed observed speed, plus dwell. Residual 10th and 90th percentiles from four independent synthetic days define the 80%-target interval. Evaluation uses the held-out day, samples every five minutes, and compares only actual future stop arrivals within the horizon. Reported metrics: MAE, median absolute error, P90 absolute error, empirical interval coverage, average width and sample count. Intervals can under-cover and are not guaranteed to generalize to real-world GPS.

## Demand

For each origin/direction/15-minute bin, the forecast is the mean across twelve historical synthetic days. The approximate empirical low/high range is the second through eleventh ordered observations. Expected available seats come from a separate planning simulation after upstream occupancy. Risk thresholds are >100% high, >80% medium, otherwise low. Interval totals do not ensure that a particular passenger arrives before a particular bus.

Demand MAE averages absolute error across all defined origin/route/time cells, including zero-demand tail bins. WAPE is 100 × sum absolute error / total observed arrivals; null if no observed demand. Stop and peak/off-peak MAE are available in the API and dashboard. Peak is 08:15–09:00.

## Limits

One held-out realization per scenario demonstrates reproducibility, not statistical significance. Search candidates can overfit the one planning realization. Equal seeds control randomness but are not evidence that a field deployment will achieve the same benefit. Larger experiments should use multiple planning days and many evaluation seeds with confidence intervals. Original run JSON is the source of truth for every reported result.

## Multi-day follow-up evaluation

The independent fixed-plan validation suite is documented in [ROBUSTNESS.md](ROBUSTNESS.md). It evaluates twenty additional seeds per saved plan, pairing identical passenger and traffic inputs. Its bootstrap interval estimates mean difference under the simulator; it is not an ETA prediction interval or evidence of real-world benefit. Validation results are never used to select candidates, and evaluating a proposal does not accept it. Transfer and origin-level regressions remain visible.
