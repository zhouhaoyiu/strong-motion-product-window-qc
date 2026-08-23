# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
PNWAccelerometers,ALL,6107,38.07106598984771,45.226788930735225,16.702145079417065,150.01,150.01
ALL,ALL,6107,38.07106598984771,45.226788930735225,16.702145079417065,150.01,150.01
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
PNWAccelerometers,ALL,product_spectral_safeguard,0.2,6107,4,0.06549860815457671,1.0,1.0,0.9999999978317472,150.01
PNWAccelerometers,ALL,product_spectral_safeguard,1.0,6107,76,1.2444735549369577,1.0,0.999944070857576,0.9389248974213747,150.01
PNWAccelerometers,ALL,product_spectral_safeguard,3.0,6107,199,3.2585557556901916,1.0,0.9732537163933581,0.9155945261424892,150.01
ALL,ALL,product_spectral_safeguard,0.2,6107,4,0.06549860815457671,1.0,1.0,0.9999999978317472,150.01
ALL,ALL,product_spectral_safeguard,1.0,6107,76,1.2444735549369577,1.0,0.999944070857576,0.9389248974213747,150.01
ALL,ALL,product_spectral_safeguard,3.0,6107,199,3.2585557556901916,1.0,0.9732537163933581,0.9155945261424892,150.01
```
