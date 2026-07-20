"""
DiSFM-GS calibration objective.
=================================================================
Four loss components on the simulation core (disfm_cg_core), under a strict
calibrate/validate split.

    J(Theta) = w1*E_v + w2*KS_exit + w3*Delta_dir + w4*ERR_exit

  E_v      : mean absolute error of simulated able-bodied and aggregated-IWD
             class-speed means against the fixed targets 1.28 and 0.77 m/s.
  KS_exit  : 2-sample KS distance between simulated exit times (real, from the
             agents that reach their door) and observed exit times.
  Delta_dir: normalized Frobenius distance between observed and simulated
             continuous delayed directional-alignment matrices.
  ERR_exit : aggregate door-usage total-variation distance on the controlled
             calibration scenarios {4, 15}; it is not a person-level error.

"""
from __future__ import annotations
import pickle
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from disfm_cg_core import (
    Building, Simulation, build_leader_P_directional, load_observed_exits,
    directional_leadership_matrix, _unit_vel,
    SCENARIOS, CALIBRATION_SCENARIOS, VALIDATION_SCENARIOS, CONTROLLED_SCENARIOS,
    IWD_IDS, CODES_DIR, TA_RESULTS,
)

N_BINS = 10   # legacy TE helper only; TE is not used by the active loss

# Reported per-group mean walking speeds: each participant's total distance /
# total time.  E_v compares simulated class-mean speed with these targets.
AB_MEAN_SPEED = 1.28
IWD_MEAN_SPEED = 0.77


# --------------------------------------------------------------------------
# Legacy transfer-entropy helpers (not used by the active calibration loss)
# --------------------------------------------------------------------------
def transfer_entropy(v_src: np.ndarray, v_tgt: np.ndarray, n_bins: int = N_BINS) -> float:
    """TE from source velocity series to target (predictive of target future
    from source present).  Identical 10-bin plug-in estimator, k=l=1."""
    v_src = np.asarray(v_src, float)
    v_tgt = np.asarray(v_tgt, float)
    if len(v_src) < 3 or len(v_tgt) < 3:
        return 0.0
    lo = min(v_src.min(), v_tgt.min())
    hi = max(v_src.max(), v_tgt.max())
    if hi - lo < 1e-9:
        return 0.0
    bins = np.linspace(lo, hi, n_bins + 1)
    s = np.clip(np.digitize(v_src, bins) - 1, 0, n_bins - 1)
    t = np.clip(np.digitize(v_tgt, bins) - 1, 0, n_bins - 1)
    n = min(len(s), len(t))
    joint = np.zeros((n_bins, n_bins))
    for i in range(n - 1):
        joint[t[i + 1], s[i]] += 1     # target_future vs source_present
    tot = joint.sum()
    if tot <= 0:
        return 0.0
    joint /= tot
    tm = joint.sum(1)
    sm = joint.sum(0)
    te = 0.0
    for a in range(n_bins):
        for b in range(n_bins):
            if joint[a, b] > 0 and tm[a] > 0 and sm[b] > 0:
                te += joint[a, b] * np.log2(joint[a, b] / (tm[a] * sm[b]))
    return max(te, 0.0)


def te_matrix(speed_by_agent: Dict[int, np.ndarray], agent_ids: List[int]) -> np.ndarray:
    n = len(agent_ids)
    M = np.zeros((n, n))
    for i, ai in enumerate(agent_ids):
        for j, aj in enumerate(agent_ids):
            if i == j:
                continue
            si, sj = speed_by_agent.get(ai), speed_by_agent.get(aj)
            if si is None or sj is None:
                continue
            M[i, j] = transfer_entropy(sj, si)   # j -> i
    return M


