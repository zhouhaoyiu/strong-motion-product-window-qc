"""Tests for result-blind PNW SNR stratification."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from scripts import audit_pnw_strong_motion_snr as audit


class PnwSnrAuditTests(unittest.TestCase):
    def test_record_snr_separates_signal_from_noise(self) -> None:
        rng = np.random.default_rng(4)
        waveform = rng.normal(0.0, 0.1, size=(3, 10000))
        waveform[:, 4000:7000] += rng.normal(0.0, 1.0, size=(3, 3000))

        out = audit.record_snr(waveform, 100.0, p_sec=40.0, s_sec=45.0)

        self.assertGreater(out["snr_db"], 10.0)

    def test_summary_preserves_full_denominator_bins(self) -> None:
        frame = pd.DataFrame(
            {
                "snr_bin": pd.Categorical(["<3 dB", ">=10 dB"], categories=["<3 dB", "3-10 dB", ">=10 dB"]),
                "magnitude": [2.0, 4.0],
                "snr_db": [1.0, 12.0],
                "feature_fixed_unstable": [True, False],
                "full_record_assignment": [True, False],
                "selected_duration_sec": [150.0, 60.0],
                "selected_3s_psa_failure": [True, False],
                "spectral_stage": ["full_record_fallback", "primary"],
                "final_duration_sec": [150.0, 60.0],
            }
        )

        summary = audit.summarize(frame)

        self.assertEqual(int(summary["records"].sum()), 2)
        self.assertEqual(set(summary["snr_bin"]), {"<3 dB", ">=10 dB"})
        low = summary[summary["snr_bin"].eq("<3 dB")].iloc[0]
        self.assertEqual(float(low["spectral_full_record_fallback_pct"]), 100.0)


if __name__ == "__main__":
    unittest.main()
