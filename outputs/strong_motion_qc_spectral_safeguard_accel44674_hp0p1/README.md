# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
InstanceGM,ALL,23533,69.26443717333106,24.969192198189777,5.766370628479157,92.0,110.5
K-NET,ALL,21141,49.86046071614398,14.384371600208127,35.75516768364789,44.81,81.0
ALL,ALL,44674,60.08192684783096,19.960155795317185,19.95791735685186,60.0,110.23
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
InstanceGM,ALL,product_spectral_safeguard,0.2,23533,0,0.0,1.0,0.9999999988406751,0.9999920471911043,92.0
InstanceGM,ALL,product_spectral_safeguard,1.0,23533,0,0.0,0.9999999069810518,0.9991116878984767,0.9788963812305077,92.0
InstanceGM,ALL,product_spectral_safeguard,3.0,23533,0,0.0,0.9998507124677428,0.975251810123285,0.9565877129837729,92.0
K-NET,ALL,product_spectral_safeguard,0.2,21141,0,0.0,1.0,0.9999998266885916,0.9999758014846958,44.81
K-NET,ALL,product_spectral_safeguard,1.0,21141,0,0.0,1.0,0.9987500085424368,0.9922217816008924,44.81
K-NET,ALL,product_spectral_safeguard,3.0,21141,0,0.0,1.0,0.9722197970512172,0.9554458128957177,44.81
ALL,ALL,product_spectral_safeguard,0.2,44674,0,0.0,1.0,0.9999999642897139,0.9999825042927615,60.0
ALL,ALL,product_spectral_safeguard,1.0,44674,0,0.0,0.999999977781572,0.9988996402108042,0.9859321421069914,60.0
ALL,ALL,product_spectral_safeguard,3.0,44674,0,0.0,0.9999648278917797,0.9736098353340635,0.9560567007645572,60.0
```
