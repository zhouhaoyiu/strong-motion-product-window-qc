#!/usr/bin/env python3
"""Build a lightweight reproducibility-release package for the StrongMotion-QC SRL route."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTDIR = "outputs/strong_motion_qc_srl_reproducibility_release_current"


CODE_FILES = [
    "requirements.txt",
    "strong_motion_qc/__init__.py",
    "strong_motion_qc/config.py",
    "strong_motion_qc/onset.py",
    "strong_motion_qc/features.py",
    "scripts/build_strong_motion_qc_full_manifest.py",
    "scripts/build_strong_motion_qc_worklist.py",
    "scripts/compute_strong_motion_qc_features.py",
    "scripts/evaluate_strong_motion_window_stability.py",
    "scripts/evaluate_strong_motion_product_window_selector.py",
    "scripts/analyze_strong_motion_window_product_impact.py",
    "scripts/evaluate_strong_motion_selector_sensitivity.py",
    "scripts/evaluate_strong_motion_response_spectrum_retention.py",
    "scripts/evaluate_strong_motion_pgv_retention.py",
    "scripts/build_strong_motion_record_audit_packet.py",
    "scripts/build_strong_motion_qc_dataset_table.py",
    "scripts/make_strong_motion_qc_figures.py",
    "scripts/audit_strong_motion_srl_draft.py",
    "scripts/check_submission_metadata.py",
    "scripts/build_submission_metadata_worksheet.py",
    "scripts/build_strong_motion_srl_latex_package.py",
    "scripts/build_strong_motion_srl_readiness_report.py",
    "scripts/build_strong_motion_srl_submission_packet.py",
    "scripts/build_strong_motion_srl_reproducibility_release.py",
    "docs/strong_motion_qc_srl_submission_metadata_template.csv",
    "docs/strong_motion_qc_srl_reference_verification.md",
]

TEST_FILES = [
    "tests/test_strong_motion_qc.py",
    "tests/test_build_strong_motion_qc_full_manifest.py",
    "tests/test_build_strong_motion_qc_worklist.py",
    "tests/test_compute_strong_motion_qc_features.py",
    "tests/test_evaluate_strong_motion_window_stability.py",
    "tests/test_evaluate_strong_motion_product_window_selector.py",
    "tests/test_analyze_strong_motion_window_product_impact.py",
    "tests/test_evaluate_strong_motion_selector_sensitivity.py",
    "tests/test_evaluate_strong_motion_response_spectrum_retention.py",
    "tests/test_evaluate_strong_motion_pgv_retention.py",
    "tests/test_build_strong_motion_record_audit_packet.py",
    "tests/test_build_strong_motion_qc_dataset_table.py",
    "tests/test_make_strong_motion_qc_figures.py",
    "tests/test_audit_strong_motion_srl_draft.py",
    "tests/test_check_submission_metadata.py",
    "tests/test_build_submission_metadata_worksheet.py",
    "tests/test_build_strong_motion_srl_readiness_report.py",
    "tests/test_build_strong_motion_srl_submission_packet.py",
]

SUMMARY_FILES = [
    ("outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv", "derived_summaries/dataset_summary.csv"),
    ("outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/priority_strata_summary.csv", "derived_summaries/priority_strata_summary.csv"),
    ("outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv", "derived_summaries/product_window_selector_summary.csv"),
    ("outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv", "derived_summaries/selector_candidate_usage.csv"),
    ("outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv", "derived_summaries/product_impact_summary.csv"),
    ("outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv", "derived_summaries/selector_sensitivity_summary.csv"),
    ("outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv", "derived_summaries/response_spectrum_summary.csv"),
    ("outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000/summary.csv", "derived_summaries/pgv_retention_summary.csv"),
    ("outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000/README.md", "derived_summaries/pgv_retention_README.md"),
    ("outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000/load_errors.csv", "derived_summaries/pgv_retention_load_errors.csv"),
    ("outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000/README.md", "record_audit/README.md"),
    ("outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000/cases.csv", "record_audit/cases.csv"),
    ("outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000/case_windows.csv", "record_audit/case_windows.csv"),
    ("outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000/plot_manifest.csv", "record_audit/plot_manifest.csv"),
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/figure_manifest.csv", "derived_summaries/figure_manifest.csv"),
    ("manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md", "manuscript/strong_motion_qc_srl_draft.md"),
    ("manuscripts/strong_motion_qc_srl/main.tex", "manuscript/main.tex"),
    ("manuscripts/strong_motion_qc_srl/main.pdf", "manuscript/main.pdf"),
]

FIGURE_FILES = [
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/smqc_figure_01_workflow.pdf", "figures/smqc_figure_01_workflow.pdf"),
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/smqc_figure_02_fixed_window_failure.pdf", "figures/smqc_figure_02_fixed_window_failure.pdf"),
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/smqc_figure_03_selector_duration_fallback.pdf", "figures/smqc_figure_03_selector_duration_fallback.pdf"),
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/smqc_figure_04_product_impact_recovery.pdf", "figures/smqc_figure_04_product_impact_recovery.pdf"),
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/smqc_figure_05_threshold_sensitivity.pdf", "figures/smqc_figure_05_threshold_sensitivity.pdf"),
    ("outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/smqc_figure_06_response_spectrum_retention.pdf", "figures/smqc_figure_06_response_spectrum_retention.pdf"),
]


@dataclass(frozen=True)
class FileEntry:
    source: Path
    target: Path
    category: str
    required: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_entry(entry: FileEntry, outdir: Path) -> dict[str, str]:
    target = outdir / entry.target
    status = "copied"
    checksum = ""
    size_bytes = ""
    if not entry.source.exists():
        status = "missing_required" if entry.required else "missing_optional"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(entry.source, target)
        checksum = sha256(target)
        size_bytes = str(target.stat().st_size)
    return {
        "status": status,
        "category": entry.category,
        "source": str(entry.source),
        "target": str(entry.target),
        "size_bytes": size_bytes,
        "sha256": checksum,
    }


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n")


def license_text() -> str:
    return """
