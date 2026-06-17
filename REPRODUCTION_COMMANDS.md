# Reproduction Commands

Run from the repository root after installing dependencies.

```bash
python scripts/make_strong_motion_qc_figures.py \
  --selector-summary outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \
  --outdir outputs/strong_motion_qc_figures_knet22119_hp1_inst3000

python scripts/audit_strong_motion_srl_draft.py \
  --draft manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \
  --dataset-summary outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv \
  --selector-summary outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \
  --selector-usage outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv \
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \
  --key-metrics outputs/strong_motion_qc_journal_evidence_packet_knet22119_hp1_inst3000/key_metrics.csv \
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \
  --outdir outputs/strong_motion_qc_srl_draft_audit_knet22119_hp1_inst3000

python scripts/build_strong_motion_srl_latex_package.py --compile

python scripts/check_submission_metadata.py \
  --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv \
  --outdir outputs/strong_motion_qc_srl_submission_metadata

python scripts/build_submission_metadata_worksheet.py \
  --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv \
  --manuscript manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \
  --outdir outputs/strong_motion_qc_srl_submission_metadata

python scripts/evaluate_strong_motion_pgv_retention.py \
  --outdir outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000

python scripts/build_strong_motion_qc_full_manifest.py \
  --skip-instance --skip-knet --include-pnw \
  --outdir outputs/strong_motion_qc_full_manifest_pnw_external

python scripts/build_strong_motion_qc_worklist.py \
  --manifest outputs/strong_motion_qc_full_manifest_pnw_external/strong_motion_qc_full_manifest.csv \
  --include-all-dataset PNWAccelerometers \
  --outdir outputs/strong_motion_qc_worklist_pnw_external

python scripts/compute_strong_motion_qc_features.py \
  --worklist outputs/strong_motion_qc_worklist_pnw_external/waveform_qc_worklist.csv \
  --outdir outputs/strong_motion_qc_waveform_features_pnw_external

python scripts/evaluate_strong_motion_window_stability.py \
  --features outputs/strong_motion_qc_waveform_features_pnw_external/waveform_features.csv \
  --outdir outputs/strong_motion_qc_window_stability_pnw_external

python scripts/evaluate_strong_motion_product_window_selector.py \
  --window-stability outputs/strong_motion_qc_window_stability_pnw_external/window_stability.csv \
  --outdir outputs/strong_motion_qc_product_window_selector_pnw_external

python scripts/evaluate_strong_motion_response_spectrum_retention.py \
  --features outputs/strong_motion_qc_waveform_features_pnw_external/waveform_features.csv \
  --selected-windows outputs/strong_motion_qc_product_window_selector_pnw_external/selected_windows.csv \
  --outdir outputs/strong_motion_qc_response_spectrum_pnw_external \
  --policies feature_onset_fixed energy_onset_fixed catalog_p_fixed adaptive_energy_end shortest_stable_no_catalog

python scripts/build_strong_motion_product_production_case.py \
  --outdir outputs/strong_motion_qc_product_production_case

python scripts/build_strong_motion_record_audit_packet.py \
  --outdir outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000
```

Run focused tests:

```bash
python -m unittest \
  tests.test_make_strong_motion_qc_figures \
  tests.test_audit_strong_motion_srl_draft \
  tests.test_build_strong_motion_srl_readiness_report \
  tests.test_build_strong_motion_srl_submission_packet \
  tests.test_build_submission_metadata_worksheet \
  tests.test_check_submission_metadata \
  tests.test_build_strong_motion_record_audit_packet \
  tests.test_evaluate_strong_motion_pgv_retention \
  tests.test_evaluate_strong_motion_response_spectrum_retention \
  tests.test_build_strong_motion_product_production_case \
  tests.test_build_strong_motion_qc_full_manifest \
  tests.test_compute_strong_motion_qc_features \
  tests.test_build_strong_motion_qc_worklist
```
