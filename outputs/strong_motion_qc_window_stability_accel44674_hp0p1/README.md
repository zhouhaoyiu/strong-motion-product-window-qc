# StrongMotion-QC Window Stability

This audit evaluates whether candidate windows preserve full-record waveform products.

The endpoints are product stability metrics: PGA retention, relative energy retention, and whether the full-record peak falls inside the candidate window. They are closer to engineering processing needs than spike-threshold classification.

Catalog P windows are included only as an evaluation comparator when catalog P is present.

## Summary

| dataset | priority_group | candidate | records | unstable_records | unstable_pct | median_pga_retention | p05_pga_retention | median_energy_retention | p05_energy_retention |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | ALL | 402066 | 96895 | 24.099 | 1.000 | 0.624 | 0.993 | 0.271 |
| InstanceGM | low_magnitude_background | arias_1_99_padded | 9000 | 39 | 0.433 | 1.000 | 1.000 | 1.000 | 0.993 |
| InstanceGM | low_magnitude_background | catalog_p_fixed | 9000 | 6066 | 67.400 | 1.000 | 0.617 | 0.822 | 0.351 |
| InstanceGM | low_magnitude_background | energy_onset_fixed | 9000 | 5976 | 66.400 | 1.000 | 0.550 | 0.827 | 0.331 |
| InstanceGM | low_magnitude_background | feature_onset_fixed | 9000 | 6454 | 71.711 | 1.000 | 0.364 | 0.778 | 0.240 |
| InstanceGM | low_magnitude_background | feature_onset_fixed_20s | 9000 | 8365 | 92.944 | 0.688 | 0.041 | 0.202 | 0.005 |
| InstanceGM | low_magnitude_background | feature_onset_fixed_60s | 9000 | 5633 | 62.589 | 1.000 | 0.723 | 0.880 | 0.505 |
| InstanceGM | low_magnitude_background | feature_onset_fixed_90s | 9000 | 4298 | 47.756 | 1.000 | 0.933 | 0.958 | 0.782 |
| InstanceGM | low_magnitude_background | feature_onset_to_energy_end | 9000 | 218 | 2.422 | 1.000 | 1.000 | 0.969 | 0.952 |
| InstanceGM | low_magnitude_background | full_record | 9000 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| InstanceGM | m3_to_m4_small_event | arias_1_99_padded | 9000 | 28 | 0.311 | 1.000 | 1.000 | 0.999 | 0.994 |
| InstanceGM | m3_to_m4_small_event | catalog_p_fixed | 9000 | 4229 | 46.989 | 1.000 | 0.755 | 0.960 | 0.376 |
| InstanceGM | m3_to_m4_small_event | energy_onset_fixed | 9000 | 4071 | 45.233 | 1.000 | 0.648 | 0.965 | 0.342 |
| InstanceGM | m3_to_m4_small_event | feature_onset_fixed | 9000 | 5571 | 61.900 | 1.000 | 0.447 | 0.886 | 0.239 |
| InstanceGM | m3_to_m4_small_event | feature_onset_fixed_20s | 9000 | 8527 | 94.744 | 0.456 | 0.027 | 0.139 | 0.001 |
| InstanceGM | m3_to_m4_small_event | feature_onset_fixed_60s | 9000 | 3646 | 40.511 | 1.000 | 0.841 | 0.975 | 0.531 |
| InstanceGM | m3_to_m4_small_event | feature_onset_fixed_90s | 9000 | 2168 | 24.089 | 1.000 | 1.000 | 0.994 | 0.813 |
| InstanceGM | m3_to_m4_small_event | feature_onset_to_energy_end | 9000 | 166 | 1.844 | 1.000 | 1.000 | 0.967 | 0.953 |
| InstanceGM | m3_to_m4_small_event | full_record | 9000 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| InstanceGM | m4plus_strong_motion | arias_1_99_padded | 5533 | 19 | 0.343 | 1.000 | 1.000 | 0.998 | 0.995 |
| InstanceGM | m4plus_strong_motion | catalog_p_fixed | 5533 | 3013 | 54.455 | 1.000 | 0.510 | 0.928 | 0.257 |
| InstanceGM | m4plus_strong_motion | energy_onset_fixed | 5533 | 2757 | 49.828 | 1.000 | 0.546 | 0.952 | 0.281 |
| InstanceGM | m4plus_strong_motion | feature_onset_fixed | 5533 | 3871 | 69.962 | 1.000 | 0.322 | 0.800 | 0.117 |
| InstanceGM | m4plus_strong_motion | feature_onset_fixed_20s | 5533 | 5314 | 96.042 | 0.370 | 0.024 | 0.086 | 0.001 |
| InstanceGM | m4plus_strong_motion | feature_onset_fixed_60s | 5533 | 2510 | 45.364 | 1.000 | 0.612 | 0.965 | 0.366 |
| InstanceGM | m4plus_strong_motion | feature_onset_fixed_90s | 5533 | 1277 | 23.080 | 1.000 | 1.000 | 0.995 | 0.793 |
| InstanceGM | m4plus_strong_motion | feature_onset_to_energy_end | 5533 | 40 | 0.723 | 1.000 | 1.000 | 0.966 | 0.956 |
| InstanceGM | m4plus_strong_motion | full_record | 5533 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| K-NET | low_magnitude_background | arias_1_99_padded | 21 | 0 | 0.000 | 1.000 | 1.000 | 0.999 | 0.996 |
| K-NET | low_magnitude_background | catalog_p_fixed | 21 | 0 | 0.000 | 1.000 | 1.000 | 0.999 | 0.995 |
| K-NET | low_magnitude_background | energy_onset_fixed | 21 | 0 | 0.000 | 1.000 | 1.000 | 0.999 | 0.995 |
| K-NET | low_magnitude_background | feature_onset_fixed | 21 | 0 | 0.000 | 1.000 | 1.000 | 0.999 | 0.996 |
| K-NET | low_magnitude_background | feature_onset_fixed_20s | 21 | 1 | 4.762 | 1.000 | 1.000 | 0.993 | 0.950 |
| K-NET | low_magnitude_background | feature_onset_fixed_60s | 21 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 0.999 |
| K-NET | low_magnitude_background | feature_onset_fixed_90s | 21 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 0.999 |
| K-NET | low_magnitude_background | feature_onset_to_energy_end | 21 | 0 | 0.000 | 1.000 | 1.000 | 0.974 | 0.965 |
| K-NET | low_magnitude_background | full_record | 21 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| K-NET | m3_to_m4_small_event | arias_1_99_padded | 5647 | 0 | 0.000 | 1.000 | 1.000 | 0.998 | 0.994 |
| K-NET | m3_to_m4_small_event | catalog_p_fixed | 5647 | 96 | 1.700 | 1.000 | 1.000 | 0.998 | 0.979 |
| K-NET | m3_to_m4_small_event | energy_onset_fixed | 5647 | 94 | 1.665 | 1.000 | 1.000 | 0.998 | 0.979 |
| K-NET | m3_to_m4_small_event | feature_onset_fixed | 5647 | 94 | 1.665 | 1.000 | 1.000 | 0.998 | 0.979 |
| K-NET | m3_to_m4_small_event | feature_onset_fixed_20s | 5647 | 1124 | 19.904 | 1.000 | 1.000 | 0.981 | 0.898 |
| K-NET | m3_to_m4_small_event | feature_onset_fixed_60s | 5647 | 59 | 1.045 | 1.000 | 1.000 | 0.999 | 0.988 |
| K-NET | m3_to_m4_small_event | feature_onset_fixed_90s | 5647 | 11 | 0.195 | 1.000 | 1.000 | 1.000 | 0.995 |
| K-NET | m3_to_m4_small_event | feature_onset_to_energy_end | 5647 | 20 | 0.354 | 1.000 | 1.000 | 0.972 | 0.961 |
| K-NET | m3_to_m4_small_event | full_record | 5647 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| K-NET | m4plus_strong_motion | arias_1_99_padded | 15473 | 0 | 0.000 | 1.000 | 1.000 | 0.998 | 0.995 |
| K-NET | m4plus_strong_motion | catalog_p_fixed | 15473 | 757 | 4.892 | 1.000 | 1.000 | 0.994 | 0.951 |
| K-NET | m4plus_strong_motion | energy_onset_fixed | 15473 | 563 | 3.639 | 1.000 | 1.000 | 0.994 | 0.959 |
| K-NET | m4plus_strong_motion | feature_onset_fixed | 15473 | 783 | 5.060 | 1.000 | 1.000 | 0.994 | 0.950 |
| K-NET | m4plus_strong_motion | feature_onset_fixed_20s | 15473 | 8875 | 57.358 | 1.000 | 0.974 | 0.938 | 0.503 |
| K-NET | m4plus_strong_motion | feature_onset_fixed_60s | 15473 | 119 | 0.769 | 1.000 | 1.000 | 0.999 | 0.987 |
| K-NET | m4plus_strong_motion | feature_onset_fixed_90s | 15473 | 20 | 0.129 | 1.000 | 1.000 | 1.000 | 0.997 |
| K-NET | m4plus_strong_motion | feature_onset_to_energy_end | 15473 | 23 | 0.149 | 1.000 | 1.000 | 0.968 | 0.960 |
| K-NET | m4plus_strong_motion | full_record | 15473 | 0 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Outputs

- `window_stability.csv`: per-record candidate-window product retention.
- `summary.csv`: grouped instability and retention metrics.

## Interpretation

A failed window indicates a product-level issue, not a manual QC label. The next model objective should predict or reduce these failures directly.

## Common Failure Reasons

| candidate | failure_reason | records |
| --- | --- | --- |
| feature_onset_fixed_20s | peak_outside,pga_loss,energy_loss | 18083 |
| feature_onset_fixed_20s | energy_loss | 13987 |
| feature_onset_fixed | energy_loss | 10458 |
| catalog_p_fixed | energy_loss | 9999 |
| energy_onset_fixed | energy_loss | 8880 |
| feature_onset_fixed_60s | energy_loss | 8725 |
| feature_onset_fixed_90s | energy_loss | 6446 |
| feature_onset_fixed | peak_outside,pga_loss,energy_loss | 6166 |
| energy_onset_fixed | peak_outside,pga_loss,energy_loss | 4396 |
| catalog_p_fixed | peak_outside,pga_loss,energy_loss | 4040 |
| feature_onset_fixed_60s | peak_outside,pga_loss,energy_loss | 3087 |
| feature_onset_fixed_90s | peak_outside,pga_loss,energy_loss | 1207 |
