# Reproduction Note

The packet contains the compact summary tables used by the manuscript. From the repository root, the figures, review PDFs, and packet are rebuilt with:

```bash
python scripts/make_strong_motion_qc_figures.py
python scripts/make_strong_motion_qc_figures.py --language zh --outdir outputs/strong_motion_qc_figures_accel44674_hp0p1_zh
python scripts/build_strong_motion_srl_latex_package.py --compile
python scripts/build_strong_motion_srl_chinese_latex.py --compile
python scripts/build_strong_motion_srl_submission_packet.py
python scripts/check_strong_motion_srl_submission_compliance.py
```

The full analysis and a rerun of `scripts/audit_strong_motion_qc_revised_evidence.py` require provider-authorized copies of InstanceGM, K-NET, and PNWAccelerometers plus the record-level feature, window, and response-spectrum tables. The archived evidence report verifies record counts, component-level peak and PSA definitions, tested periods, five-cycle oscillator ringdown, safeguard grain, filter-sample identity, PNW SNR summaries, manuscript key numbers, and stale-result markers.
