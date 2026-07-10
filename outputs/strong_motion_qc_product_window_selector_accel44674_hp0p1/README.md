# StrongMotion-QC Product Window Selector

This evaluation selects waveform windows by product retention: PGA retention, relative energy retention, and peak inclusion.

The selector uses waveform-derived product checks. It is not a human-label classifier and it is not a learned model result.

## Dataset-Level Summary

| dataset | priority_group | policy | records | unstable_records | unstable_pct | median_window_duration_sec | p25_window_duration_sec | p75_window_duration_sec | p05_energy_retention | median_energy_retention | p05_pga_retention | full_record_fallback_records | full_record_fallback_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | adaptive_energy_end | 44674 | 467 | 1.045 | 34.200 | 23.930 | 69.800 | 0.955 | 0.968 | 1.000 | 0 | 0.000 |
| ALL | ALL | arias_1_99_padded | 44674 | 86 | 0.193 | 66.300 | 51.980 | 111.940 | 0.994 | 0.998 | 1.000 | 0 | 0.000 |
| ALL | ALL | catalog_p_fixed | 44674 | 14161 | 31.699 | 42.000 | 42.000 | 42.000 | 0.388 | 0.988 | 0.817 | 0 | 0.000 |
| ALL | ALL | energy_first_then_adaptive | 44674 | 0 | 0.000 | 42.000 | 42.000 | 70.560 | 0.955 | 0.991 | 1.000 | 404 | 0.904 |
| ALL | ALL | energy_onset_fixed | 44674 | 13461 | 30.132 | 42.000 | 42.000 | 42.000 | 0.371 | 0.990 | 0.767 | 0 | 0.000 |
| ALL | ALL | feature_onset_fixed | 44674 | 16773 | 37.545 | 42.000 | 42.000 | 42.000 | 0.303 | 0.984 | 0.577 | 0 | 0.000 |
| ALL | ALL | full_record | 44674 | 0 | 0.000 | 120.000 | 119.000 | 120.000 | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| ALL | ALL | shortest_stable_all | 44674 | 0 | 0.000 | 34.250 | 22.000 | 69.670 | 0.953 | 0.968 | 1.000 | 29 | 0.065 |
| ALL | ALL | shortest_stable_no_catalog | 44674 | 0 | 0.000 | 34.250 | 22.000 | 69.800 | 0.953 | 0.968 | 1.000 | 37 | 0.083 |
| InstanceGM | ALL | adaptive_energy_end | 23533 | 424 | 1.802 | 64.500 | 38.720 | 102.800 | 0.953 | 0.967 | 1.000 | 0 | 0.000 |
| InstanceGM | ALL | arias_1_99_padded | 23533 | 86 | 0.365 | 107.540 | 63.910 | 120.000 | 0.994 | 0.999 | 1.000 | 0 | 0.000 |
| InstanceGM | ALL | catalog_p_fixed | 23533 | 13308 | 56.550 | 42.000 | 42.000 | 42.000 | 0.348 | 0.917 | 0.630 | 0 | 0.000 |
| InstanceGM | ALL | energy_first_then_adaptive | 23533 | 0 | 0.000 | 64.050 | 42.000 | 103.820 | 0.953 | 0.974 | 1.000 | 370 | 1.572 |
| InstanceGM | ALL | energy_onset_fixed | 23533 | 12804 | 54.409 | 42.000 | 42.000 | 42.000 | 0.328 | 0.930 | 0.584 | 0 | 0.000 |
| InstanceGM | ALL | feature_onset_fixed | 23533 | 15896 | 67.548 | 42.000 | 42.000 | 42.000 | 0.183 | 0.831 | 0.376 | 0 | 0.000 |
| InstanceGM | ALL | full_record | 23533 | 0 | 0.000 | 120.000 | 120.000 | 120.000 | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| InstanceGM | ALL | shortest_stable_all | 23533 | 0 | 0.000 | 62.000 | 38.730 | 102.790 | 0.953 | 0.969 | 1.000 | 29 | 0.123 |
| InstanceGM | ALL | shortest_stable_no_catalog | 23533 | 0 | 0.000 | 62.000 | 38.730 | 102.810 | 0.953 | 0.969 | 1.000 | 37 | 0.157 |
| K-NET | ALL | adaptive_energy_end | 21141 | 43 | 0.203 | 24.420 | 19.200 | 30.270 | 0.960 | 0.969 | 1.000 | 0 | 0.000 |
| K-NET | ALL | arias_1_99_padded | 21141 | 0 | 0.000 | 56.740 | 48.670 | 65.710 | 0.995 | 0.998 | 1.000 | 0 | 0.000 |
| K-NET | ALL | catalog_p_fixed | 21141 | 853 | 4.035 | 42.000 | 42.000 | 42.000 | 0.958 | 0.995 | 1.000 | 0 | 0.000 |
| K-NET | ALL | energy_first_then_adaptive | 21141 | 0 | 0.000 | 42.000 | 42.000 | 42.000 | 0.967 | 0.995 | 1.000 | 34 | 0.161 |
| K-NET | ALL | energy_onset_fixed | 21141 | 657 | 3.108 | 42.000 | 42.000 | 42.000 | 0.964 | 0.995 | 1.000 | 0 | 0.000 |
| K-NET | ALL | feature_onset_fixed | 21141 | 877 | 4.148 | 42.000 | 42.000 | 42.000 | 0.957 | 0.995 | 1.000 | 0 | 0.000 |
| K-NET | ALL | full_record | 21141 | 0 | 0.000 | 119.000 | 119.000 | 119.000 | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| K-NET | ALL | shortest_stable_all | 21141 | 0 | 0.000 | 22.000 | 19.200 | 30.270 | 0.955 | 0.968 | 1.000 | 0 | 0.000 |
| K-NET | ALL | shortest_stable_no_catalog | 21141 | 0 | 0.000 | 22.000 | 19.200 | 30.270 | 0.955 | 0.968 | 1.000 | 0 | 0.000 |

