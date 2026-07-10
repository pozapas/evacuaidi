# DiSFM-GS: Disability-Inclusive Social Force Model with a Guidance Switch

Model code, calibration protocol, configuration, and derived results for the
paper *"Experimental analysis and disability-inclusive social force modeling of
heterogeneous crowd evacuation with probabilistic guidance compliance"*
(Physica A, PHYSA-261820).

The model extends the social force model with class-specific kinematics for
able-bodied occupants and individuals with disabilities, a data-driven
directional leader-follower force, a probabilistic guidance-compliance switch,
and an exit-familiarity factor. Parameters are calibrated with a covariance
matrix adaptation evolution strategy (CMA-ES) under a strict split of thirteen
calibration scenarios and three hold-out scenarios.

## Repository layout

```
parameters_DiSFM_CG.yml  literature-based parameter priors, bounds, and sources
building_graph.json      building navigation graph (nodes, corridor edges, exit positions)
src/
  disfm_cg_core.py       simulation core (building graph, agents, forces, directional estimator)
  disfm_cg_loss.py       four-term calibration objective (RMSE_v, KS_exit, directional, ERR_exit)
  disfm_cg_calibrate.py  CMA-ES driver, strict 13/3 split, M0-M4 ablation ladder
results/
  calibrated_parameters.csv  headline calibrated parameters (Table 5)
  ablation.csv               M0-M4 objective values (mean and seed range)
  holdout_validation.csv     hold-out Kolmogorov-Smirnov distances vs the small-sample critical value
  calibration_log_seed1.csv  per-generation objective and component decomposition (seed 1)
```

## Reproducing the calibration

```bash
python src/disfm_cg_calibrate.py --gens 100 --seed 1 --jobs 8 --ablation M4_full
```

Free parameters (15): the class-specific desired speeds, relaxation times, and
interaction ranges; the leader and guidance strengths; the exit-choice
parameters; the pre-movement time; and the familiarity factor. The two repulsion
strengths are frozen at 2000 N and the two compliance-curve shape parameters are
fixed from priors.

## Data availability

The raw radio-frequency identification (RFID) trajectories were collected from
human participants under an approved protocol with privacy restrictions and are
**not** redistributed here. The scripts read the trajectory and exit-time inputs
from local paths (`processed_data/`, `trajectory_analysis/results/`,
`Exit times/`). The de-identified derived quantities needed to inspect the
reported results are provided in `results/`. The underlying data may be made
available by the authors on reasonable request, subject to the data owner's
approval.

## Requirements

Python 3.10+ with `numpy`, `scipy`, `pandas`, `networkx`, `cma`, and `joblib`.

## Citation

Rafe, A., Singleton, P. A., and Christensen, K. M. Experimental analysis and
disability-inclusive social force modeling of heterogeneous crowd evacuation
with probabilistic guidance compliance. *Physica A: Statistical Mechanics and
its Applications* (under review).
