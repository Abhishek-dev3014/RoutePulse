from copy import deepcopy
import pytest
from pydantic import ValidationError
from app.constraints import arrivals, validate
from app.demand import generate, forecast, PLANNING_SEED, HISTORY_SEEDS
from app.domain import Leg, Passenger, Plan, Vehicle, OptimizeRequest, Trip
from app.eta import predict, evaluate, match
from app.optimization import optimize, assign
from app.seed import network, baseline, scenarios
from app.simulation import simulate, quantile


@pytest.fixture
def net():
    return network()


@pytest.fixture
def sc():
    return scenarios()[0]


def test_published_baseline_feasible(net, sc):
    report = validate(net, sc, baseline(), baseline())
    assert report.feasible, report.violations
    assert len(report.checked) == 10


def test_seed_reproducibility_and_capacity(net, sc):
    passengers = generate(net, sc, sc.seed)
    a = simulate(net, sc, baseline(), passengers, sc.seed)
    b = simulate(net, sc, baseline(), generate(net, sc, sc.seed), sc.seed)
    assert a.model_dump() == b.model_dump()
    assert all(e.occupancy <= e.capacity for e in a.events)
    assert a.metrics.served + a.metrics.unserved == len(passengers)
    assert [e.time for e in a.events] == sorted(e.time for e in a.events)
    assert a.metrics.capacity_violations == 0


def test_alighting_before_boarding(net, sc):
    net.vehicles[0].capacity = 1
    trip = baseline().trips[0]
    passengers = [
        Passenger(
            id="a",
            arrival=0,
            origin="S00",
            destination="S01",
            legs=[Leg(route_id="R1", origin="S00", destination="S01")],
        ),
        Passenger(
            id="b",
            arrival=0,
            origin="S01",
            destination="S03",
            legs=[Leg(route_id="R1", origin="S01", destination="S03")],
        ),
    ]
    result = simulate(net, sc, Plan(id="one", trips=[trip]), passengers, sc.seed)
    at = next(e for e in result.events if e.stop_id == "S01")
    assert (at.alighted, at.boarded, at.occupancy) == (1, 1, 1)
    assert result.metrics.served == 2


def test_queue_overflow_and_unserved(net, sc):
    net.vehicles[0].capacity = 1
    people = [
        Passenger(
            id=str(i),
            arrival=0,
            origin="S00",
            destination="S03",
            legs=[Leg(route_id="R1", origin="S00", destination="S03")],
        )
        for i in range(3)
    ]
    result = simulate(net, sc, Plan(id="one", trips=[baseline().trips[0]]), people, 1)
    assert result.metrics.served == 1
    assert result.metrics.unserved == 2
    assert result.metrics.average_wait > 60
    assert result.events[0].waiting == 2


@pytest.mark.parametrize(
    "mutation,constraint",
    [
        ("unavailable", "availability"),
        ("window", "departure_window"),
        ("overlap", "vehicle_exclusivity"),
        ("turnaround", "route_continuity"),
        ("disconnected", "network_validity"),
        ("fleet", "fleet_inventory"),
        ("service", "minimum_service"),
        ("duplicate", "trip_identity"),
        ("depot", "route_continuity"),
        ("capacity", "capacity"),
    ],
)
def test_hard_constraints(net, sc, mutation, constraint):
    plan = baseline()
    if mutation == "unavailable":
        net.vehicles[0].status = "maintenance"
    if mutation == "window":
        plan.trips[0].departure = 0
    if mutation == "overlap":
        plan.trips[1].vehicle_id = plan.trips[0].vehicle_id
    if mutation == "turnaround":
        plan.trips[1].vehicle_id = plan.trips[0].vehicle_id
        plan.trips[1].departure = arrivals(net, sc, plan.trips[0])[-1] + 1
    if mutation == "disconnected":
        net.edges = net.edges[1:]
    if mutation == "fleet":
        plan.trips[0].vehicle_id = "V99"
    if mutation == "service":
        plan.trips = plan.trips[1:]
    if mutation == "duplicate":
        plan.trips.append(deepcopy(plan.trips[0]))
    if mutation == "depot":
        net.vehicles[0].depot = "S01"
        plan.trips[0].departure = 0
    if mutation == "capacity":
        net.vehicles[0].capacity = 0
    report = validate(net, sc, plan, baseline())
    assert not report.feasible
    assert constraint in {v.constraint for v in report.violations}


def test_cannot_widen_published_windows(net, sc):
    plan = baseline()
    plan.trips[0].earliest = 0
    plan.trips[0].departure = 0
    assert not validate(net, sc, plan, baseline()).feasible


def test_invalid_capacity_rejected():
    with pytest.raises(ValidationError):
        Vehicle(id="bad", number="bad", capacity=0)


