"""Turn the executed notebook's printed outputs into the deck's DataExports.

Every number the deck shows must trace to the notebook (INV-1). This script
reads the notebook's own text outputs, parses them with anchored patterns,
and writes one JSON file per topic under data/. Any pattern that fails to
match stops the export: a silent gap is worse than a loud one.

It also writes data/MANIFEST.md (source cell and sha256 per file) and
data/FIXTURES.md, which checks the exports against the values quoted in the
build spec. A fixture mismatch is reported, never "fixed" here: the notebook
wins, and a human decides what the slide should say.

Usage:  python tools/export_deck_data.py
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "source" / "CS667_Fall2026_Midterm_RafiulHaider_ShadmanRahman_RestaurantInspections.ipynb"
DATA = ROOT / "data"
AS_OF = "2026-10-21"


# ---------------------------------------------------------------- parsing

def cell_text(cells, idx):
    """All stream and text/plain output of one cell, joined."""
    parts = []
    for o in cells[idx].get("outputs", []):
        if o["output_type"] == "stream":
            parts.append("".join(o["text"]))
        elif "text/plain" in o.get("data", {}):
            parts.append("".join(o["data"]["text/plain"]))
    return "\n".join(parts)


def grab(pattern, text, cast=float, where=""):
    m = re.search(pattern, text, re.M)
    if not m:
        sys.exit(f"export failed: no match for {pattern!r} {where}")
    return cast(m.group(1).replace(",", ""))


def table_rows(text, header_pattern, n_rows, where=""):
    """The n_rows whitespace-split lines after the line matching header_pattern."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.search(header_pattern, line):
            rows = [l for l in lines[i + 1:] if l.strip()][:n_rows]
            if len(rows) < n_rows:
                break
            return rows
    sys.exit(f"export failed: table {header_pattern!r} with {n_rows} rows not found {where}")


def num(s):
    return float(s.replace(",", ""))


# ---------------------------------------------------------------- exports

