# StrongMotion-QC Product Window Selector

This evaluation selects waveform windows by product retention: PGA retention, relative energy retention, and peak inclusion.

The selector uses waveform-derived product checks. It is not a human-label classifier and it is not a learned model result.

## Dataset-Level Summary

| dataset | priority_group | policy | records | unstable_records | unstable_pct | median_window_duration_sec | p25_window_duration_sec | p75_window_duration_sec | p05_energy_retention | median_energy_retention | p05_pga_retention | full_record_fallback_records | full_record_fallback_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | adaptive_energy_end | 6107 | 1205 | 19.731 | 137.870 | 91.595 | 145.090 | 0.945 | 0.962 | 1.000 | 0 | 0.000 |
| ALL | ALL | arias_1_99_padded | 6107 | 1 | 0.016 | 150.010 | 150.010 | 150.010 | 0.989 | 1.000 | 1.000 | 0 | 0.000 |
| ALL | ALL | catalog_p_fixed | 6107 | 5120 | 83.838 | 42.000 | 42.000 | 42.000 | 0.272 | 0.619 | 0.654 | 0 | 0.000 |
| ALL | ALL | energy_first_then_adaptive | 6107 | 0 | 0.000 | 143.990 | 132.765 | 149.320 | 0.953 | 0.969 | 1.000 | 1194 | 19.551 |
| ALL | ALL | energy_onset_fixed | 6107 | 5273 | 86.344 | 42.000 | 40.940 | 42.000 | 0.037 | 0.203 | 0.038 | 0 | 0.000 |
| ALL | ALL | feature_onset_fixed | 6107 | 5286 | 86.556 | 42.000 | 40.940 | 42.000 | 0.036 | 0.202 | 0.037 | 0 | 0.000 |
| ALL | ALL | full_record | 6107 | 0 | 0.000 | 150.010 | 150.010 | 150.010 | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| ALL | ALL | shortest_stable_all | 6107 | 0 | 0.000 | 142.370 | 111.180 | 147.005 | 0.952 | 0.966 | 1.000 | 1 | 0.016 |
| ALL | ALL | shortest_stable_no_catalog | 6107 | 0 | 0.000 | 142.370 | 111.180 | 147.005 | 0.952 | 0.966 | 1.000 | 1 | 0.016 |
| PNWAccelerometers | ALL | adaptive_energy_end | 6107 | 1205 | 19.731 | 137.870 | 91.595 | 145.090 | 0.945 | 0.962 | 1.000 | 0 | 0.000 |
| PNWAccelerometers | ALL | arias_1_99_padded | 6107 | 1 | 0.016 | 150.010 | 150.010 | 150.010 | 0.989 | 1.000 | 1.000 | 0 | 0.000 |
| PNWAccelerometers | ALL | catalog_p_fixed | 6107 | 5120 | 83.838 | 42.000 | 42.000 | 42.000 | 0.272 | 0.619 | 0.654 | 0 | 0.000 |
| PNWAccelerometers | ALL | energy_first_then_adaptive | 6107 | 0 | 0.000 | 143.990 | 132.765 | 149.320 | 0.953 | 0.969 | 1.000 | 1194 | 19.551 |
| PNWAccelerometers | ALL | energy_onset_fixed | 6107 | 5273 | 86.344 | 42.000 | 40.940 | 42.000 | 0.037 | 0.203 | 0.038 | 0 | 0.000 |
| PNWAccelerometers | ALL | feature_onset_fixed | 6107 | 5286 | 86.556 | 42.000 | 40.940 | 42.000 | 0.036 | 0.202 | 0.037 | 0 | 0.000 |
| PNWAccelerometers | ALL | full_record | 6107 | 0 | 0.000 | 150.010 | 150.010 | 150.010 | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| PNWAccelerometers | ALL | shortest_stable_all | 6107 | 0 | 0.000 | 142.370 | 111.180 | 147.005 | 0.952 | 0.966 | 1.000 | 1 | 0.016 |
| PNWAccelerometers | ALL | shortest_stable_no_catalog | 6107 | 0 | 0.000 | 142.370 | 111.180 | 147.005 | 0.952 | 0.966 | 1.000 | 1 | 0.016 |

## Candidate Usage

| dataset | policy | selected_candidate | records | pct |
| --- | --- | --- | --- | --- |
| PNWAccelerometers | adaptive_energy_end | feature_onset_to_energy_end | 6107 | 100.000 |
| PNWAccelerometers | arias_1_99_padded | arias_1_99_padded | 6107 | 100.000 |
| PNWAccelerometers | catalog_p_fixed | catalog_p_fixed | 6107 | 100.000 |
| PNWAccelerometers | energy_first_then_adaptive | feature_onset_to_energy_end | 4079 | 66.792 |
| PNWAccelerometers | energy_first_then_adaptive | full_record | 1194 | 19.551 |
| PNWAccelerometers | energy_first_then_adaptive | energy_onset_fixed | 834 | 13.656 |
| PNWAccelerometers | energy_onset_fixed | energy_onset_fixed | 6107 | 100.000 |
| PNWAccelerometers | feature_onset_fixed | feature_onset_fixed | 6107 | 100.000 |
| PNWAccelerometers | full_record | full_record | 6107 | 100.000 |
| PNWAccelerometers | shortest_stable_all | feature_onset_to_energy_end | 4487 | 73.473 |
| PNWAccelerometers | shortest_stable_all | arias_1_99_padded | 1001 | 16.391 |
| PNWAccelerometers | shortest_stable_all | feature_onset_fixed_90s | 328 | 5.371 |
| PNWAccelerometers | shortest_stable_all | catalog_p_fixed | 203 | 3.324 |
| PNWAccelerometers | shortest_stable_all | feature_onset_fixed_60s | 44 | 0.720 |
| PNWAccelerometers | shortest_stable_all | feature_onset_fixed_20s | 37 | 0.606 |
| PNWAccelerometers | shortest_stable_all | energy_onset_fixed | 6 | 0.098 |
| PNWAccelerometers | shortest_stable_all | full_record | 1 | 0.016 |
| PNWAccelerometers | shortest_stable_no_catalog | feature_onset_to_energy_end | 4588 | 75.127 |
| PNWAccelerometers | shortest_stable_no_catalog | arias_1_99_padded | 1001 | 16.391 |
| PNWAccelerometers | shortest_stable_no_catalog | feature_onset_fixed_90s | 332 | 5.436 |
| PNWAccelerometers | shortest_stable_no_catalog | feature_onset_fixed_60s | 111 | 1.818 |
| PNWAccelerometers | shortest_stable_no_catalog | energy_onset_fixed | 37 | 0.606 |
| PNWAccelerometers | shortest_stable_no_catalog | feature_onset_fixed_20s | 37 | 0.606 |
| PNWAccelerometers | shortest_stable_no_catalog | full_record | 1 | 0.016 |

## Interpretation Boundary

`shortest_stable_*` policies are retrospective product-stability selectors computed from available waveform records. They are valid for offline strong-motion processing audits and as upper-bound baselines for learned selectors. They should not be described as real-time phase picking or as evidence that a neural model has solved window selection.