# StrongMotion-QC SRL Reproducibility Release License

Copyright (c) 2026 Haoyu Zhou and Qiang Ma

## Code

The code files in `code/` and the focused tests in `tests/` are released under
the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Derived Summary Artifacts

The derived summary tables, figure PDFs, record-audit plots, manuscript-support
metadata, and documentation included in this release are released under the
Creative Commons Attribution 4.0 International License (CC BY 4.0), unless a
file states a different license.

## Third-Party Data Boundary

Raw InstanceGM/INSTANCE and K-NET waveform archives are not redistributed in
this release. Those data remain governed by their original provider terms,
citation requirements, and access conditions.
"""


def archive_metadata_template_text() -> str:
    return """
# Public Archive Metadata

Use this file as the public repository and release metadata summary.

## Recommended Title

StrongMotion-QC SRL Reproducibility Release for "Auditable Product-Stable Window
Selection for Strong-Motion Records"

## Creators

- Haoyu Zhou
- Qiang Ma

## Description

This archive supports the manuscript "Auditable Product-Stable Window Selection
for Strong-Motion Records". It contains code, focused tests, compact derived
summary tables, manuscript figures, record-level audit cases, the manuscript
PDF/source files, checksums, and data-source boundary notes. Raw waveform
archives are excluded and should be obtained from their public providers.

## Keywords

strong-motion records; processing windows; ground-motion products; response
spectra; engineering seismology; reproducible audit

## License Statement

Code and tests: MIT License. Derived summary tables, figures, record-audit
plots, manuscript-support metadata, and documentation: CC BY 4.0. Raw
InstanceGM/INSTANCE and K-NET waveform archives are excluded and remain subject
to provider terms.

## Data and Resource Access Dates

- InstanceGM/INSTANCE accessed: 2026-06-16
- K-NET/NIED accessed: 2026-06-16
- Final public archive created/accessed: 2026-06-16

## Related Identifiers

- Manuscript: [journal DOI after acceptance, if available]
- INSTANCE article: https://doi.org/10.5194/essd-13-5509-2021
- INSTANCE dataset: https://doi.org/10.13127/INSTANCE
- NIED K-NET, KiK-net: https://doi.org/10.17598/NIED.0004
- Public GitHub release: https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.1.0

