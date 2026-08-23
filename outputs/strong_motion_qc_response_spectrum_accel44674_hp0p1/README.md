# StrongMotion-QC Response-Spectrum Retention

This audit compares 5%-damped pseudo-spectral acceleration computed inside selected processing windows with the same product computed on the full record.

Periods: 0.2 s, 1 s, 3 s.

Each oscillator response is continued for 5 zero-input cycles after the waveform ends so that a window boundary does not truncate free vibration.

The result is a relative retention audit. It strengthens the product-window claim because response spectra are closer to strong-motion engineering products than PGA and waveform energy alone.

## Summary

| dataset | priority_group | policy | period_sec | records | spectrum_unstable_records | spectrum_unstable_pct | median_psa_retention | p05_psa_retention | p01_psa_retention | median_window_duration_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| InstanceGM | ALL | arias_1_99_padded | 0.200 | 23533 | 85 | 0.361 | 1.000 | 1.000 | 1.000 | 107.540 |
| InstanceGM | ALL | arias_1_99_padded | 1.000 | 23533 | 241 | 1.024 | 1.000 | 1.000 | 0.947 | 107.540 |
| InstanceGM | ALL | arias_1_99_padded | 3.000 | 23533 | 1431 | 6.081 | 1.000 | 0.913 | 0.621 | 107.540 |
| InstanceGM | ALL | feature_onset_fixed | 0.200 | 23533 | 5259 | 22.347 | 1.000 | 0.376 | 0.025 | 42.000 |
| InstanceGM | ALL | feature_onset_fixed | 1.000 | 23533 | 10872 | 46.199 | 0.992 | 0.235 | 0.046 | 42.000 |
| InstanceGM | ALL | feature_onset_fixed | 3.000 | 23533 | 15182 | 64.514 | 0.808 | 0.234 | 0.066 | 42.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 0.200 | 23533 | 49 | 0.208 | 1.000 | 1.000 | 1.000 | 62.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 1.000 | 23533 | 1884 | 8.006 | 1.000 | 0.882 | 0.678 | 62.000 |
| InstanceGM | ALL | shortest_stable_no_catalog | 3.000 | 23533 | 6374 | 27.085 | 0.998 | 0.630 | 0.437 | 62.000 |
| K-NET | ALL | arias_1_99_padded | 0.200 | 21141 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 56.740 |
| K-NET | ALL | arias_1_99_padded | 1.000 | 21141 | 425 | 2.010 | 1.000 | 1.000 | 0.711 | 56.740 |
| K-NET | ALL | arias_1_99_padded | 3.000 | 21141 | 7998 | 37.832 | 1.000 | 0.246 | 0.128 | 56.740 |
| K-NET | ALL | feature_onset_fixed | 0.200 | 21141 | 37 | 0.175 | 1.000 | 1.000 | 1.000 | 42.000 |
| K-NET | ALL | feature_onset_fixed | 1.000 | 21141 | 1101 | 5.208 | 1.000 | 0.939 | 0.465 | 42.000 |
| K-NET | ALL | feature_onset_fixed | 3.000 | 21141 | 10861 | 51.374 | 0.941 | 0.151 | 0.071 | 42.000 |
| K-NET | ALL | shortest_stable_no_catalog | 0.200 | 21141 | 2 | 0.009 | 1.000 | 1.000 | 1.000 | 22.000 |
| K-NET | ALL | shortest_stable_no_catalog | 1.000 | 21141 | 1507 | 7.128 | 1.000 | 0.867 | 0.482 | 22.000 |
| K-NET | ALL | shortest_stable_no_catalog | 3.000 | 21141 | 10228 | 48.380 | 0.960 | 0.157 | 0.071 | 22.000 |
| ALL | ALL | arias_1_99_padded | 0.200 | 44674 | 85 | 0.190 | 1.000 | 1.000 | 1.000 | 66.300 |
| ALL | ALL | arias_1_99_padded | 1.000 | 44674 | 666 | 1.491 | 1.000 | 1.000 | 0.818 | 66.300 |
| ALL | ALL | arias_1_99_padded | 3.000 | 44674 | 9429 | 21.106 | 1.000 | 0.350 | 0.170 | 66.300 |
| ALL | ALL | feature_onset_fixed | 0.200 | 44674 | 5296 | 11.855 | 1.000 | 0.598 | 0.107 | 42.000 |
| ALL | ALL | feature_onset_fixed | 1.000 | 44674 | 11973 | 26.801 | 1.000 | 0.374 | 0.110 | 42.000 |
| ALL | ALL | feature_onset_fixed | 3.000 | 44674 | 26043 | 58.296 | 0.857 | 0.177 | 0.069 | 42.000 |
| ALL | ALL | shortest_stable_no_catalog | 0.200 | 44674 | 51 | 0.114 | 1.000 | 1.000 | 1.000 | 34.250 |
| ALL | ALL | shortest_stable_no_catalog | 1.000 | 44674 | 3391 | 7.591 | 1.000 | 0.876 | 0.598 | 34.250 |
| ALL | ALL | shortest_stable_no_catalog | 3.000 | 44674 | 16602 | 37.163 | 0.991 | 0.249 | 0.100 | 34.250 |

## Outputs

- `response_spectrum_retention.csv`: per-record, per-policy, per-period response-spectrum retention.
- `summary.csv`: grouped spectrum-retention summary.

## Boundary

The current calculation reports relative pseudo-spectral acceleration retention. It does not establish absolute site-specific design spectra.
