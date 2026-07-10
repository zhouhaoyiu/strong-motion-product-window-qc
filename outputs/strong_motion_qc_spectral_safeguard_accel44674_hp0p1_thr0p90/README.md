# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
InstanceGM,ALL,23533,75.99541069986827,19.602260655250074,4.402328644881655,88.26,109.52
K-NET,ALL,21141,54.90279551582233,11.371269097961308,33.72593538621636,38.87,70.6
ALL,ALL,44674,66.01378878094641,15.70712271119667,18.27908850785692,60.0,108.63
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
InstanceGM,ALL,product_spectral_safeguard,0.2,23533,19,0.08073768750265584,1.0,0.9999999957386323,0.9999849705092261,88.26
InstanceGM,ALL,product_spectral_safeguard,1.0,23533,343,1.4575277270216291,0.9999998031569852,0.997086083480473,0.9354319410590552,88.26
InstanceGM,ALL,product_spectral_safeguard,3.0,23533,1459,6.199804529809204,0.9997277608759272,0.9416215121534054,0.908918606754794,88.26
K-NET,ALL,product_spectral_safeguard,0.2,21141,0,0.0,1.0,0.9999997212487136,0.9999678346729942,38.87
K-NET,ALL,product_spectral_safeguard,1.0,21141,121,0.5723475710704319,1.0,0.99813319398963,0.9790846597950088,38.87
K-NET,ALL,product_spectral_safeguard,3.0,21141,1088,5.146397994418429,1.0,0.9489961393783972,0.912583572162131,38.87
ALL,ALL,product_spectral_safeguard,0.2,44674,19,0.04253033084120517,1.0,0.999999932167563,0.9999742805491897,60.0
ALL,ALL,product_spectral_safeguard,1.0,44674,464,1.038635447911537,0.9999998877684999,0.9978387575836205,0.9488403195112778,60.0
ALL,ALL,product_spectral_safeguard,3.0,44674,2547,5.70130277118682,0.9998612780867232,0.9450415356286626,0.9105486051437315,60.0
```