def export_all(cells):
    out = {}

    t = cell_text(cells, 4)
    raw_rows = grab(r"Shape \(rows, columns\): \((\d+),", t, int, "cell 4")
    raw_cols = grab(r"Shape \(rows, columns\): \(\d+, (\d+)\)", t, int, "cell 4")
    t8 = cell_text(cells, 8)
    t9 = cell_text(cells, 9)
    out["dataset.json"] = ([4, 8, 9], {
        "raw_rows": raw_rows,
        "raw_columns": raw_cols,
        "placeholder_1900_rows": grab(r"never inspected\): (\d+)", t8, int, "cell 8"),
        "placeholder_share_pct": grab(r"Share of all rows: ([\d.]+)%", t8, float, "cell 8"),
        "earliest_inspection": grab(r"Earliest real inspection date: (\S+)", t8, str, "cell 8"),
        "latest_inspection": grab(r"Latest real inspection date:\s+(\S+)", t8, str, "cell 8"),
        "inspections": grab(r"one row per inspection\): (\d+)", t9, int, "cell 9"),
        "restaurants": grab(r"Unique restaurants \(camis\) in the data: (\d+)", t9, int, "cell 9"),
        "aggregation_key": ["camis", "inspection_date", "inspection_type"],
    })

    t = cell_text(cells, 11)
    out["score.json"] = ([11], {
        "lower_is_better": True,
        "count": grab(r"^count\s+([\d.]+)", t, lambda v: int(float(v)), "cell 11"),
        "mean": grab(r"^mean\s+([\d.]+)", t, float, "cell 11"),
        "median": grab(r"^50%\s+([\d.]+)", t, float, "cell 11"),
        "q1": grab(r"^Q1: ([\d.]+)", t, float, "cell 11"),
        "q3": grab(r"Q3: ([\d.]+)", t, float, "cell 11"),
        "upper_fence": grab(r"Upper fence: ([\d.]+)", t, float, "cell 11"),
        "n_above_fence": grab(r"above the fence: (\d+)", t, int, "cell 11"),
        "share_above_fence_pct": grab(r"above the fence: \d+ \(([\d.]+)%", t, float, "cell 11"),
        "max": grab(r"Worst \(highest\) score in the data: ([\d.]+)", t, float, "cell 11"),
        "grade_bands": {"A": [0, 13], "B": [14, 27], "C": [28, None]},
        "figure": "source/figures/eda_score_histogram.png",
    })

    t = cell_text(cells, 13)
    grades = []
    for row in table_rows(t, r"^grade\s*$", 7, "cell 13"):
        g, n, pct = row.split()
        grades.append({"grade": None if g == "None" else g, "inspections": int(n), "pct": float(pct)})
    out["grades.json"] = ([13], {"grades": grades})

    t = cell_text(cells, 15)
    miss = []
    for row in table_rows(t, r"n_missing\s+percent_missing", 14, "cell 15"):
        col, n, pct = row.split()
        miss.append({"column": col, "n_missing": int(n), "pct_missing": float(pct)})
    out["missingness.json"] = ([15], {"columns": miss})

    t = cell_text(cells, 19)
    boro = []
    for row in table_rows(t, r"count\s+median\s+mean\s+std", 7, "cell 19")[1:]:
        m = re.match(r"(.+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$", row.strip())
        boro.append({"boro": m.group(1), "count": int(m.group(2)), "median": float(m.group(3)),
                     "mean": float(m.group(4)), "std": float(m.group(5))})
    out["borough.json"] = ([19], {
        "lower_is_better": True,
        "note": "boro '0' is the raw file's unknown-borough code (84 scored inspections).",
        "boroughs": boro,
    })

    t = cell_text(cells, 21)
    cuisine = []
    for row in table_rows(t, r"inspections\s+median_score", 16, "cell 21")[1:]:
        m = re.match(r"(.+?)\s+(\d+)\s+([\d.]+)$", row.strip())
        cuisine.append({"cuisine": m.group(1), "inspections": int(m.group(2)),
                        "median_score": float(m.group(3))})
    out["cuisine.json"] = ([21], {"lower_is_better": True, "top_cuisines": cuisine})

    t = cell_text(cells, 25)
    rows = table_rows(t, r"score\s+n_violations\s+n_critical\s+latitude\s+longitude", 5, "cell 25")
    names = ["score", "n_violations", "n_critical", "latitude", "longitude"]
    matrix = [[float(v) for v in r.split()[1:]] for r in rows]
    out["correlation.json"] = ([25], {
        "columns": names,
        "matrix": matrix,
        "traps": [
            {"pair": ["score", "n_critical"], "r": matrix[0][2],
             "why": "score is built from violation points: arithmetic, not discovery"},
            {"pair": ["latitude", "longitude"], "r": matrix[3][4],
             "why": "the city's diagonal shape"},
        ],
    })

    t32 = cell_text(cells, 32)
    t42 = cell_text(cells, 42)

    def zip_rows(header_after, n):
        rows = []
        lines = t32.split(header_after, 1)[1].split("\n")
        hdr = next(i for i, l in enumerate(lines) if "zip5" in l)
        for l in lines[hdr + 1: hdr + 1 + n]:
            z, boro_, insp, graded, pct, med, crit = l.split()
            rows.append({"zip": z, "boro": boro_, "inspections": int(insp), "graded": int(graded),
                         "pct_bc": float(pct), "median_score": float(med), "mean_critical": float(crit)})
        return rows

    out["zip_risk.json"] = ([32, 42], {
        "min_graded_to_judge": 30,
        "zip_codes": grab(r"ZIP codes in the data: (\d+)", t32, int, "cell 32"),
        "reliable_zip_codes": grab(r"reliable \(30 or more graded\): (\d+)", t32, int, "cell 32"),
        "citywide_pct_bc": grab(r"Citywide, ([\d.]+)% of graded", t42, float, "cell 42"),
        "mapped_inspections": grab(r"Kept ([\d,]+) of", t42, int, "cell 42"),
        "highest_bc_reliable": zip_rows("Highest B or C share", 10),
        "busiest": zip_rows("Most inspections:", 5),
    })

    t = cell_text(cells, 40)
    nta = []
    for row in table_rows(t, r"ntaname\s+inspections\s+graded", 5, "cell 40"):
        m = re.match(r"(.+?)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)$", row.strip())
        nta.append({"nta": m.group(1), "inspections": int(m.group(2)), "graded": int(m.group(3)),
                    "pct_bc": float(m.group(4)), "median_score": float(m.group(5))})
    out["nta_risk.json"] = ([40], {"min_graded_to_judge": 30, "highest_bc": nta})

    t = cell_text(cells, 52)
    init_a = grab(r"initial inspection\s+(\d+)\s+\d+", t, int, "cell 52")
    init_bc = grab(r"initial inspection\s+\d+\s+(\d+)", t, int, "cell 52")
    other_a = grab(r"all other inspections\s+(\d+)\s+\d+", t, int, "cell 52")
    other_bc = grab(r"all other inspections\s+\d+\s+(\d+)", t, int, "cell 52")
    out["population.json"] = ([52], {
        "crosstab": {
            "initial": {"A": init_a, "BC": init_bc},
            "all_other": {"A": other_a, "BC": other_bc},
        },
        "graded_inspections": grab(r"Graded inspections \(A, B or C\): ([\d,]+)", t, int, "cell 52"),
        "excluded_initial": grab(r"Excluded initial inspections: ([\d,]+)", t, int, "cell 52"),
        "modeling_population": grab(r"Modeling population: ([\d,]+)", t, int, "cell 52"),
        "modeling_bc": grab(r"Ended B or C: ([\d,]+)", t, int, "cell 52"),
        "modeling_bc_pct": grab(r"Ended B or C: [\d,]+ \(([\d.]+)%\)", t, float, "cell 52"),
    })

    t54 = cell_text(cells, 54)
    t56 = cell_text(cells, 56)
    out["history.json"] = ([54, 56], {
        "features": ["prior_count", "prior_mean_score", "prior_bc_share", "prior_mean_critical",
                     "days_since_prior", "last_score", "has_history"],
        "first_row_check_passed": grab(r"first row has prior_count 0: (\w+)", t54, str, "cell 54") == "True",
        "share_with_history_pct": grab(r"any prior history: ([\d.]+)%", t54, float, "cell 54"),
        "zip_excluded": True,
        "dropped_bad_coordinates": grab(r"bad coordinates: ([\d,]+) of", t56, int, "cell 56"),
        "cuisine_levels_raw": grab(r"Cuisine levels: (\d+) raw", t56, int, "cell 56"),
        "cuisine_levels_grouped": grab(r"raw, (\d+) after grouping", t56, int, "cell 56"),
        "feature_table_rows": grab(r"Feature table: ([\d,]+) rows", t56, int, "cell 56"),
        "split": {
            "train": {"rule": "inspection year <= 2024",
                      "rows": grab(r"train: ([\d,]+) rows", t56, int, "cell 56"),
                      "bc_pct": grab(r"train: [\d,]+ rows, B or C rate ([\d.]+)%", t56, float, "cell 56")},
            "test": {"rule": "inspection year >= 2025",
                     "rows": grab(r"test: ([\d,]+) rows", t56, int, "cell 56"),
                     "bc_pct": grab(r"test: [\d,]+ rows, B or C rate ([\d.]+)%", t56, float, "cell 56")},
        },
        "example_restaurant": {
            "camis": grab(r"One restaurant \(camis (\d+)\)", t54, str, "cell 54"),
            "rows": [dict(zip(["inspection_date", "inspection_type", "score", "prior_count",
                               "prior_mean_score", "last_score"], r))
                     for r in _example_rows(t54)],
        },
    })

    t = cell_text(cells, 58)
    models = []
    for row in table_rows(t, r"model\s+train ROC-AUC\s+test ROC-AUC", 4, "cell 58"):
        m = re.match(r"(.+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$", row.strip())
        models.append({"model": m.group(1), "train_roc_auc": float(m.group(2)),
                       "test_roc_auc": float(m.group(3)), "test_pr_auc": float(m.group(4)),
                       "test_accuracy": float(m.group(5)), "precision_at_0_5": float(m.group(6)),
                       "recall_at_0_5": float(m.group(7))})
    out["models.json"] = ([58], {"sorted_by": "test_roc_auc", "models": models})

    t = cell_text(cells, 60)
    thr = []
    for row in table_rows(t, r"threshold\s+precision\s+recall\s+F1", 5, "cell 60"):
        a, p, r, f = (float(v) for v in row.split())
        thr.append({"threshold": a, "precision": p, "recall": r, "f1": f, "confusion": None})
    chosen = grab(r"at least 80% of B or C: ([\d.]+)", t, float, "cell 60")
    thr.append({"threshold": chosen,
                "precision": grab(r"precision ([\d.]+)\)", t, float, "cell 60"),
                "recall": grab(r"\(recall ([\d.]+),", t, float, "cell 60"),
                "f1": None, "confusion": None})
    thr.sort(key=lambda d: d["threshold"])
    out["thresholds.json"] = ([60], {
        "model": grab(r"Best model by test ROC-AUC: (.+)", t, str, "cell 60").strip(),
        "default_threshold": chosen,
        "rule": "highest threshold still catching at least 80% of B or C",
        "stops": thr,
        "confusion_counts_note": (
            "The notebook prints precision/recall per threshold but no confusion counts. "
            "Counts at 0.5 exist only in source/figures/pred_confusion.png. "
            "Per-stop counts need a notebook export (see data/FIXTURES.md)."),
        "figures": {"confusion_at_0_5": "source/figures/pred_confusion.png",
                    "curves": "source/figures/pred_curves.png"},
    })

    t = cell_text(cells, 62)
    perm = []
    for row in table_rows(t, r"feature\s+AUC drop when shuffled\s+std", 14, "cell 62"):
        f, d, s = row.split()
        perm.append({"feature": f, "auc_drop": float(d), "std": float(s)})
    out["importance.json"] = ([62], {"permutation": perm, "figure": "source/figures/pred_importance.png"})

    t = cell_text(cells, 66)
    comps = []
    for row in table_rows(t, r"component\s+variance %\s+cumulative %", 11, "cell 66"):
        c, v, cum = row.split()
        comps.append({"component": c, "variance_pct": float(v), "cumulative_pct": float(cum)})
    out["pca.json"] = ([66], {
        "components": comps,
        "n_for_80pct": grab(r"80% of variance: (\d+) of", t, int, "cell 66"),
        "n_for_90pct": grab(r"90% of variance: (\d+) of", t, int, "cell 66"),
        "n_features": grab(r"90% of variance: \d+ of (\d+)", t, int, "cell 66"),
        "pc1_reading": "past-performance axis (prior_mean_score, last_score, prior_mean_critical)",
        "pc2_reading": "history-depth axis (prior_count, has_history, prior_bc_share)",
        "logreg_all_components_auc": grab(r"all 11 components: test ROC-AUC ([\d.]+)", t, float, "cell 66"),
        "logreg_90pct_components_auc": grab(r"reaching 90%: test ROC-AUC ([\d.]+)", t, float, "cell 66"),
        "logreg_original_features_auc": grab(r"original numeric features: test ROC-AUC ([\d.]+)", t, float, "cell 66"),
        "figures": {"variance": "source/figures/pca_variance.png", "scatter": "source/figures/pca_scatter.png"},
    })

    t = cell_text(cells, 64)
    out["summary.json"] = ([64], {
        "best_model": grab(r"Best model: (.+)", t, str, "cell 64").strip(),
        "test_roc_auc": grab(r"test ROC-AUC ([\d.]+), test PR-AUC", t, float, "cell 64"),
        "test_pr_auc": grab(r"test PR-AUC ([\d.]+)", t, float, "cell 64"),
        "threshold": grab(r"at threshold ([\d.]+):", t, float, "cell 64"),
        "recall_at_threshold": grab(r"recall ([\d.]+), precision", t, float, "cell 64"),
        "precision_at_threshold": grab(r"recall [\d.]+, precision ([\d.]+)", t, float, "cell 64"),
        "train_rows": grab(r"Learned from ([\d,]+) inspections", t, int, "cell 64"),
        "test_rows": grab(r"tested on ([\d,]+) inspections", t, int, "cell 64"),
    })
    return out