## Files To Include

- `strong_motion_qc_srl_reproducibility_release_current.zip`
- `README.md`
- `REPRODUCTION_COMMANDS.md`
- `LICENSE`
- `metadata/file_checksums.csv`
- `metadata/data_source_manifest.csv`
"""


def readme_text() -> str:
    return """
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
- `ARCHIVE_METADATA_TEMPLATE.md`: final public-archive metadata template.

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
"""


def data_source_rows() -> list[dict[str, str]]:
    return [
        {
            "dataset_or_artifact": "InstanceGM / INSTANCE",
            "status": "public_source_required",
            "included_in_release": "no raw waveforms",
            "notes": "Use public provider access; release includes derived manuscript summaries only.",
        },
        {
            "dataset_or_artifact": "K-NET",
            "status": "public_source_required",
            "included_in_release": "no raw waveforms",
            "notes": "Use NIED K-NET access; local workflow uses explicit UD->Z, NS->N, EW->E mapping and 1 Hz high-pass feature preprocessing.",
        },
        {
            "dataset_or_artifact": "Manuscript summary CSVs",
            "status": "included",
            "included_in_release": "yes",
            "notes": "Compact tables used to reproduce manuscript numbers, figures, and audits.",
        },
        {
            "dataset_or_artifact": "Record-level response-spectrum retention CSV",
            "status": "large_intermediate",
            "included_in_release": "summary only",
            "notes": "The full record-level CSV is large; included summary reproduces manuscript claims.",
        },
        {
            "dataset_or_artifact": "Relative PGV-retention audit",
            "status": "supplemental_summary_included",
            "included_in_release": "summary and load-error boundary",
            "notes": "This is a relative peak-vector-velocity retention proxy, not an absolute PGV product release.",
        },
        {
            "dataset_or_artifact": "Representative record-level audit packet",
            "status": "included",
            "included_in_release": "case tables and generated plots",
            "notes": "Representative cases support reviewability while preserving the statistical denominator.",
        },
        {
            "dataset_or_artifact": "Converted K-NET HDF5",
            "status": "large_local_intermediate",
            "included_in_release": "no",
            "notes": "Regenerate from K-NET source files with documented component mapping before full reruns.",
        },
    ]


def commands_text() -> str:
    return """
# Reproduction Commands

Run from the repository root after installing dependencies.

```bash
python scripts/make_strong_motion_qc_figures.py \\
  --selector-summary outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \\
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \\
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \\
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \\
  --outdir outputs/strong_motion_qc_figures_knet22119_hp1_inst3000

python scripts/audit_strong_motion_srl_draft.py \\
  --draft manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \\
  --dataset-summary outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv \\
  --selector-summary outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \\
  --selector-usage outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv \\
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \\
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \\
  --key-metrics outputs/strong_motion_qc_journal_evidence_packet_knet22119_hp1_inst3000/key_metrics.csv \\
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \\
  --outdir outputs/strong_motion_qc_srl_draft_audit_knet22119_hp1_inst3000

python scripts/build_strong_motion_srl_latex_package.py --compile

python scripts/check_submission_metadata.py \\
  --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv \\
  --outdir outputs/strong_motion_qc_srl_submission_metadata

python scripts/build_submission_metadata_worksheet.py \\
  --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv \\
  --manuscript manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \\
  --outdir outputs/strong_motion_qc_srl_submission_metadata

python scripts/evaluate_strong_motion_pgv_retention.py \\
  --outdir outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000

python scripts/build_strong_motion_record_audit_packet.py \\
  --outdir outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000
```

Run focused tests:

