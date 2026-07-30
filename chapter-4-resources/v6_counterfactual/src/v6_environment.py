"""Predeclared V6 environmental-factor semantics.

These helpers define reproducible counterfactual stressors.  They deliberately
do not create a fire, claim a measured lighting layout, change DiSFM physical
parameters, or estimate human compliance.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable


V6 = Path(__file__).resolve().parents[1]
CONTRACT = V6 / "configs" / "v6_environment_factor_contract.json"


def load_contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def smoke_visibility_m(level: str, cue_constant: float | None = None) -> float:
    """Return predeclared cue visibility from the extinction relation S=C/K."""

    contract = load_contract()
    smoke = contract["smoke"]
    levels = smoke["levels"]
    if level not in levels:
        raise ValueError(f"unknown smoke level: {level}")
    constant = float(smoke["cue_constant_C"] if cue_constant is None else cue_constant)
    extinction = float(levels[level]["K_m_inv"])
    return constant / extinction


def unavailable_marker_ids(marker_ids: Iterable[str], emergency_lighting: str, environment_seed: int) -> set[str]:
    """Select paired virtual marker outages without asserting physical fixture locations.

    The input IDs must come from registered route-decision portals. Selection is
    deterministic, independent of uptake C, and has no effect under nominal
    lighting.  For an odd marker count, floor(n/2) is the closest lower exact
    fraction, as fixed in the contract.
    """

    markers = sorted(set(marker_ids))
    if emergency_lighting == "nominal":
        return set()
    if emergency_lighting != "outage_50pct":
        raise ValueError(f"unknown emergency lighting condition: {emergency_lighting}")
    generator = random.Random(int(environment_seed))
    generator.shuffle(markers)
    return set(markers[: len(markers) // 2])


def marker_is_available(marker_id: str, marker_ids: Iterable[str], emergency_lighting: str, environment_seed: int) -> bool:
    return marker_id not in unavailable_marker_ids(marker_ids, emergency_lighting, environment_seed)
