#!/usr/bin/env python3
"""Render Figure 6 (matched-length composition--length decomposition).

Reads the released per-seed matched-length CSVs, recomputes every aggregate,
asserts them against the values printed in the paper's matched-length decomposition table, and only then
renders the two-panel figure. The figure therefore cannot silently diverge
from the released data or the paper table.

Reads:   ../data/matchedlen/s3xs3_matchedlen_baselines.csv
         ../data/matchedlen/s3xs3_matchedlen_carrier.csv
Writes:  fig6_matchedlen_decomposition.{pdf,png}  (next to this script)
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_HERE = Path(__file__).resolve().parent
DATA = _HERE.parent / "data" / "matchedlen"

CHANCE = 1.0 / 36.0
LENGTHS = (8, 64)
MODELS = [
    ("Hard-projected (ours)", "Hard-projected\n(ours)"),
    ("GRU + prototype readout", "GRU +\nprototype"),
    ("Holonomy-style recurrence (ours)", "Holonomy-style\n(ours)"),
    ("PD-SSM (adapted public impl.)", "PD-SSM\n(adapted)"),
]
# Paper matched-length decomposition table values, asserted before rendering.
EXPECTED = {
    ("Hard-projected (ours)", 8): (1.000, 1.000),
    ("Hard-projected (ours)", 64): (1.000, 1.000),
    ("GRU + prototype readout", 8): (1.000, 0.984),
    ("GRU + prototype readout", 64): (0.856, 0.568),
    ("Holonomy-style recurrence (ours)", 8): (1.000, 1.000),
    ("Holonomy-style recurrence (ours)", 64): (0.030, 0.017),
    ("PD-SSM (adapted public impl.)", 8): (0.990, 0.579),
    ("PD-SSM (adapted public impl.)", 64): (0.031, 0.022),
}
# Palette shared with the other figures in the paper.
BLUE = "#6F9FC9"
RED = "#CD7B7B"


def aggregate() -> dict:
    acc = {}
    sums = defaultdict(lambda: [0, 0, 0, 0])
    with open(DATA / "s3xs3_matchedlen_baselines.csv", newline="") as f:
        for row in csv.DictReader(f):
            s = sums[(row["model"], int(row["length"]))]
            s[0] += int(row["iid_exact"]); s[1] += int(row["iid_total"])
            s[2] += int(row["heldout_exact"]); s[3] += int(row["heldout_total"])
    for key, (ie, it, he, ht) in sums.items():
        acc[key] = (ie / it, he / ht)
    csums = defaultdict(lambda: [0, 0])
    with open(DATA / "s3xs3_matchedlen_carrier.csv", newline="") as f:
        for row in csv.DictReader(f):
            s = csums[(row["regime"].strip().lower(), int(row["eval_len"]))]
            s[0] += int(row["exact_count"]); s[1] += int(row["total_count"])
    for L in LENGTHS:
        acc[("Hard-projected (ours)", L)] = (
            csums[("iid", L)][0] / csums[("iid", L)][1],
            csums[("heldout", L)][0] / csums[("heldout", L)][1],
        )
    for key, (e_iid, e_ho) in EXPECTED.items():
        a_iid, a_ho = acc[key]
        assert abs(round(a_iid, 3) - e_iid) < 5e-4, (key, a_iid, e_iid)
        assert abs(round(a_ho, 3) - e_ho) < 5e-4, (key, a_ho, e_ho)
    return acc


def render(acc: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.1), sharey=True)
    width = 0.36
    x = np.arange(len(MODELS))
    for ax, L in zip(axes, LENGTHS):
        iid_vals = [acc[(k, L)][0] for k, _ in MODELS]
        ho_vals = [acc[(k, L)][1] for k, _ in MODELS]
        b1 = ax.bar(x - width / 2, iid_vals, width, label="IID", color=BLUE)
        b2 = ax.bar(x + width / 2, ho_vals, width, label="held-out", color=RED)
        for bars in (b1, b2):
            for b in bars:
                v = b.get_height()
                ax.annotate(f"{v:.3f}", (b.get_x() + b.get_width() / 2, v),
                            ha="center", va="bottom", fontsize=7.5, xytext=(0, 1.5),
                            textcoords="offset points")
        ax.axhline(CHANCE, color="black", linestyle=":", linewidth=1.2,
                   label=r"chance $= 1/36 \approx 0.0278$")
        ax.set_title(f"$L = {L}$", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([name for _, name in MODELS], fontsize=8.5)
        ax.set_ylim(0.0, 1.12)
        ax.grid(True, axis="y", alpha=0.25, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].set_ylabel("final-state accuracy (5 seeds)", fontsize=10)
    fig.suptitle("Matched-length decomposition under the held-out transition-pair protocol",
                 fontsize=12)
    handles, labels = axes[0].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    want = [l for l in labels if l.startswith("chance")] + ["IID", "held-out"]
    fig.legend([by_label[l] for l in want], want,
               loc="lower center", ncol=3, fontsize=9.5, frameon=False,
               bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    for ext in ("pdf", "png"):
        fig.savefig(_HERE / f"fig6_matchedlen_decomposition.{ext}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    render(aggregate())
    print("wrote fig6_matchedlen_decomposition.{pdf,png}; all 16 cells asserted "
          "against the paper's matched-length decomposition table")
