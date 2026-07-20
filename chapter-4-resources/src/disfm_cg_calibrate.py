"""
DiSFM-GS calibration driver.
=================================================================
CMA-ES calibration under a strict 13/3 split, with A frozen at 2000 N.

Optimization coordinates (15):
    v0_amb, tau_amb, B_amb, v0_mob, tau_mob, B_mob,
    beta_leader, lambda_door, w_cong, k_AI, a_D2, a_D3, a_D4,
    t_premove, phi_unfam
Held / from priors (not in the search vector):
    A_amb = A_mob = 2000 N  (frozen; data uninformative)
    alpha_c, beta_c         (fixed structural response settings)
    dt = 0.05, max_time     (integration settings)

The archived calibration supplies no route recommendation distinct from the
sampled self-route.  Therefore the formal ``k_AI`` coordinate has zero force
and is non-identifiable in its reported outputs; it is retained here only to
reproduce the archived code configuration.  Population candidates are
evaluated in parallel (joblib).  Every generation logs the full loss
decomposition; checkpoints occur every 10 generations.
"""
from __future__ import annotations
import argparse
import pickle
import time
from pathlib import Path

import numpy as np

from disfm_cg_core import CODES_DIR
from disfm_cg_loss import Objective

# name, lower, upper, x0 (literature prior)
PARAM_SPACE = [
    ("v0_amb",      1.0,  2.0,  1.34),   # DESIRED (free) speed; may exceed observed mean 1.28 (orig calib v0_ab=1.64)
    ("tau_amb",     0.2,  0.8,  0.50),
    ("B_amb",       0.05, 0.15, 0.08),
    ("v0_mob",      0.5,  1.1,  0.77),   # IWD desired speed; stays below AB (disability-slower); low bound 0.5 prevents crawl
    ("tau_mob",     0.4,  1.2,  0.70),
    ("B_mob",       0.08, 0.20, 0.10),
    ("beta_leader", 0.1,  5.0,  1.60),  # continuous directional-alignment strength
    ("lambda_door", 2.0,  20.0, 8.00),
    ("w_cong",      0.0,  3.0,  0.50),
    ("k_AI",        0.5,  10.0, 2.19),  # formal zero-force coordinate in archived calibration
    ("a_D2",       -2.0,  4.0,  0.00),   # per-door attractiveness (D1 = reference 0)
    ("a_D3",       -2.0,  4.0,  0.00),
    ("a_D4",       -2.0,  4.0,  0.00),
    ("t_premove",   0.0,  35.0, 12.00),  # mean pre-movement/reaction time (s), SFPE educational
    ("phi_unfam",   0.3,  1.0,  0.60),   # familiarity speed factor on unfamiliar exits D3/D4 (1=no effect)
]
FIXED = dict(A_amb=2000.0, A_mob=2000.0, alpha_c=5.0, beta_c=0.0,
             dt=0.05, max_time=250.0)

# Ablation ladder (M0-M4). Each entry sets the model toggles; disabled
# mechanisms have their parameter pinned so CMA-ES does not search an inactive
# term.  The formal guidance toggle has zero force under the archived
# self-route calibration.  use_familiarity is the unfamiliar-exit (D3/D4)
# tentative-speed effect, active for M1+ and off for the plain-SFM baseline.
ABLATIONS = {
    "M4_full":     dict(single_class=False, use_leader=True,  use_guidance=True,  use_familiarity=True),
    "M0_sfm":      dict(single_class=True,  use_leader=False, use_guidance=False, use_familiarity=False),
    "M1_kinematic":dict(single_class=False, use_leader=False, use_guidance=False, use_familiarity=True),
    "M2_leader":   dict(single_class=False, use_leader=True,  use_guidance=False, use_familiarity=True),
    "M3_guidance": dict(single_class=False, use_leader=False, use_guidance=True,  use_familiarity=True),
}


def vec_to_params(x, ablation: str = "M4_full") -> dict:
    p = dict(FIXED)
    p.update(ABLATIONS.get(ablation, ABLATIONS["M4_full"]))
    for (name, lo, hi, _), val in zip(PARAM_SPACE, x):
        p[name] = float(np.clip(val, lo, hi))
    if not p["use_leader"]:
        p["beta_leader"] = 0.0
    if not p["use_guidance"]:
        p["k_AI"] = 0.0
    if not p.get("use_familiarity", True):
        p["phi_unfam"] = 1.0
    return p


