"""Multi-floor route handling for the V6 CAD/map pilot.

Floor layers are spatially separated to prevent cross-floor force interactions.
When a route reaches a declared vertical stair link, the agent is transferred to
the linked lower-floor stair after its declared transfer time.  This adapter is
for the explicit evacuation-map-derived pilot topology only; it is not a claim
that the flattened drawing layout is physical three-dimensional geometry.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from src.v6_spatial_core import SpatiallyCulledSimulation


class MultiFloorSpatialSimulation(SpatiallyCulledSimulation):
    """Spatial core with explicit, timed inter-floor transfers."""

    def __init__(self, *args, vertical_links: Mapping[frozenset[str], float], **kwargs):
        super().__init__(*args, **kwargs)
        self.vertical_links = {frozenset((str(a), str(b))): float(seconds) for (a, b), seconds in vertical_links.items()}

    def install_node_routes(self) -> None:
        """Replace geometric-only waypoints with node IDs for transfer detection."""

        for agent in self.agents:
            entry = self.b.nearest_node(agent.pos)
            path = self.b.G.nodes
            try:
                nodes = __import__("networkx").shortest_path(self.b.G, entry, agent.target_door, weight="weight")
            except Exception as exc:
                raise RuntimeError(f"No graph route for agent {agent.id} to {agent.target_door}") from exc
            agent.node_route = [str(node) for node in nodes]
            agent.waypoints = [self.b.node_pos[node] for node in agent.node_route]
            agent.wp_idx = 0
            agent.transfer_until = -1.0

    def _desired_dir(self, agent) -> np.ndarray:
        route = getattr(agent, "node_route", None)
        if not route:
            return super()._desired_dir(agent)
        if self.time < getattr(agent, "transfer_until", -1.0):
            return np.zeros(2)
        while agent.wp_idx < len(route) - 1:
            current = route[agent.wp_idx]
            following = route[agent.wp_idx + 1]
            target = self.b.node_pos[current]
            delta = target - agent.pos
            distance = float(np.hypot(*delta))
            vertical_time = self.vertical_links.get(frozenset((current, following)))
            if vertical_time is not None:
                if distance >= self.wp_reach:
                    return delta / distance
                # The vertical movement is not represented as a fictitious
                # horizontal corridor.  The agent remains unavailable for the
                # declared transfer duration, then resumes on the linked floor.
                agent.pos = self.b.node_pos[following].copy()
                agent.vel[:] = 0.0
                agent.wp_idx += 1
                agent.transfer_until = self.time + vertical_time
                return np.zeros(2)
            if distance < self.wp_reach:
                agent.wp_idx += 1
                continue
            return delta / distance
        target = self.b.node_pos[route[agent.wp_idx]] if route else self.b.exits[agent.target_door]
        delta = target - agent.pos
        distance = float(np.hypot(*delta))
        return delta / distance if distance > 1e-9 else np.zeros(2)

    def _forces(self) -> np.ndarray:
        forces = super()._forces()
        for index, agent in enumerate(self.agents):
            if self.time < getattr(agent, "transfer_until", -1.0):
                forces[index] = 0.0
        return forces

    def step(self):
        if not hasattr(self, "_last_exit"):
            self._last_exit = {}
        forces = self._forces()
        for index, agent in enumerate(self.agents):
            if agent.exited_at is not None:
                continue
            if self.time < agent.pre_delay or self.time < getattr(agent, "transfer_until", -1.0):
                agent.vel[:] = 0.0
                continue
            agent.vel = agent.vel + (forces[index] / agent.mass) * self.dt
            speed = float(np.hypot(*agent.vel))
            maximum = 2.0 * agent.v0
            if speed > maximum:
                agent.vel *= maximum / speed
            agent.pos = agent.pos + agent.vel * self.dt
            if np.hypot(*(self.b.exits[agent.target_door] - agent.pos)) < self.exit_reach:
                if self.time - self._last_exit.get(agent.target_door, -1e9) >= self.exit_gap:
                    agent.exited_at = self.time
                    agent.exit_door = agent.target_door
                    self._last_exit[agent.target_door] = self.time
        self.time += self.dt
