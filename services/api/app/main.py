"""Versioned thin controllers over deterministic domain services."""

import csv
import io
import json
import logging
import os
import threading
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Literal
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from . import persistence as store
from .constraints import arrivals, validate
from .demand import forecast, generate
from .domain import (
    GPS,
    Model,
    Network,
    OptimizeRequest,
    Plan,
    RunRequest,
    Scenario,
    Route,
    Stop,
    Vehicle,
    Trip,
    Feasibility,
    Passenger,
    ValidateRequest,
)
from .eta import evaluate, predict
from .optimization import optimize
from .robustness import PROTOCOL_VERSION, evaluate_plan
from .seed import baseline, network
from .simulation import simulate
from .responses import (
    ArrivalPrediction,
    DashboardResponse,
    DemandReport,
    ETAForecast,
    SimulationResponse,
    OptimizationResponse,
    HistoryRow,
    RobustnessResponse,
)

logger = logging.getLogger("routepulse")
lock = threading.BoundedSemaphore(2)


@asynccontextmanager
async def lifespan(app):
    store.seed_database()
    yield


app = FastAPI(
    title="RoutePulse",
    version="1.0.0",
    description="Single-campus synthetic operations demo. No authentication; bind locally.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(
        status_code=exc.status_code, content={"error": {"code": exc.status_code, "message": exc.detail}}
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Invalid request",
                "details": [{"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()],
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc):
    logger.exception(json.dumps({"event": "request_failed", "path": request.url.path}))
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Unable to complete the operation. See server logs."}},
    )


def load_network() -> Network:
    with Session(store.engine) as db:
        row = db.get(store.Entity, "network:network-v1")
        return Network.model_validate(row.payload) if row else network()


def load_plan() -> Plan:
    with Session(store.engine) as db:
        row = db.get(store.Entity, "plan:published-v1")
        return Plan.model_validate(row.payload) if row else baseline()


def scenario(req: RunRequest) -> Scenario:
    with Session(store.engine) as db:
        row = db.get(store.Entity, f"scenario:{req.scenario_id}")
    if not row:
        raise HTTPException(404, "Scenario not found")
    changes = req.model_dump(
        exclude_unset=True,
        exclude={"scenario_id", "objective", "max_candidates", "timeout_seconds", "plan", "observations", "as_of"},
    )
    try:
        sc = Scenario.model_validate({**row.payload, **changes})
    except ValueError as exc:
        raise HTTPException(422, "Invalid disruption interval or scenario parameters") from exc
    net = load_network()
    if sc.breakdown_vehicle and sc.breakdown_vehicle not in {v.id for v in net.vehicles}:
        raise HTTPException(422, "Unknown breakdown vehicle")
    if sc.affected_route not in {r.id for r in net.routes}:
        raise HTTPException(422, "Unknown affected route")
    return sc


@lru_cache(maxsize=24)
def bundle(serialized: str, net_json: str, plan_json: str):
    sc = Scenario.model_validate_json(serialized)
    net = Network.model_validate_json(net_json)
    plan = Plan.model_validate_json(plan_json)
    demand = generate(net, sc, sc.seed)
    sim = simulate(net, sc, plan, demand, sc.seed)
    eta = evaluate(net, sc, plan, sim)
    demand_forecast = forecast(net, sc, plan, demand)
    alerts = []
    for route in net.routes:
        rows = [e for e in sim.events if e.route_id == route.id]
        denied = sum(e.waiting for e in rows)
        if denied:
            alerts.append(
                dict(
                    id=f"capacity-{route.id}",
                    severity="warning",
                    type="capacity_pressure",
                    route_id=route.id,
                    title=f"Capacity pressure · {route.name}",
                    description=f"{denied} queue observations left behind after boarding (may include repeat riders). Physical capacity remains enforced.",
                )
            )
    if sim.metrics.unserved:
        alerts.append(
            dict(
                id="unserved",
                severity="critical",
                type="unmet_demand",
                title=f"{sim.metrics.unserved} journeys incomplete",
                description="Passengers waiting or still travelling at the end of the evaluation window.",
            )
        )
    if sim.metrics.missed_connections:
        alerts.append(
            dict(
                id="transfers",
                severity="warning",
                type="missed_connection",
                title=f"{sim.metrics.missed_connections} missed connections",
                description="First-leg riders missed their intended onward service or remained incomplete.",
            )
        )
    delayed = sum(e.time - e.scheduled > 2 for e in sim.events)
    if delayed:
        alerts.append(
            dict(
                id="delays",
                severity="warning",
                type="vehicle_delay",
                title=f"{delayed} late stop arrivals",
                description="More than 2 minutes after the published planned arrival.",
            )
        )
    for i, v in enumerate(sim.feasibility.violations):
        alerts.append(
            dict(
                id=f"constraint-{i}",
                severity="critical",
                type=v.constraint,
                title=f"Plan issue · {v.trip_id or 'service'}",
                description=v.detail,
            )
        )
    for d in sim.operational_events:
        if d["type"] == "trip_cancelled":
            alerts.append(
                dict(
                    id=d["trip_id"],
                    severity="critical",
                    type="service_disruption",
                    title=f"{d['trip_id']} cancelled",
                    description=d["reason"],
                )
            )
    return dict(simulation=sim.model_dump(), eta=eta, demand=demand_forecast, alerts=alerts)


def overview(req: RunRequest):
    sc = scenario(req)
    net, plan = load_network(), load_plan()
    active = store.active(sc.model_dump())
    if active:
        plan = Plan.model_validate(active["plan"])
    result = bundle(sc.model_dump_json(), net.model_dump_json(), plan.model_dump_json())
    return {
        **result,
        "network": net.model_dump(),
        "scenario": sc.model_dump(),
        "active_plan": active,
        "timetable": [{**t.model_dump(), "scheduled_arrivals": arrivals(net, sc, t)} for t in plan.trips],
    }


@app.get("/health")
def health() -> dict:
    with store.engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "version": "1.0.0", "database": store.engine.dialect.name}


