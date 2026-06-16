# StrongMotion-QC SRL Reproducibility Release

This lightweight release supports the manuscript "Auditable Product-Stable Window Selection for Strong-Motion Records".

## Contents

- `code/`: analysis scripts and the `strong_motion_qc` package needed to rebuild the workflow.
- `tests/`: focused tests for the strong-motion manuscript route.
- `derived_summaries/`: compact CSV summaries used by the manuscript, figures, and audits.
- `figures/`: manuscript figure PDFs.
- `manuscript/`: Markdown, LaTeX, and PDF manuscript files.
- `record_audit/`: representative record-level case metrics and waveform-window plots.
- `metadata/file_checksums.csv`: SHA-256 checksums for copied release files.
- `metadata/data_source_manifest.csv`: data-source and upload-boundary notes.
- `LICENSE`: license boundary for code, derived summaries, and third-party data.
- `ARCHIVE_METADATA_TEMPLATE.md`: public archive metadata summary.

## Data Boundary

Raw waveform archives are excluded from this release. InstanceGM/INSTANCE and K-NET records should be obtained from their public data providers under the providers' access terms. Large intermediate record-level CSV/HDF5 artifacts are regenerated from those public sources and local conversion steps.

## License Boundary

Code and focused tests are prepared for MIT release. Derived summary tables,
figures, record-audit plots, manuscript-support metadata, and documentation are
prepared for CC BY 4.0 release. Raw third-party waveform archives are excluded
and remain under their provider terms.

## Main Rebuild Path

Create a Python environment with `requirements.txt`, or use an equivalent local
environment that provides the listed packages.

The manuscript-level numbers and figures can be regenerated from the compact summary CSVs included here. Full waveform-level reruns require the public waveform archives and the K-NET converted HDF5 path used by the local workflow.