_WORKER_OBJ = None


def calibrate(max_gen=100, popsize=None, seed=0, n_jobs=1, tag="main",
              ablation="M4_full", sigma0=0.3, early_stop_tol=1e-3, early_stop_patience=10):
    import cma
    from joblib import Parallel, delayed

    x0 = [p[3] for p in PARAM_SPACE]
    bounds = [[p[1] for p in PARAM_SPACE], [p[2] for p in PARAM_SPACE]]
    # scale to unit-ish box for CMA-ES stability
    es = cma.CMAEvolutionStrategy(x0, sigma0, {
        "bounds": bounds, "popsize": popsize, "seed": seed + 1, "verbose": -9,
    })
    obj_main = Objective()             # single-process evaluator
    scenarios = obj_main.scenarios
    log_rows = []
    best_J, best_x, stall = np.inf, None, 0
    t0 = time.time()
    gen = 0
    while not es.stop() and gen < max_gen:
        X = es.ask()
        # each eval returns (J, components); no wasteful re-eval for logging
        if n_jobs == 1:
            results = [obj_main.evaluate(vec_to_params(x, ablation), seed=seed, breakdown=True) for x in X]
        else:
            results = Parallel(n_jobs=n_jobs, backend="loky")(
                delayed(_ev)(x, scenarios, seed, ablation) for x in X)
        fits = [r[0] for r in results]
        es.tell(X, fits)
        gen += 1
        i_best = int(np.argmin(fits))
        gbest = fits[i_best]
        if gbest < best_J - early_stop_tol:
            best_J, best_x, stall = gbest, X[i_best], 0
        else:
            stall += 1
        comps = results[i_best][1]
        row = dict(gen=gen, J=float(es.result.fbest), **comps,
                   elapsed_min=(time.time() - t0) / 60)
        log_rows.append(row)
        print(f"gen {gen:3d} | J={es.result.fbest:.3f} | "
              f"RMSE_v={comps['rmse_v']:.3f} KS={comps['ks_exit']:.3f} "
              f"dTE={comps['dte']:.3f} ERR={comps['err_exit']:.3f} | "
              f"{row['elapsed_min']:.1f} min", flush=True)
        if gen % 10 == 0:
            _save(tag, es, log_rows, gen, ablation=ablation)
        if stall >= early_stop_patience:
            print(f"early stop: no improvement in {early_stop_patience} gens")
            break
    _save(tag, es, log_rows, gen, ablation=ablation, final=True)
    return es, log_rows


def _ev(x, scenarios, seed, ablation="M4_full"):
    """Worker: build the Objective once per process, return (J, components)."""
    global _WORKER_OBJ
    if _WORKER_OBJ is None:
        _WORKER_OBJ = Objective(scenarios=scenarios)
    return _WORKER_OBJ.evaluate(vec_to_params(x, ablation), seed=seed, breakdown=True)


def _save(tag, es, log_rows, gen, ablation="M4_full", final=False):
    import pandas as pd
    out = CODES_DIR / "calib_out"
    out.mkdir(exist_ok=True)
    xbest = es.result.xbest
    params = vec_to_params(xbest, ablation)
    suffix = "final" if final else f"gen{gen}"
    with open(out / f"theta_{tag}_{suffix}.pkl", "wb") as f:
        pickle.dump({"params": params, "xbest": xbest, "fbest": float(es.result.fbest),
                     "ablation": ablation, "generations": gen,
                     "cma_C": es.C.tolist() if hasattr(es, "C") else None,
                     "param_names": [p[0] for p in PARAM_SPACE]}, f)
    pd.DataFrame(log_rows).to_csv(out / f"calib_log_{tag}.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=100)
    ap.add_argument("--pop", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--tag", type=str, default="main")
    ap.add_argument("--ablation", type=str, default="M4_full", choices=list(ABLATIONS))
    ap.add_argument("--patience", type=int, default=10)   # early-stop patience; high => run to CMA-ES natural convergence
    args = ap.parse_args()
    calibrate(max_gen=args.gens, popsize=args.pop, seed=args.seed,
              n_jobs=args.jobs, tag=args.tag, ablation=args.ablation,
              early_stop_patience=args.patience)
