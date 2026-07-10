# StrongMotion-QC Figures

Publication-oriented figures for the SRL route.

| figure_id | title | manuscript_role | source | boundary |
| --- | --- | --- | --- | --- |
| Fig. 1 | Two-stage product-window audit | Defines candidate generation, amplitude-energy checks, spectral safeguard, and conservative fallback. | `method schematic` | Offline product preparation with the full record available. |
| Fig. 2 | Fixed-duration sensitivity by dataset | Shows how 20-90 s fixed windows remain archive dependent. | `outputs/strong_motion_qc_window_stability_accel44674_hp0p1/summary.csv; outputs/strong_motion_qc_window_stability_pnw_accel6107_hp0p1/summary.csv` | Rates use minimum-component peak retention, three-component energy retention, and component peak-time inclusion. |
| Fig. 3 | Spectral-audit routes and output duration | Reports primary acceptance, energy-window escalation, full-record fallback, and final duration. | `outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/summary.csv; outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/summary.csv` | Routing is determined from full-record product retention. |
| Fig. 4 | PSA retention before and after spectral safeguard | Compares fixed, primary, and safeguarded outputs at three oscillator periods. | `outputs/strong_motion_qc_response_spectrum_accel44674_hp0p1/summary.csv` | Relative PSA retention is evaluated against the full record. |
| Fig. 5 | High-pass filter sensitivity | Shows the 0.05/0.10 Hz effect on 3.0 s PSA failures and full-record fallback. | `outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p05_sample1521/summary.csv; outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p1_sample1521/summary.csv; outputs/strong_motion_qc_spectral_safeguard_filter_sensitivity_e2e_hp0p05_sample1521/summary.csv; outputs/strong_motion_qc_spectral_safeguard_filter_sensitivity_e2e_hp0p1_sample1521/summary.csv` | The same predeclared stratified record sample and windows are compared. |
| Fig. 6 | PNW SNR-stratified external audit | Separates fixed-window, primary-spectrum, and final-fallback behavior by result-blind SNR. | `outputs/strong_motion_qc_pnw_snr_accel6107_hp0p1/summary.csv` | SNR uses catalog timing and waveform amplitudes before window outcomes are joined. |
