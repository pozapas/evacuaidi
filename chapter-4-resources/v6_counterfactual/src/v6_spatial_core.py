"""Scalable V6 adapter for the locked DiSFM physical core.

The archived core evaluates all agent pairs, although its exponential social
force is numerically negligible beyond a finite distance.  This adapter keeps
the locked force equation, kinematics, routing, exits, and wall handling; it
only finds pairs inside a declared 2 m interaction neighbourhood using a
KD-tree.  It is acceptable for V6 only after its approximation audit passes.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

V6 = Path(__file__).resolve().parents[1]
VENDOR = V6 / ".vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))

import numpy as np
from scipy.spatial import cKDTree


CORE_PATH = V6 / "legacy_core" / "disfm_cg_core.py"
INTERACTION_CUTOFF_M = 2.0


def load_locked_core():
    """Load the hash-pinned core without copying or altering it."""

    module_name = "v6_locked_disfm_core"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(module_name, CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import locked core at {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


LOCKED_CORE = load_locked_core()
Building = LOCKED_CORE.Building


class SpatiallyCulledSimulation(LOCKED_CORE.Simulation):
    """Locked simulation with a KD-tree locality implementation of pair force."""

    interaction_cutoff_m = INTERACTION_CUTOFF_M

    def _forces(self) -> np.ndarray:
        n = len(self.agents)
        force = np.zeros((n, 2))
        positions = np.asarray([agent.pos for agent in self.agents], dtype=float)
        radii = np.asarray([agent.radius for agent in self.agents], dtype=float)
        amplitudes = np.asarray([agent.A for agent in self.agents], dtype=float)
        ranges = np.asarray([agent.B for agent in self.agents], dtype=float)
        active = np.asarray([agent.exited_at is None for agent in self.agents], dtype=bool)

        # For each unordered pair, retain the two asymmetric force terms from
        # the locked core: A_i exp((r_i+r_j-d)/B_i) * unit(i-j), and vice versa.
        if n > 1 and np.any(active):
            pairs = cKDTree(positions[active]).query_pairs(self.interaction_cutoff_m, output_type="ndarray")
            active_indices = np.flatnonzero(active)
            if len(pairs):
                i = active_indices[pairs[:, 0]]
                j = active_indices[pairs[:, 1]]
                difference = positions[i] - positions[j]
                distance = np.linalg.norm(difference, axis=1)
                keep = distance > 1e-6
                i, j, difference, distance = i[keep], j[keep], difference[keep], distance[keep]
                if len(i):
                    unit = difference / distance[:, None]
                    summed_radii = radii[i] + radii[j]
                    magnitude_i = np.clip(amplitudes[i] * np.exp((summed_radii - distance) / ranges[i]), 0.0, 1e5)
                    magnitude_j = np.clip(amplitudes[j] * np.exp((summed_radii - distance) / ranges[j]), 0.0, 1e5)
                    np.add.at(force, i, magnitude_i[:, None] * unit)
                    np.add.at(force, j, -magnitude_j[:, None] * unit)

        # These terms are intentionally identical to the locked implementation.
        for index, agent in enumerate(self.agents):
            if agent.exited_at is not None:
                force[index] = 0.0
                continue
            desired_direction = self._desired_dir(agent)
            force[index] += agent.mass * (agent.v0 * desired_direction - agent.vel) / agent.tau
            force[index] += self._guidance_force(agent)
            force[index] += self._leader_force(agent)
            force[index] += self._boundary_force(agent)
        return force


def conservative_omitted_pair_force_bound(max_amplitude: float, max_radius: float, max_range: float) -> float:
    """Upper bound for one omitted pair at the fixed cutoff, in newtons."""

    if min(max_amplitude, max_radius, max_range) <= 0.0:
        raise ValueError("physical parameters must be positive")
    return float(max_amplitude * np.exp((2.0 * max_radius - INTERACTION_CUTOFF_M) / max_range))
