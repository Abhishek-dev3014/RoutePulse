"""Deterministic planning feasibility; includes directed depot/deadhead travel."""

import heapq
from .domain import Feasibility, Network, Plan, Scenario, Trip, Violation

CHECKS = [
    "fleet_inventory",
    "availability",
    "capacity",
    "departure_window",
    "vehicle_exclusivity",
    "route_continuity",
    "travel_time",
    "network_validity",
    "minimum_service",
    "trip_identity",
]
DWELL = 0.45
TURNAROUND = 2.0


def edge_time(net: Network, a: str, b: str) -> float:
    return next(e.minutes * e.congestion_factor for e in net.edges if e.origin == a and e.destination == b)


def multiplier(sc: Scenario, route: str, t: float) -> float:
    return sc.traffic_factor if route == sc.affected_route and sc.disruption_start <= t < sc.disruption_end else 1


def arrivals(net: Network, sc: Scenario, trip: Trip) -> list[float]:
    route = next(r for r in net.routes if r.id == trip.route_id)
    out = [trip.departure]
    for a, b in zip(route.stops, route.stops[1:]):
        out.append(out[-1] + DWELL + edge_time(net, a, b) * multiplier(sc, route.id, out[-1]))
    return out


def deadhead(net: Network, a: str, b: str, factor: float = 1) -> float:
    q = [(0.0, a)]
    visited = set()
    while q:
        cost, node = heapq.heappop(q)
        if node == b:
            return cost
        if node in visited:
            continue
        visited.add(node)
        for e in net.edges:
            if e.origin == node:
                heapq.heappush(q, (cost + e.minutes * e.congestion_factor * factor, e.destination))
    return float("inf")


def blocked(sc: Scenario, vehicle_id: str, start: float, end: float) -> bool:
    return vehicle_id == sc.breakdown_vehicle and start < sc.disruption_end and end > sc.disruption_start


def validate(net: Network, sc: Scenario, plan: Plan, published: Plan | None = None) -> Feasibility:
    violations: list[Violation] = []

    def fail(c, t, detail):
        violations.append(Violation(constraint=c, trip_id=t, detail=detail))

    routes = {r.id: r for r in net.routes}
    vehicles = {v.id: v for v in net.vehicles}
    stop_ids = {s.id for s in net.stops}
    edge_ids = {(e.origin, e.destination) for e in net.edges}
    original = {t.id: t for t in published.trips} if published else {}
    seen = set()
    duties = {v.id: [] for v in net.vehicles}
    for t in plan.trips:
        if t.id in seen:
            fail("trip_identity", t.id, "Trip IDs must be unique")
        seen.add(t.id)
        if t.route_id not in routes or t.vehicle_id not in vehicles:
            fail("fleet_inventory", t.id, "Unknown route or vehicle")
            continue
        r, v = routes[t.route_id], vehicles[t.vehicle_id]
        if (
            len(r.stops) < 2
            or any(s not in stop_ids for s in r.stops)
            or any((a, b) not in edge_ids for a, b in zip(r.stops, r.stops[1:]))
        ):
            fail("network_validity", t.id, "Route must follow permitted connected edges")
            continue
        if v.capacity <= 0:
            fail("capacity", t.id, "Capacity must be positive")
        window = original.get(t.id, t)
        if (
            not window.earliest <= t.departure <= window.latest
            or t.earliest != window.earliest
            or t.latest != window.latest
        ):
            fail("departure_window", t.id, "Departure must respect the published immutable window")
        if t.id in original and t.route_id != original[t.id].route_id:
            fail("minimum_service", t.id, "Published trip route must be preserved")
        end = arrivals(net, sc, t)[-1]
        if t.departure < r.operating_window[0] or end > r.operating_window[1]:
            fail("travel_time", t.id, "Trip exceeds the route operating window")
        if (
            v.status in ("unavailable", "maintenance")
            or t.departure < v.available_from
            or end > v.available_until
            or blocked(sc, v.id, t.departure, end)
        ):
            fail("availability", t.id, "Vehicle is unavailable during this duty")
        duties[v.id].append((t.departure, end, t, r))
    for v in net.vehicles:
        previous_end, location = v.available_from, v.depot
        for start, end, t, r in sorted(duties[v.id], key=lambda x: (x[0], x[2].id)):
            travel = deadhead(net, location, r.stops[0], sc.traffic_factor)
            if start < previous_end:
                fail("vehicle_exclusivity", t.id, f"{v.id} is still on its previous duty")
            if start + 1e-8 < previous_end + travel:
                fail("route_continuity", t.id, "Insufficient time for deadhead / turnaround")
            previous_end, location = end + TURNAROUND, r.stops[-1]
    for r in net.routes:
        if sum(t.route_id == r.id for t in plan.trips) < r.minimum_trips:
            fail("minimum_service", None, f"{r.name} needs {r.minimum_trips} departures")
    if published and not set(original).issubset(seen):
        fail("minimum_service", None, "Published trips cannot be removed")
    return Feasibility(
        plan_id=plan.id,
        feasible=not violations,
        checked=CHECKS,
        violations=violations,
        vehicles_used=len({t.vehicle_id for t in plan.trips}),
        trips_scheduled=len(plan.trips),
        status="feasible" if not violations else "infeasible",
    )
