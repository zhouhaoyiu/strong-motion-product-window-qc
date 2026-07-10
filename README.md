# StrongMotion-QC

StrongMotion-QC audits whether a proposed processing window preserves the strong-motion products calculated from the available full record. The current study targets offline archive preparation and batch product generation.

## Method

The audit has two stages:

1. Select the shortest waveform-derived candidate that retains at least 99% of every component peak, at least 95% of the three-component squared-motion integral, and every component peak time.
2. Check the minimum component-wise retention of 5%-damped pseudo-spectral acceleration at 0.2, 1.0, and 3.0 s. Failed records move to a padded 1%-99% cumulative-energy window and then to the full record if needed.

The final output includes the selected sample bounds, candidate source, product-retention values, spectral route, and preprocessing settings.

## Evidence

- Main analysis: 44,674 three-component acceleration records from InstanceGM and K-NET.
- External analysis: 6,107 PNWAccelerometers records.
- Common preprocessing: linear detrend and fourth-order zero-phase 0.1 Hz high-pass filter.
- Final main routing at a 0.95 PSA-retention threshold: 60.08% primary window, 19.96% energy-percentile window, and 19.96% full record.
- Current evidence audit: 44 checks passed, 0 failed.

The manuscript does not evaluate phase picking, real-time warning latency, or operator-time reduction.

## Rebuild from Included Summaries

The tested local environment is the `zhy` Conda environment. Equivalent Python environments can install the packages in `requirements.txt`.

```bash
conda run -n zhy python scripts/make_strong_motion_qc_figures.py
conda run -n zhy python scripts/make_strong_motion_qc_figures.py \
  --language zh \
  --outdir outputs/strong_motion_qc_figures_accel44674_hp0p1_zh
conda run -n zhy python scripts/build_strong_motion_srl_latex_package.py --compile
conda run -n zhy python scripts/build_strong_motion_srl_chinese_latex.py --compile
conda run -n zhy python scripts/build_strong_motion_srl_submission_packet.py
conda run -n zhy python scripts/check_strong_motion_srl_submission_compliance.py
```

`pandoc` and a TeX Live installation with `pdflatex` and `xelatex` are required to build both PDFs.

The public repository contains compact summary tables for these commands. A full rerun of `scripts/audit_strong_motion_qc_revised_evidence.py` also requires provider-authorized waveforms and the record-level feature, window, and response-spectrum tables generated from them. The archived audit report records the checks applied to those full tables.

## Verification

```bash
conda run -n zhy python -m unittest \
  tests/test_build_strong_motion_srl_submission_packet.py \
  tests/test_build_strong_motion_srl_latex_package.py \
  tests/test_build_strong_motion_srl_chinese_latex.py \
  tests/test_make_strong_motion_qc_figures.py \
  tests/test_evaluate_strong_motion_response_spectrum_retention.py \
  tests/test_build_strong_motion_qc_filter_sensitivity_sample.py
```

## Main Files

- Versioned public archive: `https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.2.0`
- English manuscript: `manuscripts/strong_motion_qc_srl/qc.pdf`
- Chinese advisor manuscript: `manuscripts/strong_motion_qc_srl_zh/qc_chinese.pdf`
- Evidence audit: `outputs/strong_motion_qc_revised_evidence_audit/README.md`
- Submission-review packet: `outputs/strong_motion_qc_srl_submission_packet_current.zip`
- Reference verification: `docs/strong_motion_qc_srl_reference_verification.md`
- Core feature and window code: `strong_motion_qc/` and `scripts/`

## Data

- InstanceGM/INSTANCE: `https://doi.org/10.13127/INSTANCE`, accessed 16 June 2026.
- NIED K-NET: `https://doi.org/10.17598/NIED.0004`, accessed 16 June 2026.
- PNWAccelerometers through SeisBench, accessed 18 June 2026; dataset article: `https://doi.org/10.26443/seismica.v2i1.368`.

Raw waveforms are not redistributed. Users must obtain them from the providers and follow the corresponding terms of use.

## Licenses

Source code and tests are released under the MIT License in `LICENSE`. Derived tables, figures, and documentation are released under CC BY 4.0 as stated in `LICENSE-DATA`.
