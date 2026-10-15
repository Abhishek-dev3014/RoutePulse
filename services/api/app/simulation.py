"""Chronological event simulation. No HTTP, database or optimization dependency."""

import hashlib
import heapq
import random
from collections import defaultdict
from .constraints import DWELL, TURNAROUND, arrivals, blocked, deadhead, edge_time, multiplier, validate
from .domain import GPS, Metrics, Network, Outcome, Passenger, Plan, Scenario, Simulation, StopEvent


def quantile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    x = sorted(values)
    pos = (len(x) - 1) * p
    lo = int(pos)
    return x[lo] + (x[min(lo + 1, len(x) - 1)] - x[lo]) * (pos - lo)


def travel(net: Network, sc: Scenario, route: str, a: str, b: str, t: float, seed: int) -> float:
    # A keyed exogenous field: changing the plan never advances an RNG stream.
    key = f"{seed}:{a}:{b}:{int(t // 10)}".encode()
    rng = random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8]))
    return edge_time(net, a, b) * multiplier(sc, route, t) * max(0.72, min(1.5, rng.lognormvariate(-0.005, 0.16)))


def simulate(net: Network, sc: Scenario, plan: Plan, passengers: list[Passenger], seed: int) -> Simulation:
    routes, vehicles, stops = (
        {r.id: r for r in net.routes},
        {v.id: v for v in net.vehicles},
        {s.id: s for s in net.stops},
    )
    feasibility = validate(net, sc, plan)
    queue: list[tuple] = []
    serial = 0

    def push(t, priority, kind, payload):
        nonlocal serial
        serial += 1
        heapq.heappush(queue, (t, priority, serial, kind, payload))

    states = {
        p.id: dict(p=p, leg=0, ready=p.arrival, wait=0.0, done=None, first=False, missed=False, target=None)
        for p in passengers
    }
    waiting = defaultdict(list)
    onboard = defaultdict(list)
    operational = []
    for p in passengers:
        push(p.arrival, 0, "passenger", p.id)
    vehicle_ready = {v.id: (v.available_from, v.depot) for v in net.vehicles}
    times, scheduled = {}, {}
    gps = []
    operating = 0.0
    delays = 0.0
    for t in sorted(plan.trips, key=lambda t: (t.departure, t.id)):
        if t.route_id not in routes or t.vehicle_id not in vehicles:
            operational.append(dict(type="invalid_assignment", trip_id=t.id, time=t.departure))
            continue
        route, v = routes[t.route_id], vehicles[t.vehicle_id]
        try:
            schedule = arrivals(net, sc.model_copy(update={"traffic_factor": 1.0}), t)
        except StopIteration:
            continue
        ready, location = vehicle_ready[v.id]
        start = max(t.departure, ready + deadhead(net, location, route.stops[0], sc.traffic_factor))
        ts = [start]
        for a, b in zip(route.stops, route.stops[1:]):
            ts.append(ts[-1] + DWELL + travel(net, sc, route.id, a, b, ts[-1] + DWELL, seed))
        if v.status in ("unavailable", "maintenance") or blocked(sc, v.id, start, ts[-1]) or ts[-1] > v.available_until:
            operational.append(
                dict(
                    type="trip_cancelled",
                    trip_id=t.id,
                    vehicle_id=v.id,
                    time=t.departure,
                    reason="Vehicle unavailable over duty interval",
                )
            )
            continue
        times[t.id], scheduled[t.id] = ts, schedule
        vehicle_ready[v.id] = (ts[-1] + TURNAROUND, route.stops[-1])
        operating += max(0, min(sc.horizon, ts[-1]) - min(sc.horizon, start))
        delays += max(0, ts[-1] - schedule[-1])
        operational.append(dict(type="vehicle_departure", trip_id=t.id, vehicle_id=v.id, time=start))
        if start > t.departure + 0.5:
            operational.append(dict(type="vehicle_delay", trip_id=t.id, time=start, minutes=start - t.departure))
        for i, at in enumerate(ts):
            push(at, 1, "stop", (t, i))
        # Interpolated GPS follows each connected directed edge; dwell remains stationary.
        for i, (a, b) in enumerate(zip(route.stops, route.stops[1:])):
            left, right = stops[a], stops[b]
            duration = ts[i + 1] - ts[i] - DWELL
            distance = next(e.distance_km for e in net.edges if e.origin == a and e.destination == b)
            for k in range(max(1, int((ts[i + 1] - ts[i]) * 2))):
                at = ts[i] + k * 0.5
                progress = max(0, min(1, (at - ts[i] - DWELL) / duration))
                if at <= sc.horizon:
                    gps.append(
                        GPS(
                            vehicle_id=v.id,
                            trip_id=t.id,
                            timestamp=at,
                            latitude=left.latitude + (right.latitude - left.latitude) * progress,
                            longitude=left.longitude + (right.longitude - left.longitude) * progress,
                            speed_kph=distance / duration * 60 if progress > 0 else 0,
                        )
                    )
    events = []
    while queue:
        now, _, _, kind, payload = heapq.heappop(queue)
        if now > sc.horizon:
            break
        if kind == "passenger":
            st = states[payload]
            leg = st["p"].legs[st["leg"]]
            waiting[(leg.route_id, leg.origin)].append(payload)
            continue
        trip, index = payload
        route = routes[trip.route_id]
        stop = route.stops[index]
        capacity = vehicles[trip.vehicle_id].capacity
        alighted = 0
        retained = []
        for pid in onboard[trip.id]:
            st = states[pid]
            leg = st["p"].legs[st["leg"]]
            if leg.destination != stop:
                retained.append(pid)
                continue
            alighted += 1
            st["leg"] += 1
            if st["leg"] == len(st["p"].legs):
                st["done"] = now
            else:
                st["first"] = True
                st["ready"] = now + 2
                next_leg = st["p"].legs[st["leg"]]
                # Intended onward service is based on scheduled first-leg arrival, not future truth.
                planned_ready = scheduled[trip.id][index] + 2
                onward = []
                for ot in plan.trips:
                    if ot.route_id == next_leg.route_id:
                        rr = routes[ot.route_id]
                        oi = rr.stops.index(next_leg.origin)
                        pt = arrivals(net, sc, ot)[oi]
                        if pt >= planned_ready:
                            onward.append((pt, ot.id))
                st["target"] = min(onward) if onward else None
                push(now + 2, 0, "passenger", pid)
                operational.append(dict(type="transfer_queue", passenger_id=pid, time=now + 2, stop_id=stop))
        onboard[trip.id] = retained
        eligible = []
        others = []
        for pid in waiting[(route.id, stop)]:
            st = states[pid]
            leg = st["p"].legs[st["leg"]]
            if st["ready"] <= now and leg.destination in route.stops[index + 1 :]:
                eligible.append(pid)
            else:
                others.append(pid)
        eligible.sort(key=lambda pid: (states[pid]["ready"], pid))
        boarding = eligible[: max(0, capacity - len(retained))]
        waiting[(route.id, stop)] = others + eligible[len(boarding) :]
        for pid in boarding:
            st = states[pid]
            st["wait"] += now - st["ready"]
            if st["leg"] > 0 and (
                st["target"] is None or (st["target"][1] != trip.id and scheduled[trip.id][index] > st["target"][0])
            ):
                st["missed"] = True
            onboard[trip.id].append(pid)
        events.append(
            StopEvent(
                time=round(now, 4),
                scheduled=round(scheduled[trip.id][index], 4),
                trip_id=trip.id,
                route_id=route.id,
                vehicle_id=trip.vehicle_id,
                stop_id=stop,
                stop_index=index,
                boarded=len(boarding),
                alighted=alighted,
                occupancy=len(onboard[trip.id]),
                capacity=capacity,
                waiting=len(eligible) - len(boarding),
            )
        )
        if index == len(route.stops) - 1:
            operational.append(dict(type="trip_completed", trip_id=trip.id, time=now))
    pending = {pid for ids in waiting.values() for pid in ids}
    outcomes = []
    for pid, st in states.items():
        wait = st["wait"] + (max(0, sc.horizon - st["ready"]) if pid in pending else 0)
        missed = st["missed"] or (st["first"] and st["done"] is None)
        outcomes.append(
            Outcome(
                passenger_id=pid,
                status="completed" if st["done"] is not None else "unserved",
                wait=round(wait, 4),
                completed_at=st["done"],
                transfer=len(st["p"].legs) > 1,
                missed_connection=missed,
            )
        )
        if missed:
            operational.append(dict(type="missed_connection", passenger_id=pid, time=sc.horizon))
    if sc.breakdown_vehicle:
        operational.append(dict(type="vehicle_breakdown", vehicle_id=sc.breakdown_vehicle, time=sc.disruption_start))
    served = sum(o.status == "completed" for o in outcomes)
    waits = [o.wait for o in outcomes]
    metrics = Metrics(
        passengers=len(passengers),
        served=served,
        unserved=len(passengers) - served,
        service_rate=round(100 * served / max(1, len(passengers)), 3),
        average_wait=round(sum(waits) / max(1, len(waits)), 3),
        p95_wait=round(quantile(waits, 0.95), 3),
        missed_connections=sum(o.missed_connection for o in outcomes),
        successful_connections=sum(
            o.transfer and o.status == "completed" and not o.missed_connection for o in outcomes
        ),
        fleet_utilization=round(100 * operating / (len(vehicles) * sc.horizon), 3),
        operating_minutes=round(operating, 3),
        total_trip_delay=round(delays, 3),
        capacity_violations=sum(e.occupancy > e.capacity for e in events),
        feasibility_violations=len(feasibility.violations),
    )
    return Simulation(
        seed=seed,
        scenario_id=sc.id,
        plan=plan,
        metrics=metrics,
        feasibility=feasibility,
        events=events,
        gps=sorted(gps, key=lambda g: (g.timestamp, g.vehicle_id)),
        outcomes=outcomes,
        operational_events=sorted(operational, key=lambda e: e["time"]),
    )