## Candidate Usage

| dataset | policy | selected_candidate | records | pct |
| --- | --- | --- | --- | --- |
| InstanceGM | adaptive_energy_end | feature_onset_to_energy_end | 23533 | 100.000 |
| InstanceGM | arias_1_99_padded | arias_1_99_padded | 23533 | 100.000 |
| InstanceGM | catalog_p_fixed | catalog_p_fixed | 23533 | 100.000 |
| InstanceGM | energy_first_then_adaptive | feature_onset_to_energy_end | 12434 | 52.836 |
| InstanceGM | energy_first_then_adaptive | energy_onset_fixed | 10729 | 45.591 |
| InstanceGM | energy_first_then_adaptive | full_record | 370 | 1.572 |
| InstanceGM | energy_onset_fixed | energy_onset_fixed | 23533 | 100.000 |
| InstanceGM | feature_onset_fixed | feature_onset_fixed | 23533 | 100.000 |
| InstanceGM | full_record | full_record | 23533 | 100.000 |
| InstanceGM | shortest_stable_all | feature_onset_to_energy_end | 17658 | 75.035 |
| InstanceGM | shortest_stable_all | catalog_p_fixed | 3332 | 14.159 |
| InstanceGM | shortest_stable_all | feature_onset_fixed_90s | 619 | 2.630 |
| InstanceGM | shortest_stable_all | energy_onset_fixed | 597 | 2.537 |
| InstanceGM | shortest_stable_all | feature_onset_fixed_20s | 565 | 2.401 |
| InstanceGM | shortest_stable_all | feature_onset_fixed_60s | 384 | 1.632 |
| InstanceGM | shortest_stable_all | arias_1_99_padded | 336 | 1.428 |
| InstanceGM | shortest_stable_all | full_record | 29 | 0.123 |
| InstanceGM | shortest_stable_all | feature_onset_fixed | 13 | 0.055 |
| InstanceGM | shortest_stable_no_catalog | feature_onset_to_energy_end | 17708 | 75.248 |
| InstanceGM | shortest_stable_no_catalog | energy_onset_fixed | 3762 | 15.986 |
| InstanceGM | shortest_stable_no_catalog | feature_onset_fixed_90s | 619 | 2.630 |
| InstanceGM | shortest_stable_no_catalog | feature_onset_fixed_20s | 565 | 2.401 |
| InstanceGM | shortest_stable_no_catalog | feature_onset_fixed_60s | 388 | 1.649 |
| InstanceGM | shortest_stable_no_catalog | arias_1_99_padded | 337 | 1.432 |
| InstanceGM | shortest_stable_no_catalog | feature_onset_fixed | 117 | 0.497 |
| InstanceGM | shortest_stable_no_catalog | full_record | 37 | 0.157 |
| K-NET | adaptive_energy_end | feature_onset_to_energy_end | 21141 | 100.000 |
| K-NET | arias_1_99_padded | arias_1_99_padded | 21141 | 100.000 |
| K-NET | catalog_p_fixed | catalog_p_fixed | 21141 | 100.000 |
| K-NET | energy_first_then_adaptive | energy_onset_fixed | 20484 | 96.892 |
| K-NET | energy_first_then_adaptive | feature_onset_to_energy_end | 623 | 2.947 |
| K-NET | energy_first_then_adaptive | full_record | 34 | 0.161 |
| K-NET | energy_onset_fixed | energy_onset_fixed | 21141 | 100.000 |
| K-NET | feature_onset_fixed | feature_onset_fixed | 21141 | 100.000 |
| K-NET | full_record | full_record | 21141 | 100.000 |
| K-NET | shortest_stable_all | feature_onset_to_energy_end | 17409 | 82.347 |
| K-NET | shortest_stable_all | feature_onset_fixed_20s | 3112 | 14.720 |
| K-NET | shortest_stable_all | catalog_p_fixed | 318 | 1.504 |
| K-NET | shortest_stable_all | energy_onset_fixed | 219 | 1.036 |
| K-NET | shortest_stable_all | feature_onset_fixed_60s | 52 | 0.246 |
| K-NET | shortest_stable_all | feature_onset_fixed_90s | 23 | 0.109 |
| K-NET | shortest_stable_all | arias_1_99_padded | 4 | 0.019 |
| K-NET | shortest_stable_all | feature_onset_fixed | 4 | 0.019 |
| K-NET | shortest_stable_no_catalog | feature_onset_to_energy_end | 17410 | 82.352 |
| K-NET | shortest_stable_no_catalog | feature_onset_fixed_20s | 3112 | 14.720 |
| K-NET | shortest_stable_no_catalog | energy_onset_fixed | 510 | 2.412 |
| K-NET | shortest_stable_no_catalog | feature_onset_fixed_60s | 52 | 0.246 |
| K-NET | shortest_stable_no_catalog | feature_onset_fixed | 30 | 0.142 |
| K-NET | shortest_stable_no_catalog | feature_onset_fixed_90s | 23 | 0.109 |
| K-NET | shortest_stable_no_catalog | arias_1_99_padded | 4 | 0.019 |

## Interpretation Boundary

`shortest_stable_*` policies are retrospective product-stability selectors computed from available waveform records. They are valid for offline strong-motion processing audits and as upper-bound baselines for learned selectors. They should not be described as real-time phase picking or as evidence that a neural model has solved window selection.
