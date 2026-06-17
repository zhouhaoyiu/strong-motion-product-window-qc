# StrongMotion-QC Product-Production Routing Case

This is a retrospective product-production case built from the same audit outputs used by the manuscript.

- Selected-window policy: `shortest_stable_no_catalog`.
- Long-period review trigger: PSA retention failure at 3 s.
- `stable_window_accept`: selected window passes the product audit and the long-period PSA check.
- `full_record_required`: no shorter candidate passes the product audit; process and store the full record.
- `long_period_psa_review`: selected window passes PGA, energy, and peak-time checks, but the 3.0 s PSA retention check remains below threshold.

The case is an operational routing example. It does not measure human review time.

## Batch Summary

| dataset | production_route | records | pct | full_record_required | long_period_psa_review | median_window_duration_sec | median_psa_retention_3s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | ALL | 59570 | 100.000 | 1097 | 3554 | 42.000 | 1.000 |
| ALL | full_record_required | 1097 | 1.842 | 1097 | 0 | 150.010 | 1.000 |
| ALL | long_period_psa_review | 3554 | 5.966 | 0 | 3554 | 40.730 | 0.857 |
| ALL | stable_window_accept | 54919 | 92.192 | 0 | 0 | 42.000 | 1.000 |
| InstanceGM | ALL | 31344 | 100.000 | 412 | 2012 | 84.945 | 1.000 |
| InstanceGM | full_record_required | 412 | 1.314 | 412 | 0 | 120.000 | 1.000 |
| InstanceGM | long_period_psa_review | 2012 | 6.419 | 0 | 2012 | 42.005 | 0.847 |
| InstanceGM | stable_window_accept | 28920 | 92.266 | 0 | 0 | 86.035 | 1.000 |
| K-NET | ALL | 22119 | 100.000 | 39 | 960 | 24.660 | 1.000 |
| K-NET | full_record_required | 39 | 0.176 | 39 | 0 | 119.000 | 1.000 |
| K-NET | long_period_psa_review | 960 | 4.340 | 0 | 960 | 25.050 | 0.866 |
| K-NET | stable_window_accept | 21120 | 95.484 | 0 | 0 | 24.620 | 1.000 |
| PNWAccelerometers | ALL | 6107 | 100.000 | 646 | 582 | 142.930 | 1.000 |
| PNWAccelerometers | full_record_required | 646 | 10.578 | 646 | 0 | 150.010 | 1.000 |
| PNWAccelerometers | long_period_psa_review | 582 | 9.530 | 0 | 582 | 54.740 | 0.873 |
| PNWAccelerometers | stable_window_accept | 4879 | 79.892 | 0 | 0 | 142.590 | 1.000 |

## Review Queue

Records routed away from direct acceptance: 4651.

## Outputs

- `production_routes.csv`: one row per record with route flags and selected-window metrics.
- `production_route_summary.csv`: route counts by dataset.
- `review_queue.csv`: records requiring full-record processing or long-period PSA review.
