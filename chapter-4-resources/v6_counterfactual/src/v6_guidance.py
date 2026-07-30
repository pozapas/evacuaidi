"""V6 counterfactual route recommendation semantics.

This module deliberately has no behavioural calibration logic.  It implements
the counterfactual intervention as a persistent, nested uptake gate followed by
replacement of an agent's navigation target.  It never applies a k_AI force.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class TargetDecision:
    """Auditable route assignment for one agent in one uptake condition."""

    agent_id: int
    baseline_target: str
    recommended_target: str
    realized_target: str
    uptake_uniform: float
    uptake_gate: bool
    route_changed: bool


def persistent_uptake_gate(uniforms: Mapping[int, float], uptake: float) -> dict[int, bool]:
    """Return the nested gate A_i = 1(U_i < C), validating its domain."""
    if not 0.0 <= uptake <= 1.0:
        raise ValueError("uptake must lie in [0, 1]")
    out: dict[int, bool] = {}
    for agent_id, value in uniforms.items():
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"uptake uniform for agent {agent_id} is outside [0, 1]")
        out[int(agent_id)] = bool(float(value) < uptake)
    return out


def _eligible_exits(agent: Mapping[str, Any], exits: Sequence[str]) -> tuple[str, ...]:
    permitted = tuple(str(x) for x in agent.get("permitted_exits", exits))
    if not permitted:
        raise ValueError(f"agent {agent['agent_id']} has no permitted exit")
    unknown = set(permitted).difference(exits)
    if unknown:
        raise ValueError(f"agent {agent['agent_id']} references unknown exits: {sorted(unknown)}")
    return permitted


def static_capacity_aware_targets(
    agents: Iterable[Mapping[str, Any]],
    exits: Sequence[str],
    exit_gap_s: Mapping[str, float],
) -> tuple[dict[int, str], dict[int, str]]:
    """Generate baseline and recommended targets from declared graph distances.

    ``graph_distance_m`` is an agent-to-exit mapping computed from registered
    geometry.  The recommendation is a deterministic serial list-scheduling
    allocation using travel-time plus the projected exit queue.  It is not a
    learned or tuned policy.  IWD accessibility is enforced through each
    agent's ``permitted_exits`` list before any target is considered.
    """
    exits = tuple(str(x) for x in exits)
    if not exits:
        raise ValueError("at least one exit is required")
    if set(exits) != set(exit_gap_s):
        raise ValueError("exit_gap_s must contain exactly the declared exits")
    loads = {door: 0 for door in exits}
    baseline: dict[int, str] = {}
    recommended: dict[int, str] = {}
    records = sorted(agents, key=lambda row: int(row["agent_id"]))
    for agent in records:
        agent_id = int(agent["agent_id"])
        speed = float(agent["free_speed_mps"])
        if speed <= 0.0:
            raise ValueError(f"agent {agent_id} has non-positive free speed")
        distance = {str(k): float(v) for k, v in agent["graph_distance_m"].items()}
        choices = _eligible_exits(agent, exits)
        missing = set(choices).difference(distance)
        if missing:
            raise ValueError(f"agent {agent_id} lacks graph distance for {sorted(missing)}")
        # Stable lexical tie-break is intentional and becomes part of the audit record.
        baseline[agent_id] = min(choices, key=lambda door: (distance[door] / speed, door))
        recommended[agent_id] = min(
            choices,
            key=lambda door: (distance[door] / speed + loads[door] * float(exit_gap_s[door]), door),
        )
        loads[recommended[agent_id]] += 1
    return baseline, recommended


def target_replacement_decisions(
    baseline_targets: Mapping[int, str],
    recommended_targets: Mapping[int, str],
    uniforms: Mapping[int, float],
    uptake: float,
) -> list[TargetDecision]:
    """Apply the uptake gate once and select one navigation target per agent."""
    expected = set(baseline_targets)
    if set(recommended_targets) != expected or set(uniforms) != expected:
        raise ValueError("baseline targets, recommendations, and uniforms must have identical agent IDs")
    gate = persistent_uptake_gate(uniforms, uptake)
    decisions: list[TargetDecision] = []
    for agent_id in sorted(expected):
        base = str(baseline_targets[agent_id])
        recommended = str(recommended_targets[agent_id])
        realized = recommended if gate[agent_id] else base
        decisions.append(
            TargetDecision(
                agent_id=agent_id,
                baseline_target=base,
                recommended_target=recommended,
                realized_target=realized,
                uptake_uniform=float(uniforms[agent_id]),
                uptake_gate=gate[agent_id],
                route_changed=(realized != base),
            )
        )
    return decisions


def apply_targets_to_disfm(simulation: Any, decisions: Iterable[TargetDecision]) -> None:
    """Install V6 targets in the locked V5 physics object without a force term.

    The function rejects configurations that could silently invoke the legacy
    guidance force.  It uses the existing building route method only to form
    waypoints after the intervention has selected a target exit.
    """
    if float(simulation.p.get("k_AI", 0.0)) != 0.0:
        raise ValueError("V6 prohibits a nonzero k_AI guidance force")
    if bool(simulation.p.get("use_guidance", False)):
        raise ValueError("V6 target replacement requires legacy guidance force to be disabled")
    by_id = {int(item.agent_id): item for item in decisions}
    agent_ids = {int(agent.id) for agent in simulation.agents}
    if set(by_id) != agent_ids:
        raise ValueError("target decisions do not match initialized simulation agents")
    for agent in simulation.agents:
        decision = by_id[int(agent.id)]
        agent.natural_door = decision.baseline_target
        agent.target_door = decision.realized_target
        agent.waypoints = simulation.b.route(agent.pos, agent.target_door)
        agent.wp_idx = 0
        # Prevent _guidance_force from applying an independent force even if a
        # future core changes its default k_AI handling.
        agent.guided_door = None
        agent.complies = False
