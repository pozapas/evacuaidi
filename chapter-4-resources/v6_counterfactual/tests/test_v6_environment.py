"""Tests for the V6 predeclared environmental-factor semantics."""

from __future__ import annotations

import unittest

from src.v6_environment import marker_is_available, smoke_visibility_m, unavailable_marker_ids


class V6EnvironmentTests(unittest.TestCase):
    def test_smoke_visibility_uses_the_locked_extinction_relation(self):
        self.assertEqual(smoke_visibility_m("low"), 60.0)
        self.assertEqual(smoke_visibility_m("medium"), 20.0)
        self.assertEqual(smoke_visibility_m("high"), 5.0)
        self.assertEqual(smoke_visibility_m("medium", cue_constant=8.0), 8.0 / 0.15)

    def test_marker_outage_is_paired_and_exact_for_even_marker_count(self):
        markers = ["P4", "P1", "P3", "P2"]
        first = unavailable_marker_ids(markers, "outage_50pct", 117)
        second = unavailable_marker_ids(reversed(markers), "outage_50pct", 117)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 2)
        self.assertEqual(unavailable_marker_ids(markers, "nominal", 117), set())
        self.assertTrue(marker_is_available("P1", markers, "nominal", 117))
        self.assertEqual(marker_is_available("P1", markers, "outage_50pct", 117), "P1" not in first)

    def test_invalid_conditions_are_rejected(self):
        with self.assertRaises(ValueError):
            smoke_visibility_m("unknown")
        with self.assertRaises(ValueError):
            unavailable_marker_ids(["P1"], "failure", 1)


if __name__ == "__main__":
    unittest.main()
