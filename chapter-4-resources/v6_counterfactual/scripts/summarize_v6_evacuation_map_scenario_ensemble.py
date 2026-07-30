"""Summarize the completed 100-scenario map-topology V6 screen without overclaiming."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import fmean


V6 = Path(__file__).resolve().parents[1]
RAW = V6 / "results_raw" / "evacuation_map_pilot"
ENSEMBLE = V6 / "results_raw" / "evacuation_map_scenario_ensemble"
SUMMARY = V6 / "results_summary"
UPTAKES = (0.0, 0.1, 0.3, 0.5, 0.7)
STATUS = "MAP_DERIVED_BUILDING_SCENARIO_SCREEN"


def load_rows() -> list[dict[str, object]]:
    manifest = json.loads((ENSEMBLE / "V6_PROVISIONAL_SCENARIO_ENSEMBLE_MANIFEST.json").read_text(encoding="utf-8"))
    scenario_ids = [int(value) for value in manifest["execution"]["completed_scenarios"]]
    rows: list[dict[str, object]] = []
    for scenario_id in scenario_ids:
        path = RAW / f"V6_PROVISIONAL_PILOT_S{scenario_id:03d}_H360_c0p0-c0p1-c0p3-c0p5-c0p7_SUMMARY.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        cell_rows = payload["rows"]
        if [float(row["uptake_C"]) for row in cell_rows] != list(UPTAKES):
            raise RuntimeError(f"S{scenario_id:03d} has a malformed uptake sequence")
        baseline = cell_rows[0]
        for row in cell_rows:
            record = dict(row)
            record["scenario_id"] = scenario_id
            record["paired_total_exit_difference_from_C0"] = int(row["total_exited"]) - int(baseline["total_exited"])
            record["paired_iwd_exit_difference_from_C0"] = int(row["iwd_exited"]) - int(baseline["iwd_exited"])
            rows.append(record)
    return rows


def main() -> None:
    rows = load_rows()
    by_uptake: dict[float, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_uptake[float(row["uptake_C"])].append(row)
    aggregate = []
    for uptake in UPTAKES:
        values = by_uptake[uptake]
        if len(values) != 100:
            raise RuntimeError(f"expected 100 rows at C={uptake}, found {len(values)}")
        aggregate.append({
            "uptake_C": uptake,
            "scenario_count": len(values),
            "mean_total_completion_rate": round(fmean(float(row["total_completion_rate"]) for row in values), 6),
            "mean_iwd_completion_rate": round(fmean(float(row["iwd_completion_rate"]) for row in values), 6),
            "mean_total_exit_difference_from_C0": round(fmean(float(row["paired_total_exit_difference_from_C0"]) for row in values), 3),
            "mean_iwd_exit_difference_from_C0": round(fmean(float(row["paired_iwd_exit_difference_from_C0"]) for row in values), 3),
            "total_completion_loss_scenarios_vs_C0": sum(int(row["paired_total_exit_difference_from_C0"]) < 0 for row in values),
            "iwd_completion_loss_scenarios_vs_C0": sum(int(row["paired_iwd_exit_difference_from_C0"]) < 0 for row in values),
        })
    SUMMARY.mkdir(parents=True, exist_ok=True)
    csv_path = SUMMARY / "V6_PROVISIONAL_MAP_SCENARIO_ENSEMBLE_100X5.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    result = {
        "status": STATUS,
        "scenario_count": 100,
        "uptakes": list(UPTAKES),
        "paired_comparison": "Within each scenario, placement, movement, uptake-uniform, and planner-tie-break streams are shared at every uptake level.",
        "hard_limit": "This is one A1 parameter set and one replication per scenario. It is a building-specific counterfactual screen, not a multi-parameter validation ensemble or an estimate of observed response.",
        "aggregate_by_uptake": aggregate,
        "raw_row_file": csv_path.relative_to(V6).as_posix(),
    }
    json_path = SUMMARY / "V6_MAP_DERIVED_SCENARIO_ENSEMBLE_100X5.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
