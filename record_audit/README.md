# StrongMotion-QC Record-Level Audit Packet

This packet provides representative record-level traces for checking how fixed windows and the shortest-stable selector behave on individual records.

## Scope

- The cases are explanatory examples selected from the current 53,463-record audit.
- The packet supports reviewability; it is not a separate statistical experiment.
- Window metrics come from `selected_windows.csv` under the same product-retention rules used by the manuscript.

## Case Summary

| case_id | case_category | record_uid | dataset | priority_group | magnitude | window_duration_sec_baseline | window_duration_sec_selected | energy_retention_baseline | energy_retention_selected | pga_retention_baseline | pga_retention_selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| case_01 | instance_fixed_failure_rescued | InstanceGM:327031 | InstanceGM | low_magnitude_background | 1.900 | 42.000 | 42.000 | 0.000 | 1.000 | 0.001 | 1.000 |
| case_02 | instance_fixed_failure_rescued | InstanceGM:208045 | InstanceGM | low_magnitude_background | 2.100 | 42.010 | 42.000 | 0.000 | 1.000 | 0.001 | 1.000 |
| case_03 | knet_fixed_failure_rescued | K-NET:13561 | K-NET | m4plus_strong_motion | 8.000 | 42.000 | 42.000 | 0.024 | 0.980 | 0.152 | 1.000 |
| case_04 | knet_fixed_failure_rescued | K-NET:13569 | K-NET | m4plus_strong_motion | 8.000 | 42.000 | 42.000 | 0.065 | 0.987 | 0.310 | 1.000 |
| case_05 | knet_compact_stable_window | K-NET:16611 | K-NET | m3_to_m4_small_event | 3.500 | 42.000 | 6.590 | 1.000 | 0.999 | 1.000 | 1.000 |
| case_06 | knet_compact_stable_window | K-NET:10315 | K-NET | low_magnitude_background | 2.900 | 42.000 | 6.510 | 1.000 | 0.998 | 1.000 | 1.000 |
| case_07 | full_record_fallback_boundary | InstanceGM:1159122 | InstanceGM | m4plus_strong_motion | 5.300 | 42.010 | 120.000 | 0.909 | 1.000 | 1.000 | 1.000 |
| case_08 | full_record_fallback_boundary | K-NET:17355 | K-NET | m4plus_strong_motion | 6.100 | 42.000 | 60.000 | 0.952 | 1.000 | 0.943 | 1.000 |

## Outputs

- `cases.csv`: selected case-level metrics and rationale.
- `case_windows.csv`: all plotted policy windows for the selected records.
- `plot_manifest.csv`: generated case figure files.
- `figures/`: per-record waveform plots with fixed and selected windows.