def _example_rows(text):
    rows = []
    pat = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s+(.+?)\s+NaN\s+([\d.]+)\s+(\d+)\s+(\S+)\s+NaN\s+(\S+)\s*$")
    for line in text.split("\n"):
        m = pat.match(line)
        if m:
            d, typ, score, pc, pms, last = m.groups()
            rows.append([d, typ, float(score), int(pc),
                         None if pms == "NaN" else round(float(pms), 3),
                         None if last == "NaN" else float(last)])
    if not rows:
        sys.exit("export failed: example restaurant rows not found in cell 54")
    return rows


# ---------------------------------------------------------------- fixtures

# Values quoted in the build spec (Part 2). They validate the exports; they
# are never copied into a slide. path is a JSON lookup into data/<file>.
FIXTURES = [
    ("dataset.json", "raw_rows", 295356),
    ("dataset.json", "inspections", 96897),
    ("dataset.json", "restaurants", 31443),
    ("score.json", "median", 13.0),
    ("score.json", "mean", 17.9, 1),
    ("score.json", "upper_fence", 46.5),
    ("score.json", "n_above_fence", 4095),
    ("score.json", "max", 214.0),
    ("missingness.json", "columns[grade_date].pct_missing", 45.5, 1),
    ("missingness.json", "columns[grade].pct_missing", 43.2, 1),
    ("missingness.json", "columns[score].pct_missing", 14.7, 1),
    ("missingness.json", "columns[cuisine_description].pct_missing", 4.1, 1),
    ("borough.json", "boroughs[Manhattan].median", 12.0),
    ("borough.json", "boroughs[Bronx].median", 13.0),
    ("borough.json", "boroughs[Brooklyn].median", 13.0),
    ("borough.json", "boroughs[Queens].median", 13.0),
    ("borough.json", "boroughs[Staten Island].median", 13.0),
    ("cuisine.json", "top_cuisines[Donuts].median_score", 10.0),
    ("cuisine.json", "top_cuisines[Hamburgers].median_score", 10.0),
    ("cuisine.json", "top_cuisines[Latin American].median_score", 16.0),
    ("correlation.json", "traps[0].r", 0.86),
    ("correlation.json", "traps[1].r", -1.0),
    ("population.json", "crosstab.initial.A", 31758),
    ("population.json", "crosstab.initial.BC", 0),
    ("history.json", "feature_table_rows", 18998),
    ("history.json", "split.train.rows", 9111),
    ("history.json", "split.test.rows", 9887),
    ("population.json", "modeling_bc_pct", 33.8),
    ("pca.json", "components[PC1].variance_pct", 21.8),
    ("pca.json", "components[PC2].variance_pct", 16.6),
    ("pca.json", "n_for_90pct", 8),
    ("pca.json", "n_features", 11),
    ("pca.json", "logreg_90pct_components_auc", 0.631),
    ("pca.json", "logreg_original_features_auc", 0.644),
    ("models.json", "models[Logistic regression].test_roc_auc", 0.644),
    ("models.json", "models[Logistic regression].train_roc_auc", 0.644),
    ("models.json", "models[Random forest].test_roc_auc", 0.640),
    ("models.json", "models[Random forest].train_roc_auc", 1.000),
    ("models.json", "models[Gradient boosting].test_roc_auc", 0.637),
    ("models.json", "models[Gradient boosting].train_roc_auc", 0.870),
    ("models.json", "models[Dummy (always A)].test_roc_auc", 0.500),
    ("models.json", "models[Dummy (always A)].test_accuracy", 0.668),
    ("thresholds.json", "default_threshold", 0.45),
    ("summary.json", "recall_at_threshold", 0.822),
    ("summary.json", "precision_at_threshold", 0.376),
    ("zip_risk.json", "highest_bc_reliable[0].pct_bc", 33.3),
    ("zip_risk.json", "citywide_pct_bc", 12.9),
]

