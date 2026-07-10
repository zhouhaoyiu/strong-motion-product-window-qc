# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
PNWAccelerometers,ALL,6107,32.06156869166531,49.549697068937284,18.388734239397415,150.01,150.01
ALL,ALL,6107,32.06156869166531,49.549697068937284,18.388734239397415,150.01,150.01
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
PNWAccelerometers,ALL,product_spectral_safeguard,0.2,6107,0,0.0,1.0,1.0,0.9999999999999996,150.01
PNWAccelerometers,ALL,product_spectral_safeguard,1.0,6107,0,0.0,1.0,0.9999999999999936,0.9993471010241631,150.01
PNWAccelerometers,ALL,product_spectral_safeguard,3.0,6107,0,0.0,1.0,0.9999999653226606,0.990788311262289,150.01
ALL,ALL,product_spectral_safeguard,0.2,6107,0,0.0,1.0,1.0,0.9999999999999996,150.01
ALL,ALL,product_spectral_safeguard,1.0,6107,0,0.0,1.0,0.9999999999999936,0.9993471010241631,150.01
ALL,ALL,product_spectral_safeguard,3.0,6107,0,0.0,1.0,0.9999999653226606,0.990788311262289,150.01
```