@app.get("/api/v1/scenarios", response_model=list[Scenario])
def scenario_list():
    with Session(store.engine) as db:
        return [r.payload for r in db.scalars(select(store.Entity).where(store.Entity.kind == "scenario"))]


@app.get("/api/v1/scenarios/{identity}", response_model=Scenario)
def scenario_get(identity: str):
    return scenario(RunRequest(scenario_id=identity))


@app.get("/api/v1/network", response_model=Network)
def network_get():
    return load_network()


@app.get("/api/v1/routes", response_model=list[Route])
def routes_get():
    return load_network().routes


@app.get("/api/v1/stops", response_model=list[Stop])
def stops_get():
    return load_network().stops


@app.get("/api/v1/vehicles", response_model=list[Vehicle])
def vehicles_get():
    return load_network().vehicles


@app.get("/api/v1/trips", response_model=list[Trip])
def trips_get():
    return load_plan().trips


@app.get("/api/v1/dashboard", response_model=DashboardResponse)
def dashboard(scenario_id: str = "rush") -> dict:
    return overview(RunRequest(scenario_id=scenario_id))


@app.get("/api/v1/vehicles/positions", response_model=list[GPS])
def positions(scenario_id: str = "rush", minute: float = Query(40, ge=0, le=120)) -> list[dict]:
    data = overview(RunRequest(scenario_id=scenario_id))
    current = {}
    for g in data["simulation"]["gps"]:
        if g["timestamp"] <= minute and minute - g["timestamp"] < 1:
            current[g["vehicle_id"]] = g
    return list(current.values())


@app.get("/api/v1/stops/{identity}/arrivals", response_model=list[ArrivalPrediction])
def stop_arrivals(identity: str, scenario_id: str = "rush", minute: float = Query(40, ge=0, le=120)) -> list[dict]:
    net = load_network()
    if identity not in {s.id for s in net.stops}:
        raise HTTPException(404, "Stop not found")
    data = overview(RunRequest(scenario_id=scenario_id))
    return [
        r
        for r in predict(
            net,
            Scenario.model_validate(data["scenario"]),
            Plan.model_validate(data["simulation"]["plan"]),
            [GPS.model_validate(g) for g in data["simulation"]["gps"]],
            minute,
            tuple(data["eta"]["residual_bounds"]),
            data["eta"].get("segment_priors"),
        )
        if r["stop_id"] == identity
    ]


@app.post("/api/v1/demand", response_model=list[Passenger])
def passenger_demand(req: RunRequest):
    sc = scenario(req)
    return generate(load_network(), sc, sc.seed)


@app.post("/api/v1/forecasts/demand", response_model=DemandReport)
def forecast_demand(req: RunRequest) -> dict:
    return overview(req)["demand"]


class ETARequest(RunRequest):
    plan: Plan | None = None
    observations: list[GPS] = Field(max_length=1000)
    as_of: float = Field(ge=0, le=140)


