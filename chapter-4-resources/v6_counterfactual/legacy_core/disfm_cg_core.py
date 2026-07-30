"""
DiSFM-GS simulation core.
=================================================================
Disability-Inclusive Social Force Model with a Guidance Switch.

Self-contained implementation in a single meter frame: agents navigate the
building navigation graph to the available exits.

Design (all in ONE meter frame = the building-graph frame):
  * Building navigation graph (nodes + corridor edges) from building_graph.json.
  * Agents initialised from the frame-aligned trajectories
    (`trajectory_analysis/results/{s}_kalman_aligned.csv`, columns
     X_smooth_aligned / Y_smooth_aligned), which live in the building frame.
  * Per-scenario door availability from exit_usage_summary.csv.
  * Graph shortest-path routing: each agent follows corridor waypoints to its
    target door (nearest OPEN door by graph distance, unless AI-guided).

Mechanisms (Eq. 1 terms) are added on top of this foundation; see the force
methods.  Nothing here prints during simulation (calibration-friendly).
"""

from __future__ import annotations
import json
import os
import re
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import networkx as nx

# --------------------------------------------------------------------------
# Paths.  Environment overrides make a submitted code package runnable against
# the archived study data without copying it into the package tree.
# --------------------------------------------------------------------------
CODES_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = CODES_DIR.parent
TA_RESULTS = Path(os.environ.get(
    "DISFM_TRAJECTORY_RESULTS", str(PACKAGE_DIR / "trajectory_analysis" / "results")
))
PROCESSED = Path(os.environ.get("DISFM_PROCESSED_DATA", str(CODES_DIR / "processed_data")))
EXIT_TIMES = Path(os.environ.get("DISFM_EXIT_TIMES", str(CODES_DIR / "Exit times")))
BUILDING_GRAPH_PATH = Path(os.environ.get(
    "DISFM_BUILDING_GRAPH", str(PACKAGE_DIR / "config" / "building_graph.json")
))
_wall_geometry_env = os.environ.get("DISFM_WALL_GEOMETRY")
WALL_GEOMETRY_PATH = Path(_wall_geometry_env) if _wall_geometry_env else None

VALID_SCENARIOS = list(range(1, 17))
IWD_IDS = {18, 22, 31, 36, 39}   # anonymized IDs of the tracked IWD participants

# Authoritative scenario metadata (paper Table 4-1). Controlled = guided
# evacuation: in the drill a marshal gave explicit instructions as the physical
# proxy for AI guidance; the paper frames/measures this as AI-guided evacuation.
# Available doors govern routing.
# NOTE: for scenario 6 the table lists D3,D4; the usage records show all four
# doors used. The table is treated as authoritative here.
SCENARIOS = {
    1:  ("Classroom",               False, ["D1", "D2"]),
    2:  ("Classroom",               False, ["D1"]),
    3:  ("Classroom",               False, ["D2"]),
    4:  ("Classroom",               True,  ["D1", "D2"]),
    5:  ("Computer Lab",            False, ["D1", "D2"]),
    6:  ("Computer Lab",            False, ["D3", "D4"]),
    7:  ("Computer Lab",            False, ["D4"]),
    8:  ("Classroom+Computer Lab",  False, ["D1", "D2", "D3", "D4"]),
    9:  ("Classroom+Computer Lab",  False, ["D1", "D2", "D4"]),
    10: ("Classroom+Computer Lab",  False, ["D2", "D4"]),
    11: ("Classroom",               True,  ["D3", "D4"]),
    12: ("Lecture hall",            False, ["D2"]),
    13: ("Lecture hall",            False, ["D1", "D2"]),
    14: ("Lecture hall",            False, ["D3", "D4"]),
    15: ("Computer Lab",            True,  ["D1", "D2", "D3", "D4"]),
    16: ("All",                     False, ["D1", "D2", "D3", "D4"]),
}
CONTROLLED_SCENARIOS = [s for s, v in SCENARIOS.items() if v[1]]   # [4, 11, 15]
CALIBRATION_SCENARIOS = [1, 2, 3, 4, 6, 7, 8, 10, 12, 13, 14, 15, 16]  # strict split
VALIDATION_SCENARIOS = [5, 9, 11]   # untouched by any loss component
FAMILIAR_EXITS = {"D1", "D2"}       # main/familiar exits
UNFAMILIAR_EXITS = {"D3", "D4"}     # less-familiar exits (empirical egress delay when forced onto them)