# Values the spec quotes that no notebook output carries. INV-1 keeps them
# off the slides until the notebook prints them.
NOT_IN_NOTEBOOK = [
    ("32.9% of graded re-inspections end B or C (slide 9)",
     "cell 38 (initial vs re-inspection map) was saved as 'Output hidden'; cell 52 only "
     "prints 'all other inspections' (6,497 of 19,242 = 33.8%), which is not the same population."),
    ("8,456 same-day restaurant pairs (slide 3 beat)",
     "described in a markdown cell as a one-off check; no cell prints it."),
    ("confusion counts per threshold stop (slide 13 slider)",
     "cell 60 prints precision/recall/F1 only; counts at 0.5 exist only inside pred_confusion.png."),
    ("ROC / PR curve points (curves.json for the native rebuild)",
     "cell 60 draws the curves into pred_curves.png but prints no points."),
]


def lookup(doc, path):
    cur = doc
    for part in re.findall(r"[^.\[\]]+(?:\[[^\]]+\])?", path):
        m = re.match(r"([^\[]+)(?:\[([^\]]+)\])?$", part)
        cur = cur[m.group(1)]
        if m.group(2) is not None:
            key = m.group(2)
            if key.isdigit():
                cur = cur[int(key)]
            else:
                cur = next(d for d in cur if key in d.values())
    return cur


