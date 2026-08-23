# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
InstanceGM,ALL,23533,62.911655972464196,29.473505290443207,7.614838737092594,96.54,111.69
K-NET,ALL,21141,42.24019677404096,20.476798637718176,37.28300458824086,54.01,98.71
ALL,ALL,44674,53.129336974526574,25.216009311904013,21.654653713569413,65.17500000000001,111.57
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
InstanceGM,ALL,product_spectral_safeguard,0.2,23533,0,0.0,1.0,0.9999999998081409,0.9999971805890002,96.54
InstanceGM,ALL,product_spectral_safeguard,1.0,23533,0,0.0,0.9999999619447828,0.9996035578195558,0.9945518054324622,96.54
InstanceGM,ALL,product_spectral_safeguard,3.0,23533,0,0.0,0.9999324694556062,0.9890495791972317,0.9825349940181674,96.54
K-NET,ALL,product_spectral_safeguard,0.2,21141,0,0.0,1.0,0.9999999379783302,0.9999840319967268,54.01
K-NET,ALL,product_spectral_safeguard,1.0,21141,0,0.0,1.0,0.9992709673250892,0.9957903172217095,54.01
K-NET,ALL,product_spectral_safeguard,3.0,21141,0,0.0,1.0,0.9881974414561026,0.9818713188001696,54.01
ALL,ALL,product_spectral_safeguard,0.2,44674,0,0.0,1.0,0.999999989743914,0.9999913699591824,65.17500000000001
ALL,ALL,product_spectral_safeguard,1.0,44674,0,0.0,0.9999999994248274,0.9994269623242177,0.9952909548587818,65.17500000000001
ALL,ALL,product_spectral_safeguard,3.0,44674,0,0.0,0.9999981484107915,0.9886186057803467,0.9821615168727064,65.17500000000001
```