```bash
python -m unittest \\
  tests.test_make_strong_motion_qc_figures \\
  tests.test_audit_strong_motion_srl_draft \\
  tests.test_build_strong_motion_srl_readiness_report \\
  tests.test_build_strong_motion_srl_submission_packet \\
  tests.test_build_submission_metadata_worksheet \\
  tests.test_check_submission_metadata \\
  tests.test_build_strong_motion_record_audit_packet \\
  tests.test_evaluate_strong_motion_pgv_retention \\
  tests.test_evaluate_strong_motion_response_spectrum_retention \\
  tests.test_build_strong_motion_qc_full_manifest \\
  tests.test_compute_strong_motion_qc_features \\
  tests.test_build_strong_motion_qc_worklist
```
"""


def release_entries() -> list[FileEntry]:
    entries: list[FileEntry] = []
    for path in CODE_FILES:
        source = Path(path)
        entries.append(FileEntry(source=source, target=Path("code") / source, category="code"))
    for path in TEST_FILES:
        source = Path(path)
        entries.append(FileEntry(source=source, target=Path("tests") / source.name, category="tests"))
    for source, target in SUMMARY_FILES:
        entries.append(FileEntry(source=Path(source), target=Path(target), category="derived_summary"))
    for source, target in FIGURE_FILES:
        entries.append(FileEntry(source=Path(source), target=Path(target), category="figure"))
    for source in sorted(Path("outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000/figures").glob("case_*.*")):
        if source.suffix.lower() in {".png", ".pdf"}:
            entries.append(FileEntry(source=source, target=Path("record_audit/figures") / source.name, category="record_audit_figure"))
    return entries


def zip_release(outdir: Path) -> Path:
    zip_path = outdir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(outdir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(outdir.parent))
    return zip_path


def build_release(outdir: Path) -> dict[str, str | int]:
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    rows = [copy_entry(entry, outdir) for entry in release_entries()]
    write_text(outdir / "README.md", readme_text())
    write_text(outdir / "REPRODUCTION_COMMANDS.md", commands_text())
    write_text(outdir / "LICENSE", license_text())
    write_text(outdir / "ARCHIVE_METADATA_TEMPLATE.md", archive_metadata_template_text())
    rows.extend(
        [
            {
                "status": "generated",
                "category": "metadata",
                "source": "script",
                "target": "README.md",
                "size_bytes": str((outdir / "README.md").stat().st_size),
                "sha256": sha256(outdir / "README.md"),
            },
            {
                "status": "generated",
                "category": "metadata",
                "source": "script",
                "target": "REPRODUCTION_COMMANDS.md",
                "size_bytes": str((outdir / "REPRODUCTION_COMMANDS.md").stat().st_size),
                "sha256": sha256(outdir / "REPRODUCTION_COMMANDS.md"),
            },
            {
                "status": "generated",
                "category": "metadata",
                "source": "script",
                "target": "LICENSE",
                "size_bytes": str((outdir / "LICENSE").stat().st_size),
                "sha256": sha256(outdir / "LICENSE"),
            },
            {
                "status": "generated",
                "category": "metadata",
                "source": "script",
                "target": "ARCHIVE_METADATA_TEMPLATE.md",
                "size_bytes": str((outdir / "ARCHIVE_METADATA_TEMPLATE.md").stat().st_size),
                "sha256": sha256(outdir / "ARCHIVE_METADATA_TEMPLATE.md"),
            },
        ]
    )
    write_csv(
        outdir / "metadata/data_source_manifest.csv",
        data_source_rows(),
        ["dataset_or_artifact", "status", "included_in_release", "notes"],
    )
    rows.append(
        {
            "status": "generated",
            "category": "metadata",
            "source": "script",
            "target": "metadata/data_source_manifest.csv",
            "size_bytes": str((outdir / "metadata/data_source_manifest.csv").stat().st_size),
            "sha256": sha256(outdir / "metadata/data_source_manifest.csv"),
        }
    )
    write_csv(outdir / "metadata/file_checksums.csv", rows, ["status", "category", "source", "target", "size_bytes", "sha256"])
    missing = sum(1 for row in rows if row["status"] not in {"copied", "generated"})
    zip_path = zip_release(outdir)
    return {"outdir": str(outdir), "zip": str(zip_path), "entries": len(rows), "missing": missing}


def main() -> None:
    args = parse_args()
    result = build_release(Path(args.outdir))
    print(f"Wrote {Path(result['outdir']).resolve()}")
    print(f"Wrote {Path(result['zip']).resolve()}")
    print(f"Entries: {result['entries']}; missing required: {result['missing']}")
    if result["missing"]:
        raise SystemExit("Release package has missing required files")


if __name__ == "__main__":
    main()
