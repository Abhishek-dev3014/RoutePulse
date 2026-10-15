"""Re-evaluate saved baseline and candidate snapshots without re-running search."""

import argparse
import json
from pathlib import Path
from app.domain import Network, Passenger, Plan, Scenario
from app.demand import generate
from app.simulation import simulate

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=Path)
args = parser.parse_args()
run = json.loads(args.experiment.read_text())
net = Network.model_validate(run["input_snapshot"]["network"])
sc = Scenario.model_validate(run["scenario"])
demand = (
    [Passenger.model_validate(p) for p in run["input_snapshot"]["passenger_demand"]]
    if "passenger_demand" in run["input_snapshot"]
    else generate(net, sc, run["evaluation_seed"])
)
for label in ("baseline", "candidate"):
    saved = run[label]
    if saved is None:
        continue
    replay = simulate(net, sc, Plan.model_validate(saved["plan"]), demand, run["evaluation_seed"])
    if replay.metrics.model_dump() != saved["metrics"]:
        raise SystemExit(f"{label} metric mismatch; inspect simulator version / input changes")
    print(f"{label}: all {len(saved['metrics'])} saved metrics reproduced exactly")
