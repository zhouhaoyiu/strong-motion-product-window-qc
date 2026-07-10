# StrongMotion-QC Response-Spectrum Retention

This audit compares 5%-damped pseudo-spectral acceleration computed inside selected processing windows with the same product computed on the full record.

Periods: 0.2 s, 1 s, 3 s.

Each oscillator response is continued for 5 zero-input cycles after the waveform ends so that a window boundary does not truncate free vibration.

The result is a relative retention audit. It strengthens the product-window claim because response spectra are closer to strong-motion engineering products than PGA and waveform energy alone.

## Summary

| dataset | priority_group | policy | period_sec | records | spectrum_unstable_records | spectrum_unstable_pct | median_psa_retention | p05_psa_retention | p01_psa_retention | median_window_duration_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| InstanceGM | ALL | arias_1_99_padded | 0.200 | 900 | 4 | 0.444 | 1.000 | 1.000 | 1.000 | 104.915 |
| InstanceGM | ALL | arias_1_99_padded | 1.000 | 900 | 7 | 0.778 | 1.000 | 1.000 | 0.999 | 104.915 |
| InstanceGM | ALL | arias_1_99_padded | 3.000 | 900 | 51 | 5.667 | 1.000 | 0.918 | 0.596 | 104.915 |
| InstanceGM | ALL | feature_onset_fixed | 0.200 | 900 | 213 | 23.667 | 1.000 | 0.312 | 0.002 | 42.000 |
| InstanceGM | ALL | feature_onset_fixed | 1.000 | 900 | 424 | 47.111 | 0.991 | 0.207 | 0.015 | 42.000 |
| InstanceGM | ALL | feature_onset_fixed | 3.000 | 900 | 570 | 63.333 | 0.790 | 0.201 | 0.053 | 42.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 0.200 | 900 | 2 | 0.222 | 1.000 | 1.000 | 1.000 | 62.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 1.000 | 900 | 64 | 7.111 | 1.000 | 0.893 | 0.751 | 62.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 3.000 | 900 | 227 | 25.222 | 0.998 | 0.656 | 0.409 | 62.000 |
| K-NET | ALL | arias_1_99_padded | 0.200 | 621 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 53.670 |
| K-NET | ALL | arias_1_99_padded | 1.000 | 621 | 24 | 3.865 | 1.000 | 1.000 | 0.479 | 53.670 |
| K-NET | ALL | arias_1_99_padded | 3.000 | 621 | 312 | 50.242 | 0.949 | 0.199 | 0.104 | 53.670 |
| K-NET | ALL | feature_onset_fixed | 0.200 | 621 | 1 | 0.161 | 1.000 | 1.000 | 1.000 | 42.000 |
| K-NET | ALL | feature_onset_fixed | 1.000 | 621 | 52 | 8.374 | 1.000 | 0.755 | 0.379 | 42.000 |
| K-NET | ALL | feature_onset_fixed | 3.000 | 621 | 403 | 64.895 | 0.679 | 0.153 | 0.075 | 42.000 |
| K-NET | ALL | shortest_stable_no_catalog | 0.200 | 621 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 22.000 |
| K-NET | ALL | shortest_stable_no_catalog | 1.000 | 621 | 67 | 10.789 | 1.000 | 0.755 | 0.379 | 22.000 |
| K-NET | ALL | shortest_stable_no_catalog | 3.000 | 621 | 386 | 62.158 | 0.738 | 0.116 | 0.057 | 22.000 |
| ALL | ALL | arias_1_99_padded | 0.200 | 1521 | 4 | 0.263 | 1.000 | 1.000 | 1.000 | 66.000 |
| ALL | ALL | arias_1_99_padded | 1.000 | 1521 | 31 | 2.038 | 1.000 | 1.000 | 0.649 | 66.000 |
| ALL | ALL | arias_1_99_padded | 3.000 | 1521 | 363 | 23.866 | 1.000 | 0.309 | 0.147 | 66.000 |
| ALL | ALL | feature_onset_fixed | 0.200 | 1521 | 214 | 14.070 | 1.000 | 0.464 | 0.018 | 42.000 |
| ALL | ALL | feature_onset_fixed | 1.000 | 1521 | 476 | 31.295 | 1.000 | 0.302 | 0.073 | 42.000 |
| ALL | ALL | feature_onset_fixed | 3.000 | 1521 | 973 | 63.971 | 0.763 | 0.170 | 0.069 | 42.000 |
| ALL | ALL | shortest_stable_no_catalog | 0.200 | 1521 | 2 | 0.131 | 1.000 | 1.000 | 1.000 | 36.890 |
| ALL | ALL | shortest_stable_no_catalog | 1.000 | 1521 | 131 | 8.613 | 1.000 | 0.852 | 0.476 | 36.890 |
| ALL | ALL | shortest_stable_no_catalog | 3.000 | 1521 | 613 | 40.302 | 0.988 | 0.211 | 0.090 | 36.890 |

## Outputs

- `response_spectrum_retention.csv`: per-record, per-policy, per-period response-spectrum retention.
- `summary.csv`: grouped spectrum-retention summary.

## Boundary

The current calculation reports relative pseudo-spectral acceleration retention. It does not establish absolute site-specific design spectra.
