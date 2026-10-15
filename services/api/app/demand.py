"""Time-of-day Poisson arrivals and independent historical-day forecasts."""

import math
import random
from collections import Counter
from .domain import Leg, Network, Passenger, Scenario

HISTORY_SEEDS = tuple(range(110, 122))
PLANNING_SEED = 809
BIN = 15


def pairs(net: Network):
    for r in net.routes:
        yield r.id, r.stops[0], r.stops[3], 0.45
        yield r.id, r.stops[1], r.stops[3], 0.65
        yield r.id, r.stops[2], r.stops[4], 0.4
        yield r.id, r.stops[3], r.stops[-1], 0.18
    yield "transfer", "S01", "S06", 0.30


def rate(sc: Scenario, route: str, origin: str, minute: float, base: float) -> float:
    peak = 1 + 1.8 * math.exp(-(((minute - 27) / 18) ** 2)) if origin in ("S01", "S02") else 1
    event = 3.5 if sc.id == "event" and route == "R3" and 25 <= minute < 65 else 1
    return base * peak * event * sc.demand_multiplier


def generate(net: Network, sc: Scenario, seed: int) -> list[Passenger]:
    rng = random.Random(seed)
    out = []
    for route, origin, dest, base in pairs(net):
        for minute in range(int(sc.horizon) - 20):
            lam = rate(sc, route, origin, minute, base)
            # Exact small-rate Poisson sampling, independent of plan decisions.
            n, product = -1, 1.0
            while product > math.exp(-lam):
                n += 1
                product *= rng.random()
            for _ in range(n):
                legs = (
                    [
                        Leg(route_id="R1", origin=origin, destination="S00"),
                        Leg(route_id="R2", origin="S00", destination=dest),
                    ]
                    if route == "transfer"
                    else [Leg(route_id=route, origin=origin, destination=dest)]
                )
                out.append(
                    Passenger(
                        id=f"P{len(out):05}", arrival=minute + rng.random(), origin=origin, destination=dest, legs=legs
                    )
                )
    return sorted(out, key=lambda p: (p.arrival, p.id))


def counts(passengers: list[Passenger]):
    return Counter((p.origin, int(p.arrival // BIN) * BIN, p.legs[0].route_id) for p in passengers)


def forecast(net: Network, sc: Scenario, plan, actual: list[Passenger]) -> dict:
    from .simulation import simulate

    histories = [counts(generate(net, sc, s)) for s in HISTORY_SEEDS]
    truth = counts(actual)
    # Expected available seats account for upstream boardings using an independent planning realization.
    planning = simulate(net, sc, plan, generate(net, sc, PLANNING_SEED), PLANNING_SEED)
    available = Counter()
    for e in planning.events:
        available[(e.stop_id, int(e.time // BIN) * BIN, e.route_id)] += e.capacity - e.occupancy + e.boarded
    rows = []
    keys = {(o, b, "R1" if r == "transfer" else r) for r, o, _, _ in pairs(net) for b in range(0, 120, BIN)}
    for origin, b, r in sorted(keys):
        samples = [h[(origin, b, r)] for h in histories]
        expected = sum(samples) / len(samples)
        low, high = sorted(samples)[1], sorted(samples)[-2]
        capacity = available[(origin, b, r)]
        risk = expected / max(capacity, 1)
        rows.append(
            dict(
                stop_id=origin,
                route_id=r,
                minute=b,
                expected=round(expected, 2),
                low=low,
                high=high,
                actual=truth[(origin, b, r)],
                capacity=capacity,
                expected_boardings=round(min(expected, capacity), 2),
                unmet=round(max(0, expected - capacity), 2),
                risk=round(risk, 2),
                category="high" if risk > 1 else "medium" if risk > 0.8 else "low",
            )
        )
    error = sum(abs(r["expected"] - r["actual"]) for r in rows)
    total = sum(r["actual"] for r in rows)

    def mae(subset):
        return round(sum(abs(r["expected"] - r["actual"]) for r in subset) / max(len(subset), 1), 3)

    return dict(
        rows=rows,
        mae=mae(rows),
        wape=round(error / total * 100, 2) if total else None,
        by_stop={s.id: mae([r for r in rows if r["stop_id"] == s.id]) for s in net.stops},
        by_period={
            "peak": mae([r for r in rows if 15 <= r["minute"] < 60]),
            "off_peak": mae([r for r in rows if not 15 <= r["minute"] < 60]),
        },
        historical_seeds=list(HISTORY_SEEDS),
        interval_minutes=BIN,
        assumptions="12 independent synthetic weekdays; empirical 10–90% demand range. Risk: >100% high, >80% medium. Seats estimated after upstream boarding; interval totals do not guarantee connection timing.",
    )
