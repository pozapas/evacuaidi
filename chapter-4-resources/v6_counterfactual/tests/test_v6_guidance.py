import unittest

from src.v6_guidance import (
    persistent_uptake_gate,
    static_capacity_aware_targets,
    target_replacement_decisions,
)


class TargetReplacementTests(unittest.TestCase):
    def setUp(self):
        self.uniforms = {1: 0.05, 2: 0.25, 3: 0.65}
        self.baseline = {1: "D1", 2: "D1", 3: "D2"}
        self.recommended = {1: "D2", 2: "D2", 3: "D2"}

    def test_gate_is_nested(self):
        low = persistent_uptake_gate(self.uniforms, 0.3)
        high = persistent_uptake_gate(self.uniforms, 0.7)
        self.assertTrue(all(not low[key] or high[key] for key in self.uniforms))

    def test_zero_uptake_reduces_to_baseline(self):
        decisions = target_replacement_decisions(self.baseline, self.recommended, self.uniforms, 0.0)
        self.assertEqual({item.agent_id: item.realized_target for item in decisions}, self.baseline)
        self.assertTrue(all(not item.uptake_gate for item in decisions))

    def test_accessibility_restriction_is_respected(self):
        agents = [
            {"agent_id": 1, "free_speed_mps": 1.0, "permitted_exits": ["D1", "D2"], "graph_distance_m": {"D1": 10, "D2": 11}},
            {"agent_id": 2, "free_speed_mps": 1.0, "permitted_exits": ["D1"], "graph_distance_m": {"D1": 10, "D2": 1}},
        ]
        baseline, recommended = static_capacity_aware_targets(agents, ["D1", "D2"], {"D1": 1.0, "D2": 1.0})
        self.assertEqual(baseline[2], "D1")
        self.assertEqual(recommended[2], "D1")


if __name__ == "__main__":
    unittest.main()
