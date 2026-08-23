#!/usr/bin/env python3
"""Create publication-oriented StrongMotion-QC figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_WINDOW_STABILITY = "outputs/strong_motion_qc_window_stability_accel44674_hp0p1/summary.csv"
DEFAULT_PNW_WINDOW_STABILITY = "outputs/strong_motion_qc_window_stability_pnw_accel6107_hp0p1/summary.csv"
DEFAULT_SAFEGUARD = "outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/summary.csv"
DEFAULT_PNW_SAFEGUARD = "outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/summary.csv"
DEFAULT_RESPONSE_SPECTRUM = "outputs/strong_motion_qc_response_spectrum_accel44674_hp0p1/summary.csv"
DEFAULT_SAFEGUARD_SPECTRUM = "outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/spectrum_summary.csv"
DEFAULT_FILTER_RESPONSE_005 = "outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p05_sample1521/summary.csv"
DEFAULT_FILTER_RESPONSE_010 = "outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p1_sample1521/summary.csv"
DEFAULT_FILTER_SAFEGUARD_005 = "outputs/strong_motion_qc_spectral_safeguard_filter_sensitivity_e2e_hp0p05_sample1521/summary.csv"
DEFAULT_FILTER_SAFEGUARD_010 = "outputs/strong_motion_qc_spectral_safeguard_filter_sensitivity_e2e_hp0p1_sample1521/summary.csv"
DEFAULT_PNW_SNR = "outputs/strong_motion_qc_pnw_snr_accel6107_hp0p1/summary.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_figures_accel44674_hp0p1"
DATASETS = ["InstanceGM", "K-NET"]
DISPLAY_DATASETS = ["InstanceGM", "K-NET", "PNW"]
LANGUAGE = "en"
FIXED_METHODS = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed"]
CORE_METHODS = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed", "adaptive_energy_end", "shortest_stable_no_catalog"]
METHOD_LABELS_EN = {
    "feature_onset_fixed": "Feature fixed",
    "energy_onset_fixed": "Energy fixed",
    "catalog_p_fixed": "Catalog-P fixed",
    "adaptive_energy_end": "Adaptive",
    "shortest_stable_no_catalog": "Shortest stable",
    "full_record": "Full record",
}
METHOD_LABELS_ZH = {
    "feature_onset_fixed": "特征起点窗",
    "energy_onset_fixed": "能量起点窗",
    "catalog_p_fixed": "目录P窗",
    "adaptive_energy_end": "适应性窗",
    "shortest_stable_no_catalog": "最短稳定窗",
    "full_record": "全记录",
}
HATCHES = ["", "///", "\\\\\\", "xxx", "...", "---"]
COLORS = {
    "feature_onset_fixed": "#4d4d4d",
    "energy_onset_fixed": "#7a7a7a",
    "catalog_p_fixed": "#a6a6a6",
    "adaptive_energy_end": "#d9d9d9",
    "shortest_stable_no_catalog": "#111111",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-stability", default=DEFAULT_WINDOW_STABILITY)
    parser.add_argument("--pnw-window-stability", default=DEFAULT_PNW_WINDOW_STABILITY)
    parser.add_argument("--spectral-safeguard", default=DEFAULT_SAFEGUARD)
    parser.add_argument("--pnw-spectral-safeguard", default=DEFAULT_PNW_SAFEGUARD)
    parser.add_argument("--response-spectrum", default=DEFAULT_RESPONSE_SPECTRUM)
    parser.add_argument("--spectral-safeguard-spectrum", default=DEFAULT_SAFEGUARD_SPECTRUM)
    parser.add_argument("--filter-response-005", default=DEFAULT_FILTER_RESPONSE_005)
    parser.add_argument("--filter-response-010", default=DEFAULT_FILTER_RESPONSE_010)
    parser.add_argument("--filter-safeguard-005", default=DEFAULT_FILTER_SAFEGUARD_005)
    parser.add_argument("--filter-safeguard-010", default=DEFAULT_FILTER_SAFEGUARD_010)
    parser.add_argument("--pnw-snr", default=DEFAULT_PNW_SNR)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--formats", nargs="+", default=["png", "pdf"])
    parser.add_argument("--language", choices=["en", "zh"], default="en")
    return parser.parse_args()


def text(en: str, zh: str) -> str:
    return zh if LANGUAGE == "zh" else en


def method_label(method: str) -> str:
    labels = METHOD_LABELS_ZH if LANGUAGE == "zh" else METHOD_LABELS_EN
    return labels[method]


def configure_matplotlib() -> None:
    import matplotlib.pyplot as plt

    font_family = "DejaVu Sans"
    if LANGUAGE == "zh":
        font_family = ["Hiragino Sans GB", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.family": font_family,
            "font.size": 9.4,
            "axes.titlesize": 10.0,
            "axes.labelsize": 9.4,
            "legend.fontsize": 8.6,
            "xtick.labelsize": 8.4,
            "ytick.labelsize": 8.4,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linewidth": 0.6,
            "axes.unicode_minus": False,
        }
    )


def save_figure(fig, outdir: Path, stem: str, formats: list[str]) -> list[Path]:
    paths = []
    for fmt in formats:
        path = outdir / f"{stem}.{fmt}"
        fig.savefig(path, bbox_inches="tight", pad_inches=0.04)
        paths.append(path)
    return paths


def dataset_policy(summary: pd.DataFrame, policy: str) -> pd.DataFrame:
    return summary[summary["dataset"].isin(DATASETS) & summary["priority_group"].eq("ALL") & summary["policy"].eq(policy)]


def figure_workflow(outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    fig, ax = plt.subplots(figsize=(7.5, 2.55), constrained_layout=True)
    ax.axis("off")
    line = "#202020"
    blue = "#4f86a6"
    light_blue = "#a8c7d6"
    gray = "#d6d6d6"
    pale = "#f4f4f4"
    headings = [
        text("(a) Candidate\nwindows", "(a) 候选处理窗"),
        text("(b) Amplitude-energy\naudit", "(b) 幅值与能量审计"),
        text("(c) Spectral\nsafeguard", "(c) 反应谱保障"),
        text("(d) Product\nwindow", "(d) 产品处理窗"),
    ]
    lefts = [0.02, 0.27, 0.52, 0.77]
    for left, heading in zip(lefts, headings):
        ax.text(left, 0.94, heading, ha="left", va="center", fontsize=8.8, fontweight="bold", linespacing=1.0)
    for xx in [0.25, 0.50, 0.75]:
        ax.plot([xx, xx], [0.10, 0.88], color="#dedede", lw=0.8)

    t = np.linspace(0, 60, 500)
    signal = 0.08 * np.sin(0.7 * t)
    signal += 0.9 * np.exp(-((t - 24) ** 2) / 52) * np.sin(2.7 * t)
    signal += 0.18 * np.exp(-((t - 39) ** 2) / 120) * np.sin(2.0 * t)
    x_wave = 0.045 + 0.175 * (t / 60)
    y_wave = 0.67 + 0.13 * signal
    ax.plot(x_wave, y_wave, color=line, lw=1.0)
    onset_x = 0.045 + 0.175 * (13 / 60)
    ax.plot([onset_x, onset_x], [0.54, 0.80], color="#555555", lw=0.8, ls="--")
    ax.text(onset_x, 0.515, text("onset", "起点"), ha="center", va="top", fontsize=7.8)
    window_rows = [
        (text("20-90 s", "20-90 s"), onset_x, 0.075, 0.39, gray),
        (text("energy end", "能量结束"), onset_x, 0.112, 0.28, light_blue),
        (text("1%-99% energy", "1%-99% 能量窗"), 0.052, 0.163, 0.17, pale),
    ]
    for label, x0, width, yy, color in window_rows:
        ax.text(0.042, yy + 0.018, label, ha="right", va="center", fontsize=7.5)
        ax.add_patch(Rectangle((x0, yy), width, 0.036, facecolor=color, edgecolor=line, lw=0.65))

    checks = [
        (text("Peak ratio", "峰值比"), r"$\geq 0.99$"),
        (text("Energy ratio", "能量比"), r"$\geq 0.95$"),
        (text("Peak times", "峰值时刻"), text("inside", "窗内")),
    ]
    for idx, (label, value) in enumerate(checks):
        yy = 0.73 - idx * 0.17
        ax.text(0.285, yy, label, ha="left", va="center", fontsize=8.0)
        ax.text(0.475, yy, value, ha="right", va="center", fontsize=8.0)
        if idx < 2:
            ax.plot([0.285, 0.475], [yy - 0.075, yy - 0.075], color="#dddddd", lw=0.7)
    ax.text(0.285, 0.18, text("Keep the shortest passing window", "保留通过审计的最短窗"), ha="left", va="center", fontsize=7.7, color="#555555")

    periods = ["0.2 s", "1.0 s", "3.0 s"]
    for idx, label in enumerate(periods):
        yy = 0.72 - idx * 0.15
        ax.text(0.545, yy, text("PSA", "PSA") + f" ({label})", ha="left", va="center", fontsize=8.0)
        ax.text(0.72, yy, r"$\geq 0.95$", ha="right", va="center", fontsize=8.0)
    ax.text(0.545, 0.23, text("Fail: 1%-99% energy window", "未通过：升级 1%-99% 能量窗"), ha="left", va="center", fontsize=7.7)
    ax.text(0.545, 0.14, text("Fail again: full record", "再次未通过：全记录"), ha="left", va="center", fontsize=7.7)

    outputs = [
        (text("Primary window", "初选窗"), blue, 0.68),
        (text("Energy-window escalation", "能量窗升级"), light_blue, 0.48),
        (text("Full-record fallback", "全记录回退"), pale, 0.28),
    ]
    for label, color, yy in outputs:
        ax.add_patch(Rectangle((0.795, yy), 0.045, 0.055, facecolor=color, edgecolor=line, lw=0.7))
        ax.text(0.85, yy + 0.027, label, ha="left", va="center", fontsize=8.0)
    ax.text(0.795, 0.13, text("Record-level audit trail", "记录级审计字段"), ha="left", va="center", fontsize=7.7, color="#555555")

    arrow_style = dict(arrowstyle="->", mutation_scale=9, lw=0.9, color=line)
    for start, end in [((0.232, 0.83), (0.263, 0.83)), ((0.482, 0.83), (0.513, 0.83)), ((0.732, 0.83), (0.763, 0.83))]:
        ax.add_patch(FancyArrowPatch(start, end, **arrow_style))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return save_figure(fig, outdir, "smqc_figure_01_workflow", formats)


def aggregate_instability(summary: pd.DataFrame, dataset: str, candidate: str) -> float:
    rows = summary[summary["dataset"].eq(dataset) & summary["candidate"].eq(candidate)]
    return 100.0 * float(rows["unstable_records"].sum() / rows["records"].sum())


def figure_fixed_window_failure(
    window_stability: pd.DataFrame,
    pnw_window_stability: pd.DataFrame,
    outdir: Path,
    formats: list[str],
) -> list[Path]:
    import matplotlib.pyplot as plt

    combined = pd.concat([window_stability, pnw_window_stability], ignore_index=True)
    durations = [20, 40, 60, 90]
    candidates = ["feature_onset_fixed_20s", "feature_onset_fixed", "feature_onset_fixed_60s", "feature_onset_fixed_90s"]
    source_names = ["InstanceGM", "K-NET", "PNWAccelerometers"]
    display_names = ["InstanceGM", "K-NET", "PNW"]
    styles = [
        ("#555555", "o", "-"),
        ("#111111", "s", "--"),
        ("#4f86a6", "^", "-."),
    ]
    fig, ax = plt.subplots(figsize=(6.9, 3.35), constrained_layout=True)
    for source, label, (color, marker, linestyle) in zip(source_names, display_names, styles):
        values = [aggregate_instability(combined, source, candidate) for candidate in candidates]
        ax.plot(durations, values, color=color, marker=marker, linestyle=linestyle, lw=1.5, ms=4.5, label=label)
        for x_value, y_value in zip(durations, values):
            offset = -12 if source == "PNWAccelerometers" and x_value == 20 else 5
            ax.annotate(f"{y_value:.1f}", (x_value, y_value), xytext=(0, offset), textcoords="offset points", ha="center", fontsize=7.2)
    ax.set_xticks(durations)
    ax.set_xlabel(text("Post-onset duration (s); total window adds 2 s pre-onset", "起点后时长 (s)；总窗长另含起点前 2 s"))
    ax.set_ylabel(text("Unstable windows (%)", "不稳定率 (%)"))
    ax.set_ylim(0, 103)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    return save_figure(fig, outdir, "smqc_figure_02_fixed_window_failure", formats)


def safeguard_rows(main: pd.DataFrame, pnw: pd.DataFrame) -> pd.DataFrame:
    combined = pd.concat([main, pnw], ignore_index=True)
    rows = combined[combined["priority_group"].eq("ALL") & combined["dataset"].ne("ALL")].copy()
    rows["display_dataset"] = rows["dataset"].replace({"PNWAccelerometers": "PNW"})
    return rows


def figure_selector_duration(
    safeguard: pd.DataFrame,
    pnw_safeguard: pd.DataFrame,
    outdir: Path,
    formats: list[str],
) -> list[Path]:
    import matplotlib.pyplot as plt

    rows = safeguard_rows(safeguard, pnw_safeguard).set_index("display_dataset").loc[DISPLAY_DATASETS].reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.45, 1.0]}, constrained_layout=True)
    x = np.arange(len(rows))
    stages = [
        ("primary_pct", text("Primary", "初选窗"), "#4f86a6", ""),
        ("arias_escalation_pct", text("Energy escalation", "能量窗升级"), "#a8c7d6", "///"),
        ("full_record_fallback_pct", text("Full record", "全记录"), "#e0e0e0", "..."),
    ]
    bottom = np.zeros(len(rows))
    for column, label, color, hatch in stages:
        values = rows[column].to_numpy(float)
        bars = axes[0].bar(x, values, bottom=bottom, color=color, edgecolor="black", linewidth=0.45, hatch=hatch, label=label)
        for bar, value, base in zip(bars, values, bottom):
            if value >= 7:
                axes[0].text(bar.get_x() + bar.get_width() / 2, base + value / 2, f"{value:.1f}", ha="center", va="center", fontsize=7.2)
        bottom += values
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(rows["display_dataset"])
    axes[0].set_ylabel(text("Records (%)", "记录比例 (%)"))
    axes[0].set_ylim(0, 100)
    axes[0].set_title(text("(a) Spectral-audit route", "(a) 反应谱审计分流"))
    axes[0].legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=3)

    medians = rows["median_window_duration_sec"].to_numpy(float)
    p75 = rows["p75_window_duration_sec"].to_numpy(float)
    bars = axes[1].bar(x, medians, color=["#6f6f6f", "#292929", "#4f86a6"], edgecolor="black", linewidth=0.45)
    axes[1].errorbar(x, medians, yerr=np.vstack([np.zeros(len(rows)), p75 - medians]), fmt="none", ecolor="black", capsize=3, lw=0.8)
    axes[1].bar_label(bars, labels=[f"{value:.1f}" for value in medians], padding=2, fontsize=7.2)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(rows["display_dataset"])
    axes[1].set_ylabel(text("Window duration (s)", "处理窗时长 (s)"))
    axes[1].set_title(text("(b) Median and 75th percentile", "(b) 中位数与 75 分位"))
    axes[1].set_ylim(0, max(p75) * 1.12)
    return save_figure(fig, outdir, "smqc_figure_03_selector_duration_fallback", formats)


def figure_product_impact(
    response_spectrum: pd.DataFrame,
    safeguard_spectrum: pd.DataFrame,
    outdir: Path,
    formats: list[str],
) -> list[Path]:
    import matplotlib.pyplot as plt

    data = pd.concat([response_spectrum, safeguard_spectrum], ignore_index=True)
    policies = ["feature_onset_fixed", "shortest_stable_no_catalog", "product_spectral_safeguard"]
    labels = [text("42 s fixed", "42 s 固定窗"), text("Primary", "初选窗"), text("Safeguarded", "谱保障窗")]
    colors = ["#8a8a8a", "#4f86a6", "#d8d8d8"]
    hatches = ["///", "", "..."]
    periods = [0.2, 1.0, 3.0]
    datasets = ["ALL", "InstanceGM", "K-NET"]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.9), sharey=True)
    x = np.arange(len(periods))
    width = 0.24
    max_failure = 0.0
    for ax, dataset in zip(axes, datasets):
        for idx, (policy, label, color, hatch) in enumerate(zip(policies, labels, colors, hatches)):
            values = []
            for period in periods:
                row = data[
                    data["dataset"].eq(dataset)
                    & data["priority_group"].eq("ALL")
                    & data["policy"].eq(policy)
                    & data["period_sec"].eq(period)
                ].iloc[0]
                values.append(float(row["spectrum_unstable_pct"]))
            max_failure = max(max_failure, *values)
            bars = ax.bar(x + (idx - 1) * width, values, width=width, color=color, edgecolor="black", linewidth=0.4, hatch=hatch, label=label)
            for bar, value in zip(bars, values):
                if value >= 0.05:
                    ax.text(bar.get_x() + bar.get_width() / 2, value + 0.8, f"{value:.1f}", ha="center", va="bottom", fontsize=6.8, rotation=90)
                elif policy == "product_spectral_safeguard":
                    ax.text(bar.get_x() + bar.get_width() / 2, 0.6, "0", ha="center", va="bottom", fontsize=6.6)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{period:g}" for period in periods])
        ax.set_xlabel(text("Period (s)", "周期 (s)"))
        ax.set_title(dataset)
    axes[0].set_ylabel(text("PSA-retention failures (%)", "PSA 保留失败率 (%)"))
    axes[0].set_ylim(0, max(5.0, max_failure * 1.16 + 1.5))
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.28, wspace=0.08)
    fig.legend(handles, legend_labels, frameon=False, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.01))
    return save_figure(fig, outdir, "smqc_figure_04_product_impact_recovery", formats)


def figure_filter_sensitivity(
    response_005: pd.DataFrame,
    response_010: pd.DataFrame,
    safeguard_005: pd.DataFrame,
    safeguard_010: pd.DataFrame,
    outdir: Path,
    formats: list[str],
) -> list[Path]:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.85), constrained_layout=True)
    x = np.arange(len(DATASETS))
    width = 0.34
    max_primary = 0.0
    max_fallback = 0.0
    corners = [("0.05 Hz", response_005, safeguard_005, "#8a8a8a", "///"), ("0.10 Hz", response_010, safeguard_010, "#4f86a6", "")]
    for idx, (label, response, safeguard, color, hatch) in enumerate(corners):
        primary = []
        fallback = []
        for dataset in DATASETS:
            row = response[
                response["dataset"].eq(dataset)
                & response["priority_group"].eq("ALL")
                & response["policy"].eq("shortest_stable_no_catalog")
                & response["period_sec"].eq(3.0)
            ].iloc[0]
            primary.append(float(row["spectrum_unstable_pct"]))
            safe_row = safeguard[safeguard["dataset"].eq(dataset) & safeguard["priority_group"].eq("ALL")].iloc[0]
            fallback.append(float(safe_row["full_record_fallback_pct"]))
        max_primary = max(max_primary, *primary)
        max_fallback = max(max_fallback, *fallback)
        offset = (idx - 0.5) * width
        bars_a = axes[0].bar(x + offset, primary, width=width, color=color, edgecolor="black", linewidth=0.45, hatch=hatch, label=label)
        bars_b = axes[1].bar(x + offset, fallback, width=width, color=color, edgecolor="black", linewidth=0.45, hatch=hatch, label=label)
        axes[0].bar_label(bars_a, fmt="%.1f", padding=2, fontsize=7.0)
        axes[1].bar_label(bars_b, fmt="%.1f", padding=2, fontsize=7.0)
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(DATASETS)
        ax.legend(frameon=False, ncol=2)
    axes[0].set_ylabel(text("Failure rate (%)", "失败率 (%)"))
    axes[0].set_title(text("(a) Primary-window 3.0 s PSA", "(a) 初选窗 3.0 s PSA"))
    axes[0].set_ylim(0, max(5.0, max_primary * 1.17 + 1.0))
    axes[1].set_ylabel(text("Full-record fallback (%)", "全记录回退比例 (%)"))
    axes[1].set_title(text("(b) Final spectral safeguard", "(b) 最终反应谱保障"))
    axes[1].set_ylim(0, max(5.0, max_fallback * 1.17 + 1.0))
    return save_figure(fig, outdir, "smqc_figure_05_filter_sensitivity", formats)


def figure_response_spectrum_retention(pnw_snr: pd.DataFrame, outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    order = ["<3 dB", "3-10 dB", ">=10 dB"]
    data = pnw_snr.set_index("snr_bin").loc[order].reset_index()
    panels = [
        ("feature_fixed_unstable_pct", text("(a) Fixed window", "(a) 固定窗"), "#8a8a8a", "///"),
        ("selected_3s_psa_failure_pct", text("(b) Primary 3.0 s PSA", "(b) 初选窗 3.0 s PSA"), "#4f86a6", ""),
        ("spectral_full_record_fallback_pct", text("(c) Full-record fallback", "(c) 全记录采用率"), "#d8d8d8", "..."),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.85), sharey=True)
    x = np.arange(len(order))
    for ax, (column, title, color, hatch) in zip(axes, panels):
        values = data[column].to_numpy(float)
        bars = ax.bar(x, values, color=color, edgecolor="black", linewidth=0.45, hatch=hatch)
        ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=7.0)
        ax.set_xticks(x)
        tick_labels = [f"{label}\nn={int(count):,}" for label, count in zip(order, data["records"])]
        ax.set_xticklabels(tick_labels, rotation=0, ha="center", fontsize=7.0)
        ax.set_title(title, fontsize=9.0, pad=8)
        ax.set_xlabel(text("RMS SNR", "RMS 信噪比"))
    axes[0].set_ylabel(text("Records (%)", "记录比例 (%)"))
    axes[0].set_ylim(0, 108)
    fig.subplots_adjust(bottom=0.25, wspace=0.10)
    return save_figure(fig, outdir, "smqc_figure_06_response_spectrum_retention", formats)


def write_manifest(outdir: Path, generated: dict[str, list[Path]], source_paths: dict[str, str]) -> None:
    rows = [
        {
            "figure_id": "Fig. 1",
            "stem": "smqc_figure_01_workflow",
            "title": "Two-stage product-window audit",
            "source": "method schematic",
            "manuscript_role": "Defines candidate generation, amplitude-energy checks, spectral safeguard, and conservative fallback.",
            "boundary": "Offline product preparation with the full record available.",
        },
        {
            "figure_id": "Fig. 2",
            "stem": "smqc_figure_02_fixed_window_failure",
            "title": "Fixed-duration sensitivity by dataset",
            "source": source_paths["window_stability"],
            "manuscript_role": "Shows how 20-90 s fixed windows remain archive dependent.",
            "boundary": "Rates use minimum-component peak retention, three-component energy retention, and component peak-time inclusion.",
        },
        {
            "figure_id": "Fig. 3",
            "stem": "smqc_figure_03_selector_duration_fallback",
            "title": "Spectral-audit routes and output duration",
            "source": source_paths["safeguard"],
            "manuscript_role": "Reports primary acceptance, energy-window escalation, full-record fallback, and final duration.",
            "boundary": "Routing is determined from full-record product retention.",
        },
        {
            "figure_id": "Fig. 4",
            "stem": "smqc_figure_04_product_impact_recovery",
            "title": "PSA retention before and after spectral safeguard",
            "source": source_paths["response_spectrum"],
            "manuscript_role": "Compares fixed, primary, and safeguarded outputs at three oscillator periods.",
            "boundary": "Relative PSA retention is evaluated against the full record.",
        },
        {
            "figure_id": "Fig. 5",
            "stem": "smqc_figure_05_filter_sensitivity",
            "title": "High-pass filter sensitivity",
            "source": source_paths["filter_sensitivity"],
            "manuscript_role": "Shows the 0.05/0.10 Hz effect on 3.0 s PSA failures and full-record fallback.",
            "boundary": "The same predeclared stratified record sample and windows are compared.",
        },
        {
            "figure_id": "Fig. 6",
            "stem": "smqc_figure_06_response_spectrum_retention",
            "title": "PNW SNR-stratified external audit",
            "source": source_paths["pnw_snr"],
            "manuscript_role": "Separates fixed-window, primary-spectrum, and final-fallback behavior by result-blind SNR.",
            "boundary": "SNR uses catalog timing and waveform amplitudes before window outcomes are joined.",
        },
    ]
    for row in rows:
        paths = generated.get(row["stem"], [])
        for path in paths:
            row[path.suffix.lstrip("_ .")] = str(path)
    manifest = pd.DataFrame(rows)
    manifest.to_csv(outdir / "figure_manifest.csv", index=False)
    lines = [
        "# StrongMotion-QC Figures",
        "",
        "Publication-oriented figures for the SRL route.",
        "",
        "| figure_id | title | manuscript_role | source | boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['figure_id']} | {row['title']} | {row['manuscript_role']} | `{row['source']}` | {row['boundary']} |"
        )
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def make_figures(
    window_stability_path: Path,
    pnw_window_stability_path: Path,
    safeguard_path: Path,
    pnw_safeguard_path: Path,
    response_spectrum_path: Path,
    safeguard_spectrum_path: Path,
    filter_response_005_path: Path,
    filter_response_010_path: Path,
    filter_safeguard_005_path: Path,
    filter_safeguard_010_path: Path,
    pnw_snr_path: Path,
    outdir: Path,
    formats: list[str],
) -> dict[str, list[Path]]:
    configure_matplotlib()
    outdir.mkdir(parents=True, exist_ok=True)
    window_stability = pd.read_csv(window_stability_path)
    pnw_window_stability = pd.read_csv(pnw_window_stability_path)
    safeguard = pd.read_csv(safeguard_path)
    pnw_safeguard = pd.read_csv(pnw_safeguard_path)
    response_spectrum = pd.read_csv(response_spectrum_path)
    safeguard_spectrum = pd.read_csv(safeguard_spectrum_path)
    filter_response_005 = pd.read_csv(filter_response_005_path)
    filter_response_010 = pd.read_csv(filter_response_010_path)
    filter_safeguard_005 = pd.read_csv(filter_safeguard_005_path)
    filter_safeguard_010 = pd.read_csv(filter_safeguard_010_path)
    pnw_snr = pd.read_csv(pnw_snr_path)
    generated = {
        "smqc_figure_01_workflow": figure_workflow(outdir, formats),
        "smqc_figure_02_fixed_window_failure": figure_fixed_window_failure(window_stability, pnw_window_stability, outdir, formats),
        "smqc_figure_03_selector_duration_fallback": figure_selector_duration(safeguard, pnw_safeguard, outdir, formats),
        "smqc_figure_04_product_impact_recovery": figure_product_impact(response_spectrum, safeguard_spectrum, outdir, formats),
        "smqc_figure_05_filter_sensitivity": figure_filter_sensitivity(filter_response_005, filter_response_010, filter_safeguard_005, filter_safeguard_010, outdir, formats),
        "smqc_figure_06_response_spectrum_retention": figure_response_spectrum_retention(pnw_snr, outdir, formats),
    }
    write_manifest(
        outdir,
        generated,
        {
            "window_stability": f"{window_stability_path}; {pnw_window_stability_path}",
            "safeguard": f"{safeguard_path}; {pnw_safeguard_path}",
            "response_spectrum": str(response_spectrum_path),
            "filter_sensitivity": f"{filter_response_005_path}; {filter_response_010_path}; {filter_safeguard_005_path}; {filter_safeguard_010_path}",
            "pnw_snr": str(pnw_snr_path),
        },
    )
    return generated


def main() -> None:
    global LANGUAGE
    args = parse_args()
    LANGUAGE = args.language
    generated = make_figures(
        window_stability_path=Path(args.window_stability),
        pnw_window_stability_path=Path(args.pnw_window_stability),
        safeguard_path=Path(args.spectral_safeguard),
        pnw_safeguard_path=Path(args.pnw_spectral_safeguard),
        response_spectrum_path=Path(args.response_spectrum),
        safeguard_spectrum_path=Path(args.spectral_safeguard_spectrum),
        filter_response_005_path=Path(args.filter_response_005),
        filter_response_010_path=Path(args.filter_response_010),
        filter_safeguard_005_path=Path(args.filter_safeguard_005),
        filter_safeguard_010_path=Path(args.filter_safeguard_010),
        pnw_snr_path=Path(args.pnw_snr),
        outdir=Path(args.outdir),
        formats=args.formats,
    )
    for paths in generated.values():
        for path in paths:
            print(f"Wrote {path.resolve()}")
    print(f"Wrote {(Path(args.outdir) / 'figure_manifest.csv').resolve()}")
    print(f"Wrote {(Path(args.outdir) / 'README.md').resolve()}")


if __name__ == "__main__":
    main()
