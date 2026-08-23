# StrongMotion-QC Dataset Table

Compact dataset description for the SRL manuscript route.

## Dataset Summary

| dataset | candidate_records | records | load_error_records | events | stations | loaded_records | catalog_p_records | median_sampling_rate_hz | median_duration_sec | p05_duration_sec | p95_duration_sec | median_magnitude | min_magnitude | max_magnitude |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| InstanceGM | 23533 | 23533 | 0 | 8811 | 299 | 23533 | 23533 | 100.000 | 120.000 | 120.000 | 120.000 | 3.100 | 0.200 | 6.500 |
| K-NET | 22119 | 21141 | 978 | 1528 | 917 | 21141 | 21141 | 100.000 | 119.000 | 60.000 | 120.000 | 4.300 | 2.800 | 8.000 |

## Priority Strata

| dataset | priority_group | records | median_duration_sec | median_magnitude |
| --- | --- | --- | --- | --- |
| InstanceGM | low_magnitude_background | 9000 | 120.000 | 2.200 |
| InstanceGM | m3_to_m4_small_event | 9000 | 120.000 | 3.200 |
| InstanceGM | m4plus_strong_motion | 5533 | 120.000 | 4.200 |
| K-NET | low_magnitude_background | 21 | 60.000 | 2.900 |
| K-NET | m3_to_m4_small_event | 5647 | 119.000 | 3.800 |
| K-NET | m4plus_strong_motion | 15473 | 119.000 | 4.500 |

## Interpretation Boundary

The analysis count includes records that loaded successfully. Candidate and load-error counts preserve the pre-analysis sample flow. These counts are not the full underlying InstanceGM or K-NET archive sizes.
