# Judging evidence

These are inspectable features, not a guarantee of rubric points. The source-of-truth results are in the timestamped experiment JSON and its `summary.json`.

| Criterion | Implemented feature / app location | Backend evidence | Verification | Demonstration |
|---|---|---|---|---|
| Feasibility and constraints · 20 | Studio feasibility grid, fleet duties, validated accept action | `constraints.py`, `optimization.py`, `simulation.py` | `test_hard_constraints` (10 cases), immutable-window test, runtime overlap test, optimizer feasibility test | Trigger a breakdown, inspect baseline violations, generate a plan that passes all categories |
| ETA quality · 15 | Next arrivals, moving vehicles, measured error/coverage and ground-truth chart in Reports | `eta.py`: projection, past-only observations, residual quantiles | `test_eta_ordering_no_future_leakage`, `test_gps_follows_connected_edges`, `test_eta_metrics` | Scrub GPS playback; compare target 80% interval with measured coverage |
| Demand and capacity · 15 | Historical forecast, stop/direction heatmap, FIFO capacity pressure alerts | `demand.py`, `simulation.py` | Seed/capacity, alighting-before-boarding, overflow, transfer, demand-holdout tests | Switch from normal to rush; show queues and zero physical overcapacity |
| Operational improvement · 20 | Two decision types, candidate explanations, baseline/candidate chart and table | `optimization.py` planning/evaluation separation | `test_optimizer_feasible_and_measured`; same demand/seed and delta assertions | Rush: 706→849 completed, 35.304→28.062 minute mean wait in recorded run |
| Disruption robustness · 10 | Five selectable scenarios and editable disruption controls | `seed.py`, `constraints.py`, `simulation.py` | `test_disruptions_change_outcomes`, `test_clear_breakdown`, browser disruption workflow | Breakdown recovery: 602→739 completed; expose transfer regression 3→12 |
| Engineering and reproducibility · 10 | Versioned API, migration, Docker/PostgreSQL, saved snapshots, downloads, CI | `main.py`, `persistence.py`, Alembic, `scripts/experiments.py` | API persistence/export tests, migration and Compose startup, unit/API/browser tests | Export JSON, identify seeds/snapshots, rerun experiment command |
| Explainability and commercial relevance · 10 | Operator workflow, objective selection, constraints, changes/trade-offs, accept/reject audit | Objective definition and change records in `optimization.py`; decisions in `persistence.py` | API accept/reject and active-plan tests, end-to-end workflow | Explain reserve consumption and local-search limits; accept a plan and monitor it |

The brief's mandatory capabilities map directly: **A** network/fleet/timetable + domain contracts; **B** GPS ETA and held-out calibration; **C** alerts, queues, transfers and constraint violations; **D** CP-SAT assignments plus bounded timetable search; **E** same-realization simulator comparison with saved experiment evidence.

Measured scenario tables and executed-check results are in [VERIFICATION.md](VERIFICATION.md). Assumptions and metric definitions are in [EVALUATION.md](EVALUATION.md). Domain behavior and limitations are in [SIMULATION.md](SIMULATION.md).

## Added evidence from the competition audit

The **Evidence lab** and **2-minute demo** make the decision workflow immediately inspectable. `robustness.py` evaluates each frozen proposal on twenty prespecified days without calling optimization. It exposes all daily deltas, bootstrap intervals for mean change, transfer regressions and service/wait by origin. Saved JSON contains reproduction inputs and demand hashes; the replay command asserts exact results. See [ROBUSTNESS.md](ROBUSTNESS.md), [HACKATHON_STRATEGY.md](HACKATHON_STRATEGY.md) and [PILOT_PLAN.md](PILOT_PLAN.md).
