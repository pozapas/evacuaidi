"""Create a result audit for the completed V6 scenario screen."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


V6 = Path(__file__).resolve().parents[1]
SUMMARY = V6 / "results_summary"
AUDIT = V6 / "audit" / "V6_MAP_DERIVED_SCENARIO_ENSEMBLE_RESULT_AUDIT.md"
CSV_PATH = SUMMARY / "V6_PROVISIONAL_MAP_SCENARIO_ENSEMBLE_100X5.csv"
JSON_PATH = SUMMARY / "V6_MAP_DERIVED_SCENARIO_ENSEMBLE_100X5.json"
STATUS = "MAP_DERIVED_BUILDING_SCENARIO_SCREEN"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if result.get("status") != STATUS:
        raise RuntimeError("Unexpected summary status")
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 500:
        raise RuntimeError(f"Expected 500 paired scenario rows; found {len(rows)}")
    expected = [0.0, 0.1, 0.3, 0.5, 0.7]
    observed = sorted({float(row["uptake_C"]) for row in rows})
    if observed != expected or {int(row["scenario_id"]) for row in rows} != set(range(1, 101)):
        raise RuntimeError("Scenario or uptake coverage is incomplete")

    lines = [
        "# V6 map-derived scenario-ensemble result audit",
        "",
        "## Status",
        "",
        f"`{STATUS}`",
        "",
        "This audit records a 100-scenario x 5-uptake paired screen (500 result rows). It documents the reported counterfactual application and its scope conditions.",
        "",
        "## Paired aggregate results",
        "",
        "| Uptake C | Mean total completion | Mean IWD completion | Mean total exits vs C=0 | Mean IWD exits vs C=0 | Total-loss scenarios | IWD-loss scenarios |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in result["aggregate_by_uptake"]:
        lines.append(
            "| {uptake_C:.1f} | {mean_total_completion_rate:.1%} | {mean_iwd_completion_rate:.1%} | {mean_total_exit_difference_from_C0:+.3f} | {mean_iwd_exit_difference_from_C0:+.3f} | {total_completion_loss_scenarios_vs_C0} | {iwd_completion_loss_scenarios_vs_C0} |".format(**record)
        )
    lines.extend([
        "",
        "## Traceability",
        "",
        f"- Result CSV: `{CSV_PATH.relative_to(V6).as_posix()}` (SHA-256 `{sha256(CSV_PATH)}`)",
        f"- Result summary: `{JSON_PATH.relative_to(V6).as_posix()}` (SHA-256 `{sha256(JSON_PATH)}`)",
        "- Pairing: within each scenario, placement, movement, uptake-uniform, and planner tie-break streams are shared across uptake levels.",
        "- Model scope: one locked A1 parameter set and one replication per scenario; map-derived egress topology; declared IWD final-exit restriction.",
        "",
        "## Limits that remain binding",
        "",
        "- The screen uses one locked physical parameter configuration and one movement realization per scenario.",
        "- The results are a counterfactual application rather than a multi-parameter validation ensemble.",
        "- A positive screen result does not establish observed individual response, marshal performance, or causal guidance efficacy.",
        "",
    ])
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text("\n".join(lines), encoding="utf-8")
    print(AUDIT)


if __name__ == "__main__":
    main()
