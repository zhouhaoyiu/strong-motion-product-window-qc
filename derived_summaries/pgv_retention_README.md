# StrongMotion-QC Relative PGV Retention

This diagnostic compares a peak-vector-velocity proxy inside each processing window with the same proxy computed on the full record.

## Summary

| dataset | priority_group | policy | records | pgv_unstable_records | pgv_unstable_pct | median_pgv_retention | p05_pgv_retention | p01_pgv_retention | median_window_duration_sec | direct_velocity_records | integrated_acceleration_records | integrated_knet_acceleration_records | unknown_units_direct_records |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| InstanceGM | ALL | adaptive_energy_end | 31344 | 175 | 0.558 | 1.000 | 1.000 | 1.000 | 84.120 | 22830 | 8514 | 0 | 0 |
| InstanceGM | ALL | catalog_p_fixed | 31344 | 5256 | 16.769 | 1.000 | 0.544 | 0.252 | 42.000 | 22830 | 8514 | 0 | 0 |
| InstanceGM | ALL | energy_onset_fixed | 31344 | 5330 | 17.005 | 1.000 | 0.577 | 0.308 | 42.000 | 22830 | 8514 | 0 | 0 |
| InstanceGM | ALL | feature_onset_fixed | 31344 | 8727 | 27.843 | 1.000 | 0.352 | 0.175 | 42.000 | 22830 | 8514 | 0 | 0 |
| InstanceGM | ALL | shortest_stable_no_catalog | 31344 | 174 | 0.555 | 1.000 | 1.000 | 1.000 | 84.945 | 22830 | 8514 | 0 | 0 |
| K-NET | ALL | adaptive_energy_end | 21141 | 2 | 0.009 | 1.000 | 1.000 | 1.000 | 24.430 | 0 | 0 | 21141 | 0 |
| K-NET | ALL | catalog_p_fixed | 21141 | 29 | 0.137 | 1.000 | 1.000 | 1.000 | 42.000 | 0 | 0 | 21141 | 0 |
| K-NET | ALL | energy_onset_fixed | 21141 | 6 | 0.028 | 1.000 | 1.000 | 1.000 | 42.000 | 0 | 0 | 21141 | 0 |
| K-NET | ALL | feature_onset_fixed | 21141 | 31 | 0.147 | 1.000 | 1.000 | 1.000 | 42.000 | 0 | 0 | 21141 | 0 |
| K-NET | ALL | shortest_stable_no_catalog | 21141 | 1 | 0.005 | 1.000 | 1.000 | 1.000 | 24.430 | 0 | 0 | 21141 | 0 |
| ALL | ALL | adaptive_energy_end | 52485 | 177 | 0.337 | 1.000 | 1.000 | 1.000 | 45.080 | 22830 | 8514 | 21141 | 0 |
| ALL | ALL | catalog_p_fixed | 52485 | 5285 | 10.070 | 1.000 | 0.695 | 0.324 | 42.000 | 22830 | 8514 | 21141 | 0 |
| ALL | ALL | energy_onset_fixed | 52485 | 5336 | 10.167 | 1.000 | 0.709 | 0.378 | 42.000 | 22830 | 8514 | 21141 | 0 |
| ALL | ALL | feature_onset_fixed | 52485 | 8758 | 16.687 | 1.000 | 0.452 | 0.223 | 42.000 | 22830 | 8514 | 21141 | 0 |
| ALL | ALL | shortest_stable_no_catalog | 52485 | 175 | 0.333 | 1.000 | 1.000 | 1.000 | 42.000 | 22830 | 8514 | 21141 | 0 |

## Outputs

- `pgv_retention.csv`: per-record, per-policy relative PGV-retention proxy.
- `summary.csv`: grouped PGV-retention summary.

## Boundary

This is a relative retention audit, not an absolute PGV product release. Records already in velocity units use the waveform directly. Acceleration records use demeaned acceleration, trapezoidal integration, and linear velocity detrending before the retention ratio is computed. The ratio is useful for checking whether a window contains the full-record peak velocity proxy; final manuscript use should keep this unit-processing boundary visible.