@app.post("/api/v1/forecasts/eta", response_model=ETAForecast)
def forecast_eta(req: ETARequest) -> dict:
    sc = scenario(req)
    net = load_network()
    if req.plan and any(
        t.route_id not in {r.id for r in net.routes} or t.vehicle_id not in {v.id for v in net.vehicles}
        for t in req.plan.trips
    ):
        raise HTTPException(422, "ETA plan references an unknown route or vehicle")
    base_req = RunRequest.model_validate(
        {k: v for k, v in req.model_dump(exclude_unset=True).items() if k in RunRequest.model_fields}
    )
    data = overview(base_req)
    predictions = predict(
        load_network(),
        sc,
        req.plan or Plan.model_validate(data["simulation"]["plan"]),
        req.observations,
        req.as_of,
        tuple(data["eta"]["residual_bounds"]),
        data["eta"].get("segment_priors"),
    )
    return {"predictions": predictions, "target_coverage": 80, "assumptions": data["eta"]["assumptions"]}


@app.post("/api/v1/plans/validate", response_model=Feasibility)
def validate_plan(req: ValidateRequest):
    return validate(load_network(), scenario(req), req.plan, load_plan())


@app.post("/api/v1/simulations", status_code=201, response_model=SimulationResponse)
def simulation_create(req: RunRequest) -> dict:
    result = overview(req)
    return store.save_run(
        "simulation",
        req.scenario_id,
        {
            **result,
            "request": req.model_dump(),
            "input_snapshot": {
                "network": result["network"],
                "plan": result["simulation"]["plan"],
                "demand_model_version": "1.0.0",
                "passenger_demand": [
                    p.model_dump()
                    for p in generate(
                        load_network(), Scenario.model_validate(result["scenario"]), result["scenario"]["seed"]
                    )
                ],
            },
        },
    )


@app.get("/api/v1/simulations/{identity}", response_model=SimulationResponse)
def simulation_get(identity: str) -> dict:
    result = store.get_run(identity)
    if not result or "simulation" not in result:
        raise HTTPException(404, "Simulation not found")
    return result


@app.post("/api/v1/optimizations", status_code=201, response_model=OptimizationResponse)
def optimization_create(req: OptimizeRequest) -> dict:
    sc = scenario(req)
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "Two optimizations are already running; retry shortly")
    try:
        result = optimize(load_network(), sc, load_plan(), req)
        return store.save_run("optimization", sc.id, result)
    finally:
        lock.release()


@app.get("/api/v1/optimizations", response_model=list[HistoryRow])
def optimization_list() -> list[dict]:
    return store.history()


@app.get("/api/v1/optimizations/{identity}", response_model=OptimizationResponse)
def optimization_get(identity: str) -> dict:
    result = store.get_run(identity)
    if not result or "comparison" not in result:
        raise HTTPException(404, "Optimization not found")
    return result


@app.get("/api/v1/optimizations/{identity}/validation", response_model=RobustnessResponse | None)
def validation_get(identity: str):
    optimization_get(identity)
    return store.validation_for(identity, PROTOCOL_VERSION)


@app.post("/api/v1/optimizations/{identity}/validation", response_model=RobustnessResponse)
def validation_create(identity: str):
    run = optimization_get(identity)
    cached = store.validation_for(identity, PROTOCOL_VERSION)
    if cached:
        return cached
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "Evaluation workers are busy; retry shortly")
    try:
        result = evaluate_plan(run)
        return store.save_run("validation", identity, result)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    finally:
        lock.release()


class DecisionRequest(Model):
    decision: Literal["accepted", "rejected"]


@app.post("/api/v1/optimizations/{identity}/decision")
def decision_create(identity: str, req: DecisionRequest) -> dict:
    run = optimization_get(identity)
    if req.decision == "accepted":
        if not run["candidate"]:
            raise HTTPException(409, "No candidate to accept")
        report = validate(
            load_network(),
            Scenario.model_validate(run["scenario"]),
            Plan.model_validate(run["candidate"]["plan"]),
            load_plan(),
        )
        if not report.feasible:
            raise HTTPException(409, "Candidate no longer passes feasibility validation")
    store.decide(identity, req.decision)
    return {"id": identity, "decision": req.decision}


@app.get("/api/v1/reports/{identity}")
def report_get(identity: str, format: Literal["json", "csv"] = "json"):
    result = store.get_run(identity)
    if not result:
        raise HTTPException(404, "Report not found")
    if format == "json":
        return JSONResponse(
            result, headers={"Content-Disposition": f'attachment; filename="routepulse-{identity}.json"'}
        )
    if "protocol_version" in result:
        rows = [dict(seed=row["seed"], **row["delta"]) for row in result["rows"]]
    else:
        rows = result.get("comparison") or [
            {"metric": k, "value": v} for k, v in result["simulation"]["metrics"].items()
        ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="routepulse-{identity}.csv"'},
    )
