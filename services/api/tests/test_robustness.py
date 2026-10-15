from copy import deepcopy
import pytest
from app.demand import PLANNING_SEED
from app.robustness import evaluate_plan, summarize
from app.seed import baseline, network, scenarios


def frozen_run():
    return dict(
        id="frozen-test",
        scenario=scenarios()[0].model_dump(),
        planning_seed=PLANNING_SEED,
        evaluation_seed=70001,
        candidate=dict(plan=baseline().model_dump()),
        input_snapshot=dict(network=network().model_dump(), published=baseline().model_dump()),
    )


def test_paired_identity_and_protocol_independence():
    run = frozen_run()
    original = deepcopy(run)
    report = evaluate_plan(run)
    assert run == original  # validation cannot change the plan or optimizer inputs
    assert len(set(report["seeds"])) == 20
    assert not set(report["seeds"]) & set(report["excluded_seeds"])
    assert 70001 not in report["seeds"]
    assert report["service_win_days"] == report["service_loss_days"] == 0
    for row in report["rows"]:
        assert row["baseline"] == row["candidate"]
        assert set(row["delta"].values()) == {0}
    assert sum(o["passengers"] for o in report["origins"]) == sum(r["baseline"]["passengers"] for r in report["rows"])
    assert all(o["mean_wait_delta"] == 0 for o in report["origins"])
    assert evaluate_plan(run) == report  # including demand hashes, bootstrap bounds, and origin groups


def test_invalid_frozen_candidate_is_not_evaluated():
    run = frozen_run()
    run["candidate"]["plan"]["trips"][0]["vehicle_id"] = "missing"
    with pytest.raises(ValueError, match="hard-constraint"):
        evaluate_plan(run)
    run["candidate"] = None
    with pytest.raises(ValueError, match="candidate"):
        evaluate_plan(run)


def test_mean_interval_and_daily_range_are_different():
    report = summarize([-10, -5, 0, 5, 10] * 4)
    assert report["mean_delta"] == 0
    assert report["minimum_delta"] == -10 and report["maximum_delta"] == 10
    assert -10 < report["mean_ci_low"] < 0 < report["mean_ci_high"] < 10


def test_cli_replays_json_export(tmp_path):
    import json
    import os
    import subprocess
    import sys

    run = frozen_run()
    run["evaluation_seed"] = run["scenario"]["seed"]
    path = tmp_path / "validation.json"
    path.write_text(json.dumps(evaluate_plan(run)))
    result = subprocess.run(
        [sys.executable, "scripts/validate_plan.py", str(path)],
        env={**os.environ, "PYTHONPATH": "services/api"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Exact replay" in result.stdout
