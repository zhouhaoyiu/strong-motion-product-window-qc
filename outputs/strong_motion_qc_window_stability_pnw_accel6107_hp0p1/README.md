# StrongMotion-QC Window Stability

This audit evaluates whether candidate windows preserve full-record waveform products.

The endpoints are product stability metrics: PGA retention, relative energy retention, and whether the full-record peak falls inside the candidate window. They are closer to engineering processing needs than spike-threshold classification.

Catalog P windows are included only as an evaluation comparator when catalog P is present.

## Summary

| dataset | priority_group | candidate | records | unstable_records | unstable_pct | median_pga_retention | p05_pga_retention | median_energy_retention | p05_energy_retention |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | ALL | 54963 | 32129 | 58.456 | 1.000 | 0.057 | 0.835 | 0.048 |
| PNWAccelerometers | low_magnitude_background | arias_1_99_padded | 5563 | 1 | 0.018 | 1.000 | 1.000 | 1.000 | 0.990 |
| PNWAccelerometers | low_magnitude_background | catalog_p_fixed | 5563 | 4912 | 88.298 | 1.000 | 0.630 | 0.572 | 0.270 |
| PNWAccelerometers | low_magnitude_background | energy_onset_fixed | 5563 | 5020 | 90.239 | 0.181 | 0.038 | 0.197 | 0.038 |
| PNWAccelerometers | low_magnitude_background | feature_onset_fixed | 5563 | 5026 | 90.347 | 0.181 | 0.038 | 0.196 | 0.037 |
| PNWAccelerometers | low_magnitude_background | feature_onset_fixed_20s | 5563 | 5176 | 93.043 | 0.146 | 0.026 | 0.095 | 0.012 |
| PNWAccelerometers | low_magnitude_background | feature_onset_fixed_60s | 5563 | 4855 | 87.273 | 1.000 | 0.202 | 0.544 | 0.244 |
| PNWAccelerometers | low_magnitude_background | feature_onset_fixed_90s | 5563 | 4514 | 81.143 | 1.000 | 0.834 | 0.780 | 0.582 |
| PNWAccelerometers | low_magnitude_background | feature_onset_to_energy_end | 5563 | 1092 | 19.630 | 1.000 | 1.000 | 0.962 | 0.945 |
| PNWAccelerometers | low_magnitude_background | full_record | 5563 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| PNWAccelerometers | m3_to_m4_small_event | arias_1_99_padded | 468 | 0 | 0.000 | 1.000 | 1.000 | 0.997 | 0.988 |
| PNWAccelerometers | m3_to_m4_small_event | catalog_p_fixed | 468 | 185 | 39.530 | 1.000 | 1.000 | 0.971 | 0.621 |
| PNWAccelerometers | m3_to_m4_small_event | energy_onset_fixed | 468 | 230 | 49.145 | 1.000 | 0.034 | 0.955 | 0.025 |
| PNWAccelerometers | m3_to_m4_small_event | feature_onset_fixed | 468 | 235 | 50.214 | 1.000 | 0.034 | 0.948 | 0.025 |
| PNWAccelerometers | m3_to_m4_small_event | feature_onset_fixed_20s | 468 | 320 | 68.376 | 0.302 | 0.018 | 0.196 | 0.007 |
| PNWAccelerometers | m3_to_m4_small_event | feature_onset_fixed_60s | 468 | 192 | 41.026 | 1.000 | 0.120 | 0.977 | 0.142 |
| PNWAccelerometers | m3_to_m4_small_event | feature_onset_fixed_90s | 468 | 120 | 25.641 | 1.000 | 1.000 | 0.988 | 0.775 |
| PNWAccelerometers | m3_to_m4_small_event | feature_onset_to_energy_end | 468 | 110 | 23.504 | 1.000 | 1.000 | 0.958 | 0.946 |
| PNWAccelerometers | m3_to_m4_small_event | full_record | 468 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| PNWAccelerometers | m4plus_strong_motion | arias_1_99_padded | 76 | 0 | 0.000 | 1.000 | 1.000 | 0.996 | 0.990 |
| PNWAccelerometers | m4plus_strong_motion | catalog_p_fixed | 76 | 23 | 30.263 | 1.000 | 1.000 | 0.975 | 0.892 |
| PNWAccelerometers | m4plus_strong_motion | energy_onset_fixed | 76 | 23 | 30.263 | 1.000 | 1.000 | 0.975 | 0.878 |
| PNWAccelerometers | m4plus_strong_motion | feature_onset_fixed | 76 | 25 | 32.895 | 1.000 | 0.843 | 0.974 | 0.669 |
| PNWAccelerometers | m4plus_strong_motion | feature_onset_fixed_20s | 76 | 62 | 81.579 | 1.000 | 0.138 | 0.804 | 0.023 |
| PNWAccelerometers | m4plus_strong_motion | feature_onset_fixed_60s | 76 | 4 | 5.263 | 1.000 | 1.000 | 0.991 | 0.932 |
| PNWAccelerometers | m4plus_strong_motion | feature_onset_fixed_90s | 76 | 1 | 1.316 | 1.000 | 1.000 | 0.999 | 0.987 |
| PNWAccelerometers | m4plus_strong_motion | feature_onset_to_energy_end | 76 | 3 | 3.947 | 1.000 | 1.000 | 0.961 | 0.951 |
| PNWAccelerometers | m4plus_strong_motion | full_record | 76 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Outputs

- `window_stability.csv`: per-record candidate-window product retention.
- `summary.csv`: grouped instability and retention metrics.

## Interpretation

A failed window indicates a product-level issue, not a manual QC label. The next model objective should predict or reduce these failures directly.

## Common Failure Reasons

| candidate | failure_reason | records |
| --- | --- | --- |
| feature_onset_fixed_20s | peak_outside,pga_loss,energy_loss | 5304 |
| feature_onset_fixed | peak_outside,pga_loss,energy_loss | 4977 |
| energy_onset_fixed | peak_outside,pga_loss,energy_loss | 4966 |
| catalog_p_fixed | energy_loss | 4339 |
| feature_onset_fixed_90s | energy_loss | 4175 |
| feature_onset_fixed_60s | energy_loss | 3253 |
| feature_onset_fixed_60s | peak_outside,pga_loss,energy_loss | 1790 |
| feature_onset_to_energy_end | energy_loss | 1124 |
| catalog_p_fixed | peak_outside,pga_loss,energy_loss | 773 |
| feature_onset_fixed_90s | peak_outside,pga_loss,energy_loss | 448 |
| feature_onset_fixed | energy_loss | 306 |
| energy_onset_fixed | energy_loss | 304 |
