"""Tests for the response-spectrum safeguard."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import apply_strong_motion_spectral_safeguard as safeguard


def window(uid: str, policy: str, duration: float) -> dict[str, object]:
    return {
        "record_uid": uid,
        "dataset": "K-NET",
        "priority_group": "m4plus_strong_motion",
        "policy": policy,
        "selected_candidate": policy,
        "window_start_sample": 0,
        "window_end_sample": int(duration * 100),
        "window_duration_sec": duration,
    }


def spectra(uid: str, policy: str, retentions: list[float]) -> list[dict[str, object]]:
    return [
        {
            "record_uid": uid,
            "dataset": "K-NET",
            "priority_group": "m4plus_strong_motion",
            "policy": policy,
            "period_sec": period,
            "full_psa": 2.0,
            "window_psa": 2.0 * retention,
            "psa_retention": retention,
            "spectrum_unstable": retention < 0.95,
            "window_duration_sec": 20.0 if policy == safeguard.PRIMARY_POLICY else 60.0,
        }
        for period, retention in zip([0.2, 1.0, 3.0], retentions)
    ]


class SpectralSafeguardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.selected = pd.DataFrame(
            [
                window("a", safeguard.PRIMARY_POLICY, 20.0),
                window("a", safeguard.ARIAS_POLICY, 60.0),
                window("a", safeguard.FULL_POLICY, 120.0),
                window("b", safeguard.PRIMARY_POLICY, 20.0),
                window("b", safeguard.ARIAS_POLICY, 60.0),
                window("b", safeguard.FULL_POLICY, 120.0),
            ]
        )

    def test_escalates_to_arias_when_primary_psa_fails(self) -> None:
        response = pd.DataFrame(
            spectra("a", safeguard.PRIMARY_POLICY, [1.0, 1.0, 0.8])
            + spectra("a", safeguard.ARIAS_POLICY, [1.0, 1.0, 0.98])
        )

        selected = safeguard.apply_safeguard(self.selected, response, [0.2, 1.0, 3.0])

        row = selected[selected["record_uid"].eq("a")].iloc[0]
        self.assertEqual(row["source_policy"], safeguard.ARIAS_POLICY)
        self.assertEqual(row["spectral_stage"], "arias_escalation")

    def test_escalates_to_full_record_when_both_windows_fail(self) -> None:
        response = pd.DataFrame(
            spectra("b", safeguard.PRIMARY_POLICY, [1.0, 0.8, 0.7])
            + spectra("b", safeguard.ARIAS_POLICY, [1.0, 0.9, 0.8])
        )

        selected = safeguard.apply_safeguard(self.selected, response, [0.2, 1.0, 3.0])

        row = selected[selected["record_uid"].eq("b")].iloc[0]
        self.assertEqual(row["source_policy"], safeguard.FULL_POLICY)
        self.assertEqual(float(row["spectral_min_retention"]), 1.0)

    def test_selected_spectra_uses_arias_rows_and_synthesizes_full_record(self) -> None:
        response = pd.DataFrame(
            spectra("a", safeguard.PRIMARY_POLICY, [1.0, 1.0, 0.8])
            + spectra("a", safeguard.ARIAS_POLICY, [1.0, 1.0, 0.98])
            + spectra("b", safeguard.PRIMARY_POLICY, [1.0, 0.8, 0.7])
            + spectra("b", safeguard.ARIAS_POLICY, [1.0, 0.9, 0.8])
        )
        selected = safeguard.apply_safeguard(self.selected, response, [0.2, 1.0, 3.0])

        out = safeguard.selected_spectra(selected, response, [0.2, 1.0, 3.0], 0.95)

        self.assertEqual(len(out), 6)
        self.assertTrue(out[out["record_uid"].eq("a")]["psa_retention"].ge(0.95).all())
        self.assertTrue(out[out["record_uid"].eq("b")]["psa_retention"].eq(1.0).all())


if __name__ == "__main__":
    unittest.main()
