#!/usr/bin/env python3
"""Freeze the record set used for end-to-end high-pass sensitivity checks."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--worklist",
        default="outputs/strong_motion_qc_worklist_accel45652/waveform_qc_worklist.csv",
    )
    parser.add_argument(
        "--reference-response",
        default="outputs/strong_motion_qc_response_spectrum_filter_sensitivity_hp0p1_sample/response_spectrum_retention.csv",
    )
    parser.add_argument(
        "--outdir",
        default="outputs/strong_motion_qc_filter_sensitivity_sample1521",
    )
    return parser.parse_args()


def freeze_sample(worklist: pd.DataFrame, response: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    record_ids = response["record_uid"].astype(str).drop_duplicates()
    sample = worklist[worklist["record_uid"].astype(str).isin(set(record_ids))].copy()
    if sample["record_uid"].astype(str).duplicated().any():
        raise ValueError("worklist contains duplicate record_uid values")
    missing = sorted(set(record_ids) - set(sample["record_uid"].astype(str)))
    if missing:
        raise ValueError(f"{len(missing)} reference records are absent from the worklist")
    if len(sample) != len(record_ids):
        raise ValueError(f"expected {len(record_ids)} records, found {len(sample)}")
    summary = (
        sample.groupby(["dataset", "priority_group"], dropna=False)
        .size()
        .rename("records")
        .reset_index()
    )
    return sample, summary


def main() -> None:
    args = parse_args()
    worklist = pd.read_csv(args.worklist, low_memory=False)
    response = pd.read_csv(args.reference_response, low_memory=False)
    sample, summary = freeze_sample(worklist, response)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    sample.to_csv(outdir / "waveform_qc_worklist.csv", index=False)
    summary.to_csv(outdir / "summary.csv", index=False)
    print(f"Wrote {(outdir / 'waveform_qc_worklist.csv').resolve()}")
    print(f"Wrote {(outdir / 'summary.csv').resolve()}")


if __name__ == "__main__":
    main()
