# Chapter 4 reproducibility materials

This directory contains the non-sensitive code, configurations, derived inputs, and summarized outputs supporting the V6 revision of the associated Physica A manuscript on disability-inclusive evacuation modeling and counterfactual route guidance.

The current release is `v6_counterfactual/`. It provides the locked two-class physical DiSFM core, the accessibility-aware route-planner implementation, the paired 100-scenario route-guidance screen, and the data used to prepare the reported aggregate outcomes. The planner changes an agent's selected route target; it does not estimate observed individual compliance.

```text
v6_counterfactual/
  configs/          locked A1 parameter snapshot and scenario specifications
  inputs/           non-sensitive topology, occupancy allocation, and scenarios
  legacy_core/      locked physical DiSFM implementation
  src/              route-planning and multi-floor simulation adapters
  scripts/          runner and result-summary scripts
  results_summary/  reported paired 100-scenario aggregate output
  tests/            unit tests for route-target and environmental-factor logic
manuscript/
  manuscript_v6_clean.pdf
```

Earlier files at this level are retained as an archived prior package. Use `v6_counterfactual/` for the current implementation and accompanying results.

## Data scope

The repository does not include raw RFID trajectories, original building drawings, or run-level agent records. Those materials remain restricted under the human-participant protocol. The released inputs and summaries are non-sensitive derived materials sufficient to inspect the reported model configuration, scenario design, target-allocation logic, and aggregate results.

## Citation

Rafe, A., Singleton, P. A., and Christensen, K. M. Disability-inclusive social force modeling of heterogeneous evacuation with counterfactual route guidance. *Physica A: Statistical Mechanics and its Applications* (revision in preparation).
