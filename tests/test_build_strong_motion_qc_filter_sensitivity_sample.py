"""Tests for the frozen filter-sensitivity sample."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts.build_strong_motion_qc_filter_sensitivity_sample import freeze_sample


class FilterSensitivitySampleTests(unittest.TestCase):
    def test_freeze_sample_preserves_reference_membership(self) -> None:
        worklist = pd.DataFrame(
            {
                "record_uid": ["a", "b", "c"],
                "dataset": ["A", "A", "B"],
                "priority_group": ["low", "high", "high"],
            }
        )
        response = pd.DataFrame({"record_uid": ["c", "a", "c"]})

        sample, summary = freeze_sample(worklist, response)

        self.assertEqual(sample["record_uid"].tolist(), ["a", "c"])
        self.assertEqual(int(summary["records"].sum()), 2)


if __name__ == "__main__":
    unittest.main()
