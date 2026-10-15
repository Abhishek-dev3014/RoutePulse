"""Bounded timetable search + CP-SAT assignment. Evaluation truth is never ranked."""

import time
from copy import deepcopy
from ortools.sat.python import cp_model
from .constraints import TURNAROUND, arrivals, blocked, deadhead, validate
from .demand import PLANNING_SEED, generate
from .domain import Network, OptimizeRequest, Plan, Scenario
from .simulation import simulate


def assign(net: Network, sc: Scenario, plan: Plan, forecast_passengers, seconds: float) -> tuple[Plan | None, str]:
    model = cp_model.CpModel()
    choices = {}
    route_map = {r.id: r for r in net.routes}
    times = {t.id: (t.departure, arrivals(net, sc, t)[-1]) for t in plan.trips}
    rewards = []
    for ti, t in enumerate(plan.trips):
        start, end = times[t.id]
        demand = sum(
            p.legs[0].route_id == t.route_id and start - 15 <= p.arrival < start + 8 for p in forecast_passengers
        )
        for vi, v in enumerate(net.vehicles):
            x = model.new_bool_var(f"t{ti}v{vi}")
            choices[ti, vi] = x
            if (
                v.status in ("unavailable", "maintenance")
                or start < v.available_from + deadhead(net, v.depot, route_map[t.route_id].stops[0], sc.traffic_factor)
                or end > v.available_until
                or blocked(sc, v.id, start, end)
            ):
                model.add(x == 0)
            rewards.append(x * (min(v.capacity, demand) * 100 - (v.id != t.vehicle_id) * 3 - vi))
        model.add_exactly_one(choices[ti, vi] for vi in range(len(net.vehicles)))
    for i, a in enumerate(plan.trips):
        for j in range(i + 1, len(plan.trips)):
            b = plan.trips[j]
            first, second = (a, b) if a.departure <= b.departure else (b, a)
            relocation = deadhead(
                net, route_map[first.route_id].stops[-1], route_map[second.route_id].stops[0], sc.traffic_factor
            )
            if times[first.id][1] + TURNAROUND + relocation > times[second.id][0]:
                for vi in range(len(net.vehicles)):
                    model.add(choices[i, vi] + choices[j, vi] <= 1)
    model.maximize(sum(rewards))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(0.001, seconds)
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 23
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, solver.status_name(status)
    result = deepcopy(plan)
    for ti, t in enumerate(result.trips):
        t.vehicle_id = next(v.id for vi, v in enumerate(net.vehicles) if solver.value(choices[ti, vi]))
    return result, solver.status_name(status)


def score(run, objective, changes=0):
    m = run.metrics
    # Service is always first, so abandoning difficult passengers cannot improve the score.
    secondary = (
        (m.average_wait, m.missed_connections) if objective == "wait" else (m.missed_connections, m.average_wait)
    )
    cost = m.operating_minutes + (changes * 2 if objective == "balanced" else changes * 0.1)
    return (m.unserved, *secondary, cost)


