"""Run a paired V6 integration pilot on the evacuation-map-derived topology.

This runner exercises the locked physical core, mapped room origins,
map-derived egress topology, timed floor transfer, and persistent uptake
intervention. It produces a building-specific counterfactual screen under the
declared scenario assumptions.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

V6 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V6))

import numpy as np
from shapely.geometry import Point, Polygon

from src.v6_guidance import apply_targets_to_disfm, static_capacity_aware_targets, target_replacement_decisions
from src.v6_multifloor import MultiFloorSpatialSimulation
from src.v6_spatial_core import Building


GEOMETRY = V6 / "inputs" / "geometry"
TOPOLOGY = GEOMETRY / "evacuation_map_topology_provisional.json"
GRAPH = GEOMETRY / "evacuation_map_topology_provisional_core_graph.json"
ALLOCATION = V6 / "inputs" / "room_population_2096.csv"
SCENARIOS = V6 / "inputs" / "environment_scenarios.csv"
PARAMETERS = V6 / "configs" / "A1_disfm_optimizer_0.json"
# Keep the earlier unrestricted-IWD diagnostic intact.  The map itself marks
# two final exits as accessible, so the authoritative rerun must enforce that
# declared restriction for IWD route planning.
RESULTS = V6 / "results_raw" / "evacuation_map_pilot"


def point_in_polygon(points: list[list[float]], rng: np.random.Generator) -> tuple[float, float]:
    polygon = Polygon(points)
    if not polygon.is_valid or polygon.area <= 0.01:
        return float(polygon.centroid.x), float(polygon.centroid.y)
    min_x, min_y, max_x, max_y = polygon.bounds
    for _ in range(500):
        point = Point(rng.uniform(min_x, max_x), rng.uniform(min_y, max_y))
        if polygon.buffer(-0.05).contains(point) or polygon.contains(point):
            return float(point.x), float(point.y)
    return float(polygon.centroid.x), float(polygon.centroid.y)


def load_scenario(scenario_id: int) -> dict[str, str]:
    with SCENARIOS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return next(row for row in rows if int(row["scenario_id"]) == scenario_id)


def prepare_population(topology: dict[str, object], scenario: dict[str, str]) -> tuple[list[tuple[float, float, bool]], dict[str, int]]:
    allocation = {row["occupancy_key"]: row for row in csv.DictReader(ALLOCATION.open(newline="", encoding="utf-8"))}
    rng = np.random.default_rng(int(scenario["initial_placement_seed"]))
    raw: list[tuple[float, float]] = []
    room_for_agent: list[str] = []
    for room in topology["rooms"]:
        count = int(allocation[room["occupancy_key"]]["assigned_agents"])
        for _ in range(count):
            raw.append(point_in_polygon(room["world_polygon_m"], rng))
            room_for_agent.append(room["occupancy_key"])
    iwd_count = int(round(float(scenario["iwd_share"]) * len(raw)))
    iwd_indices = set(int(index) for index in rng.choice(len(raw), size=iwd_count, replace=False))
    specs = [(point[0], point[1], index in iwd_indices) for index, point in enumerate(raw)]
    return specs, {"total_agents": len(specs), "iwd_agents": iwd_count, "room_origins": len(set(room_for_agent))}


def summary(simulation, result: dict[str, object], decisions, uptake: float, elapsed_seconds: float, population: dict[str, int]) -> dict[str, object]:
    iwd_ids = {agent.id for agent in simulation.agents if agent.is_iwd}
    exited = set(result["exit_times"])
    iwd_exited = exited.intersection(iwd_ids)
    exit_values = list(result["exit_times"].values())
    return {
        "uptake_C": uptake,
        "total_agents": population["total_agents"],
        "iwd_agents": population["iwd_agents"],
        "total_exited": result["n_exited"],
        "iwd_exited": len(iwd_exited),
        "total_completion_rate": round(result["n_exited"] / population["total_agents"], 6),
        "iwd_completion_rate": round(len(iwd_exited) / population["iwd_agents"], 6) if population["iwd_agents"] else None,
        "median_exit_time_s": round(float(np.median(exit_values)), 6) if exit_values else None,
        "max_exit_time_s": round(float(max(exit_values)), 6) if exit_values else None,
        "route_changes": sum(item.route_changed for item in decisions),
        "uptake_agents": sum(item.uptake_gate for item in decisions),
        "runtime_seconds": round(elapsed_seconds, 3),
        "simulated_horizon_s": result["final_time"],
    }


def run(args) -> None:
    topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
    if topology["status"] != "MAP_DERIVED_BUILDING_TOPOLOGY":
        raise RuntimeError("runner requires the supplied map-derived topology")
    scenario = load_scenario(args.scenario)
    specs, population = prepare_population(topology, scenario)
    if population["total_agents"] != 2096:
        raise RuntimeError(f"expected 2096 agents, found {population['total_agents']}")
    params = json.loads(PARAMETERS.read_text(encoding="utf-8"))["parameters"]
    params.update({"k_AI": 0.0, "use_guidance": False, "use_leader": False, "max_time": args.horizon_s, "t_premove": float(scenario["alarm_delay_s"])})
    building = Building(GRAPH)
    exits = list(building.exits)
    accessible_exits = sorted(str(item["id"]) for item in topology["exits"] if bool(item.get("accessible", False)))
    if len(accessible_exits) != 2:
        raise RuntimeError(f"expected two map-marked accessible final exits, found {accessible_exits}")
    distances = [{exit_id: building.graph_distance(np.asarray(spec[:2]), exit_id) for exit_id in exits} for spec in specs]
    planner_agents = [
        {
            "agent_id": index,
            "free_speed_mps": params["v0_mob"] if spec[2] else params["v0_amb"],
            "permitted_exits": accessible_exits if spec[2] else exits,
            "graph_distance_m": distances[index],
        }
        for index, spec in enumerate(specs)
    ]
    baseline, recommendation = static_capacity_aware_targets(planner_agents, exits, {exit_id: params.get("exit_gap", 0.4) for exit_id in exits})
    uniform_rng = np.random.default_rng(int(scenario["uptake_uniform_seed"]))
    uniforms = {index: float(value) for index, value in enumerate(uniform_rng.random(len(specs)))}
    vertical = {frozenset((item["from"], item["to"])): item["transfer_time_s"] for item in topology["vertical_links"]}
    rows = []
    RESULTS.mkdir(parents=True, exist_ok=True)
    for uptake in args.uptakes:
        simulation = MultiFloorSpatialSimulation(
            building, dict(params), open_doors={}, rng=np.random.default_rng(int(scenario["movement_seed"])), vertical_links=vertical
        )
        simulation.init_custom(specs, exits, guidance="none")
        decisions = target_replacement_decisions(baseline, recommendation, uniforms, uptake)
        apply_targets_to_disfm(simulation, decisions)
        simulation.install_node_routes()
        started = time.perf_counter()
        result = simulation.run(record_speed=False)
        elapsed = time.perf_counter() - started
        rows.append(summary(simulation, result, decisions, uptake, elapsed, population))
        (RESULTS / f"v6_provisional_s{args.scenario:03d}_c{uptake:.1f}_agent_decisions.json").write_text(
            json.dumps([item.__dict__ for item in decisions], indent=2) + "\n", encoding="utf-8"
        )
    payload = {
        "status": "MAP_DERIVED_BUILDING_SCENARIO_SCREEN",
        "purpose": "Executes mapped origin allocation, evacuation-map topology, timed transfers, locked physical core, and nested uptake target replacement.",
        "iwd_route_constraint": "IWD planning is restricted to the two final exits marked accessible on the supplied map-derived topology.",
        "prohibitions": [
            "The screen does not estimate observed individual response, marshal performance, or causal guidance efficacy.",
            "The screen uses one locked physical parameter configuration and one movement realization per scenario.",
        ],
        "scenario": scenario,
        "topology_path": str(TOPOLOGY),
        "topology_status": topology["status"],
        "parameter_source": str(PARAMETERS),
        "rows": rows,
    }
    uptake_tag = "-".join(f"c{value:.1f}".replace(".", "p") for value in args.uptakes)
    name = RESULTS / f"V6_PROVISIONAL_PILOT_S{args.scenario:03d}_H{args.horizon_s:g}_{uptake_tag}_SUMMARY.json"
    name.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=int, default=4)
    parser.add_argument("--uptakes", type=float, nargs="+", default=[0.0, 0.7])
    parser.add_argument("--horizon-s", type=float, default=360.0)
    args = parser.parse_args()
    if any(value not in {0.0, 0.1, 0.3, 0.5, 0.7} for value in args.uptakes):
        raise ValueError("pilot uptake values must be from the locked V6 set")
    run(args)


if __name__ == "__main__":
    main()
