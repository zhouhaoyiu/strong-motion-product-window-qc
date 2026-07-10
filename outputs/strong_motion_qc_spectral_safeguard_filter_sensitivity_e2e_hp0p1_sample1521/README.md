# StrongMotion-QC Spectral Safeguard

The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.

## Window Summary

```csv
dataset,priority_group,records,primary_pct,arias_escalation_pct,full_record_fallback_pct,median_window_duration_sec,p75_window_duration_sec
InstanceGM,ALL,900,70.22222222222221,23.77777777777778,6.0,91.36500000000001,109.98
K-NET,ALL,621,40.41867954911433,15.780998389694043,43.80032206119163,59.0,119.0
ALL,ALL,1521,58.05391190006575,20.51282051282051,21.43326758711374,66.59,111.02
```

## PSA Summary

```csv
dataset,priority_group,policy,period_sec,records,spectrum_unstable_records,spectrum_unstable_pct,median_psa_retention,p05_psa_retention,p01_psa_retention,median_window_duration_sec
InstanceGM,ALL,product_spectral_safeguard,0.2,900,0,0.0,1.0,0.9999999982343456,0.9999951911965014,91.36500000000001
InstanceGM,ALL,product_spectral_safeguard,1.0,900,0,0.0,0.9999999332255665,0.999208926097038,0.9852484494800647,91.36500000000001
InstanceGM,ALL,product_spectral_safeguard,3.0,900,0,0.0,0.9999120533148731,0.979034319433047,0.9622489442911579,91.36500000000001
K-NET,ALL,product_spectral_safeguard,0.2,621,0,0.0,1.0,0.9999995109521166,0.9999697759415606,59.0
K-NET,ALL,product_spectral_safeguard,1.0,621,0,0.0,1.0,0.998259445483927,0.9931193547231382,59.0
K-NET,ALL,product_spectral_safeguard,3.0,621,0,0.0,1.0,0.9748907911478152,0.9591904454643972,59.0
ALL,ALL,product_spectral_safeguard,0.2,1521,0,0.0,1.0,0.999999938869767,0.9999780051857265,66.59
ALL,ALL,product_spectral_safeguard,1.0,1521,0,0.0,0.9999999976753784,0.9986799752092024,0.9880345972619761,66.59
ALL,ALL,product_spectral_safeguard,3.0,1521,0,0.0,0.999986282220429,0.977280514421358,0.9602934453976611,66.59
```