# --------------------------------------------------------------------------
# Building geometry + navigation graph
# --------------------------------------------------------------------------
class Building:
    """Navigation graph in the building meter frame."""

    def __init__(self, graph_path: Path, wall_geometry_path: Optional[Path] = None):
        with open(graph_path, encoding="utf-8") as handle:
            bg = json.load(handle)
        self.node_pos: Dict[str, np.ndarray] = {
            n["id"]: np.array([n["x"], n["y"]], float) for n in bg["nodes"]
        }
        self.exits: Dict[str, np.ndarray] = {
            e["id"]: np.array([e["x"], e["y"]], float) for e in bg["exits"]
        }
        # Undirected walkable graph, edge weights = corridor length.
        self.G = nx.Graph()
        for nid, pos in self.node_pos.items():
            self.G.add_node(nid, pos=pos)
        for e in bg["edges"]:
            self.G.add_edge(e["from"], e["to"], weight=float(e["length"]))
        # bounding box (for a soft outer boundary only)
        P = np.array(list(self.node_pos.values()))
        self.bbox_min = P.min(0) - 3.0
        self.bbox_max = P.max(0) + 3.0
        self.wall_segments = np.empty((0, 2, 2), dtype=float)
        geometry_path = wall_geometry_path if wall_geometry_path is not None else WALL_GEOMETRY_PATH
        if geometry_path is not None:
            with open(geometry_path, encoding="utf-8") as handle:
                geometry = json.load(handle)
            segments = [
                [item["start"], item["end"]]
                for item in geometry.get("segments", [])
                if len(item.get("start", [])) == 2 and len(item.get("end", [])) == 2
            ]
            if segments:
                self.wall_segments = np.asarray(segments, dtype=float)

    def nearest_node(self, pos: np.ndarray) -> str:
        return min(self.node_pos, key=lambda n: np.hypot(*(self.node_pos[n] - pos)))

    def route(self, start_pos: np.ndarray, door_id: str) -> List[np.ndarray]:
        """Waypoint list (positions) from start to a door, via the graph."""
        entry = self.nearest_node(start_pos)
        try:
            node_path = nx.shortest_path(self.G, entry, door_id, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            node_path = [door_id]
        return [self.node_pos[n] for n in node_path]

    def graph_distance(self, start_pos: np.ndarray, door_id: str) -> float:
        entry = self.nearest_node(start_pos)
        try:
            return float(nx.shortest_path_length(self.G, entry, door_id, weight="weight"))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return float(np.hypot(*(self.exits[door_id] - start_pos)))

    def wall_force(self, pos: np.ndarray, radius: float, A_wall: float, B_wall: float) -> np.ndarray:
        """Repel an agent from the nearest CAD-derived wall segment.

        Segment walls are used only when an explicitly registered geometry file
        is supplied; otherwise the historical soft bounding box remains the
        backward-compatible fallback.
        """
        if len(self.wall_segments) == 0:
            return np.zeros(2)
        starts = self.wall_segments[:, 0, :]
        vectors = self.wall_segments[:, 1, :] - starts
        rel = pos - starts
        denom = np.einsum("ij,ij->i", vectors, vectors)
        frac = np.divide(np.einsum("ij,ij->i", rel, vectors), denom,
                         out=np.zeros_like(denom), where=denom > 1e-12)
        frac = np.clip(frac, 0.0, 1.0)
        closest = starts + frac[:, None] * vectors
        away = pos - closest
        distances = np.linalg.norm(away, axis=1)
        index = int(np.argmin(distances))
        distance = float(distances[index])
        direction = away[index]
        if distance < 1e-9:
            tangent = vectors[index]
            tangent_norm = float(np.linalg.norm(tangent))
            if tangent_norm < 1e-9:
                return np.zeros(2)
            direction = np.array([-tangent[1], tangent[0]]) / tangent_norm
            distance = 1e-9
        else:
            direction = direction / distance
        magnitude = min(1e5, A_wall * np.exp((radius - distance) / B_wall))
        return magnitude * direction


# --------------------------------------------------------------------------
# Data loaders
# --------------------------------------------------------------------------
def load_open_doors(usage_csv: Path) -> Dict[int, List[str]]:
    """scenario -> list of open door ids (available == 'Y')."""
    df = pd.read_csv(usage_csv)
    out = {}
    for s, grp in df.groupby("session"):
        out[int(s)] = list(grp[grp["available"] == "Y"]["exit"].values)
    return out


def load_observed_exits(events_csv: Path) -> Dict[int, Dict[int, str]]:
    """scenario -> {agent_id -> observed door id}."""
    df = pd.read_csv(events_csv)
    out: Dict[int, Dict[int, str]] = {}
    for _, r in df.iterrows():
        out.setdefault(int(r["session"]), {})[int(r["ID"])] = str(r["exit_id"])
    return out


def load_scenario_agents(scenario_id: int) -> pd.DataFrame:
    """Per-agent start position (building frame) + class, from aligned traj."""
    f = TA_RESULTS / f"{scenario_id}_kalman_aligned.csv"
    df = pd.read_csv(f)
    df = df.sort_values("Time")
    rows = []
    for aid, g in df.groupby("ID"):
        first = g.iloc[0]
        rows.append({
            "ID": int(aid),
            "x0": float(first["X_smooth_aligned"]),
            "y0": float(first["Y_smooth_aligned"]),
            "is_iwd": int(aid) in IWD_IDS,
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Directional correlation delay (Nagy et al. 2010) leader-follower network.
# Robust replacement for transfer entropy on short trajectory series: the peak
# lag of the velocity-direction correlation gives who moves first (the leader).
# --------------------------------------------------------------------------
_TMAX_LAG = 6   # +/- 6 samples = +/- 12 s at 0.5 Hz


def _unit_vel(vx, vy):
    v = np.column_stack([vx, vy]); n = np.linalg.norm(v, axis=1, keepdims=True)
    return np.divide(v, n, out=np.zeros_like(v), where=n > 1e-6)


def _dir_corr(vi, vj, tau):
    if tau >= 0:
        a, b = vi[:len(vi) - tau], vj[tau:]
    else:
        a, b = vi[-tau:], vj[:len(vj) + tau]
    L = min(len(a), len(b))
    return np.nan if L < 5 else float(np.mean(np.sum(a[:L] * b[:L], axis=1)))


def _peak_lag_corr(vi, vj, tmax=_TMAX_LAG):
    taus = np.arange(-tmax, tmax + 1)
    C = np.array([_dir_corr(vi, vj, t) for t in taus])
    if np.all(np.isnan(C)):
        return 0, 0.0
    k = int(np.nanargmax(C))
    return int(taus[k]), float(C[k])          # tau*>0 => i leads j


def directional_leadership_matrix(vel_by_agent: Dict[int, np.ndarray], ids: List[int]):
    """L[i,j] = peak directional correlation when i leads j (tau*>0), else 0.
    Works on observed OR simulated unit-velocity series (same estimator)."""
    n = len(ids); L = np.zeros((n, n))
    for a in range(n):
        for b in range(a + 1, n):
            va, vb = vel_by_agent.get(ids[a]), vel_by_agent.get(ids[b])
            if va is None or vb is None:
                continue
            tau, c = _peak_lag_corr(va, vb)
            if tau > 0:
                L[a, b] = c        # a leads b
            elif tau < 0:
                L[b, a] = c        # b leads a
    return L


def build_leader_P_directional(cap: float = 0.6) -> Dict[int, Dict[int, float]]:
    """P[follower][leader] from the directional correlation delay network,
    aggregated across sessions (row-normalise per follower, cap, average)."""
    precomputed_path = os.environ.get("DISFM_LEADER_WEIGHTS_PATH")
    if precomputed_path:
        with open(precomputed_path, encoding="utf-8") as handle:
            saved = json.load(handle)
        weights = saved.get("leader_P", saved)
        return {
            int(follower): {int(leader): float(weight) for leader, weight in row.items()}
            for follower, row in weights.items()
        }
    with open(PROCESSED / "clean_traj.pkl", "rb") as handle:
        traj = pickle.load(handle)
    per_follower: Dict[int, List[Dict[int, float]]] = {}
    for s, df in traj.items():
        vel = {int(a): _unit_vel(g.sort_values("Time")["vx"].values,
                                 g.sort_values("Time")["vy"].values)
               for a, g in df.groupby("ID")}
        ids = sorted(vel)
        L = directional_leadership_matrix(vel, ids)   # L[leader_idx? no: L[a,b]=a leads b]
        # follower b's leaders are a with L[a,b]>0
        for bi, b in enumerate(ids):
            leaders = {ids[ai]: L[ai, bi] for ai in range(len(ids)) if L[ai, bi] > 0}
            tot = sum(leaders.values())
            if tot <= 0:
                continue
            norm = {j: min(v / tot, cap) for j, v in leaders.items()}
            t2 = sum(norm.values())
            norm = {j: v / t2 for j, v in norm.items()} if t2 > 0 else norm
            per_follower.setdefault(b, []).append(norm)
    P: Dict[int, Dict[int, float]] = {}
    for follower, dists in per_follower.items():
        agg: Dict[int, float] = {}
        for d in dists:
            for j, v in d.items():
                agg[j] = agg.get(j, 0.0) + v
        P[follower] = {j: v / len(dists) for j, v in agg.items()}
    return P


# --------------------------------------------------------------------------
# Transfer-entropy leader network (optional; the directional correlation-delay
# method is used by default for the leader force).
# --------------------------------------------------------------------------
_GML_EDGE = re.compile(
    r"edge\s*\[\s*source\s+(\d+)\s+target\s+(\d+)\s+weight\s+[A-Za-z.]*\(?([-\d.eE]+)\)?",
)
_GML_NODE = re.compile(r"node\s*\[\s*id\s+(\d+)\s+label\s+\"(\d+)\"")


def _parse_leader_gml(path: Path):
    """Return list of (follower_id, leader_id, te_weight) from a leader GML.

    Edge source->target in these graphs means source LEADS target (information
    flows source->target), i.e. `target` follows `source`.  We therefore emit
    (follower=target, leader=source, weight).
    """
    text = path.read_text()
    id2label = {int(i): int(lbl) for i, lbl in _GML_NODE.findall(text)}
    edges = []
    for s, t, w in _GML_EDGE.findall(text):
        src, tgt, wt = id2label[int(s)], id2label[int(t)], float(w)
        edges.append((tgt, src, wt))   # (follower, leader, weight)
    return edges


def build_leader_P(threshold: str = "97", cap: float = 0.6) -> Dict[int, Dict[int, float]]:
    """Aggregate per-session leader graphs into P[follower][leader] = prob.

    Steps (per DiSFM-CG.md Step 0): keep the (already-thresholded) 97% edges,
    row-normalise per follower, cap any single leader's share at `cap`,
    renormalise, then average each follower's row across the sessions in which
    that follower had outgoing (following) edges.
    """
    prefix = "97leader_graph_" if threshold == "97" else "leader_graph_"
    files = sorted(TA_RESULTS.glob(f"{prefix}*.gml"))
    # follower -> list of per-session normalised leader-distributions
    per_follower: Dict[int, List[Dict[int, float]]] = {}
    for f in files:
        rows: Dict[int, Dict[int, float]] = {}
        for follower, leader, w in _parse_leader_gml(f):
            d = rows.setdefault(follower, {})
            d[leader] = d.get(leader, 0.0) + max(w, 0.0)
        for follower, leaders in rows.items():
            tot = sum(leaders.values())
            if tot <= 0:
                continue
            norm = {j: min(v / tot, cap) for j, v in leaders.items()}
            tot2 = sum(norm.values())
            norm = {j: v / tot2 for j, v in norm.items()} if tot2 > 0 else norm
            per_follower.setdefault(follower, []).append(norm)
    # average each follower's row across its sessions
    P: Dict[int, Dict[int, float]] = {}
    for follower, dists in per_follower.items():
        agg: Dict[int, float] = {}
        for d in dists:
            for j, v in d.items():
                agg[j] = agg.get(j, 0.0) + v
        P[follower] = {j: v / len(dists) for j, v in agg.items()}
    return P


# --------------------------------------------------------------------------
# Agent + simulation
# --------------------------------------------------------------------------
@dataclass
class Agent:
    id: int
    pos: np.ndarray
    vel: np.ndarray
    is_iwd: bool
    v0: float
    tau: float
    A: float
    B: float
    radius: float
    mass: float
    c_i: float                       # latent compliance trait ~ Beta
    target_door: str = ""
    waypoints: List[np.ndarray] = field(default_factory=list)
    wp_idx: int = 0
    exited_at: Optional[float] = None
    exit_door: Optional[str] = None
    natural_door: str = ""       # nearest door among ALL doors (intrinsic preference)
    guided_door: Optional[str] = None   # marshal/AI-designated door (controlled scenarios)
    complies: bool = False       # compliance-gate outcome for this run
    pre_delay: float = 0.0       # pre-movement / reaction time before the agent starts moving


class Simulation:
    """One scenario simulation in the building frame."""

    def __init__(self, building: Building, params: dict, open_doors: Dict[int, List[str]],
                 rng: Optional[np.random.Generator] = None,
                 leader_P: Optional[Dict[int, Dict[int, float]]] = None):
        self.b = building
        self.p = params
        self.open_doors = open_doors
        self.rng = rng or np.random.default_rng(0)
        self.leader_P = leader_P or {}
        # ablation toggles (M0-M4): default full model
        self.use_leader = params.get("use_leader", True)
        self.use_guidance = params.get("use_guidance", True)
        self.single_class = params.get("single_class", False)   # M0 SFM baseline
        # A homogeneous SFM may explicitly suppress the class-dependent body
        # constants as well as the class-dependent kinematics.  The default
        # preserves the historical DiSFM behaviour and all existing runs.
        self.shared_body = params.get("shared_body", False)
        self.shared_mass = params.get("shared_mass", 75.0)
        self.shared_radius = params.get("shared_radius", 0.275)
        self.use_familiarity = params.get("use_familiarity", True)
        # familiarity speed factor on the unfamiliar exits (D3/D4): agents routed
        # to a less-familiar exit move more tentatively (v0 -> v0*phi). Grounds the
        # empirical unfamiliar-exit delay in the route-familiarity
        # literature; phi=1.0 disables the effect (backward compatible).
        self.phi_unfam = params.get("phi_unfam", 1.0)
        # calibrated behaviour parameters
        self.beta_leader = params.get("beta_leader", 1.0)   # leader-attraction strength
        self.lambda_door = params.get("lambda_door", 8.0)   # exit-choice distance sensitivity (m)
        self.w_cong = params.get("w_cong", 0.0)             # congestion aversion in door choice
        self.t_premove = params.get("t_premove", 12.0)      # mean pre-movement/reaction time (s), SFPE educational
        self.premove_cv = params.get("premove_cv", 0.6)     # lognormal CV of pre-movement time
        # fixed physical constants (held, not calibrated)
        self.dt = params.get("dt", 0.05)
        self.A_wall = params.get("A_wall", 2000.0)
        self.B_wall = params.get("B_wall", 0.08)
        self.leader_range = params.get("leader_range", 15.0)  # local following range (m)
        self.exit_gap = params.get("exit_gap", 0.4)     # min s between exits per door (flow capacity ~2.5 P/s); non-binding at low density
        self.wp_reach = params.get("wp_reach", 2.0)     # waypoint switch radius
        self.exit_reach = params.get("exit_reach", 2.0)  # door reach radius
        self.max_time = params.get("max_time", 200.0)

    # ---- setup -----------------------------------------------------------
    def _body_properties(self, is_iwd: bool) -> tuple[float, float]:
        """Return radius and mass, optionally as common SFM constants."""
        if self.shared_body:
            return float(self.shared_radius), float(self.shared_mass)
        return (0.30 if is_iwd else 0.25), (80.0 if is_iwd else 70.0)

    def init_agents(self, scenario_id: int, guidance_doors: Optional[Dict[int, str]] = None):
        agents_df = load_scenario_agents(scenario_id)
        doors = self.open_doors.get(scenario_id, list(self.b.exits.keys()))
        self.agents: List[Agent] = []
        for _, r in agents_df.iterrows():
            pos = np.array([r["x0"], r["y0"]], float)
            is_iwd = bool(r["is_iwd"])
            # M0 (SFM baseline): single class -> all agents use able-bodied params
            use_mob = is_iwd and not self.single_class
            v0 = self.p["v0_mob"] if use_mob else self.p["v0_amb"]
            tau = self.p["tau_mob"] if use_mob else self.p["tau_amb"]
            A = self.p["A_mob"] if use_mob else self.p["A_amb"]
            B = self.p["B_mob"] if use_mob else self.p["B_amb"]
            radius, mass = self._body_properties(is_iwd)
            c_i = float(self.rng.beta(self.p.get("beta_a", 2.0), self.p.get("beta_b", 2.0)))
            ag = Agent(id=int(r["ID"]), pos=pos, vel=np.zeros(2), is_iwd=is_iwd,
                       v0=max(0.1, v0), tau=tau, A=A, B=B, radius=radius, mass=mass, c_i=c_i)
            ag.pre_delay = self._sample_pre_delay()
            self.agents.append(ag)
        self.guidance_doors = guidance_doors or {}
        self._assign_doors(scenario_id, doors)
        self.time = 0.0

    def _sample_pre_delay(self) -> float:
        """Pre-movement / reaction time ~ LogNormal with mean t_premove (SFPE)."""
        m, cv = max(self.t_premove, 1e-3), self.premove_cv
        sigma = np.sqrt(np.log(1 + cv * cv))
        mu = np.log(m) - 0.5 * sigma * sigma
        return float(self.rng.lognormal(mu, sigma))

    def _make_agent(self, aid, pos, is_iwd):
        use_mob = is_iwd and not self.single_class
        v0 = self.p["v0_mob"] if use_mob else self.p["v0_amb"]
        tau = self.p["tau_mob"] if use_mob else self.p["tau_amb"]
        A = self.p["A_mob"] if use_mob else self.p["A_amb"]
        B = self.p["B_mob"] if use_mob else self.p["B_amb"]
        c_i = float(self.rng.beta(self.p.get("beta_a", 2.0), self.p.get("beta_b", 2.0)))
        radius, mass = self._body_properties(is_iwd)
        ag = Agent(id=int(aid), pos=np.array(pos, float), vel=np.zeros(2), is_iwd=is_iwd,
                   v0=max(0.1, v0), tau=tau, A=A, B=B,
                   radius=radius, mass=mass, c_i=c_i)
        ag.pre_delay = self._sample_pre_delay()
        return ag

    def init_custom(self, specs, doors, guidance: str = "none"):
        """High-density design-occupancy setup for policy analysis.
        specs = list of (x, y, is_iwd). guidance: 'none' (emergent exit choice)
        or 'balanced' (marshal load-balances compliant agents across doors)."""
        self.agents = [self._make_agent(i, (x, y), bool(iw)) for i, (x, y, iw) in enumerate(specs)]
        all_doors = list(self.b.exits.keys())
        alpha_c = self.p.get("alpha_c", 5.0); beta_c = self.p.get("beta_c", 0.0)
        attract = {"D1": 0.0, "D2": self.p.get("a_D2", 0.0),
                   "D3": self.p.get("a_D3", 0.0), "D4": self.p.get("a_D4", 0.0)}
        dist = {a.id: {d: self.b.graph_distance(a.pos, d) for d in doors} for a in self.agents}
        load = {d: 0 for d in doors}
        order = list(range(len(self.agents))); self.rng.shuffle(order)
        for k in order:
            ag = self.agents[k]
            ag.natural_door = min(all_doors, key=lambda d: self.b.graph_distance(ag.pos, d))
            # emergent choice (softmax by distance + attractiveness + congestion)
            util = {d: -dist[ag.id][d]/self.lambda_door - self.w_cong*load[d] + attract.get(d, 0.0)
                    for d in doors}
            m = max(util.values()); ex = {d: np.exp(util[d]-m) for d in doors}; Z = sum(ex.values())
            chosen = doors[int(self.rng.choice(len(doors), p=np.array([ex[d]/Z for d in doors])))]
            if guidance == "balanced":
                # marshal assigns the least-loaded door (congestion relief); compliant agents follow
                guided = min(doors, key=lambda d: (load[d], dist[ag.id][d]))
                ag.guided_door = guided
                p_comply = 1.0/(1.0+np.exp(-(alpha_c*ag.c_i+beta_c)))
                ag.complies = bool(self.rng.random() < p_comply)
                if ag.complies:
                    chosen = guided
            if (self.use_familiarity and chosen in UNFAMILIAR_EXITS
                    and not any(fd in doors for fd in FAMILIAR_EXITS)):
                ag.v0 = max(0.1, ag.v0 * self.phi_unfam)   # tentative movement on unfamiliar route
            ag.target_door = chosen; load[chosen] += 1; self._set_route(ag)
        self.guidance_doors = {}
        self.time = 0.0

    def _assign_doors(self, scenario_id: int, doors: List[str]):
        """Emergent exit choice: softmax over open doors by graph distance and
        (optionally) congestion.  lambda_door sets distance sensitivity; w_cong
        the aversion to a door many others are already heading to.

        Controlled scenarios: the marshal/AI directs each participant to their
        NEAREST available designated door (group/location-based split).
        A compliant agent (Bernoulli sigma(alpha_c*c_i +
        beta_c)) adopts that door; a non-compliant agent uses the softmax
        choice.  natural_door (nearest among ALL doors) is the intrinsic
        preference used by the continuous guidance force."""
        controlled = SCENARIOS[scenario_id][1]
        all_doors = list(self.b.exits.keys())
        dist = {a.id: {d: self.b.graph_distance(a.pos, d) for d in doors} for a in self.agents}
        load = {d: 0 for d in doors}
        alpha_c = self.p.get("alpha_c", 5.0)
        beta_c = self.p.get("beta_c", 0.0)
        # per-door attractiveness (familiarity / visibility): captures the
        # observed preference for some doors over nearer ones (e.g. D2 chosen
        # over the closer D1). D1 is the reference (a_D1 = 0).
        attract = {"D1": 0.0,
                   "D2": self.p.get("a_D2", 0.0),
                   "D3": self.p.get("a_D3", 0.0),
                   "D4": self.p.get("a_D4", 0.0)}
        order = list(range(len(self.agents)))
        self.rng.shuffle(order)
        for k in order:
            ag = self.agents[k]
            ag.natural_door = min(all_doors, key=lambda d: self.b.graph_distance(ag.pos, d))
            util = {d: -dist[ag.id][d] / self.lambda_door - self.w_cong * load[d]
                    + attract.get(d, 0.0) for d in doors}
            m = max(util.values())
            ex = {d: np.exp(util[d] - m) for d in doors}
            Z = sum(ex.values())
            probs = np.array([ex[d] / Z for d in doors])
            chosen = doors[int(self.rng.choice(len(doors), p=probs))]
            # Exit choice is EMERGENT (distance + congestion + door attractiveness)
            # in all scenarios. The drill data show guidance reinforced, not
            # redirected, door choice (guided scen 4 split ~= free-choice scen 1),
            # so there is no "nearest-door" override. The guidance force remains a
            # modelled capability: compliant agents in controlled scenarios can be
            # steered toward an explicitly-supplied guidance door for counterfactual
            # policy runs; during calibration the guided door is their own choice.
            if controlled and self.use_guidance:
                ag.guided_door = self.guidance_doors.get(ag.id, chosen)
                p_comply = 1.0 / (1.0 + np.exp(-(alpha_c * ag.c_i + beta_c)))
                ag.complies = bool(self.rng.random() < p_comply)
            ag.target_door = chosen
            # Unfamiliar-exit slowdown applies only when the scenario FORCES
            # occupants onto the less-familiar exits (no familiar D1/D2 open) —
            # matching the empirical coding (scenarios whose open set is a
            # subset of {D3,D4}: 6,7,11,14). Freely choosing D3/D4 when a familiar
            # exit is available carries no penalty.
            if (self.use_familiarity and chosen in UNFAMILIAR_EXITS
                    and not any(fd in doors for fd in FAMILIAR_EXITS)):
                ag.v0 = max(0.1, ag.v0 * self.phi_unfam)   # tentative movement on unfamiliar route
            load[chosen] += 1
            self._set_route(ag)

    def _set_route(self, ag: Agent):
        ag.waypoints = self.b.route(ag.pos, ag.target_door)
        ag.wp_idx = 0

    # ---- routing helpers -------------------------------------------------
    def _desired_dir(self, ag: Agent) -> np.ndarray:
        # advance waypoint if close
        while ag.wp_idx < len(ag.waypoints) - 1 and \
                np.hypot(*(ag.waypoints[ag.wp_idx] - ag.pos)) < self.wp_reach:
            ag.wp_idx += 1
        target = ag.waypoints[ag.wp_idx] if ag.waypoints else self.b.exits[ag.target_door]
        d = target - ag.pos
        n = np.hypot(*d)
        return d / n if n > 1e-9 else np.zeros(2)

    # ---- forces ----------------------------------------------------------
    def _forces(self) -> np.ndarray:
        n = len(self.agents)
        F = np.zeros((n, 2))
        pos = np.array([a.pos for a in self.agents])
        rad = np.array([a.radius for a in self.agents])
        A = np.array([a.A for a in self.agents])
        B = np.array([a.B for a in self.agents])
        active = np.array([a.exited_at is None for a in self.agents])
        # --- agent-agent social repulsion (vectorised, O(n^2) but in numpy) ---
        diff = pos[:, None, :] - pos[None, :, :]          # (n,n,2): i - j
        dist = np.linalg.norm(diff, axis=2)               # (n,n)
        np.fill_diagonal(dist, np.inf)
        sumrad = rad[:, None] + rad[None, :]
        with np.errstate(over="ignore"):
            mag = A[:, None] * np.exp((sumrad - dist) / B[:, None])
        mag = np.clip(mag, 0.0, 1e5)
        mag[:, ~active] = 0.0                              # exited agents exert no force
        mag[dist < 1e-6] = 0.0
        unit = np.divide(diff, dist[..., None], out=np.zeros_like(diff), where=dist[..., None] > 1e-6)
        F += np.sum(mag[..., None] * unit, axis=1)         # sum over j
        # --- per-agent terms (driving, guidance, leader, boundary) ---
        for i, ai in enumerate(self.agents):
            if ai.exited_at is not None:
                F[i] = 0.0
                continue
            e_i = self._desired_dir(ai)
            F[i] += ai.mass * (ai.v0 * e_i - ai.vel) / ai.tau
            # guidance force: A_i * k_AI * (d_guided - d_self), only for
            # compliant agents in controlled scenarios; nonzero when the guided
            # door differs from the agent's natural preference (reinforcing in
            # scen 4, counter-intuitive in scen 11).
            F[i] += self._guidance_force(ai)
            # leader-follower attraction (Eq. 1, 5th term): beta * sum_j P[i->j] * dir(x_j - x_i)
            F[i] += self._leader_force(ai)
            # CAD segment walls when registered; soft outer bbox otherwise.
            F[i] += self._boundary_force(ai)
        return F

    def _guidance_force(self, ai: Agent) -> np.ndarray:
        if not ai.complies or ai.guided_door is None:
            return np.zeros(2)
        k_ai = self.p.get("k_AI", 2.0)
        g = self.b.exits[ai.guided_door] - ai.pos
        s = self.b.exits[ai.natural_door] - ai.pos
        gn, sn = np.hypot(*g), np.hypot(*s)
        if gn < 1e-6:
            return np.zeros(2)
        d_guided = g / gn
        d_self = s / sn if sn > 1e-6 else d_guided
        return ai.mass * k_ai * (d_guided - d_self)

    def _leader_force(self, ai: Agent) -> np.ndarray:
        if not self.use_leader:
            return np.zeros(2)
        row = self.leader_P.get(ai.id)
        if not row or self.beta_leader == 0.0:
            return np.zeros(2)
        f = np.zeros(2)
        for aj in self.agents:
            if aj.id == ai.id or aj.exited_at is not None:
                continue
            p_ij = row.get(aj.id, 0.0)
            if p_ij <= 0.0:
                continue
            d = aj.pos - ai.pos
            dist = np.hypot(*d)
            if 1e-6 < dist < self.leader_range:
                f += self.beta_leader * p_ij * (d / dist)
        return f

    def _boundary_force(self, ag: Agent) -> np.ndarray:
        if len(self.b.wall_segments):
            return self.b.wall_force(ag.pos, ag.radius, self.A_wall, self.B_wall)
        f = np.zeros(2)
        for k in range(2):
            dlo = ag.pos[k] - self.b.bbox_min[k]
            dhi = self.b.bbox_max[k] - ag.pos[k]
            if dlo < 2.0:
                f[k] += self.A_wall * np.exp((ag.radius - dlo) / self.B_wall)
            if dhi < 2.0:
                f[k] -= self.A_wall * np.exp((ag.radius - dhi) / self.B_wall)
        return f

    # ---- step ------------------------------------------------------------
    def step(self):
        if not hasattr(self, "_last_exit"):
            self._last_exit = {}     # door -> time of last exit (flow capacity)
        F = self._forces()
        for i, ag in enumerate(self.agents):
            if ag.exited_at is not None:
                continue
            if self.time < ag.pre_delay:      # still in pre-movement (not yet reacting)
                ag.vel[:] = 0.0
                continue
            ag.vel = ag.vel + (F[i] / ag.mass) * self.dt
            sp = np.hypot(*ag.vel)
            vmax = 2.0 * ag.v0
            if sp > vmax:
                ag.vel *= vmax / sp
            ag.pos = ag.pos + ag.vel * self.dt
            # door flow capacity: an agent at the door exits only if the door has
            # cleared the last exit (>= exit_gap). Otherwise it queues (congestion).
            if np.hypot(*(self.b.exits[ag.target_door] - ag.pos)) < self.exit_reach:
                if self.time - self._last_exit.get(ag.target_door, -1e9) >= self.exit_gap:
                    ag.exited_at = self.time
                    ag.exit_door = ag.target_door
                    self._last_exit[ag.target_door] = self.time
        self.time += self.dt

    def run(self, record_speed: bool = False):
        # record velocity vectors at the empirical sampling rate (0.5 Hz) so
        # simulated speed distributions AND directional-correlation coupling are
        # comparable to the observed 0.5 Hz data.
        self._last_exit = {}
        vel_series: Dict[int, List[np.ndarray]] = {a.id: [] for a in self.agents}
        stride = max(1, int(round(2.0 / self.dt)))   # 2 s interval
        nsteps = int(self.max_time / self.dt)
        for k in range(nsteps):
            if all(a.exited_at is not None for a in self.agents):
                break
            self.step()
            if record_speed and (k % stride == 0):
                for a in self.agents:
                    if a.exited_at is None and self.time >= a.pre_delay:
                        vel_series[a.id].append(a.vel.copy())
        result = {
            "exit_times": {a.id: a.exited_at for a in self.agents if a.exited_at is not None},
            "exit_doors": {a.id: a.exit_door for a in self.agents if a.exited_at is not None},
            "n_exited": sum(a.exited_at is not None for a in self.agents),
            "n_total": len(self.agents),
            "final_time": self.time,
        }
        if record_speed:
            result["vel_series"] = {aid: np.array(v) for aid, v in vel_series.items()}
            result["speed_series"] = {aid: [float(np.hypot(*w)) for w in v]
                                      for aid, v in vel_series.items()}
        return result
