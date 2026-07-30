# V6 counterfactual route-guidance release

This release contains the non-sensitive materials for the V6 full-building counterfactual route-guidance analysis. It couples the locked, calibrated two-class DiSFM physical core with an accessibility-aware route planner. For a declared uptake condition `C`, the planner can replace an agent's baseline route target with a capacity-aware recommended target; the selected target then persists through the simulation.

The release supports inspection and re-execution of the reported paired 100-scenario by five-uptake screen. It is a building-specific counterfactual application, not an estimate of observed individual response, marshal performance, or causal guidance efficacy.

## Contents

```text
configs/          A1 parameter snapshot and fixed scenario specifications
inputs/           non-sensitive map-derived topology, room allocation, and scenarios
legacy_core/      locked calibrated DiSFM physical-core implementation
src/              route-target, environment, spatial, and multi-floor components
scripts/          single-scenario runner, ensemble runner, and summarization tools
results_summary/  reported 100-scenario aggregate output
tests/            unit tests for target replacement and environmental-factor logic
```

The raw RFID trajectories, original building drawings, and raw agent-level run outputs are excluded. They are not required to inspect the public aggregate screen, but the protected trajectory data are required to repeat the original physical calibration.

## Run

Use Python 3.12 or later and install the listed dependencies:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/run_v6_evacuation_map_scenario_ensemble.py --workers 4
python scripts/summarize_v6_evacuation_map_scenario_ensemble.py
```

The full ensemble command can take substantial time. It creates local `results_raw/` files, which are intentionally ignored by version control.

## Interpretation

The supplied CSV records the 500 paired scenario-by-uptake outcomes used for the V6 route-guidance analysis. Within a scenario, initial placement, movement, uptake-uniform, and planner tie-break streams are shared across uptake levels. The screen uses one locked A1 parameter configuration and one replication per scenario; its results should therefore be interpreted as a declared counterfactual application rather than a multi-parameter validation ensemble.
