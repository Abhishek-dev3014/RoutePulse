"""GPS map matching and speed/prior blending, with held-out residual calibration."""

import math
from .constraints import DWELL, arrivals, edge_time, multiplier
from .domain import GPS, Network, Plan, Scenario, Simulation
from .simulation import quantile, simulate


def match(net: Network, route_id: str, observation: GPS) -> tuple[int, float, float]:
    route = next(r for r in net.routes if r.id == route_id)
    stops = {s.id: s for s in net.stops}
    matches = []
    for i, (a, b) in enumerate(zip(route.stops, route.stops[1:])):
        aa, bb = stops[a], stops[b]
        dx, dy = bb.longitude - aa.longitude, bb.latitude - aa.latitude
        f = max(
            0,
            min(
                1,
                ((observation.longitude - aa.longitude) * dx + (observation.latitude - aa.latitude) * dy)
                / (dx * dx + dy * dy),
            ),
        )
        err = math.hypot(observation.longitude - aa.longitude - f * dx, observation.latitude - aa.latitude - f * dy)
        matches.append((err, i, f))
    err, i, f = min(matches)
    return i, f, err


def predict(
    net: Network,
    sc: Scenario,
    plan: Plan,
    observations: list[GPS],
    as_of: float,
    residuals: tuple[float, float] = (-1, 1),
    segment_priors: dict[str, float] | None = None,
) -> list[dict]:
    # Future observations are discarded before any map matching/smoothing.
    valid = sorted([o for o in observations if o.timestamp <= as_of and o.quality >= 0.5], key=lambda o: o.timestamp)
    grouped = {}
    for obs in valid:
        grouped.setdefault(obs.trip_id, []).append(obs)
    trips = {t.id: t for t in plan.trips}
    out = []
    for tid, trace in grouped.items():
        if tid not in trips:
            continue
        obs = trace[-1]
        if as_of - obs.timestamp > 1.1:
            continue
        trip = trips[tid]
        route = next(r for r in net.routes if r.id == trip.route_id)
        segment, progress, error = match(net, route.id, obs)
        if error > 0.0005:
            continue
        if progress >= 1 - 1e-8:
            segment += 1
            progress = 0.0
        speeds = [o.speed_kph for o in trace[-4:] if o.speed_kph > 0.5]
        speed = sum(speeds) / len(speeds) if speeds else 18 / multiplier(sc, route.id, obs.timestamp)
        expected = obs.timestamp
        for i in range(segment, len(route.stops) - 1):
            a, b = route.stops[i : i + 2]
            edge = next(e for e in net.edges if e.origin == a and e.destination == b)
            remaining = 1 - progress if i == segment else 1
            prior = (segment_priors or {}).get(f"{a}:{b}", edge_time(net, a, b)) * multiplier(sc, route.id, expected)
            speed_based = edge.distance_km / max(4, speed) * 60
            expected += remaining * (0.7 * prior + 0.3 * speed_based) + (
                DWELL if i > segment or obs.speed_kph == 0 else 0
            )
            schedule = arrivals(net, sc.model_copy(update={"traffic_factor": 1.0}), trip)[i + 1]
            out.append(
                dict(
                    vehicle_id=trip.vehicle_id,
                    trip_id=tid,
                    route_id=route.id,
                    stop_id=b,
                    stop_index=i + 1,
                    prediction_time=obs.timestamp,
                    expected=round(expected, 3),
                    earliest=round(max(obs.timestamp, expected + residuals[0]), 3),
                    latest=round(max(obs.timestamp, expected + residuals[1]), 3),
                    delay=round(expected - schedule, 3),
                    latitude=obs.latitude,
                    longitude=obs.longitude,
                    progress=round(progress, 3),
                    segment=segment,
                )
            )
    return out


def samples(net, sc, plan, run, residuals, segment_priors=None):
    actual = {(e.trip_id, e.stop_index): e.time for e in run.events}
    out = []
    for minute in range(10, 105, 5):
        for row in predict(net, sc, plan, run.gps, minute, residuals, segment_priors):
            truth = actual.get((row["trip_id"], row["stop_index"]))
            if truth is not None and truth > row["prediction_time"]:
                out.append({**row, "actual": round(truth, 3), "error": round(abs(truth - row["expected"]), 3)})
    return out


def evaluate(net: Network, sc: Scenario, plan: Plan, run: Simulation) -> dict:
    # Calibration days do not contain evaluation-day traces or outcomes.
    # Fit segment travel priors on separate historical journeys, before calibration.
    observations: dict[str, list[float]] = {}
    for seed in (151, 152, 153, 154):
        training = simulate(net, sc, plan, [], seed)
        by_trip = {}
        for event in training.events:
            by_trip.setdefault(event.trip_id, []).append(event)
        for events in by_trip.values():
            for left, right in zip(events, events[1:]):
                key = f"{left.stop_id}:{right.stop_id}"
                normalized = (right.time - left.time - DWELL) / multiplier(sc, left.route_id, left.time + DWELL)
                observations.setdefault(key, []).append(normalized)
    priors = {key: sum(values) / len(values) for key, values in observations.items()}
    historical = []
    for seed in (201, 202, 203, 204):
        cal = simulate(net, sc, plan, [], seed)
        historical.extend(samples(net, sc, plan, cal, (-1, 1), priors))
    residuals = [r["actual"] - r["expected"] for r in historical]
    bounds = (quantile(residuals, 0.1), quantile(residuals, 0.9))
    rows = samples(net, sc, plan, run, bounds, priors)
    errors = [r["error"] for r in rows]
    return dict(
        mae=round(sum(errors) / max(1, len(errors)), 3),
        median_absolute_error=round(quantile(errors, 0.5), 3),
        p90_absolute_error=round(quantile(errors, 0.9), 3),
        coverage=round(100 * sum(r["earliest"] <= r["actual"] <= r["latest"] for r in rows) / max(1, len(rows)), 2),
        average_width=round(sum(r["latest"] - r["earliest"] for r in rows) / max(1, len(rows)), 3),
        sample_count=len(rows),
        residual_bounds=list(bounds),
        calibration_seeds=[201, 202, 203, 204],
        training_seeds=[151, 152, 153, 154],
        segment_priors=priors,
        estimator_version="1.1.0",
        target_coverage=80,
        rows=rows,
        assumptions="Route projection; 70% historical segment prior + 30% smoothed observed speed; fixed 27-second dwell. Empirical residual interval from four independent synthetic days, target 80%; coverage is measured, not guaranteed.",
    )
