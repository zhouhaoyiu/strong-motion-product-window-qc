#!/usr/bin/env python3
"""Build bilingual submission-metadata worksheets and statement drafts."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class WorksheetItem:
    field_id: str
    section: str
    english_label: str
    chinese_label: str
    required_before_submission: str
    current_status: str
    current_value: str
    question_zh: str
    suggested_format: str
    output_location: str


FIELD_GUIDANCE = {
    "journal_target": (
        "目标期刊与文章类型",
        "确认本轮投稿目标和文章类型。",
        "Seismological Research Letters regular article",
        "submission system; cover letter",
    ),
    "submission_issue_choice": (
        "投稿栏目选择",
        "确认 Editorial Manager 中选择普通栏目还是当前专题栏目。",
        "Regular issue / Special issue name",
        "submission system",
    ),
    "srl_classification_terms": (
        "SRL 分类词",
        "选择最多四个投稿系统分类词，帮助编辑分配审稿方向。",
        "strong-motion records; ground-motion data processing; engineering seismology; seismic waveform analysis",
        "submission system",
    ),
    "flinn_engdahl_region": (
        "Flinn-Engdahl 区域",
        "选择投稿系统要求的区域项；若论文不针对单一地震或区域，按系统可选项填写最合适的通用/不适用选项。",
        "Global / Not event-specific / system-selected region",
        "submission system",
    ),
    "major_earthquake_name": (
        "主要地震名称",
        "确认论文是否聚焦某个命名地震；当前稿件为方法与数据集评估，通常可填不适用。",
        "Not applicable / earthquake name",
        "submission system",
    ),
    "license_choice": (
        "出版许可选择",
        "和所有作者确认采用普通 page-charge/copyright transfer 路线还是开放获取 CC-BY 路线。",
        "Page Charges / Open Access CC-BY",
        "submission system; publication forms",
    ),
    "editor_background_information": (
        "给编辑的背景说明",
        "填写投稿系统中给编辑、责任编辑和审稿人分配有帮助的简短背景说明。",
        "One short paragraph emphasizing offline product-window selection, auditability, cross-archive evidence, and scope limits",
        "submission system",
    ),
    "potential_referees": (
        "建议审稿人",
        "如提供建议审稿人，列出姓名、邮箱、单位和无利益冲突理由。",
        "Name, email, affiliation, rationale",
        "submission system",
    ),
    "opposed_referees": (
        "回避审稿人",
        "如存在利益冲突或竞争关系，列出应回避审稿人及理由；没有则注明不适用。",
        "Not applicable / Name, affiliation, reason",
        "submission system",
    ),
    "author_order": (
        "作者顺序",
        "按最终投稿顺序填写所有作者姓名。",
        "First Author; Second Author; Third Author",
        "title page; submission system",
    ),
    "author_orcid": (
        "作者 ORCID",
        "填写作者 ORCID，用于题名页、投稿系统或作者信息页。",
        "https://orcid.org/0000-0000-0000-0000",
        "title page; submission system",
    ),
    "author_affiliations": (
        "作者单位",
        "填写每位作者的机构、城市、国家和邮编；多单位作者请编号对应。",
        "1 Department, Institution, City, Country; 2 Department, Institution, City, Country",
        "title page",
    ),
    "corresponding_author_name": (
        "通讯作者姓名",
        "当前按作者要求留空；若导师或投稿系统要求，再指定负责投稿、修回和校样联系的通讯作者。",
        "留空，或按导师确认填写 Full Name",
        "title page; submission system",
    ),
    "corresponding_author_email": (
        "通讯作者邮箱",
        "当前按作者要求留空；若导师或投稿系统要求，再填写可长期接收投稿系统邮件的邮箱。",
        "留空，或按导师确认填写 name@example.edu",
        "title page; submission system",
    ),
    "corresponding_author_mailing_address": (
        "通讯作者邮寄地址",
        "当前按作者要求留空；若导师或投稿系统要求，再补充完整通讯地址。",
        "留空，或按导师确认填写 Department, Institution, Street, City, Postal Code, Country",
        "title page",
    ),
    "funding_statement": (
        "基金声明",
        "填写基金来源和项目号；没有外部基金时也要明确说明。",
        "This work was supported by ... grant ... / This research received no external funding.",
        "Acknowledgments; submission system",
    ),
    "data_provider_acknowledgments": (
        "数据提供方致谢",
        "按数据使用条款确认 InstanceGM/INSTANCE 和 NIED K-NET 的致谢表述。",
        "Acknowledge InstanceGM/INSTANCE and NIED K-NET according to their citation and usage terms.",
        "Acknowledgments; Data and Resources",
    ),
    "competing_interests": (
        "利益冲突声明",
        "确认没有利益冲突，或列出需要披露的关系。",
        "The authors declare no competing interests.",
        "Declaration of Competing Interests",
    ),
    "author_approval": (
        "全体作者同意",
        "确认所有作者已审阅并同意最终投稿版本。",
        "All authors have approved the final submitted version.",
        "cover letter; submission system",
    ),
    "code_archive_url": (
        "代码归档链接",
        "填写公开仓库、版本归档或 DOI 链接。",
        "https://github.com/... or https://doi.org/...",
        "Data and Resources",
    ),
    "data_access_dates": (
        "数据访问日期",
        "填写 INSTANCE、K-NET/SeisBench 和公开仓库的最终访问日期。",
        "INSTANCE accessed YYYY-MM-DD; SeisBench accessed YYYY-MM-DD; repository accessed YYYY-MM-DD",
        "Data and Resources",
    ),
    "software_release_doi": (
        "软件 DOI 或推迟决定",
        "决定是否提供软件归档 DOI；如暂不提供，写明推迟原因。",
        "Zenodo DOI ... / deferred until acceptance with repository URL provided",
        "Data and Resources; repository release notes",
    ),
    "public_release_license": (
        "公开归档许可",
        "确认代码和派生复现材料采用的公开许可。",
        "MIT / BSD-3-Clause / CC-BY-4.0 for derived tables, as appropriate",
        "Data and Resources; repository release notes",
    ),
    "supplemental_material_decision": (
        "补充材料决定",
        "决定 QC 审阅包、复现清单和表格作为补充材料还是仓库材料。",
        "Supplemental material: figures/tables/QC packet; repository: reproducibility manifests",
        "Data and Resources; supplemental upload",
    ),
    "qc_review_decision": (
        "人工 QC 或人工审阅声明决定",
        "决定是否加入人工 QC/人工审阅相关声明；如果正文不主张人工耗时减少，应明确推迟该声明。",
        "complete after review_summary generated / deferred; no measured human-workload claim",
        "Discussion; Data and Resources; submission metadata",
    ),
    "knet_scope_decision": (
        "K-NET 范围决定",
        "确认 K-NET 在当前稿件中作为第二个强震动档案参与产品窗口审计，不外推为实时或区域泛化结论。",
        "Use K-NET as a second strong-motion archive in the product-window audit; no real-time or regional-generalization claim.",
        "Results; Discussion",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", default="docs/submission_metadata_template.csv")
    parser.add_argument("--manuscript", default="docs/manuscript_draft.md")
    parser.add_argument("--outdir", default="outputs/submission_metadata")
    return parser.parse_args()


def clean(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def safe_md(value: object) -> str:
    return clean(value).replace("|", "\\|") or "[blank]"


def read_metadata(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False)


def manuscript_title(path: Path) -> str:
    if not path.exists():
        return "Offline P-Wave Picking From Locally Normalized Forecasting Residuals"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Offline P-Wave Picking From Locally Normalized Forecasting Residuals"


def row_value(df: pd.DataFrame, field_id: str) -> str:
    match = df[df["field_id"].astype(str) == field_id]
    if match.empty:
        return ""
    row = match.iloc[0]
    value = clean(row.get("value", ""))
    status = clean(row.get("status", "pending"))
    label = clean(row.get("label", field_id))
    if status == "complete" and value:
        return value
    if status == "pending" and value:
        return f"{value} [PENDING: {label}]"
    if status == "deferred":
        return f"[DEFERRED: {label}; see metadata notes]"
    if status == "not_applicable":
        return f"[NOT APPLICABLE: {label}]"
    return f"[PENDING: {label}]"


def raw_row_value(df: pd.DataFrame, field_id: str) -> str:
    match = df[df["field_id"].astype(str) == field_id]
    if match.empty:
        return ""
    return clean(match.iloc[0].get("value", ""))


def worksheet_items(df: pd.DataFrame) -> list[WorksheetItem]:
    items: list[WorksheetItem] = []
    for _, row in df.iterrows():
        field_id = clean(row.get("field_id"))
        chinese_label, question, suggested_format, output_location = FIELD_GUIDANCE.get(
            field_id,
            (clean(row.get("label", field_id)), clean(row.get("notes", "")), "", "submission metadata"),
        )
        items.append(
            WorksheetItem(
                field_id=field_id,
                section=clean(row.get("section")),
                english_label=clean(row.get("label")),
                chinese_label=chinese_label,
                required_before_submission=clean(row.get("required_before_submission")),
                current_status=clean(row.get("status")),
                current_value=clean(row.get("value")),
                question_zh=question,
                suggested_format=suggested_format,
                output_location=output_location,
            )
        )
    return items


def write_worksheet(
    items: list[WorksheetItem],
    outdir: Path,
    metadata_path: Path | str = "docs/submission_metadata_template.csv",
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "metadata_worksheet_items.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(WorksheetItem.__dataclass_fields__.keys()))
        writer.writeheader()
        for item in items:
            writer.writerow(item.__dict__)

    pending_required = [
        item
        for item in items
        if item.required_before_submission.lower() == "yes" and item.current_status == "pending"
    ]
    pending_optional = [
        item
        for item in items
        if item.required_before_submission.lower() != "yes" and item.current_status == "pending"
    ]
    lines = [
        "# 投稿元数据中英双语工作表",
        "",
        "这个工作表把 SRL 投稿前需要人工确认的信息拆成可填写字段。",
        f"它不会替代 `{Path(metadata_path).as_posix()}`；最终仍应把确认后的值写回该 CSV。",
        "",
        f"- 字段总数：{len(items)}",
        f"- 投稿前必填但未完成：{len(pending_required)}",
        f"- 可选择或可推迟：{len(pending_optional)}",
        "",
        "## 字段清单",
        "",
        "| 字段 ID | 中文标签 | 英文标签 | 必填 | 当前状态 | 当前值 | 需要确认/填写 | 建议格式 | 出现位置 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            f"| `{item.field_id}` | {safe_md(item.chinese_label)} | {safe_md(item.english_label)} | "
            f"{safe_md(item.required_before_submission)} | {safe_md(item.current_status)} | "
            f"{safe_md(item.current_value)} | {safe_md(item.question_zh)} | "
            f"{safe_md(item.suggested_format)} | {safe_md(item.output_location)} |"
        )
    lines.extend(
        [
            "",
            "## 回填规则",
            "",
            f"- 填完后，把确认值写入 `{Path(metadata_path).as_posix()}` 的 `value` 列。",
            "- 必填项确认后把 `status` 改为 `complete`。",
            "- 可推迟项如果决定暂不完成，把 `status` 改为 `deferred`，并在 `notes` 写明原因。",
            f"- 改完后运行 `conda run -n zhy python scripts/check_submission_metadata.py --metadata {Path(metadata_path).as_posix()} --outdir {outdir.as_posix()}`。",
        ]
    )
    (outdir / "metadata_worksheet_zh.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_title_page_and_statements(
    df: pd.DataFrame,
    title: str,
    outdir: Path,
    metadata_path: Path | str = "docs/submission_metadata_template.csv",
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    authors = row_value(df, "author_order")
    author_orcid = row_value(df, "author_orcid")
    affiliations = row_value(df, "author_affiliations")
    corresponding_name = raw_row_value(df, "corresponding_author_name")
    corresponding_email = raw_row_value(df, "corresponding_author_email")
    corresponding_address = raw_row_value(df, "corresponding_author_mailing_address")
    funding = row_value(df, "funding_statement")
    competing = row_value(df, "competing_interests")
    approval = row_value(df, "author_approval")
    code = row_value(df, "code_archive_url")
    access_dates = row_value(df, "data_access_dates")
    software = row_value(df, "software_release_doi")
    supplemental = row_value(df, "supplemental_material_decision")
    qc_review = row_value(df, "qc_review_decision")
    knet_scope = row_value(df, "knet_scope_decision")
    issue_choice = row_value(df, "submission_issue_choice")
    classification_terms = row_value(df, "srl_classification_terms")
    flinn_engdahl_region = row_value(df, "flinn_engdahl_region")
    major_earthquake = row_value(df, "major_earthquake_name")
    license_choice = row_value(df, "license_choice")
    editor_background = row_value(df, "editor_background_information")
    potential_referees = row_value(df, "potential_referees")
    opposed_referees = row_value(df, "opposed_referees")
    lines = [
        "# Title Page and Submission Statements Draft",
        "",
        f"This draft is generated from `{Path(metadata_path).as_posix()}`.",
        "Replace all `[PENDING: ...]` fields before journal upload.",
        "",
        "## Title Page",
        "",
        f"**Title:** {title}",
        "",
        f"**Article type:** {row_value(df, 'journal_target')}",
        "",
        f"**Issue choice:** {issue_choice}",
        "",
        f"**Authors:** {authors}",
        "",
        f"**Author ORCID:** {author_orcid}",
        "",
        f"**Affiliations:** {affiliations}",
        "",
        f"**Corresponding author:** {corresponding_name}",
        "",
        f"**Corresponding author email:** {corresponding_email}",
        "",
        f"**Corresponding author mailing address:** {corresponding_address}",
        "",
        "## Editorial Manager Metadata",
        "",
        f"Classification terms: {classification_terms}",
        "",
        f"Flinn-Engdahl region: {flinn_engdahl_region}",
        "",
        f"Major earthquake name: {major_earthquake}",
        "",
        f"Publication license choice: {license_choice}",
        "",
        f"Background information for editor: {editor_background}",
        "",
        f"Potential referees: {potential_referees}",
        "",
        f"Opposed referees: {opposed_referees}",
        "",
        "## Data and Resources",
        "",
        "The evaluation uses InstanceGM/INSTANCE-family records and K-NET",
        "strong-motion records in an offline processing-window audit. Code,",
        "generated tables, figures, reproducibility manifests, and audit reports",
        "should be archived before final upload.",
        "",
        f"Code/archive URL: {code}",
        "",
        f"Software release DOI or decision: {software}",
        "",
        f"Data and resource access dates: {access_dates}",
        "",
        f"K-NET scope decision: {knet_scope}",
        "",
        "## Declaration of Competing Interests",
        "",
        competing,
        "",
        "## Acknowledgments and Funding",
        "",
        funding,
        "",
        "## Author Approval",
        "",
        approval,
        "",
        "## Supplemental Material Decision",
        "",
        supplemental,
        "",
        "## QC Review Decision",
        "",
        qc_review,
    ]
    (outdir / "title_page_and_statements_draft.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = read_metadata(Path(args.metadata))
    items = worksheet_items(df)
    write_worksheet(items, outdir, args.metadata)
    write_title_page_and_statements(df, manuscript_title(Path(args.manuscript)), outdir, args.metadata)
    pending_required = sum(
        item.required_before_submission.lower() == "yes" and item.current_status == "pending"
        for item in items
    )
    print(f"Submission metadata worksheet: {len(items)} fields, {pending_required} pending required")
    print(f"Report written to {outdir / 'metadata_worksheet_zh.md'}")


if __name__ == "__main__":
    main()
