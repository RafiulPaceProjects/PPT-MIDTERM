#!/usr/bin/env python3
"""The money figure: headline accuracy beside accuracy including uncertain.

Every value is traced to the final record (LAYA_FINAL_RECORD.md) or to the
uplift result files; the source is named beside each panel's data below.
No number is computed here except bar placement.

Accounting rule the figure draws: headline accuracy counts an item the
arbitration labels "uncertain" as wrong. Accuracy including uncertain
scores those items by the model's own screen instead, so the two bars
differ only in how abstentions are scored. Where a headline gap between
arms vanishes or inverts between the two bars, the gap was a movement in
how often the model committed, not in how often it was right.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# Panel data: (arm label, headline acc, acc incl. uncertain, uncertain n, note)
# Sources:
#  A Stage A, record sec. 3.5 table (scorer audit recomputation).
#  B Stage B, record sec. 3.6 table; falsified headline acc 0 of 148 (sec. 3.6).
#  C Stage B tune read, uplift/stageb_tune_read.json (Amendment 16);
#    P1A labels all 100 tune items pristine (record sec. 5.4).
#  D Arm W, record sec. 5.3 (fitted accounting).
#  E Scale probe, uplift/scale_probe_results.json (Amendment 15) against
#    Stage A P0 from the same file.
PANELS = [
    (
        "A. Stage A: evidence at the\nfrozen model (probe, n=300)",
        [
            ("P0 pair-only", 0.4300, 0.5133, 44, ""),
            ("P1A evidence", 0.4500, 0.5300, 56, ""),
        ],
    ),
    (
        "B. Stage B: evidence in\ntraining (probe, n=300)",
        [
            ("P0 pair-only", 0.2533, 0.5167, 155, ""),
            ("P1A evidence", 0.5000, 0.5133, 6, "falsified acc 0 of 148"),
        ],
    ),
    (
        "C. Stage B tune read\n(n=100)",
        [
            ("P0 pair-only", 0.21, 0.55, 63, ""),
            ("P1A evidence", 0.50, 0.50, 0, "all 100 labelled pristine"),
        ],
    ),
    (
        "D. Arm W: Wikipedia evidence\n(probe, n=300)",
        [
            ("P0 pair-only", 0.4933, 0.5233, 16, ""),
            ("P1A evidence", 0.4433, 0.5567, 63, ""),
        ],
    ),
    (
        "E. Scale probe vs Stage A P0\n(probe, n=300)",
        [
            ("P0 at\n2,001 items", 0.4300, 0.5133, 44, ""),
            ("P0 at\n10,040 items", 0.0467, 0.5000, 274, "274 of 300 uncertain"),
        ],
    ),
]

# Display labels at the precision of their source (tune read is stored at 2dp).
LABELS = {(0.21, 0.55): ("0.21", "0.55"), (0.50, 0.50): ("0.50", "0.50")}

HEAD = "#2166ac"   # headline accuracy
INCL = "#e08214"   # accuracy including uncertain

fig, axes = plt.subplots(1, 5, figsize=(13.2, 4.0), sharey=True)
fig.subplots_adjust(left=0.045, right=0.995, top=0.79, bottom=0.21, wspace=0.14)

for ax, (title, arms) in zip(axes, PANELS):
    xs = [0, 1]
    width = 0.38
    for x, (label, head, incl, unc, note) in zip(xs, arms):
        b1 = ax.bar(x - width / 2, head, width, color=HEAD, zorder=3)
        b2 = ax.bar(x + width / 2, incl, width, color=INCL, zorder=3)
        head, incl = LABELS[(head, incl)] if (head, incl) in LABELS else (f"{head:.4f}", f"{incl:.4f}")
        for bar, val in ((b1[0], head), (b2[0], incl)):
            ax.annotate(
                val,
                (bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.025),
                ha="center",
                va="bottom",
                fontsize=8,
            )
        ax.annotate(
            f"uncertain {unc}",
            (x, -0.17),
            ha="center",
            va="top",
            fontsize=8,
            color="#444444",
            annotation_clip=False,
        )
        if note:
            ax.annotate(
                note,
                (x, 0.97),
                xycoords=("data", "axes fraction"),
                ha="center",
                va="top",
                fontsize=8,
                color="#b2182b",
                annotation_clip=False,
            )
    ax.axhline(0.5, color="#888888", lw=0.9, ls=(0, (4, 3)), zorder=2)
    ax.set_xticks(xs)
    ax.set_xticklabels([a[0] for a in arms], fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(axis="y", color="#dddddd", lw=0.6, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

axes[0].set_ylabel("Accuracy", fontsize=10.5)

fig.legend(
    handles=[
        Patch(facecolor=HEAD, label="Headline accuracy (uncertain counts as wrong)"),
        Patch(facecolor=INCL, label="Accuracy including uncertain"),
        Line2D([0], [0], color="#888888", lw=0.9, ls=(0, (4, 3)), label="Chance (0.50)"),
    ],
    loc="upper center",
    bbox_to_anchor=(0.5, 1.03),
    ncol=3,
    fontsize=10.5,
    frameon=False,
)

for ext in ("pdf", "png"):
    fig.savefig(f"fig_money.{ext}", dpi=220 if ext == "png" else None)
print("wrote fig_money.pdf and fig_money.png")
