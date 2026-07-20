# DiSFM-GS: Disability-Aware Social Force Model with a Formal Guidance-Response Extension

Code, calibration configuration, and derived results supporting the revised
manuscript *Experimental analysis and disability-aware social force modeling
of heterogeneous crowd evacuation with probabilistic guidance response*
(Physica A, PHYSA-261820).

## What the reported calculation does

The reported model combines:

- class-specific kinematic and interpersonal-interaction parameters for
  able-bodied occupants and the aggregated IWD class;
- graph-based routing to scenario-available exits in the building coordinate
  frame;
- continuous delayed directional-alignment weights derived from velocity
  direction correlation; and
- an exit-familiarity factor.

The empirical calibration uses a strict split of 13 calibration scenarios and
three untouched hold-out scenarios (5, 9, and 11).  Its four normalized loss
components are the mean absolute class-speed error, exit-time KS distance,
continuous directional-alignment discrepancy, and aggregate door-usage
total-variation distance.

## Important implementation scope

This repository deliberately distinguishes the reported calculation from
future extensions that require new data or validation.

- **Geometry:** `building_graph.json` supplies the navigation graph and exit
  locations.  The force implementation uses a soft, four-side outer-domain
  boundary to keep agents inside the simulation domain.  It does **not**
  implement force-resolved interior CAD walls, door openings, furnishings, or
  other obstacles.
- **Directional alignment:** the active code computes continuous lagged
  velocity-direction correlations and uses normalized positive-lag weights in
  a structural attraction term.  These are not an FDR-screened pair network
  and do not establish individual leader identities or social causation.
- **Guidance response:** the source contains a formal route-recommendation
  equation for a future scenario-level marshal/AI policy study.  In the
  reported calibration no independently specified `guidance_doors` mapping is
  supplied; the guided door defaults to the sampled self-route.  Thus the two
  direction vectors coincide, the reported guidance force is zero, and the
  optimizer coordinate `k_AI` is not an empirical estimate of response,
  compliance, or guidance benefit.
- **Controlled scenarios:** runs 4, 11, and 15 are recorded as
  scenario-level controlled conditions with specified available doors.  The
  public inputs do not contain participant-level directive, receipt, or
  response records.  The results must not be read as a causal evaluation of
  marshal or AI guidance.

## Repository layout

```text
parameters_DiSFM_CG.yml    legacy prior archive; not the active calibration configuration
building_graph.json        navigation graph and exit positions
src/
  disfm_cg_core.py         simulation core, routing, forces, alignment weights
  disfm_cg_loss.py         normalized calibration objective and strict split
  disfm_cg_calibrate.py    CMA-ES driver and M0--M4 code configurations
results/
  calibrated_parameters.csv  archived optimization output (including non-identified k_AI)
  ablation.csv               archived M0--M4 objective values
  holdout_validation.csv     archived hold-out KS distances
  calibration_log_seed1.csv  per-generation loss decomposition
```

## Reproduction status

The command below is the archived calibration entry point.  It requires the
privacy-restricted local RFID-derived inputs described below.  This
documentation-only V4 release does **not** claim that the calibration was
newly rerun or that it reproduces new numerical outputs.

```bash
python src/disfm_cg_calibrate.py --gens 100 --seed 1 --jobs 8 --ablation M4_full
```

## Data availability

The raw radio-frequency-identification trajectories were collected from human
participants under an approved protocol and are not redistributed here.  The
scripts expect local trajectory and exit-time inputs in the project layout.
De-identified derived results needed to inspect the archived reported outputs
are provided in `results/`.  Further data may be available on reasonable
request, subject to the data owner's approval.

## Requirements

Python 3.10+ with `numpy`, `scipy`, `pandas`, `networkx`, `cma`, and `joblib`.

## Citation

Rafe, A., Singleton, P. A., and Christensen, K. M. Experimental analysis and
disability-aware social force modeling of heterogeneous crowd evacuation with
probabilistic guidance response. *Physica A: Statistical Mechanics and its
Applications* (revision in preparation).
