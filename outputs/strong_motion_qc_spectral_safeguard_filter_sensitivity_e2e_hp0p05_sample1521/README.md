# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
InstanceGM,ALL,900,71.55555555555554,23.0,5.444444444444444,88.99,109.82249999999999
K-NET,ALL,621,36.39291465378422,15.619967793880837,47.987117552334944,60.0,119.0
ALL,ALL,1521,57.1992110453649,19.986850756081527,22.813938198553583,69.0,111.15
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
InstanceGM,ALL,product_spectral_safeguard,0.2,900,0,0.0,1.0,0.99999999843198,0.999982891990542,88.99
InstanceGM,ALL,product_spectral_safeguard,1.0,900,0,0.0,0.9999999150810019,0.9992501944003686,0.9861567339143782,88.99
InstanceGM,ALL,product_spectral_safeguard,3.0,900,0,0.0,0.9998694335241518,0.9770854472574243,0.9604700273310816,88.99
K-NET,ALL,product_spectral_safeguard,0.2,621,0,0.0,1.0,0.9999996213995505,0.9999779079269933,60.0
K-NET,ALL,product_spectral_safeguard,1.0,621,0,0.0,1.0,0.998579386951504,0.994340627158377,60.0
K-NET,ALL,product_spectral_safeguard,3.0,621,0,0.0,1.0,0.9750428083864844,0.9557371101446122,60.0
ALL,ALL,product_spectral_safeguard,0.2,1521,0,0.0,1.0,0.999999958093515,0.9999782029439522,69.0
ALL,ALL,product_spectral_safeguard,1.0,1521,0,0.0,0.9999999983033652,0.9990070754777822,0.989414247245458,69.0
ALL,ALL,product_spectral_safeguard,3.0,1521,0,0.0,0.9999877602335034,0.9765475514455196,0.9582388363293431,69.0
```
