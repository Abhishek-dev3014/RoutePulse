"""Evaluate a saved optimization, or reproduce and assert a saved validation report."""

import argparse
import json
from pathlib import Path
from app.robustness import evaluate_plan

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("--output", type=Path)
args = parser.parse_args()
source = json.loads(args.source.read_text())
if "protocol_version" in source:
    snapshot = source["input_snapshot"]
    # Original excluded seeds are retained so even custom evaluation seeds reproduce.
    run = dict(
        id=source["source_run_id"],
        scenario=snapshot["scenario"],
        planning_seed=809,
        evaluation_seed=snapshot["scenario"]["seed"],
        input_snapshot=snapshot,
        candidate=dict(plan=snapshot["candidate"]),
    )
else:
    run = source
report = json.loads(json.dumps(evaluate_plan(run)))
if "protocol_version" in source:
    for key, value in report.items():
        assert source[key] == value, f"Replay mismatch: {key}"
    print("Exact replay: all daily metrics, demand hashes, origin outcomes and summary intervals match.")
if args.output:
    # Preserve earlier evidence; callers must choose a new file.
    with args.output.open("x") as output:
        json.dump(report, output, indent=2)
print(
    json.dumps(
        dict(
            scenario=report["scenario_id"],
            days=report["days"],
            wins=report["service_win_days"],
            losses=report["service_loss_days"],
            transfer_regressions=report["transfer_regression_days"],
            summary=report["summary"],
        ),
        indent=2,
    )
)