def optimize(net: Network, sc: Scenario, published: Plan, request: OptimizeRequest) -> dict:
    began = time.monotonic()
    planning_demand = generate(net, sc, PLANNING_SEED)
    planning_baseline = simulate(net, sc, published, planning_demand, PLANNING_SEED)
    baseline_valid = validate(net, sc, published, published)
    best = None
    best_score = score(planning_baseline, request.objective) if baseline_valid.feasible else (float("inf"),) * 4
    history = []
    # Route-level offsets preserve within-route headways and immutable individual windows.
    offsets = [(0, 0, 0)]
    for shift in (-4, 4, -2, 2):
        offsets.extend(tuple(shift if i == r else 0 for i in range(3)) for r in range(3))
    offsets.extend(
        [
            (a, b, c)
            for a, b, c in [(-4, -4, -4), (4, 4, 4), (-4, 4, 0), (0, -4, 4), (4, 0, -4), (-2, 2, 2), (2, -2, -2)]
        ]
    )
    timed_out = False
    for index, offset in enumerate(offsets[: request.max_candidates]):
        remaining = request.timeout_seconds - (time.monotonic() - began)
        if remaining <= 0:
            timed_out = True
            break
        candidate = deepcopy(published)
        candidate.id = f"candidate-{index + 1}"
        for t in candidate.trips:
            t.departure += offset[int(t.route_id[1:]) - 1]
        candidate, status = assign(net, sc, candidate, planning_demand, min(0.4, remaining))
        if candidate is None:
            history.append(dict(index=index, status=status, feasible=False))
            continue
        feasible = validate(net, sc, candidate, published)
        if not feasible.feasible:
            history.append(dict(index=index, status="VALIDATION_REJECTED", feasible=False))
            continue
        estimated = simulate(net, sc, candidate, planning_demand, PLANNING_SEED)
        changes = sum(
            a.vehicle_id != b.vehicle_id or a.departure != b.departure for a, b in zip(published.trips, candidate.trips)
        )
        value = score(estimated, request.objective, changes)
        history.append(
            dict(index=index, status=status, feasible=True, score=list(value), metrics=estimated.metrics.model_dump())
        )
        if value < best_score:
            best_score = value
            best = (candidate, estimated, feasible)
    # Only after the recommendation is fixed do we reveal held-out evaluation outcomes.
    demand = generate(net, sc, sc.seed)
    baseline = simulate(net, sc, published, demand, sc.seed)
    result = None
    changes = []
    if best:
        candidate, estimated, feasible = best
        result = simulate(net, sc, candidate, demand, sc.seed)
        for before, after in zip(published.trips, candidate.trips):
            if before.vehicle_id != after.vehicle_id or before.departure != after.departure:
                changes.append(
                    dict(
                        trip_id=before.id,
                        route_id=before.route_id,
                        old_vehicle=before.vehicle_id,
                        new_vehicle=after.vehicle_id,
                        old_departure=before.departure,
                        new_departure=after.departure,
                        explanation=f"Assign {after.vehicle_id} to {after.id} at minute {after.departure:g}; inside [{before.earliest:g}, {before.latest:g}], with availability, turnaround and directed relocation checked.",
                    )
                )
    comparison = []
    for key, b in baseline.metrics.model_dump().items():
        c = getattr(result.metrics, key) if result else b
        higher = key in ("served", "service_rate", "successful_connections")
        neutral = key in ("passengers", "fleet_utilization", "operating_minutes")
        delta = round(c - b, 3)
        improvement = c - b if higher else b - c
        comparison.append(
            dict(
                metric=key,
                baseline=b,
                candidate=c,
                delta=delta,
                improvement_percent=round(improvement / abs(b) * 100, 2) if b and not neutral else None,
                direction="neutral" if neutral or not delta else "improved" if improvement > 0 else "regressed",
            )
        )
    elapsed = round(time.monotonic() - began, 3)
    return dict(
        scenario=sc.model_dump(),
        objective=request.objective,
        planning_seed=PLANNING_SEED,
        evaluation_seed=sc.seed,
        status=("TIME_LIMIT_FEASIBLE" if timed_out else "FEASIBLE_RECOMMENDATION")
        if best
        else ("TIME_LIMIT_NO_IMPROVEMENT" if timed_out else "NO_FEASIBLE_IMPROVEMENT"),
        runtime_seconds=elapsed,
        candidates_evaluated=len(history),
        search_history=history,
        baseline=baseline.model_dump(),
        candidate=result.model_dump() if result else None,
        planning_metrics=best[1].metrics.model_dump() if best else planning_baseline.metrics.model_dump(),
        planning_baseline_metrics=planning_baseline.metrics.model_dump(),
        comparison=comparison,
        changes=changes,
        explanation=(
            f"Change {len(changes)} published duties using the existing fleet. Selected by independent planning demand; all ten hard-constraint categories pass. Held-out evaluation is shown separately."
            if best
            else "No improving feasible plan found within the bounded search. The published plan is unchanged."
        ),
        tradeoffs=[
            "Reassignments change driver duties and may consume reserve fleet capacity.",
            "Timetable shifts may increase waits at individual stops; aggregate gains are not guaranteed on the held-out day.",
            "CP-SAT solves assignments for each fixed timetable; the whole transport plan is not proven globally optimal.",
        ],
        input_snapshot=dict(
            network=net.model_dump(),
            published=published.model_dump(),
            request=request.model_dump(),
            passenger_demand=[p.model_dump() for p in demand],
            planning_demand=[p.model_dump() for p in planning_demand],
            demand_model_version="1.0.0",
        ),
        decision="pending" if best else "not_applicable",
    )
