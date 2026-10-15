import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app import persistence
from app.main import app, bundle
from app.seed import baseline


@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    persistence.Base.metadata.create_all(engine)
    monkeypatch.setattr(persistence, "engine", engine)
    bundle.cache_clear()
    with TestClient(app) as client:
        yield client
    engine.dispose()


def test_health_and_entities(client):
    assert client.get("/health").status_code == 200
    assert len(client.get("/api/v1/scenarios").json()) == 5
    assert len(client.get("/api/v1/stops").json()) == 13
    assert len(client.get("/api/v1/vehicles").json()) == 7
    assert len(client.get("/api/v1/trips").json()) == 21
    demand = client.post("/api/v1/demand", json={"scenario_id": "rush"}).json()
    assert len(demand) == 1166
    assert any(len(p["legs"]) == 2 for p in demand)
    assert client.get("/api/v1/scenarios/missing").status_code == 404
    assert client.get("/api/v1/stops/missing/arrivals").status_code == 404


def test_simulation_persist_export(client):
    response = client.post("/api/v1/simulations", json={"scenario_id": "rush"})
    assert response.status_code == 201, response.text
    body = response.json()
    saved = client.get("/api/v1/simulations/" + body["id"]).json()
    assert body == saved
    assert body["simulation"]["metrics"]["passengers"] > 500
    assert client.get("/api/v1/reports/" + body["id"] + "?format=csv").text.startswith("metric,value")
    assert client.get("/api/v1/reports/" + body["id"]).status_code == 200


def test_requests_and_validation(client):
    for body in (
        {"demand_multiplier": 100},
        {"scenario_id": "missing"},
        {"breakdown_vehicle": "V999"},
        {"disruption_start": 90, "disruption_end": 20},
    ):
        response = client.post("/api/v1/simulations", json=body)
        assert response.status_code in (404, 422), response.text
        assert "error" in response.json()
    assert client.get("/api/v1/optimizations/missing").status_code == 404
    plan = baseline().model_dump()
    plan["trips"][0]["vehicle_id"] = "made-up"
    report = client.post("/api/v1/plans/validate", json={"scenario_id": "normal", "plan": plan}).json()
    assert not report["feasible"]


def test_optimization_decision_and_history(client):
    response = client.post(
        "/api/v1/optimizations", json={"scenario_id": "rush", "max_candidates": 5, "timeout_seconds": 15}
    )
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["candidate"]
    identity = result["id"]
    assert client.get(f"/api/v1/optimizations/{identity}/validation").json() is None
    validation = client.post(f"/api/v1/optimizations/{identity}/validation", json={})
    assert validation.status_code == 200, validation.text
    report = validation.json()
    assert report["days"] == 20 and report["source_run_id"] == identity
    assert report["candidate_capacity_violations"] == 0
    assert report["candidate_feasibility_violations"] == 0
    assert client.get(f"/api/v1/optimizations/{identity}/validation").json() == report
    assert client.post(f"/api/v1/optimizations/{identity}/validation", json={}).json() == report
    assert client.get(f"/api/v1/reports/{report['id']}?format=csv").text.startswith("seed,served")
    assert client.get(f"/api/v1/reports/{report['id']}").json() == report
    assert client.post(f"/api/v1/optimizations/{identity}/decision", json={"decision": "accepted"}).status_code == 200
    assert client.get("/api/v1/optimizations/" + identity).json()["decision"] == "accepted"
    assert client.get("/api/v1/dashboard?scenario_id=rush").json()["active_plan"]["run_id"] == identity
    assert len(client.get("/api/v1/optimizations").json()) == 1
    assert client.get("/api/v1/reports/" + identity + "?format=csv").text.startswith("metric,baseline,candidate")
    # Rejecting a later proposal must not displace an already accepted operating plan.
    later = persistence.save_run("optimization", "rush", result)
    assert (
        client.post(f"/api/v1/optimizations/{later['id']}/decision", json={"decision": "rejected"}).status_code == 200
    )
    assert client.get("/api/v1/dashboard?scenario_id=rush").json()["active_plan"]["run_id"] == identity
    assert client.post(f"/api/v1/optimizations/{identity}/decision", json={"decision": "rejected"}).status_code == 200
    assert client.get("/api/v1/dashboard?scenario_id=rush").json()["active_plan"] is None


def test_clear_breakdown(client):
    result = client.post("/api/v1/simulations", json={"scenario_id": "breakdown", "breakdown_vehicle": None})
    assert result.status_code == 201
    assert result.json()["scenario"]["breakdown_vehicle"] is None


def test_eta_invalid_plan_and_gps(client):
    plan = baseline().model_dump()
    plan["trips"][0]["route_id"] = "unknown"
    response = client.post("/api/v1/forecasts/eta", json={"observations": [], "as_of": 40, "plan": plan})
    assert response.status_code == 422
    response = client.post(
        "/api/v1/forecasts/eta",
        json={
            "observations": [
                {
                    "vehicle_id": "V01",
                    "trip_id": "T101",
                    "timestamp": -1,
                    "latitude": 100,
                    "longitude": 0,
                    "speed_kph": -10,
                }
            ],
            "as_of": 40,
        },
    )
    assert response.status_code == 422
