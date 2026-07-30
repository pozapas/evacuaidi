"""Execute the 100-scenario, five-uptake V6 map-topology ensemble screen.

This runner intentionally uses the same authoritative map-access-restricted
pilot implementation for every scenario and preserves each scenario's paired
random streams across uptake.  It is a substantial scenario-uncertainty screen,
but not the 8-parameter-set x 10-replication confirmation ensemble.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import subprocess
import sys
from pathlib import Path


V6 = Path(__file__).resolve().parents[1]
PILOT = V6 / "scripts" / "run_v6_evacuation_map_pilot.py"
SCENARIOS = V6 / "inputs" / "environment_scenarios.csv"
RAW = V6 / "results_raw" / "evacuation_map_pilot"
ENSEMBLE = V6 / "results_raw" / "evacuation_map_scenario_ensemble"
LOGS = ENSEMBLE / "logs"
UPTAKES = (0.0, 0.1, 0.3, 0.5, 0.7)
STATUS = "MAP_DERIVED_BUILDING_SCENARIO_SCREEN"


def summary_path(scenario_id: int, horizon_s: float) -> Path:
    uptake_tag = "-".join(f"c{value:.1f}".replace(".", "p") for value in UPTAKES)
    return RAW / f"V6_PROVISIONAL_PILOT_S{scenario_id:03d}_H{horizon_s:g}_{uptake_tag}_SUMMARY.json"


def is_complete(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        payload.get("status") == "MAP_DERIVED_BUILDING_SCENARIO_SCREEN"
        and [float(row["uptake_C"]) for row in payload.get("rows", [])] == list(UPTAKES)
    )


def execute_one(scenario_id: int, horizon_s: float, rerun: bool) -> tuple[int, str]:
    target = summary_path(scenario_id, horizon_s)
    if not rerun and is_complete(target):
        return scenario_id, "skipped_existing"
    command = [
        sys.executable,
        str(PILOT),
        "--scenario",
        str(scenario_id),
        "--uptakes",
        *(str(value) for value in UPTAKES),
        "--horizon-s",
        str(horizon_s),
    ]
    completed = subprocess.run(command, cwd=V6, text=True, capture_output=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / f"S{scenario_id:03d}.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (LOGS / f"S{scenario_id:03d}.stderr.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"S{scenario_id:03d} failed; inspect {LOGS / f'S{scenario_id:03d}.stderr.log'}")
    if not is_complete(target):
        raise RuntimeError(f"S{scenario_id:03d} wrote no valid five-uptake summary")
    return scenario_id, "completed"


def run(args: argparse.Namespace) -> None:
    with SCENARIOS.open(newline="", encoding="utf-8") as handle:
        available = [int(row["scenario_id"]) for row in csv.DictReader(handle)]
    selected = args.scenario_ids or available
    unknown = sorted(set(selected).difference(available))
    if unknown:
        raise ValueError(f"unknown scenario IDs: {unknown}")
    if len(set(selected)) != len(selected):
        raise ValueError("scenario IDs must be unique")
    ENSEMBLE.mkdir(parents=True, exist_ok=True)
    max_workers = min(args.workers, len(selected))
    manifest = {
        "status": STATUS,
        "purpose": "Parallel 100-scenario x five-uptake route-guidance screen using the map-derived topology and the declared IWD final-exit restriction.",
        "scenario_ids": selected,
        "uptakes": list(UPTAKES),
        "horizon_s": args.horizon_s,
        "workers": max_workers,
        "resume_existing": not args.rerun,
        "hard_limit": "One locked A1 parameter set and one replication per scenario. The screen is a building-specific counterfactual application, not a multi-parameter validation ensemble or an estimate of observed response.",
    }
    (ENSEMBLE / "V6_PROVISIONAL_SCENARIO_ENSEMBLE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    states: dict[int, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(execute_one, scenario_id, args.horizon_s, args.rerun): scenario_id for scenario_id in selected}
        for future in concurrent.futures.as_completed(futures):
            scenario_id, state = future.result()
            states[scenario_id] = state
            print(f"S{scenario_id:03d} {state}", flush=True)
    complete = [scenario_id for scenario_id in selected if is_complete(summary_path(scenario_id, args.horizon_s))]
    if len(complete) != len(selected):
        missing = sorted(set(selected).difference(complete))
        raise RuntimeError(f"ensemble incomplete; missing {missing}")
    manifest["execution"] = {"completed_scenarios": complete, "states": states}
    (ENSEMBLE / "V6_PROVISIONAL_SCENARIO_ENSEMBLE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "completed_scenarios": len(complete)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-ids", type=int, nargs="+")
    parser.add_argument("--horizon-s", type=float, default=360.0)
    parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    parser.add_argument("--rerun", action="store_true", help="replace any existing scenario summary")
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    run(args)


if __name__ == "__main__":
    main()
