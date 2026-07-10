#!/usr/bin/env python3
"""Check SRL submission-readiness constraints for the StrongMotion-QC route."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import pandas as pd


DEFAULT_DRAFT = "manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md"
DEFAULT_TEX = "manuscripts/strong_motion_qc_srl/main.tex"
DEFAULT_PDF = "manuscripts/strong_motion_qc_srl/main.pdf"
DEFAULT_PACKET = "outputs/strong_motion_qc_srl_submission_packet_current.zip"
DEFAULT_RELEASE = DEFAULT_PACKET
DEFAULT_OUTDIR = "outputs/strong_motion_qc_srl_compliance"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", default=DEFAULT_DRAFT)
    parser.add_argument("--tex", default=DEFAULT_TEX)
    parser.add_argument("--pdf", default=DEFAULT_PDF)
    parser.add_argument("--packet", default=DEFAULT_PACKET)
    parser.add_argument("--release", default=DEFAULT_RELEASE)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def section(markdown: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, markdown, flags=re.MULTILINE)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", markdown[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(markdown)
    return markdown[match.end() : end].strip()


def word_count(text: str) -> int:
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[$\\{}_\^]", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def pdf_info(pdf_path: Path) -> dict[str, str]:
    proc = subprocess.run(["pdfinfo", str(pdf_path)], text=True, check=True, stdout=subprocess.PIPE)
    info: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
    return info


def count_markdown_labels(markdown: str, prefix: str) -> int:
    return len(set(re.findall(rf"\b{prefix}\s+([0-9]+)\b", markdown)))


def add_check(
    rows: list[dict[str, object]],
    check_id: str,
    status: str,
    evidence: str,
    requirement: str,
) -> None:
    rows.append(
        {
            "check_id": check_id,
            "status": status,
            "evidence": evidence,
            "requirement": requirement,
        }
    )


def build_checks(draft_path: Path, tex_path: Path, pdf_path: Path, packet_path: Path, release_path: Path) -> pd.DataFrame:
    markdown = draft_path.read_text()
    tex = tex_path.read_text()
    info = pdf_info(pdf_path)
    rows: list[dict[str, object]] = []

    abstract_words = word_count(section(markdown, "Abstract"))
    full_words = word_count(re.split(r"\n## Figure Captions\n", markdown, maxsplit=1)[0])
    figure_count = count_markdown_labels(markdown, "Figure")
    table_count = count_markdown_labels(markdown, "Table")
    alt_text_count = max(
        len(re.findall(r"^Alt text:", markdown, flags=re.MULTILINE)),
        len(re.findall(r"\\textbf\{Alt text:\}", tex)),
    )
    pages = int(info.get("Pages", "0"))
    page_size = info.get("Page size", "")

    add_check(
        rows,
        "abstract_length",
        "PASS" if abstract_words <= 300 else "FAIL",
        f"{abstract_words} words",
        "SRL abstracts should be 300 words or less.",
    )
    add_check(
        rows,
        "regular_article_length",
        "PASS" if full_words <= 6000 else "WARN",
        f"{full_words} manuscript words before figure/table captions",
        "Regular SRL articles are recommended at 6000 words.",
    )
    add_check(
        rows,
        "figure_count",
        "PASS" if figure_count <= 10 else "WARN",
        f"{figure_count} figures",
        "Regular SRL articles are recommended at 10 figures.",
    )
    add_check(
        rows,
        "table_count",
        "PASS" if table_count <= 3 else "WARN",
        f"{table_count} tables",
        "Regular SRL articles are recommended at 3 tables; higher counts may be accepted at editor discretion.",
    )
    add_check(
        rows,
        "figure_alt_text",
        "PASS" if figure_count > 0 and alt_text_count >= figure_count else "WARN",
        f"{alt_text_count} alt-text entries for {figure_count} figures",
        "SRL asks authors to provide alt-text on a separate line after each figure caption.",
    )
    add_check(
        rows,
        "pdf_letter_size",
        "PASS" if "612 x 792 pts" in page_size else "FAIL",
        page_size,
        "All pages should use standard U.S. letter size.",
    )
    add_check(
        rows,
        "pdf_pages_present",
        "PASS" if pages > 0 else "FAIL",
        f"{pages} pages",
        "The review manuscript PDF should compile.",
    )
    add_check(
        rows,
        "one_inch_margins",
        "PASS" if r"\usepackage[margin=1in]{geometry}" in tex else "FAIL",
        "geometry margin=1in" if r"\usepackage[margin=1in]{geometry}" in tex else "missing",
        "SRL requests one-inch margins.",
    )
    add_check(
        rows,
        "font_size",
        "PASS" if r"\documentclass[12pt,letterpaper]{article}" in tex else "FAIL",
        "12pt letter article" if r"\documentclass[12pt,letterpaper]{article}" in tex else "missing",
        "SRL requests 12-point font size.",
    )
    add_check(
        rows,
        "double_spacing",
        "PASS" if r"\doublespacing" in tex else "FAIL",
        "doublespacing command present" if r"\doublespacing" in tex else "missing",
        "SRL requests double-spaced material.",
    )
    add_check(
        rows,
        "line_numbers",
        "PASS" if r"\linenumbers" in tex and r"\modulolinenumbers[1]" in tex else "FAIL",
        "continuous line numbering commands present" if r"\linenumbers" in tex else "missing",
        "SRL requires continuous line numbering.",
    )
    add_check(
        rows,
        "section_numbering",
        "PASS" if r"\setcounter{secnumdepth}{0}" in tex else "WARN",
        "section numbering disabled" if r"\setcounter{secnumdepth}{0}" in tex else "numbering setting missing",
        "SRL asks authors not to number section headers.",
    )
    data_idx = markdown.find("## Data and Resources")
    ack_idx = markdown.find("## Acknowledgments")
    add_check(
        rows,
        "data_resources_order",
        "PASS" if data_idx != -1 and ack_idx != -1 and data_idx < ack_idx else "FAIL",
        f"Data and Resources index={data_idx}; Acknowledgments index={ack_idx}",
        "SRL manuscript order places Data and Resources before Acknowledgments.",
    )
    add_check(
        rows,
        "corresponding_author_section",
        "PASS" if "## Corresponding Author" in markdown else "WARN",
        "section present" if "## Corresponding Author" in markdown else "section missing",
        "SRL asks for full corresponding-author mailing address.",
    )
    add_check(
        rows,
        "submission_packet",
        "PASS" if packet_path.exists() else "FAIL",
        str(packet_path),
        "Advisor/pre-submission packet should exist.",
    )
    add_check(
        rows,
        "reproducibility_release",
        "PASS" if release_path.exists() else "FAIL",
        str(release_path),
        "Lightweight reproducibility release should exist.",
    )
    placeholder_hit = any(
        phrase in markdown + "\n" + tex
        for phrase in [
            "Author names and affiliations to be finalized",
            "No external funding statement has been finalized",
            "designated corresponding author",
        ]
    )
    add_check(
        rows,
        "author_metadata_finalization",
        "WARN" if placeholder_hit else "PASS",
        "placeholder author/funding/corresponding-author text remains" if placeholder_hit else "no placeholder metadata detected",
        "Author, funding, acknowledgment, and corresponding-author fields should contain final text before upload.",
    )
    return pd.DataFrame(rows)


def write_report(outdir: Path, checks: pd.DataFrame) -> None:
    status_counts = checks["status"].value_counts().to_dict()
    blocking = checks[checks["status"].eq("FAIL")]
    warnings = checks[checks["status"].eq("WARN")]
    lines = [
        "# StrongMotion-QC SRL Submission Compliance",
        "",
        "- Source: SRL author information page, checked against the manuscript package.",
        f"- Checks: {len(checks)}",
        f"- Status counts: {status_counts.get('PASS', 0)} PASS, {status_counts.get('WARN', 0)} WARN, {status_counts.get('FAIL', 0)} FAIL",
        "",
        "## Blocking Items",
        "",
    ]
    if blocking.empty:
        lines.append("No blocking compliance failures detected.")
    else:
        for _, row in blocking.iterrows():
            lines.append(f"- {row['check_id']}: {row['evidence']}")
    lines.extend(["", "## Warnings", ""])
    if warnings.empty:
        lines.append("No compliance warnings detected.")
    else:
        for _, row in warnings.iterrows():
            lines.append(f"- {row['check_id']}: {row['evidence']}")
    lines.extend(["", "## Check Table", "", "| Check | Status | Evidence |", "| --- | --- | --- |"])
    for _, row in checks.iterrows():
        lines.append(f"| {row['check_id']} | {row['status']} | {row['evidence']} |")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "report.md").write_text("\n".join(lines) + "\n")


def run_check(
    draft_path: Path,
    tex_path: Path,
    pdf_path: Path,
    packet_path: Path,
    release_path: Path,
    outdir: Path,
) -> dict[str, Path]:
    checks = build_checks(draft_path, tex_path, pdf_path, packet_path, release_path)
    outdir.mkdir(parents=True, exist_ok=True)
    checks.to_csv(outdir / "compliance_checks.csv", index=False)
    write_report(outdir, checks)
    return {"checks": outdir / "compliance_checks.csv", "report": outdir / "report.md"}


def main() -> None:
    args = parse_args()
    outputs = run_check(
        draft_path=Path(args.draft),
        tex_path=Path(args.tex),
        pdf_path=Path(args.pdf),
        packet_path=Path(args.packet),
        release_path=Path(args.release),
        outdir=Path(args.outdir),
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
