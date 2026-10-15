"""Documented API response contracts, separate from persistence records."""

from typing import Literal
from .domain import Metrics, Model, Network, Plan, Scenario, Simulation, Trip


class ArrivalPrediction(Model):
    vehicle_id: str
    trip_id: str
    route_id: str
    stop_id: str
    stop_index: int
    prediction_time: float
    expected: float
    earliest: float
    latest: float
    delay: float
    latitude: float
    longitude: float
    progress: float
    segment: int
    actual: float | None = None
    error: float | None = None


class ETAReport(Model):
    mae: float
    median_absolute_error: float
    p90_absolute_error: float
    coverage: float
    average_width: float
    sample_count: int
    residual_bounds: list[float]
    calibration_seeds: list[int]
    training_seeds: list[int] = []
    segment_priors: dict[str, float] = {}
    estimator_version: str = "1.0.0"
    target_coverage: float
    rows: list[ArrivalPrediction]
    assumptions: str


class ETAForecast(Model):
    predictions: list[ArrivalPrediction]
    target_coverage: float
    assumptions: str


class DemandRow(Model):
    stop_id: str
    route_id: str
    minute: int
    expected: float
    low: float
    high: float
    actual: int
    capacity: int
    expected_boardings: float
    unmet: float
    risk: float
    category: Literal["low", "medium", "high"]


class DemandReport(Model):
    rows: list[DemandRow]
    mae: float
    wape: float | None
    by_stop: dict[str, float]
    by_period: dict[str, float]
    historical_seeds: list[int]
    interval_minutes: int
    assumptions: str


class Alert(Model):
    id: str
    severity: str
    type: str
    title: str
    description: str
    route_id: str | None = None


class TimetableTrip(Trip):
    scheduled_arrivals: list[float]


class ActivePlan(Model):
    run_id: str
    plan: Plan


class DashboardResponse(Model):
    network: Network
    scenario: Scenario
    simulation: Simulation
    active_plan: ActivePlan | None
    timetable: list[TimetableTrip]
    eta: ETAReport
    demand: DemandReport
    alerts: list[Alert]


class SimulationResponse(DashboardResponse):
    id: str
    created_at: str
    request: dict
    input_snapshot: dict


MetricName = Literal[
    "passengers",
    "served",
    "unserved",
    "service_rate",
    "average_wait",
    "p95_wait",
    "missed_connections",
    "successful_connections",
    "fleet_utilization",
    "operating_minutes",
    "total_trip_delay",
    "capacity_violations",
    "feasibility_violations",
]


class Comparison(Model):
    metric: MetricName
    baseline: float
    candidate: float
    delta: float
    improvement_percent: float | None
    direction: Literal["neutral", "improved", "regressed"]


class DutyChange(Model):
    trip_id: str
    route_id: str
    old_vehicle: str
    new_vehicle: str
    old_departure: float
    new_departure: float
    explanation: str


class OptimizationResponse(Model):
    id: str
    created_at: str
    scenario: Scenario
    objective: str
    planning_seed: int
    evaluation_seed: int
    status: str
    runtime_seconds: float
    candidates_evaluated: int
    search_history: list[dict]
    baseline: Simulation
    candidate: Simulation | None
    planning_metrics: Metrics
    planning_baseline_metrics: Metrics
    comparison: list[Comparison]
    changes: list[DutyChange]
    explanation: str
    tradeoffs: list[str]
    input_snapshot: dict
    decision: str
    eta_evaluation: ETAReport | None = None
    demand_evaluation: DemandReport | None = None


class HistoryRow(Model):
    id: str
    scenario_id: str
    created_at: str
    status: str
    baseline: Metrics
    candidate: Metrics | None


class PairedSummary(Model):
    mean_delta: float
    minimum_delta: float
    maximum_delta: float
    mean_ci_low: float
    mean_ci_high: float


class ValidationDay(Model):
    seed: int
    demand_sha256: str
    baseline: Metrics
    candidate: Metrics
    delta: dict[str, float]


class OriginImpact(Model):
    stop_id: str
    stop_name: str
    passengers: int
    baseline_service_rate: float
    candidate_service_rate: float
    mean_wait_delta: float


class RobustnessResponse(Model):
    id: str
    created_at: str
    source_run_id: str
    scenario_id: str
    protocol_version: str
    days: int
    seeds: list[int]
    excluded_seeds: list[int]
    plan_sha256: str
    input_snapshot: dict
    demand_model_version: str
    simulator_version: str
    bootstrap_seed: int
    bootstrap_samples: int
    summary: dict[str, PairedSummary]
    service_win_days: int
    service_loss_days: int
    transfer_regression_days: int
    candidate_capacity_violations: int
    candidate_feasibility_violations: int
    origins: list[OriginImpact]
    rows: list[ValidationDay]
    methodology: str