def test_runtime_prevents_overlapping_duties(net, sc):
    plan = baseline()
    plan.trips[1].vehicle_id = plan.trips[0].vehicle_id
    run = simulate(net, sc, plan, [], 1)
    first = [e for e in run.events if e.trip_id == plan.trips[0].id]
    second = [e for e in run.events if e.trip_id == plan.trips[1].id]
    assert second[0].time >= first[-1].time + 2


def test_transfer_success_and_missing_onward(net, sc):
    p = Passenger(
        id="transfer",
        arrival=0,
        origin="S01",
        destination="S06",
        legs=[Leg(route_id="R1", origin="S01", destination="S00"), Leg(route_id="R2", origin="S00", destination="S06")],
    )
    first = baseline().trips[0]
    onward = Trip(id="connect", route_id="R2", vehicle_id="V03", departure=40, earliest=40, latest=40)
    run = simulate(net, sc, Plan(id="connect", trips=[first, onward]), [p], 1)
    assert run.metrics.served == 1 and run.metrics.successful_connections == 1
    missed = simulate(net, sc, Plan(id="missing", trips=[first]), [p], 1)
    assert missed.metrics.served == 0 and missed.metrics.missed_connections == 1
    assert missed.metrics.unserved == 1


def test_disruptions_change_outcomes(net, sc):
    people = generate(net, sc, sc.seed)
    normal = simulate(net, sc, baseline(), people, sc.seed)
    for changes in ({"breakdown_vehicle": "V01"}, {"traffic_factor": 2.0}):
        disrupted = simulate(net, sc.model_copy(update=changes), baseline(), people, sc.seed)
        assert normal.metrics != disrupted.metrics
        assert disrupted.metrics.capacity_violations == 0


def test_gps_follows_connected_edges(net, sc):
    run = simulate(net, sc, baseline(), [], 42)
    for g in run.gps[::17]:
        route = next(t.route_id for t in run.plan.trips if t.id == g.trip_id)
        _, progress, error = match(net, route, g)
        assert 0 <= progress <= 1 and error < 1e-9


def test_eta_ordering_no_future_leakage(net, sc):
    run = simulate(net, sc, baseline(), [], sc.seed)
    before = [g for g in run.gps if g.timestamp <= 40]
    a = predict(net, sc, baseline(), before, 40)
    b = predict(net, sc, baseline(), list(reversed(run.gps)), 40)
    assert a == b
    assert a
    assert all(r["earliest"] <= r["expected"] <= r["latest"] for r in a)
    assert all(r["prediction_time"] <= 40 for r in a)


def test_eta_metrics(net, sc):
    run = simulate(net, sc, baseline(), [], sc.seed)
    report = evaluate(net, sc, baseline(), run)
    assert report["sample_count"] > 50
    assert 0 <= report["coverage"] <= 100
    assert 0 <= report["mae"] < 10
    assert sc.seed not in report["calibration_seeds"]
    assert sc.seed not in report["training_seeds"]
    assert set(report["training_seeds"]).isdisjoint(report["calibration_seeds"])
    assert len(report["segment_priors"]) == len(net.edges)
    rows = report["rows"]
    assert report["mae"] == round(sum(r["error"] for r in rows) / len(rows), 3)


def test_demand_holdout(net, sc):
    report = forecast(net, sc, baseline(), generate(net, sc, sc.seed))
    assert sc.seed not in HISTORY_SEEDS and sc.seed != PLANNING_SEED
    assert report["mae"] >= 0 and report["wape"] >= 0
    assert all(r["expected_boardings"] <= r["capacity"] for r in report["rows"])
    assert any(r["category"] == "high" for r in report["rows"])


def test_quantile():
    assert quantile([], 0.95) == 0
    assert quantile([0, 10], 0.5) == 5


def test_optimizer_feasible_and_measured(net):
    sc = scenarios()[1]
    result = optimize(net, sc, baseline(), OptimizeRequest(max_candidates=8, timeout_seconds=15))
    assert result["candidate"] is not None
    candidate = Plan.model_validate(result["candidate"]["plan"])
    assert validate(net, sc, candidate, baseline()).feasible
    assert {t.vehicle_id for t in candidate.trips} <= {v.id for v in net.vehicles}
    assert result["baseline"]["seed"] == result["candidate"]["seed"] == sc.seed
    assert result["baseline"]["metrics"]["passengers"] == result["candidate"]["metrics"]["passengers"]
    assert result["candidate"]["metrics"]["capacity_violations"] == 0
    assert result["planning_seed"] != result["evaluation_seed"]
    for metric in result["comparison"]:
        assert metric["delta"] == round(metric["candidate"] - metric["baseline"], 3)


def test_solver_unsatisfiable_and_timeout(net, sc):
    for v in net.vehicles:
        v.status = "maintenance"
    plan, status = assign(net, sc, baseline(), generate(net, sc, 809), 0.1)
    assert plan is None and status in {"INFEASIBLE", "UNKNOWN"}
    result = optimize(net, sc, baseline(), OptimizeRequest(timeout_seconds=0.05))
    assert result["candidate"] is None
    assert "NO_" in result["status"]
