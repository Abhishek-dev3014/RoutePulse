"""Measured held-out experiments; files are append-only by timestamp."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from app.domain import OptimizeRequest
from app.eta import evaluate
from app.demand import forecast, generate
from app.seed import baseline, network, scenarios
from app.optimization import optimize
from app.domain import Simulation

parser = argparse.ArgumentParser()
parser.add_argument("--persist", action="store_true", help="Also save runs in the configured application database")
args = parser.parse_args()
net = network()
output = Path("data/experiments") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
output.mkdir(parents=True, exist_ok=False)
summary = []
for sc in scenarios():
    result = optimize(net, sc, baseline(), OptimizeRequest(scenario_id=sc.id, timeout_seconds=20))
    eta = evaluate(net, sc, baseline(), Simulation.model_validate(result["baseline"]))
    demand = forecast(net, sc, baseline(), generate(net, sc, sc.seed))
    result["eta_evaluation"] = eta
    result["demand_evaluation"] = demand
    if args.persist:
        from app.persistence import save_run

        result = save_run("optimization", sc.id, result)
    (output / f"{sc.id}.json").write_text(json.dumps(result, indent=2))
    row = dict(
        scenario=sc.id,
        status=result["status"],
        baseline=result["baseline"]["metrics"],
        candidate=result["candidate"]["metrics"] if result["candidate"] else None,
        eta_mae=eta["mae"],
        eta_coverage=eta["coverage"],
        demand_mae=demand["mae"],
        runtime=result["runtime_seconds"],
    )
    summary.append(row)
    print(json.dumps(row), flush=True)
(output / "summary.json").write_text(json.dumps(summary, indent=2))
print(f"Saved reproducible experiments to {output}")