def check_fixtures(docs):
    lines = ["# Fixture check", "",
             "Exports compared with the values quoted in the build spec. The notebook is the",
             "source of truth: a mismatch means the slide text in the spec must change, not",
             "the export.", "",
             "| File | Field | Spec | Notebook | Status |", "|---|---|---|---|---|"]
    failures = 0
    for fixture in FIXTURES:
        fname, path, expect = fixture[:3]
        digits = fixture[3] if len(fixture) > 3 else None
        got = lookup(docs[fname], path)
        cmp = round(got, digits) if digits is not None else got
        ok = cmp == expect
        failures += not ok
        lines.append(f"| {fname} | `{path}` | {expect} | {got} | {'ok' if ok else '**MISMATCH**'} |")
    lines += ["", "## Quoted in the spec, absent from every notebook output", "",
              "These cannot appear on a slide under INV-1 until the notebook prints them.", ""]
    for what, why in NOT_IN_NOTEBOOK:
        lines.append(f"- **{what}** — {why}")
    lines.append("")
    (DATA / "FIXTURES.md").write_text("\n".join(lines))
    return failures


# ---------------------------------------------------------------- main

def main():
    nb_bytes = NOTEBOOK.read_bytes()
    cells = json.loads(nb_bytes)["cells"]
    DATA.mkdir(exist_ok=True)
    exports = export_all(cells)

    docs = {}
    manifest = ["# Data manifest", "",
                f"Every file below is generated by `tools/export_deck_data.py` from the executed notebook",
                f"`{NOTEBOOK.name}` (sha256 `{hashlib.sha256(nb_bytes).hexdigest()[:16]}…`).",
                f"Data as of {AS_OF}. Do not edit these files by hand.", "",
                "| File | Notebook cells | sha256 |", "|---|---|---|"]
    for name, (src_cells, payload) in exports.items():
        doc = {"as_of": AS_OF, "source_cells": src_cells, **payload}
        docs[name] = doc
        body = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        (DATA / name).write_text(body)
        digest = hashlib.sha256(body.encode()).hexdigest()
        manifest.append(f"| `{name}` | {', '.join(map(str, src_cells))} | `{digest[:16]}` |")
        print("wrote", name)
    manifest.append("")
    (DATA / "MANIFEST.md").write_text("\n".join(manifest))

    failures = check_fixtures(docs)
    print(f"fixtures: {len(FIXTURES) - failures} ok, {failures} mismatched (see data/FIXTURES.md)")
    print(f"spec values with no notebook output: {len(NOT_IN_NOTEBOOK)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
