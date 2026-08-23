# StrongMotion-QC Response-Spectrum Retention

This audit compares 5%-damped pseudo-spectral acceleration computed inside selected processing windows with the same product computed on the full record.

Periods: 0.2 s, 1 s, 3 s.

Each oscillator response is continued for 5 zero-input cycles after the waveform ends so that a window boundary does not truncate free vibration.

The result is a relative retention audit. It strengthens the product-window claim because response spectra are closer to strong-motion engineering products than PGA and waveform energy alone.

## Summary

| dataset | priority_group | policy | period_sec | records | spectrum_unstable_records | spectrum_unstable_pct | median_psa_retention | p05_psa_retention | p01_psa_retention | median_window_duration_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| InstanceGM | ALL | arias_1_99_padded | 0.200 | 900 | 4 | 0.444 | 1.000 | 1.000 | 1.000 | 104.650 |
| InstanceGM | ALL | arias_1_99_padded | 1.000 | 900 | 9 | 1.000 | 1.000 | 1.000 | 0.998 | 104.650 |
| InstanceGM | ALL | arias_1_99_padded | 3.000 | 900 | 58 | 6.444 | 1.000 | 0.918 | 0.607 | 104.650 |
| InstanceGM | ALL | feature_onset_fixed | 0.200 | 900 | 212 | 23.556 | 1.000 | 0.317 | 0.002 | 42.000 |
| InstanceGM | ALL | feature_onset_fixed | 1.000 | 900 | 413 | 45.889 | 0.998 | 0.208 | 0.015 | 42.000 |
| InstanceGM | ALL | feature_onset_fixed | 3.000 | 900 | 573 | 63.667 | 0.802 | 0.194 | 0.055 | 42.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 0.200 | 900 | 2 | 0.222 | 1.000 | 1.000 | 1.000 | 62.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 1.000 | 900 | 64 | 7.111 | 1.000 | 0.888 | 0.729 | 62.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 3.000 | 900 | 241 | 26.778 | 0.998 | 0.658 | 0.410 | 62.000 |
| K-NET | ALL | arias_1_99_padded | 0.200 | 621 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 53.480 |
| K-NET | ALL | arias_1_99_padded | 1.000 | 621 | 22 | 3.543 | 1.000 | 1.000 | 0.553 | 53.480 |
| K-NET | ALL | arias_1_99_padded | 3.000 | 621 | 280 | 45.089 | 0.998 | 0.216 | 0.115 | 53.480 |
| K-NET | ALL | feature_onset_fixed | 0.200 | 621 | 1 | 0.161 | 1.000 | 1.000 | 1.000 | 42.000 |
| K-NET | ALL | feature_onset_fixed | 1.000 | 621 | 47 | 7.568 | 1.000 | 0.802 | 0.425 | 42.000 |
| K-NET | ALL | feature_onset_fixed | 3.000 | 621 | 378 | 60.870 | 0.816 | 0.132 | 0.073 | 42.000 |
| K-NET | ALL | shortest_stable_no_catalog | 0.200 | 621 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 22.000 |
| K-NET | ALL | shortest_stable_no_catalog | 1.000 | 621 | 62 | 9.984 | 1.000 | 0.822 | 0.425 | 22.000 |
| K-NET | ALL | shortest_stable_no_catalog | 3.000 | 621 | 360 | 57.971 | 0.859 | 0.128 | 0.066 | 22.000 |
| ALL | ALL | arias_1_99_padded | 0.200 | 1521 | 4 | 0.263 | 1.000 | 1.000 | 1.000 | 65.880 |
| ALL | ALL | arias_1_99_padded | 1.000 | 1521 | 31 | 2.038 | 1.000 | 1.000 | 0.694 | 65.880 |
| ALL | ALL | arias_1_99_padded | 3.000 | 1521 | 338 | 22.222 | 1.000 | 0.323 | 0.163 | 65.880 |
| ALL | ALL | feature_onset_fixed | 0.200 | 1521 | 213 | 14.004 | 1.000 | 0.472 | 0.018 | 42.000 |
| ALL | ALL | feature_onset_fixed | 1.000 | 1521 | 460 | 30.243 | 1.000 | 0.318 | 0.060 | 42.000 |
| ALL | ALL | feature_onset_fixed | 3.000 | 1521 | 951 | 62.525 | 0.806 | 0.158 | 0.070 | 42.000 |
| ALL | ALL | shortest_stable_no_catalog | 0.200 | 1521 | 2 | 0.131 | 1.000 | 1.000 | 1.000 | 36.430 |
| ALL | ALL | shortest_stable_no_catalog | 1.000 | 1521 | 126 | 8.284 | 1.000 | 0.861 | 0.535 | 36.430 |
| ALL | ALL | shortest_stable_no_catalog | 3.000 | 1521 | 601 | 39.513 | 0.989 | 0.233 | 0.096 | 36.430 |

## Outputs

- `response_spectrum_retention.csv`: per-record, per-policy, per-period response-spectrum retention.
- `summary.csv`: grouped spectrum-retention summary.

## Boundary

The current calculation reports relative pseudo-spectral acceleration retention. It does not establish absolute site-specific design spectra.
