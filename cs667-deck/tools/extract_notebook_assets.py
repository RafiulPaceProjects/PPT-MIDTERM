"""Pull the figures and HTML maps out of the executed notebook's outputs.

The notebook is the single source of truth. Every PNG and HTML file written
here is a byte-for-byte copy of an output the notebook itself produced; this
script recreates nothing.

Usage:  python tools/extract_notebook_assets.py
"""
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "source" / "CS667_Fall2026_Midterm_RafiulHaider_ShadmanRahman_RestaurantInspections.ipynb"
FIG_DIR = ROOT / "source" / "figures"
HTML_DIR = ROOT / "source" / "html"

# (cell index, image index within the cell) -> file name.
# Names match the notebook's own savefig() calls where it has one; the EDA
# figures are only shown inline, so they are named after their section.
FIGURES = {
    (11, 0): "eda_score_histogram.png",
    (13, 0): "eda_grade_distribution.png",
    (15, 0): "eda_missing_values.png",
    (17, 0): "eda_top_violations.png",
    (19, 0): "eda_borough_scores.png",
    (20, 0): "eda_borough_grade_share.png",
    (21, 0): "eda_cuisine_counts.png",
    (21, 1): "eda_cuisine_scores.png",
    (23, 0): "eda_inspections_over_time.png",
    (25, 0): "eda_correlation_heatmap.png",
    (60, 0): "pred_confusion.png",
    (60, 1): "pred_curves.png",
    (62, 0): "pred_importance.png",
    (66, 0): "pca_variance.png",
    (66, 1): "pca_scatter.png",
}

# Colab rendered the importance figure twice (the returned figure and
# plt.show()); the two outputs are byte-identical, so the second is skipped.
DUPLICATES = {(62, 1)}

# cell index -> file name, for the HTML maps embedded in the outputs.
# map_risk_zip.html, map_initial_vs_reinspection.html and nyc_hex_3d.html are
# NOT recoverable: Colab saved those cells as "Output hidden".
HTML = {
    34: "map_density.html",
    44: "nyc_zip_3d_hero.html",
    48: "nyc_scatter3d.html",
}


def main():
    nb = json.loads(NOTEBOOK.read_text())
    cells = nb["cells"]
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    found = {}
    for idx, cell in enumerate(cells):
        pngs = [o["data"]["image/png"] for o in cell.get("outputs", [])
                if "image/png" in o.get("data", {})]
        for k, png in enumerate(pngs):
            found[(idx, k)] = png

    missing = sorted(set(FIGURES) - set(found))
    unnamed = sorted(set(found) - set(FIGURES) - DUPLICATES)
    if missing or unnamed:
        sys.exit(f"Figure map out of date. missing={missing} unnamed={unnamed}")

    for dup in DUPLICATES:
        original = (dup[0], dup[1] - 1)
        if found[dup] != found[original]:
            sys.exit(f"cell {dup[0]}: output {dup[1]} is no longer a duplicate; name it")

    for key, name in FIGURES.items():
        (FIG_DIR / name).write_bytes(base64.b64decode(found[key]))
        print("figure", name)

    for idx, name in HTML.items():
        htmls = ["".join(o["data"]["text/html"]) for o in cells[idx].get("outputs", [])
                 if "text/html" in o.get("data", {})]
        if len(htmls) != 1:
            sys.exit(f"cell {idx}: expected one HTML output for {name}, found {len(htmls)}")
        (HTML_DIR / name).write_text(htmls[0])
        print("html  ", name, f"{len(htmls[0]):,} chars")


if __name__ == "__main__":
    main()