# --------------------------------------------------------------------------
# Objective
# --------------------------------------------------------------------------
class Objective:
    def __init__(self, scenarios: List[int] = None, n_replications: int = 1,
                 weights=(1.0, 1.0, 1.0, 2.0), targets=(0.12, 0.08, 2.0, 0.20)):
        # targets normalise each loss so it is ~O(1) at reasonable parameters.
        # The directional-coupling term (index 2) has a structural floor ~2 (sim
        # velocity fields are goal-dominated), so its target is 2.0, not 0.25.
        self.b = Building(str(CODES_DIR / "building_graph.json"))
        self.leader_P = build_leader_P_directional()   # continuous delayed-alignment weights
        self.open_doors = {s: SCENARIOS[s][2] for s in SCENARIOS}
        self.scenarios = scenarios or CALIBRATION_SCENARIOS
        self.n_rep = n_replications
        self.w = weights
        self.tgt = targets
        self.observed_exits = load_observed_exits(TA_RESULTS / "exit_events.csv")
        self._load_observed()

    # ---- observed data ---------------------------------------------------
    def _load_observed(self):
        traj = pickle.load(open(CODES_DIR / "processed_data" / "clean_traj.pkl", "rb"))
        self.obs_speeds: Dict[int, np.ndarray] = {}          # scenario -> pooled speeds
        self.obs_speeds_ab: Dict[int, np.ndarray] = {}       # scenario -> able-bodied speeds
        self.obs_speeds_iwd: Dict[int, np.ndarray] = {}      # scenario -> IWD speeds
        self.obs_dir: Dict[int, np.ndarray] = {}          # scenario -> continuous alignment matrix
        self.obs_dir_agents: Dict[int, List[int]] = {}
        self.obs_exit_times: Dict[int, np.ndarray] = {}
        for s in self.scenarios:
            df = traj[s]
            speed_by_agent, vel_by_agent, pooled = {}, {}, []
            ab_sp, iwd_sp = [], []
            for aid, g in df.groupby("ID"):
                g = g.sort_values("Time")
                sp = g["speed"].values; sp = sp[np.isfinite(sp)]
                if len(sp):
                    speed_by_agent[int(aid)] = sp
                    pooled.extend(sp)
                    (iwd_sp if int(aid) in IWD_IDS else ab_sp).extend(sp)
                    vel_by_agent[int(aid)] = _unit_vel(g["vx"].values, g["vy"].values)
            self.obs_speeds[s] = np.array(pooled)
            self.obs_speeds_ab[s] = np.array(ab_sp)
            self.obs_speeds_iwd[s] = np.array(iwd_sp)
            ids = sorted(speed_by_agent)
            self.obs_dir_agents[s] = ids
            self.obs_dir[s] = directional_leadership_matrix(vel_by_agent, ids)
            # observed exit times from the reader-gate records (all participants)
            f = CODES_DIR / "Exit times" / f"{s}_ExitTime.txt"
            if f.exists():
                d = np.loadtxt(f, delimiter=",")
                d = d.reshape(1, -1) if d.ndim == 1 else d
                t = d[:, 1]
                self.obs_exit_times[s] = t[(t > 0) & (t < 1000) & np.isfinite(t)]
        # observed door-usage distributions (ALL participants, full sample) for ERR
        usage = pd.read_csv(TA_RESULTS / "exit_usage_summary.csv")
        self.obs_door_dist: Dict[int, Dict[str, float]] = {}
        for s, g in usage.groupby("session"):
            counts = {r.exit: float(r.used_count) for r in g.itertuples() if r.used_count > 0}
            tot = sum(counts.values())
            if tot > 0:
                self.obs_door_dist[int(s)] = {d: c / tot for d, c in counts.items()}

    # ---- one scenario ----------------------------------------------------
    def _sim_scenario(self, s: int, params: dict, seed: int):
        sim = Simulation(self.b, params, self.open_doors,
                         rng=np.random.default_rng(seed), leader_P=self.leader_P)
        sim.init_agents(s)
        res = sim.run(record_speed=True)
        agents = {a.id: a for a in sim.agents}
        return sim, res, agents

    # ---- components ------------------------------------------------------
    @staticmethod
    def _quantile_rmse(a: np.ndarray, b: np.ndarray, nq: int = 50) -> float:
        if len(a) < 2 or len(b) < 2:
            return 1.0
        q = np.linspace(0.02, 0.98, nq)
        return float(np.sqrt(np.mean((np.quantile(a, q) - np.quantile(b, q)) ** 2)))

    def evaluate(self, params: dict, seed: int = 0, breakdown: bool = False):
        rmse_list, ks_list, dte_list, err_list = [], [], [], []
        for s in self.scenarios:
            sim_speeds_all, sim_exit_all = [], []
            # Per-scenario directional/ERR terms use one replication (seed); metrics that
            # are distributional (speed, exit time) can pool replications.
            sim, res, agents = self._sim_scenario(s, params, seed + s)
            # E_v: match simulated able-bodied and aggregated-IWD class-mean
            # speed to the reported targets 1.28 and 0.77 m/s.  speed_series
            # excludes the pre-movement phase.
            sim_ab, sim_iwd = [], []
            for aid, ser in res.get("speed_series", {}).items():
                (sim_iwd if aid in IWD_IDS else sim_ab).extend(ser)
            devs = []
            if sim_ab:
                devs.append(abs(float(np.mean(sim_ab)) - AB_MEAN_SPEED))
            if sim_iwd:
                devs.append(abs(float(np.mean(sim_iwd)) - IWD_MEAN_SPEED))
            if devs:
                rmse_list.append(float(np.mean(devs)))
            # KS_exit
            et = np.array(list(res["exit_times"].values()))
            et = et[et > 0]      # drop t=0 door-adjacent starts
            if len(et) >= 3 and len(self.obs_exit_times.get(s, [])) >= 3:
                ks_list.append(float(stats.ks_2samp(et, self.obs_exit_times[s]).statistic))
            # Continuous directional-alignment mismatch: normalized Frobenius
            # distance between observed and simulated correlation-delay matrices.
            ids = self.obs_dir_agents[s]
            sim_vel = {aid: v for aid, v in res.get("vel_series", {}).items() if len(v)}
            sim_unit = {aid: v / np.clip(np.linalg.norm(v, axis=1, keepdims=True), 1e-6, None)
                        for aid, v in sim_vel.items()}
            sim_dir = directional_leadership_matrix(sim_unit, ids)
            denom = np.linalg.norm(self.obs_dir[s]) + 1e-9
            dte_list.append(float(np.linalg.norm(self.obs_dir[s] - sim_dir) / denom))
            # ERR_exit: exit-choice error on controlled calibration scenarios,
            # as the total-variation distance between the SIMULATED and OBSERVED
            # door-usage distributions (observed = full ~40-participant counts,
            # not the sparse RFID-tracked subset). This makes ERR a real, sensitive
            # function of the exit-choice parameters (lambda_door, w_cong, a_D*).
            if s in CONTROLLED_SCENARIOS and s in self.obs_door_dist:
                doors = self.open_doors.get(s, list(self.obs_door_dist[s]))
                n = sum(a.exit_door is not None for a in agents.values())
                if n:
                    sim_p = {d: sum(a.exit_door == d for a in agents.values()) / n for d in doors}
                    obs_p = self.obs_door_dist[s]
                    tv = 0.5 * sum(abs(sim_p.get(d, 0.0) - obs_p.get(d, 0.0)) for d in doors)
                    err_list.append(tv)

        rmse_v = float(np.mean(rmse_list)) if rmse_list else 1.0
        ks_exit = float(np.mean(ks_list)) if ks_list else 1.0
        dte = float(np.mean(dte_list)) if dte_list else 1.0
        err = float(np.mean(err_list)) if err_list else 0.0
        comps = dict(rmse_v=rmse_v, ks_exit=ks_exit, dte=dte, err_exit=err)
        norm = (self.w[0] * rmse_v / self.tgt[0] + self.w[1] * ks_exit / self.tgt[1]
                + self.w[2] * dte / self.tgt[2] + self.w[3] * err / self.tgt[3])
        J = float(norm)
        return (J, comps) if breakdown else J
