"""Validated domain contracts. All times are minutes after the stored UTC epoch."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Stop(Model):
    id: str
    name: str
    latitude: float
    longitude: float
    x: float
    y: float
    accessible: bool = True
    kind: str = "campus"


class Edge(Model):
    origin: str
    destination: str
    distance_km: float = Field(gt=0)
    minutes: float = Field(gt=0)
    speed_kph: float = 18
    congestion_factor: float = 1


class Route(Model):
    id: str
    name: str
    color: str
    stops: list[str]
    minimum_trips: int = 7
    operating_window: tuple[float, float] = (0, 140)
    direction: str = "clockwise"


class Vehicle(Model):
    id: str
    number: str
    capacity: int = Field(gt=0, le=100)
    status: Literal["available", "in_service", "delayed", "unavailable", "maintenance"] = "available"
    available_from: float = 0
    available_until: float = 140
    depot: str = "S00"


class Trip(Model):
    id: str
    route_id: str
    vehicle_id: str
    departure: float = Field(ge=0, le=140)
    earliest: float = Field(ge=0)
    latest: float = Field(le=140)


class Plan(Model):
    id: str
    trips: list[Trip] = Field(max_length=60)


class Scenario(Model):
    id: str
    name: str
    description: str
    challenge: str
    seed: int
    version: str = "1.0"
    demand_multiplier: float = Field(default=1, ge=0.1, le=5)
    traffic_factor: float = Field(default=1, ge=1, le=3)
    affected_route: str = "R1"
    breakdown_vehicle: str | None = None
    disruption_start: float = Field(default=20, ge=0, le=120)
    disruption_end: float = Field(default=90, ge=0, le=140)
    horizon: float = 120
    epoch_utc: str = "2026-10-14T02:30:00Z"
    timezone: str = "Asia/Kolkata"

    @model_validator(mode="after")
    def valid_interval(self):
        if self.disruption_end <= self.disruption_start:
            raise ValueError("Disruption end must be after start")
        return self


class Network(Model):
    organization_id: str = "meridian-demo"
    name: str = "Meridian University"
    synthetic: bool = True
    stops: list[Stop]
    routes: list[Route]
    edges: list[Edge]
    vehicles: list[Vehicle]


class Leg(Model):
    route_id: str
    origin: str
    destination: str


class Passenger(Model):
    id: str
    arrival: float
    origin: str
    destination: str
    legs: list[Leg]


class Violation(Model):
    constraint: str
    trip_id: str | None = None
    detail: str


class Feasibility(Model):
    plan_id: str
    feasible: bool
    checked: list[str]
    violations: list[Violation]
    vehicles_used: int
    trips_scheduled: int
    status: str


class Metrics(Model):
    passengers: int
    served: int
    unserved: int
    service_rate: float
    average_wait: float
    p95_wait: float
    missed_connections: int
    successful_connections: int
    fleet_utilization: float
    operating_minutes: float
    total_trip_delay: float
    capacity_violations: int
    feasibility_violations: int


class StopEvent(Model):
    time: float
    scheduled: float
    trip_id: str
    route_id: str
    vehicle_id: str
    stop_id: str
    stop_index: int
    boarded: int
    alighted: int
    occupancy: int
    capacity: int
    waiting: int


class GPS(Model):
    vehicle_id: str
    trip_id: str
    timestamp: float = Field(ge=0, le=1440)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kph: float = Field(ge=0, le=120)
    quality: float = Field(default=0.98, ge=0, le=1)


class Outcome(Model):
    passenger_id: str
    status: str
    wait: float
    completed_at: float | None
    transfer: bool
    missed_connection: bool


class Simulation(Model):
    simulator_version: str = "1.0.0"
    seed: int
    scenario_id: str
    plan: Plan
    metrics: Metrics
    feasibility: Feasibility
    events: list[StopEvent]
    gps: list[GPS]
    outcomes: list[Outcome]
    operational_events: list[dict]


class RunRequest(Model):
    scenario_id: str = "rush"
    demand_multiplier: float | None = Field(default=None, ge=0.1, le=5)
    traffic_factor: float | None = Field(default=None, ge=1, le=3)
    breakdown_vehicle: str | None = None
    affected_route: str | None = None
    disruption_start: float | None = Field(default=None, ge=0, le=120)
    disruption_end: float | None = Field(default=None, gt=0, le=140)
    seed: int | None = Field(default=None, ge=0, le=2147483647)


class OptimizeRequest(RunRequest):
    objective: Literal["service", "wait", "balanced"] = "service"
    max_candidates: int = Field(default=24, ge=1, le=50)
    timeout_seconds: float = Field(default=12, ge=0.05, le=30)


class ValidateRequest(RunRequest):
    plan: Plan
