"""Paired evaluation of a frozen plan. Never calls or feeds back into optimization."""

import hashlib
import json
import random
from collections import defaultdict
from statistics import mean
from .constraints import validate
from .demand import PLANNING_SEED, generate
from .domain import Network, Plan, Scenario
from .simulation import quantile, simulate

PROTOCOL_VERSION = "paired-20-v1"
METRICS = ("served", "average_wait", "missed_connections", "operating_minutes")


def summarize(values: list[float]) -> dict:
    # Percentile bootstrap of the paired mean, not a prediction interval for a day.
    rng = random.Random(91023)
    means = [mean(rng.choices(values, k=len(values))) for _ in range(2000)]
    return dict(
        mean_delta=round(mean(values), 4),
        minimum_delta=round(min(values), 4),
        maximum_delta=round(max(values), 4),
        mean_ci_low=round(quantile(means, 0.025), 4),
        mean_ci_high=round(quantile(means, 0.975), 4),
    )


def evaluate_plan(run: dict) -> dict:
    if not run.get("candidate"):
        raise ValueError("A saved candidate is required for validation")
    snapshot = run["input_snapshot"]
    net = Network.model_validate(snapshot["network"])
    published = Plan.model_validate(snapshot["published"])
    candidate = Plan.model_validate(run["candidate"]["plan"])
    sc = Scenario.model_validate(run["scenario"])
    feasibility = validate(net, sc, candidate, published)
    if not feasibility.feasible:
        raise ValueError("The frozen candidate fails hard-constraint validation")
    # Exclude the selection and original evaluation seeds even for custom requests.
    excluded = {PLANNING_SEED, run["planning_seed"], run["evaluation_seed"], *range(110, 122)}
    seeds = [s for s in range(70001, 70050) if s not in excluded][:20]
    rows = []
    stops = defaultdict(lambda: dict(passengers=0, baseline_served=0, candidate_served=0, wait_delta=0.0))
    for seed in seeds:
        day = sc.model_copy(update={"seed": seed})
        passengers = generate(net, day, seed)
        before = simulate(net, day, published, passengers, seed)
        after = simulate(net, day, candidate, passengers, seed)
        demand_json = json.dumps([p.model_dump() for p in passengers], sort_keys=True, separators=(",", ":"))
        rows.append(
            dict(
                seed=seed,
                demand_sha256=hashlib.sha256(demand_json.encode()).hexdigest(),
                baseline=before.metrics.model_dump(),
                candidate=after.metrics.model_dump(),
                delta={key: round(getattr(after.metrics, key) - getattr(before.metrics, key), 3) for key in METRICS},
            )
        )
        by_id = {p.id: p for p in passengers}
        old = {p.passenger_id: p for p in before.outcomes}
        for outcome in after.outcomes:
            origin = by_id[outcome.passenger_id].origin
            group = stops[origin]
            group["passengers"] += 1
            group["baseline_served"] += old[outcome.passenger_id].status == "completed"
            group["candidate_served"] += outcome.status == "completed"
            group["wait_delta"] += outcome.wait - old[outcome.passenger_id].wait
    names = {s.id: s.name for s in net.stops}
    origins = [
        dict(
            stop_id=key,
            stop_name=names[key],
            passengers=value["passengers"],
            baseline_service_rate=round(value["baseline_served"] / value["passengers"] * 100, 2),
            candidate_service_rate=round(value["candidate_served"] / value["passengers"] * 100, 2),
            mean_wait_delta=round(value["wait_delta"] / value["passengers"], 3),
        )
        for key, value in sorted(stops.items())
    ]
    frozen = dict(
        network=net.model_dump(),
        published=published.model_dump(),
        candidate=candidate.model_dump(),
        scenario=sc.model_dump(),
    )
    return dict(
        source_run_id=run.get("id", "file"),
        scenario_id=sc.id,
        protocol_version=PROTOCOL_VERSION,
        seeds=seeds,
        excluded_seeds=sorted(excluded),
        days=len(seeds),
        plan_sha256=hashlib.sha256(json.dumps(frozen, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        input_snapshot=frozen,
        demand_model_version="1.0.0",
        simulator_version="1.0.0",
        bootstrap_seed=91023,
        bootstrap_samples=2000,
        summary={key: summarize([r["delta"][key] for r in rows]) for key in METRICS},
        service_win_days=sum(r["delta"]["served"] > 0 for r in rows),
        service_loss_days=sum(r["delta"]["served"] < 0 for r in rows),
        transfer_regression_days=sum(r["delta"]["missed_connections"] > 0 for r in rows),
        candidate_capacity_violations=sum(r["candidate"]["capacity_violations"] for r in rows),
        candidate_feasibility_violations=sum(r["candidate"]["feasibility_violations"] for r in rows),
        origins=origins,
        rows=rows,
        methodology="Frozen plan; 20 prespecified synthetic days; identical passengers and traffic field within each pair. Deltas are candidate minus published. 95% percentile bootstrap intervals describe the mean over this simulator distribution, not real-world performance or next-day guarantees. No reoptimization or seed selection. Reusing this suite to tune the model invalidates its holdout status.",
    )
