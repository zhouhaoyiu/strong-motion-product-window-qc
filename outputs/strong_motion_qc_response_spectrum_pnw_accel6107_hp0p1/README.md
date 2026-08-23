# StrongMotion-QC Response-Spectrum Retention

This audit compares 5%-damped pseudo-spectral acceleration computed inside selected processing windows with the same product computed on the full record.

Periods: 0.2 s, 1 s, 3 s.

Each oscillator response is continued for 5 zero-input cycles after the waveform ends so that a window boundary does not truncate free vibration.

The result is a relative retention audit. It strengthens the product-window claim because response spectra are closer to strong-motion engineering products than PGA and waveform energy alone.

## Summary

| dataset | priority_group | policy | period_sec | records | spectrum_unstable_records | spectrum_unstable_pct | median_psa_retention | p05_psa_retention | p01_psa_retention | median_window_duration_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PNWAccelerometers | ALL | arias_1_99_padded | 0.200 | 6107 | 3 | 0.049 | 1.000 | 1.000 | 1.000 | 150.010 |
| PNWAccelerometers | ALL | arias_1_99_padded | 1.000 | 6107 | 410 | 6.714 | 1.000 | 0.808 | 0.474 | 150.010 |
| PNWAccelerometers | ALL | arias_1_99_padded | 3.000 | 6107 | 1067 | 17.472 | 1.000 | 0.367 | 0.160 | 150.010 |
| PNWAccelerometers | ALL | feature_onset_fixed | 0.200 | 6107 | 4985 | 81.628 | 0.206 | 0.028 | 0.012 | 42.000 |
| PNWAccelerometers | ALL | feature_onset_fixed | 1.000 | 6107 | 5130 | 84.002 | 0.649 | 0.147 | 0.055 | 42.000 |
| PNWAccelerometers | ALL | feature_onset_fixed | 3.000 | 6107 | 5699 | 93.319 | 0.511 | 0.118 | 0.053 | 42.000 |
| PNWAccelerometers | ALL | shortest_stable_no_catalog | 0.200 | 6107 | 154 | 2.522 | 1.000 | 1.000 | 0.786 | 142.370 |
| PNWAccelerometers | ALL | shortest_stable_no_catalog | 1.000 | 6107 | 2631 | 43.082 | 0.995 | 0.381 | 0.236 | 142.370 |
| PNWAccelerometers | ALL | shortest_stable_no_catalog | 3.000 | 6107 | 3811 | 62.404 | 0.768 | 0.204 | 0.106 | 142.370 |
| ALL | ALL | arias_1_99_padded | 0.200 | 6107 | 3 | 0.049 | 1.000 | 1.000 | 1.000 | 150.010 |
| ALL | ALL | arias_1_99_padded | 1.000 | 6107 | 410 | 6.714 | 1.000 | 0.808 | 0.474 | 150.010 |
| ALL | ALL | arias_1_99_padded | 3.000 | 6107 | 1067 | 17.472 | 1.000 | 0.367 | 0.160 | 150.010 |
| ALL | ALL | feature_onset_fixed | 0.200 | 6107 | 4985 | 81.628 | 0.206 | 0.028 | 0.012 | 42.000 |
| ALL | ALL | feature_onset_fixed | 1.000 | 6107 | 5130 | 84.002 | 0.649 | 0.147 | 0.055 | 42.000 |
| ALL | ALL | feature_onset_fixed | 3.000 | 6107 | 5699 | 93.319 | 0.511 | 0.118 | 0.053 | 42.000 |
| ALL | ALL | shortest_stable_no_catalog | 0.200 | 6107 | 154 | 2.522 | 1.000 | 1.000 | 0.786 | 142.370 |
| ALL | ALL | shortest_stable_no_catalog | 1.000 | 6107 | 2631 | 43.082 | 0.995 | 0.381 | 0.236 | 142.370 |
| ALL | ALL | shortest_stable_no_catalog | 3.000 | 6107 | 3811 | 62.404 | 0.768 | 0.204 | 0.106 | 142.370 |

## Outputs

- `response_spectrum_retention.csv`: per-record, per-policy, per-period response-spectrum retention.
- `summary.csv`: grouped spectrum-retention summary.

## Boundary

The current calculation reports relative pseudo-spectral acceleration retention. It does not establish absolute site-specific design spectra.
