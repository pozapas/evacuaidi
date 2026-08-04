# Provenance of `calibrated_parameters.csv`

These are the parameters of the selected A1 DiSFM configuration reported in the
manuscript.

- Family: `A1_disfm` (two mobility classes, directional attraction inactive)
- Optimizer seed: 7 of 8
- Selection rule: minimum training objective over the eight optimizer seeds,
  evaluated on the 13-scenario calibration split only
- Training objective at the optimum: 6.067754
- Budget: 30 CMA-ES generations, population 12, initial step size 0.3
- Calibration split: 13 scenarios; scenarios 5, 9 and 11 are held out and enter
  no loss term

`beta_leader` is listed as inactive because the directional-attraction term is
enabled only in the A2 family; it is zero in every A1 optimizer seed.

The across-seed ranges of these parameters, over all eight optimizer seeds, are
reported in the manuscript alongside the selected values.
