# PNWAccelerometers SNR-Stratified Audit

SNR is computed before product evaluation from a 20 s pre-P noise interval and a P-to-(S+20 s) signal interval after common acceleration preprocessing.

```csv
snr_bin,records,median_magnitude,median_snr_db,feature_fixed_unstable_pct,full_record_assignment_pct,median_selected_duration_sec,selected_3s_psa_failure_pct,spectral_escalation_pct,spectral_full_record_fallback_pct,median_final_duration_sec
<3 dB,1175,1.49,1.5526720334881574,99.14893617021276,0.0,146.37,50.808510638297875,54.638297872340424,0.6808510638297872,150.01
3-10 dB,2223,1.74,6.126201750944523,99.685110211426,0.0449842555105713,143.35,63.33783175888439,68.55600539811067,0.7647323436797121,150.01
>=10 dB,2709,2.22,17.286149306679842,70.32115171650055,0.0,92.0,66.66666666666666,67.88482834994463,38.648947951273534,150.01
```

The bins use waveform amplitude and catalog timing only. Window-selection and PSA outcomes do not define the strata.
