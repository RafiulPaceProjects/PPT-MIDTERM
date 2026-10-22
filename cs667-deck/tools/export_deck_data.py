"""Produce every data/*.json the deck reads, from the notebook's own outputs.

Sources, all under source/ (INV-1):
  * the executed notebook: its printed text outputs and the hero map HTML it
    rendered (cell 44), parsed with anchored patterns;
  * modeling_table.csv, the table the notebook saved in cell 56. The models
    are re-fitted from it with the notebook's exact pipeline so that the
    curve points and per-threshold confusion counts come from a fitted
    model, never from a person. The refit must reproduce every number the
    notebook printed for the models (cells 58, 60, 62), or the export stops;
  * nta_risk_table.csv, the table the notebook saved in cell 40;
  * deck_exports.json (optional), written by tools/notebook_export_cell.py
    when that cell is run in Colab. It carries the values no saved output
    holds. Until it exists, those values are listed as pending and the deck
    shows "awaiting export" in their place.

Outputs: data/{key_metrics,thresholds,curves,confusion,importance,tables,
pca,maps}.json, data/deck-data.js (the same JSON as one script, so the deck
also works from file://), data/MANIFEST.md and data/FIXTURES.md.

Exit status is non-zero when any fixture mismatches: this is the numbers
gate. A mismatch is reported, never "fixed" here.

Usage:  python3 tools/export_deck_data.py
"""
import hashlib
import json
import math
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
NOTEBOOK = SRC / "CS667_Fall2026_Midterm_RafiulHaider_ShadmanRahman_RestaurantInspections.ipynb"
MODELING = SRC / "modeling_table.csv"
NTA = SRC / "nta_risk_table.csv"
EXTRA = SRC / "deck_exports.json"
RISK_MAP = SRC / "html" / "map_risk_zip.html"
VISIT_MAP = SRC / "html" / "map_initial_vs_reinspection.html"
DATA = ROOT / "data"
AS_OF = "2026-10-21"
AS_OF_TEXT = "October 21, 2026"


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
    """The n_rows non-blank lines after the line matching header_pattern."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.search(header_pattern, line):
            rows = [l for l in lines[i + 1:] if l.strip()][:n_rows]
            if len(rows) == n_rows:
                return rows
    sys.exit(f"export failed: table {header_pattern!r} with {n_rows} rows not found {where}")


def clean(v):
    """JSON-safe: numpy scalars to Python, NaN to None."""
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if math.isnan(v) else float(v)
    if isinstance(v, np.bool_):
        return bool(v)
    return v


# ---------------------------------------------------------------- notebook

def from_notebook(cells):
    nb = {}

    t4, t8, t9 = cell_text(cells, 4), cell_text(cells, 8), cell_text(cells, 9)
    nb["dataset"] = {
        "raw_rows": grab(r"Shape \(rows, columns\): \((\d+),", t4, int, "cell 4"),
        "raw_columns": grab(r"Shape \(rows, columns\): \(\d+, (\d+)\)", t4, int, "cell 4"),
        "placeholder_1900_rows": grab(r"never inspected\): (\d+)", t8, int, "cell 8"),
        "placeholder_share_pct": grab(r"Share of all rows: ([\d.]+)%", t8, float, "cell 8"),
        "earliest_inspection": grab(r"Earliest real inspection date: (\S+)", t8, str, "cell 8"),
        "latest_inspection": grab(r"Latest real inspection date:\s+(\S+)", t8, str, "cell 8"),
        "inspections": grab(r"one row per inspection\): (\d+)", t9, int, "cell 9"),
        "restaurants": grab(r"Unique restaurants \(camis\) in the data: (\d+)", t9, int, "cell 9"),
    }

    t = cell_text(cells, 11)
    nb["score"] = {
        "count": grab(r"^count\s+([\d.]+)", t, lambda v: int(float(v)), "cell 11"),
        "mean": grab(r"^mean\s+([\d.]+)", t, float, "cell 11"),
        "median": grab(r"^50%\s+([\d.]+)", t, float, "cell 11"),
        "q1": grab(r"^Q1: ([\d.]+)", t, float, "cell 11"),
        "q3": grab(r"Q3: ([\d.]+)", t, float, "cell 11"),
        "upper_fence": grab(r"Upper fence: ([\d.]+)", t, float, "cell 11"),
        "n_above_fence": grab(r"above the fence: (\d+)", t, int, "cell 11"),
        "share_above_fence_pct": grab(r"above the fence: \d+ \(([\d.]+)%", t, float, "cell 11"),
        "max": grab(r"Worst \(highest\) score in the data: ([\d.]+)", t, float, "cell 11"),
    }

    t = cell_text(cells, 13)
    nb["grades"] = []
    for row in table_rows(t, r"^grade\s*$", 7, "cell 13"):
        g, n, pct = row.split()
        nb["grades"].append({"grade": None if g == "None" else g, "inspections": int(n), "pct": float(pct)})

    t = cell_text(cells, 15)
    nb["missingness"] = []
    for row in table_rows(t, r"n_missing\s+percent_missing", 14, "cell 15"):
        col, n, pct = row.split()
        nb["missingness"].append({"column": col, "n_missing": int(n), "pct_missing": float(pct)})

    t = cell_text(cells, 19)
    nb["borough"] = []
    for row in table_rows(t, r"count\s+median\s+mean\s+std", 7, "cell 19")[1:]:
        m = re.match(r"(.+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$", row.strip())
        nb["borough"].append({"boro": m.group(1), "count": int(m.group(2)), "median": float(m.group(3)),
                              "mean": float(m.group(4)), "std": float(m.group(5))})

    t = cell_text(cells, 21)
    nb["cuisine"] = []
    for row in table_rows(t, r"inspections\s+median_score", 16, "cell 21")[1:]:
        m = re.match(r"(.+?)\s+(\d+)\s+([\d.]+)$", row.strip())
        nb["cuisine"].append({"cuisine": m.group(1), "inspections": int(m.group(2)),
                              "median_score": float(m.group(3))})

    t = cell_text(cells, 25)
    rows = table_rows(t, r"score\s+n_violations\s+n_critical\s+latitude\s+longitude", 5, "cell 25")
    nb["correlation"] = {"columns": ["score", "n_violations", "n_critical", "latitude", "longitude"],
                         "matrix": [[float(v) for v in r.split()[1:]] for r in rows]}

    t32, t42 = cell_text(cells, 32), cell_text(cells, 42)

    def zip_rows(after, n):
        lines = t32.split(after, 1)[1].split("\n")
        hdr = next(i for i, l in enumerate(lines) if "zip5" in l)
        out = []
        for l in lines[hdr + 1: hdr + 1 + n]:
            z, boro, insp, graded, pct, med, crit = l.split()
            out.append({"zip": z, "boro": boro, "inspections": int(insp), "graded": int(graded),
                        "pct_bc": float(pct), "median_score": float(med), "mean_critical": float(crit)})
        return out

    nb["zip"] = {
        "zip_codes": grab(r"ZIP codes in the data: (\d+)", t32, int, "cell 32"),
        "reliable_zip_codes": grab(r"reliable \(30 or more graded\): (\d+)", t32, int, "cell 32"),
        "citywide_pct_bc": grab(r"Citywide, ([\d.]+)% of graded", t42, float, "cell 42"),
        "mapped_inspections": grab(r"Kept ([\d,]+) of", t42, int, "cell 42"),
        "highest_bc_reliable": zip_rows("Highest B or C share", 10),
        "busiest": zip_rows("Most inspections:", 5),
    }

    t = cell_text(cells, 40)
    nb["nta"] = {
        "polygons": grab(r"NTA polygons: (\d+)", t, int, "cell 40"),
        "placed": grab(r"placed in an NTA: ([\d,]+) of", t, int, "cell 40"),
        "placed_of": grab(r"placed in an NTA: [\d,]+ of ([\d,]+)", t, int, "cell 40"),
        "neighborhoods": grab(r"nta_risk_table.csv \((\d+) neighborhoods\)", t, int, "cell 40"),
    }

    t = cell_text(cells, 52)
    nb["population"] = {
        "initial_A": grab(r"initial inspection\s+(\d+)\s+\d+", t, int, "cell 52"),
        "initial_BC": grab(r"initial inspection\s+\d+\s+(\d+)", t, int, "cell 52"),
        "other_A": grab(r"all other inspections\s+(\d+)\s+\d+", t, int, "cell 52"),
        "other_BC": grab(r"all other inspections\s+\d+\s+(\d+)", t, int, "cell 52"),
        "graded_inspections": grab(r"Graded inspections \(A, B or C\): ([\d,]+)", t, int, "cell 52"),
        "excluded_initial": grab(r"Excluded initial inspections: ([\d,]+)", t, int, "cell 52"),
        "population": grab(r"Modeling population: ([\d,]+)", t, int, "cell 52"),
        "population_bc": grab(r"Ended B or C: ([\d,]+)", t, int, "cell 52"),
        "population_bc_pct": grab(r"Ended B or C: [\d,]+ \(([\d.]+)%\)", t, float, "cell 52"),
    }

    t54, t56 = cell_text(cells, 54), cell_text(cells, 56)
    example = []
    pat = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s+(.+?)\s+NaN\s+([\d.]+)\s+(\d+)\s+(\S+)\s+NaN\s+(\S+)\s*$")
    for line in t54.split("\n"):
        m = pat.match(line)
        if m:
            d, typ, score, pc, pms, last = m.groups()
            example.append({"inspection_date": d, "inspection_type": typ, "score": float(score),
                            "prior_count": int(pc),
                            "prior_mean_score": None if pms == "NaN" else round(float(pms), 1),
                            "last_score": None if last == "NaN" else float(last)})
    if len(example) != 6:
        sys.exit("export failed: example restaurant rows not found in cell 54")
    nb["history"] = {
        "first_row_check_passed": grab(r"first row has prior_count 0: (\w+)", t54, str, "cell 54") == "True",
        "share_with_history_pct": grab(r"any prior history: ([\d.]+)%", t54, float, "cell 54"),
        "example_camis": grab(r"One restaurant \(camis (\d+)\)", t54, str, "cell 54"),
        "example": example,
        "dropped_bad_coordinates": grab(r"bad coordinates: ([\d,]+) of", t56, int, "cell 56"),
        "cuisine_levels_raw": grab(r"Cuisine levels: (\d+) raw", t56, int, "cell 56"),
        "cuisine_levels_grouped": grab(r"raw, (\d+) after grouping", t56, int, "cell 56"),
        "feature_rows": grab(r"Feature table: ([\d,]+) rows", t56, int, "cell 56"),
        "feature_columns": grab(r"Feature table: [\d,]+ rows x (\d+) columns", t56, int, "cell 56"),
        "train_rows": grab(r"train: ([\d,]+) rows", t56, int, "cell 56"),
        "train_bc_pct": grab(r"train: [\d,]+ rows, B or C rate ([\d.]+)%", t56, float, "cell 56"),
        "test_rows": grab(r"test: ([\d,]+) rows", t56, int, "cell 56"),
        "test_bc_pct": grab(r"test: [\d,]+ rows, B or C rate ([\d.]+)%", t56, float, "cell 56"),
    }

    t = cell_text(cells, 58)
    nb["models"] = []
    for row in table_rows(t, r"model\s+train ROC-AUC\s+test ROC-AUC", 4, "cell 58"):
        m = re.match(r"(.+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$", row.strip())
        nb["models"].append({"model": m.group(1), "train_roc_auc": float(m.group(2)),
                             "test_roc_auc": float(m.group(3)), "test_pr_auc": float(m.group(4)),
                             "test_accuracy": float(m.group(5)), "precision_at_0_5": float(m.group(6)),
                             "recall_at_0_5": float(m.group(7))})

    t = cell_text(cells, 60)
    printed = {}
    for row in table_rows(t, r"threshold\s+precision\s+recall\s+F1", 5, "cell 60"):
        a, p, r, f = (float(v) for v in row.split())
        printed[a] = {"precision": p, "recall": r, "f1": f}
    chosen = grab(r"at least 80% of B or C: ([\d.]+)", t, float, "cell 60")
    printed[chosen] = {"precision": grab(r"precision ([\d.]+)\)", t, float, "cell 60"),
                       "recall": grab(r"\(recall ([\d.]+),", t, float, "cell 60")}
    nb["thresholds"] = {"best_model": grab(r"Best model by test ROC-AUC: (.+)", t, str, "cell 60").strip(),
                        "chosen": chosen, "printed": printed}

    t = cell_text(cells, 62)
    nb["coef_printed"] = {}
    for header in (r"strongest pushes toward B or C:", r"strongest pushes toward A:"):
        for row in table_rows(t, header, 11, "cell 62")[1:]:
            f, c = row.rsplit(None, 1)
            nb["coef_printed"][f.strip()] = float(c)
    nb["permutation"] = []
    for row in table_rows(t, r"feature\s+AUC drop when shuffled\s+std", 14, "cell 62"):
        f, d, s = row.split()
        nb["permutation"].append({"feature": f, "auc_drop": float(d), "std": float(s)})

    t = cell_text(cells, 64)
    nb["summary"] = {
        "best_model": grab(r"Best model: (.+)", t, str, "cell 64").strip(),
        "test_roc_auc": grab(r"test ROC-AUC ([\d.]+), test PR-AUC", t, float, "cell 64"),
        "test_pr_auc": grab(r"test PR-AUC ([\d.]+)", t, float, "cell 64"),
        "threshold": grab(r"at threshold ([\d.]+):", t, float, "cell 64"),
        "recall": grab(r"recall ([\d.]+), precision", t, float, "cell 64"),
        "precision": grab(r"recall [\d.]+, precision ([\d.]+)", t, float, "cell 64"),
        "leans_on": [s.strip() for s in grab(r"Features it leans on most: (.+)", t, str, "cell 64").split(",")],
    }

    t = cell_text(cells, 66)
    comps = []
    for row in table_rows(t, r"component\s+variance %\s+cumulative %", 11, "cell 66"):
        c, v, cum = row.split()
        comps.append({"component": c, "variance_pct": float(v), "cumulative_pct": float(cum)})

    def loadings(name):
        out = []
        for row in table_rows(t, rf"{name} loadings, strongest first:", 11, "cell 66"):
            f, v = row.split()
            out.append({"feature": f, "loading": float(v)})
        return out

    nb["pca"] = {
        "components": comps,
        "n_for_80pct": grab(r"80% of variance: (\d+) of", t, int, "cell 66"),
        "n_for_90pct": grab(r"90% of variance: (\d+) of", t, int, "cell 66"),
        "n_features": grab(r"90% of variance: \d+ of (\d+)", t, int, "cell 66"),
        "pc1_loadings": loadings("PC1"),
        "pc2_loadings": loadings("PC2"),
        "auc_all_components": grab(r"all 11 components: test ROC-AUC ([\d.]+)", t, float, "cell 66"),
        "auc_90pct_components": grab(r"reaching 90%: test ROC-AUC ([\d.]+)", t, float, "cell 66"),
        "auc_original_features": grab(r"original numeric features: test ROC-AUC ([\d.]+)", t, float, "cell 66"),
    }

    # the hero map (cell 44): its embedded per-ZIP column data
    html = ["".join(o["data"]["text/html"]) for o in cells[44]["outputs"] if "text/html" in o.get("data", {})]
    m = re.search(r"const jsonInput = (\{.*?\});\s*const tooltip", html[0], re.S)
    if not m:
        sys.exit("export failed: hero jsonInput not found in cell 44")
    spec = json.loads(m.group(1))
    layer = spec["layers"][0]
    nb["hero"] = {
        "view": spec["initialViewState"],
        "elevation_scale": layer["elevationScale"],
        "radius_m": layer["radius"],
        "zips": [{"zip": d["zipcode"], "lat": round(d["lat"], 5), "lon": round(d["lon"], 5),
                  "inspections": d["inspections"], "graded": d["graded"], "n_bc": d["n_bc"],
                  "pct_bc": d["pct_bc"], "reliable": d["reliable"],
                  "elev": round(d["elev"], 4), "fill_color": [int(c) for c in d["fill_color"]]}
                 for d in layer["data"]],
    }
    return nb


# ---------------------------------------------------------------- maps

def plotly_traces(path):
    """The data array of the figure's Plotly.newPlot(...) call."""
    text = path.read_text(encoding="utf8")
    at = text.find("Plotly.newPlot(")
    if at < 0:
        sys.exit(f"export failed: no Plotly figure in {path.name}")
    return json.JSONDecoder().raw_decode(text, text.index("[", at))[0]


def z_values(trace):
    """Plotly stores z either as a list or as a base64 typed array."""
    z = trace["z"]
    if isinstance(z, dict):
        import base64
        return np.frombuffer(base64.b64decode(z["bdata"]), dtype=np.dtype(z["dtype"])).tolist()
    return z


def _rdp(points, eps):
    """Douglas-Peucker on one ring (lon scaled by cos(lat) so eps is isotropic)."""
    if len(points) < 5:
        return points
    k = math.cos(math.radians(40.7))
    a, b = points[0], points[-1]
    ax, ay, bx, by = a[0] * k, a[1], b[0] * k, b[1]
    dx, dy = bx - ax, by - ay
    norm = math.hypot(dx, dy)
    best, idx = -1.0, 0
    for i in range(1, len(points) - 1):
        px, py = points[i][0] * k, points[i][1]
        d = abs(dy * px - dx * py + bx * ay - by * ax) / norm if norm else math.hypot(px - ax, py - ay)
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [a, b]
    return _rdp(points[: idx + 1], eps)[:-1] + _rdp(points[idx:], eps)


def simplify(geometry, eps=0.00035):
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    out = []
    for poly in polys:
        rings = []
        for ring in poly:
            r = _rdp([tuple(p) for p in ring], eps)
            if len(r) >= 4:
                rings.append([[round(x, 4), round(y, 4)] for x, y in r])
        if rings:
            out.append(rings)
    return out


def from_maps(hero_zips):
    """ZIP polygons, the risk map's per-ZIP values and the visit-kind panels,
    read from the two Plotly maps the notebook wrote (cells 13.4 and 13.5)."""
    if not (RISK_MAP.exists() and VISIT_MAP.exists()):
        return None
    risk = plotly_traces(RISK_MAP)
    visit = plotly_traces(VISIT_MAP)

    shapes = {f["properties"]["zcta5"]: simplify(f["geometry"]) for f in risk[0]["geojson"]["features"]}

    hero = {z["zip"]: z for z in hero_zips}
    risk_rows, problems = [], []
    for trace in risk:
        reliable = trace.get("name") == "B or C share"
        for zip_, z, txt in zip(trace["locations"], z_values(trace), trace["text"]):
            graded = int(re.search(r"Graded: ([\d,]+)", txt).group(1).replace(",", ""))
            row = {"zip": zip_, "reliable": reliable, "graded": graded,
                   "pct_bc": round(z, 4) if reliable else None}
            h = hero.get(zip_)
            # the risk map and the hero must agree on every ZIP they share
            if h is None or h["graded"] != graded or h["reliable"] != reliable or \
                    (reliable and round(z, 1) != h["pct_bc"]):
                problems.append(zip_)
            risk_rows.append(row)
    if problems:
        sys.exit(f"export failed: risk map and hero data disagree on ZIPs {problems[:5]}")

    panels = {"initial": [], "reinspection": []}
    zmax = None
    for trace in visit:
        kind = "initial" if trace.get("subplot", "map") == "map" else "reinspection"
        reliable = "colorbar" in trace
        if reliable:
            zmax = trace["zmax"]
        for zip_, z, txt in zip(trace["locations"], z_values(trace), trace["text"]):
            scored = int(re.search(r"Scored(?: inspections)?: ([\d,]+)", txt).group(1).replace(",", ""))
            med = re.search(r"Median score: (\d+)", txt)
            panels[kind].append({"zip": zip_, "scored": scored, "reliable": reliable,
                                 "pct_high": round(z, 4) if reliable else None,
                                 "median_score": int(med.group(1)) if med else None})
    floor = 20
    bad = [p["zip"] for k in panels for p in panels[k] if (p["scored"] >= floor) != p["reliable"]]
    if bad:
        sys.exit(f"export failed: visit-kind panels break the 20-scored floor on {bad[:5]}")
    return {"shapes": shapes, "risk": risk_rows,
            "panels": {"floor_scored": floor, "shared_zmax": zmax, "measure": "share of scored inspections at 14 points or more",
                       "panels": panels}}


# ---------------------------------------------------------------- deck_exports.json

def normalize_extra(raw, mapdata):
    """Accept deck_exports.json in either shape: the one tools/notebook_export_cell.py
    writes, or the team-supplied one (same_day_multi_type_pairs, *_scored_14_plus,
    zip_boundary_match). Every share must equal its own counts, and the counts must
    fit the per-ZIP map data, or the export stops."""
    if raw is None:
        return None
    if "record_date" in raw:                      # written by the Colab cell
        if raw["record_date"] != "10/21/2026":
            sys.exit("export failed: deck_exports.json is not from the October 21, 2026 file")
        return raw
    if "October 21, 2026" not in raw.get("_about", ""):
        sys.exit("export failed: deck_exports.json does not say it is from the October 21, 2026 run")
    problems = []
    visit = {}
    for kind, key in (("initial", "initial_scored_14_plus"), ("reinspection", "reinspection_scored_14_plus")):
        v = raw[key]
        if round(100 * v["scored_14_plus"] / v["scored"], 1) != v["share_pct"]:
            problems.append(f"{key}: share does not match its counts")
        if mapdata:
            ps = mapdata["panels"]["panels"][kind]
            in_maps = sum(p["scored"] for p in ps)
            known_high = round(sum(p["pct_high"] * p["scored"] / 100 for p in ps if p["reliable"]))
            unknown = sum(p["scored"] for p in ps if not p["reliable"]) + (v["scored"] - in_maps)
            if in_maps > v["scored"] or not known_high <= v["scored_14_plus"] <= known_high + unknown:
                problems.append(f"{key}: counts do not fit the per-ZIP map data")
        visit[kind] = {"scored": v["scored"], "scored_14_plus": v["scored_14_plus"], "pct_scored_14_plus": v["share_pct"]}
    zb = raw["zip_boundary_match"]
    if round(100 * zb["inspections_matched"] / zb["inspections_with_zip"], 1) != zb["share_pct"]:
        problems.append("zip_boundary_match: share does not match its counts")
    if mapdata and zb["zips_matched_to_boundary"] != len(mapdata["risk"]):
        problems.append("zip_boundary_match: ZIP count differs from the risk map")
    if problems:
        sys.exit("export failed: deck_exports.json is inconsistent:\n  " + "\n  ".join(problems))
    return {"same_day_multi_type": raw["same_day_multi_type_pairs"], "visit_kind": visit,
            "zcta_match": {"pct_matched": zb["share_pct"], "inspections_matched": zb["inspections_matched"],
                           "inspections_with_zip": zb["inspections_with_zip"],
                           "zips_matched": zb["zips_matched_to_boundary"], "zips_in_data": zb["zips_in_data"]},
            "provenance": raw.get("_about")}


# ---------------------------------------------------------------- refit

HISTORY_COLS = ["prior_count", "prior_mean_score", "prior_bc_share", "prior_mean_critical",
                "days_since_prior", "last_score", "has_history"]
CAT_COLS = ["boro", "cuisine_grouped", "inspection_type"]
NUM_COLS = ["latitude", "longitude", "month", "weekday"] + HISTORY_COLS
STOPS = [0.3, 0.4, 0.45, 0.5, 0.6, 0.7]


def refit(pop):
    """Cell 57/58's pipeline, verbatim, on the saved modeling table."""
    from sklearn.compose import ColumnTransformer
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                                 precision_recall_curve, precision_score, recall_score,
                                 roc_auc_score, roc_curve)
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    features = CAT_COLS + NUM_COLS
    tr, te = pop[pop["split"] == "train"], pop[pop["split"] == "test"]
    pre_lr = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), NUM_COLS)])
    pre_tree = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ("num", SimpleImputer(strategy="median"), NUM_COLS)])
    models = {
        "Dummy (always A)": (pre_tree, DummyClassifier(strategy="most_frequent")),
        "Logistic regression": (pre_lr, LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42)),
        "Random forest": (pre_tree, RandomForestClassifier(
            n_estimators=300, class_weight="balanced_subsample", n_jobs=-1, random_state=42)),
        "Gradient boosting": (pre_tree, HistGradientBoostingClassifier(random_state=42)),
    }
    out = {"rows": [], "curves": {}, "y_test_positives": int(te["y"].sum()), "test_rows": len(te)}
    p_lr, lr_pipe = None, None
    for name, (pre, model) in models.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pipe.fit(tr[features], tr["y"])
        p_tr = pipe.predict_proba(tr[features])[:, 1]
        p_te = pipe.predict_proba(te[features])[:, 1]
        pred = (p_te >= 0.5).astype(int)
        out["rows"].append({
            "model": name,
            "train_roc_auc": roc_auc_score(tr["y"], p_tr),
            "test_roc_auc": roc_auc_score(te["y"], p_te),
            "test_pr_auc": average_precision_score(te["y"], p_te),
            "test_accuracy": accuracy_score(te["y"], pred),
            "precision_at_0_5": precision_score(te["y"], pred, zero_division=0),
            "recall_at_0_5": recall_score(te["y"], pred, zero_division=0),
            "caught_at_0_5": int(((pred == 1) & (te["y"] == 1)).sum()),
        })
        fpr, tpr, _ = roc_curve(te["y"], p_te)
        prec, rec, _ = precision_recall_curve(te["y"], p_te)
        out["curves"][name] = {"roc": thin(fpr, tpr), "pr": thin(rec[::-1], prec[::-1])}
        if name == "Logistic regression":
            p_lr, lr_pipe = p_te, pipe

    stops = []
    for t in STOPS:
        pred = (p_lr >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(te["y"], pred, labels=[0, 1]).ravel()
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        stops.append({"threshold": t, "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
                      "precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0,
                      "fpr": fp / (fp + tn) if fp + tn else 0.0,
                      "flagged": int(tp + fp)})
    out["stops"] = stops
    names = lr_pipe.named_steps["pre"].get_feature_names_out()
    out["coefficients"] = [{"feature": f, "coefficient": float(c)}
                           for f, c in zip(names, lr_pipe.named_steps["model"].coef_[0])]
    return out


def thin(xs, ys, n=160):
    """The curve's shape in at most n points, first and last kept."""
    idx = np.unique(np.linspace(0, len(xs) - 1, min(n, len(xs))).round().astype(int))
    return [[round(float(xs[i]), 4), round(float(ys[i]), 4)] for i in idx]


def verify_refit(nb, fit):
    """The refit must reproduce every model number the notebook printed."""
    problems = []
    by_name = {r["model"]: r for r in fit["rows"]}
    for row in nb["models"]:
        got = by_name[row["model"]]
        for k, v in row.items():
            if k != "model" and round(got[k], 3) != v:
                problems.append(f"{row['model']} {k}: notebook {v}, refit {got[k]:.4f}")
    for s in fit["stops"]:
        want = nb["thresholds"]["printed"].get(s["threshold"])
        if want is None:
            problems.append(f"threshold {s['threshold']} not printed by the notebook")
            continue
        for k, v in want.items():
            if round(s[k], 3) != v:
                problems.append(f"threshold {s['threshold']} {k}: notebook {v}, refit {s[k]:.4f}")
    coefs = {c["feature"]: c["coefficient"] for c in fit["coefficients"]}
    for f, v in nb["coef_printed"].items():
        if round(coefs.get(f, float("nan")), 3) != v:
            problems.append(f"coefficient {f}: notebook {v}, refit {coefs.get(f)}")
    if problems:
        sys.exit("export failed: the refit does not reproduce the notebook:\n  " + "\n  ".join(problems))


# ---------------------------------------------------------------- assemble

# Values the deck needs that no saved output carries. Each is filled from
# deck_exports.json when present; otherwise it stays pending (INV-1).
PENDING_REASONS = {
    "same_day_multi_type": "described in a markdown cell only; no cell prints it",
    "visit_kind_scored_14_plus": "cell 13.5 (initial vs re-inspection maps) was saved as 'Output hidden'",
    "visit_kind_zip_panels": "cell 13.5's per-ZIP panels were saved as 'Output hidden'",
    "zcta_match_pct": "cell 13.4 (ZIP risk map) was saved as 'Output hidden'",
    "zcta_shapes": "the ZIP boundary polygons were never saved by the notebook",
}


def build(nb, pop, nta, fit, extra, mapdata=None):
    pending = []

    def take(key, value):
        if value is None:
            pending.append({"key": key, "reason": PENDING_REASONS[key]})
        return value

    reins = pop[pop["inspection_type"].str.endswith("Re-inspection", na=False)]
    best = next(r for r in fit["rows"] if r["model"] == nb["thresholds"]["best_model"])
    dummy = next(r for r in fit["rows"] if r["model"].startswith("Dummy"))
    zips = nb["zip"]
    worst = zips["highest_bc_reliable"][0]
    busiest_pale = [z for z in zips["busiest"] if z["pct_bc"] < zips["citywide_pct_bc"]]
    nta_rel = nta[nta["reliable"]].sort_values("pct_bc", ascending=False)
    vk = (extra or {}).get("visit_kind")

    key_metrics = {
        "as_of_text": AS_OF_TEXT,
        "dataset": {**nb["dataset"],
                    "same_day_multi_type": take("same_day_multi_type", (extra or {}).get("same_day_multi_type"))},
        "score": {**nb["score"], "lower_is_better": True,
                  "grade_bands": {"A": "0–13", "B": "14–27", "C": "28+"}, "a_boundary": 13},
        "missing": {m["column"]: m["pct_missing"] for m in nb["missingness"]},
        "population": {**nb["population"],
                       "modeled_rows": len(pop),
                       "modeled_bc": int(pop["y"].sum()),
                       "modeled_bc_pct": round(100 * pop["y"].mean(), 1)},
        "visit_kind": {
            "initial_graded": nb["population"]["initial_A"] + nb["population"]["initial_BC"],
            "initial_bc": nb["population"]["initial_BC"],
            "initial_bc_pct": round(100 * nb["population"]["initial_BC"]
                                    / (nb["population"]["initial_A"] + nb["population"]["initial_BC"]), 1),
            "reinspection_graded": len(reins),
            "reinspection_bc": int(reins["y"].sum()),
            "reinspection_bc_pct": round(100 * reins["y"].mean(), 1),
            "reinspection_note": "graded re-inspections with a usable location (modeling_table.csv)",
            "initial_pct_scored_14_plus": take("visit_kind_scored_14_plus",
                                               vk and vk["initial"]["pct_scored_14_plus"]),
            "reinspection_pct_scored_14_plus": vk and vk["reinspection"]["pct_scored_14_plus"],
            "initial_scored": vk and vk["initial"].get("scored"),
            "reinspection_scored": vk and vk["reinspection"].get("scored"),
        },
        "history": {k: v for k, v in nb["history"].items() if k not in ("example",)},
        "split": {"train_rows": nb["history"]["train_rows"], "train_bc_pct": nb["history"]["train_bc_pct"],
                  "test_rows": nb["history"]["test_rows"], "test_bc_pct": nb["history"]["test_bc_pct"],
                  "train_rule": "up to the end of 2024", "test_rule": "2025 onward"},
        "model": {"best": nb["summary"]["best_model"],
                  "test_roc_auc": nb["summary"]["test_roc_auc"],
                  "test_pr_auc": nb["summary"]["test_pr_auc"],
                  "threshold": nb["summary"]["threshold"],
                  "recall": nb["summary"]["recall"],
                  "precision": nb["summary"]["precision"],
                  "recall_at_0_5": round(best["recall_at_0_5"], 3),
                  "test_positives": fit["y_test_positives"],
                  "test_rows": fit["test_rows"],
                  "leans_on": nb["summary"]["leans_on"]},
        "dummy": {"test_accuracy": round(dummy["test_accuracy"], 3),
                  "caught": dummy["caught_at_0_5"],
                  "recall": round(dummy["recall_at_0_5"], 3),
                  "test_positives": fit["y_test_positives"]},
        "zip": {"zip_codes": zips["zip_codes"], "reliable_zip_codes": zips["reliable_zip_codes"],
                "min_graded": 30, "citywide_pct_bc": zips["citywide_pct_bc"],
                "mapped_inspections": zips["mapped_inspections"],
                "worst": worst,
                "busiest_max": zips["busiest"][0],
                "busiest_pale_min_pct": min(z["pct_bc"] for z in busiest_pale),
                "busiest_pale_max_pct": max(z["pct_bc"] for z in busiest_pale),
                "busiest_pale_count": len(busiest_pale),
                "zcta_match_pct": take("zcta_match_pct",
                                       (extra or {}).get("zcta_match", {}).get("pct_matched"))},
        "nta": {**nb["nta"], "reliable": int(nta["reliable"].sum()),
                "worst": {"name": nta_rel.iloc[0]["ntaname"],
                          "pct_bc": round(float(nta_rel.iloc[0]["pct_bc"]), 1),
                          "graded": int(nta_rel.iloc[0]["graded"])}},
        "pca": {"pc1_pct": nb["pca"]["components"][0]["variance_pct"],
                "pc2_pct": nb["pca"]["components"][1]["variance_pct"],
                "n_for_90pct": nb["pca"]["n_for_90pct"], "n_features": nb["pca"]["n_features"],
                "auc_90pct_components": nb["pca"]["auc_90pct_components"],
                "auc_original_features": nb["pca"]["auc_original_features"]},
    }

    thresholds = {
        "model": nb["thresholds"]["best_model"],
        "default": nb["thresholds"]["chosen"],
        "rule": "the highest threshold that still catches at least 80% of B or C inspections",
        "positives": fit["y_test_positives"],
        "test_rows": fit["test_rows"],
        "stops": [{**s, "precision": round(s["precision"], 3), "recall": round(s["recall"], 3),
                   "f1": round(s["f1"], 3), "fpr": round(s["fpr"], 4)} for s in fit["stops"]],
        "source": "refit of the notebook's logistic regression on modeling_table.csv; "
                  "precision and recall verified against cell 60",
    }
    s05 = next(s for s in fit["stops"] if s["threshold"] == 0.5)
    confusion = {"threshold": 0.5, "tn": s05["tn"], "fp": s05["fp"], "fn": s05["fn"], "tp": s05["tp"],
                 "rows": "true grade", "columns": "prediction",
                 "figure": "assets/img/pred_confusion.png"}
    curves = {"models": fit["curves"], "test_positives": fit["y_test_positives"],
              "test_rows": fit["test_rows"],
              "threshold_points": [{"threshold": s["threshold"], "fpr": round(s["fpr"], 4),
                                    "tpr": round(s["recall"], 4), "precision": round(s["precision"], 4)}
                                   for s in fit["stops"]],
              "figure": "assets/img/pred_curves.png"}

    coefs = sorted(fit["coefficients"], key=lambda c: -c["coefficient"])
    importance = {
        "permutation": nb["permutation"],
        "coefficients": [{"feature": c["feature"], "coefficient": round(c["coefficient"], 3)} for c in coefs],
        "cuisine_coefficients": [
            {"cuisine": c["feature"].split("cuisine_grouped_", 1)[1], "coefficient": round(c["coefficient"], 3)}
            for c in coefs if c["feature"].startswith("cat__cuisine_grouped_")],
        "figure": "assets/img/pred_importance.png",
    }

    cuisine_pop = pop.groupby("cuisine_grouped")["y"].agg(["size", "mean"])
    cuisine = []
    for c in nb["cuisine"]:
        row = {**c, "typical_grade": "A" if c["median_score"] <= 13 else ("B" if c["median_score"] <= 27 else "C")}
        if c["cuisine"] in cuisine_pop.index:
            row["modeled"] = int(cuisine_pop.loc[c["cuisine"], "size"])
            row["modeled_bc_pct"] = round(100 * cuisine_pop.loc[c["cuisine"], "mean"], 1)
        cuisine.append(row)

    hero = {z["zip"]: z for z in nb["hero"]["zips"]}
    reliable = [z for z in nb["hero"]["zips"] if z["reliable"]]
    lowest = sorted(reliable, key=lambda z: (z["pct_bc"], -z["graded"]))[:10]
    tables = {
        "grades": nb["grades"],
        "missingness": nb["missingness"],
        "borough": nb["borough"],
        "cuisine": cuisine,
        "cuisine_bc_note": "B or C share among the modeled inspections (graded, first visits excluded)",
        "correlation": nb["correlation"],
        "models": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()} for r in fit["rows"]],
        "zip_highest": zips["highest_bc_reliable"],
        "zip_busiest": zips["busiest"],
        "zip_lowest": [{"zip": z["zip"], "inspections": z["inspections"], "graded": z["graded"],
                        "pct_bc": z["pct_bc"]} for z in lowest],
        "nta_highest": [{"nta": r.ntaname, "inspections": int(r.inspections), "graded": int(r.graded),
                         "pct_bc": round(float(r.pct_bc), 1), "median_score": float(r.median_score)}
                        for r in nta_rel.head(10).itertuples()],
        "history_example": {"camis": nb["history"]["example_camis"], "rows": nb["history"]["example"]},
    }
    # the hero data and cell 32's printed tables must agree on every shared ZIP
    for z in zips["highest_bc_reliable"] + zips["busiest"]:
        h = hero[z["zip"]]
        if (h["inspections"], h["graded"], h["pct_bc"]) != (z["inspections"], z["graded"], z["pct_bc"]):
            sys.exit(f"export failed: hero data and cell 32 disagree on ZIP {z['zip']}")

    pca = {**nb["pca"], "figures": {"variance": "assets/img/pca_variance.png",
                                    "scatter": "assets/img/pca_scatter.png"}}

    panels = (extra or {}).get("visit_kind_zip_panels") or (mapdata and mapdata["panels"])
    shapes = (extra or {}).get("zcta_shapes") or (mapdata and mapdata["shapes"])
    maps = {
        "zips": nb["hero"]["zips"],
        "view": nb["hero"]["view"],
        "color_scale": {"pale": "#FFECBE", "deep": "#C0392B", "clip_pct": 30,
                        "note": "the notebook's own ramp (cell 44): pale at 0%, deep red at 30% or more"},
        "height": "sqrt(inspections)",
        "min_graded": 30,
        "visit_kind_panels": take("visit_kind_zip_panels", panels),
        "zcta_shapes": take("zcta_shapes", shapes),
        "risk_zip": mapdata and mapdata["risk"],
        "sources": {"zips": "cell 44 hero HTML", "shapes_and_risk": "map_risk_zip.html (cell 13.4)",
                    "visit_kind_panels": "map_initial_vs_reinspection.html (cell 13.5)"},
    }
    key_metrics["pending"] = pending
    return {"key_metrics.json": key_metrics, "thresholds.json": thresholds, "curves.json": curves,
            "confusion.json": confusion, "importance.json": importance, "tables.json": tables,
            "pca.json": pca, "maps.json": maps}


# ---------------------------------------------------------------- fixtures

# Part 7's acceptance fixture plus the values Part 2 quotes. They validate
# the exports and are never copied into a slide.
FIXTURES = [
    ("thresholds.json", "stops[0.3].precision", 0.338), ("thresholds.json", "stops[0.3].recall", 0.988),
    ("thresholds.json", "stops[0.4].precision", 0.359), ("thresholds.json", "stops[0.4].recall", 0.918),
    ("thresholds.json", "stops[0.45].precision", 0.376), ("thresholds.json", "stops[0.45].recall", 0.822),
    ("thresholds.json", "stops[0.5].precision", 0.402), ("thresholds.json", "stops[0.5].recall", 0.710),
    ("thresholds.json", "stops[0.6].precision", 0.474), ("thresholds.json", "stops[0.6].recall", 0.453),
    ("thresholds.json", "stops[0.7].precision", 0.576), ("thresholds.json", "stops[0.7].recall", 0.232),
    ("key_metrics.json", "history.feature_rows", 18998),
    ("key_metrics.json", "split.train_rows", 9111),
    ("key_metrics.json", "split.test_rows", 9887),
    ("key_metrics.json", "model.test_roc_auc", 0.644),
    ("key_metrics.json", "model.test_pr_auc", 0.496),
    ("tables.json", "models[Random forest].train_roc_auc", 1.000),
    # the spec quoted 0.640, 0.637 and 3,281 from an earlier run; the team chose the
    # notebook's values (October 22 decision)
    ("tables.json", "models[Random forest].test_roc_auc", 0.641),
    ("tables.json", "models[Gradient boosting].train_roc_auc", 0.870),
    ("tables.json", "models[Gradient boosting].test_roc_auc", 0.636),
    ("tables.json", "models[Logistic regression].train_roc_auc", 0.644),
    ("key_metrics.json", "dummy.test_accuracy", 0.668),
    ("key_metrics.json", "dummy.recall", 0.000),
    ("key_metrics.json", "dummy.test_positives", 3284),
    ("key_metrics.json", "zip.worst.zip", "11355"),
    ("key_metrics.json", "zip.worst.pct_bc", 33.3),
    ("key_metrics.json", "zip.worst.graded", 342),
    ("key_metrics.json", "zip.citywide_pct_bc", 12.9),
    ("key_metrics.json", "nta.worst.name", "Queensboro Hill"),
    ("key_metrics.json", "nta.worst.pct_bc", 34.0),
    ("key_metrics.json", "pca.pc1_pct", 21.8),
    ("key_metrics.json", "pca.pc2_pct", 16.6),
    ("key_metrics.json", "pca.n_for_90pct", 8),
    ("key_metrics.json", "pca.n_features", 11),
    ("key_metrics.json", "pca.auc_90pct_components", 0.631),
    ("key_metrics.json", "dataset.raw_rows", 295356),
    ("key_metrics.json", "dataset.inspections", 96897),
    ("key_metrics.json", "dataset.restaurants", 31443),
    ("key_metrics.json", "dataset.same_day_multi_type", 8456),
    ("key_metrics.json", "score.median", 13.0),
    ("key_metrics.json", "score.mean", 17.869195),
    ("key_metrics.json", "score.upper_fence", 46.5),
    ("key_metrics.json", "score.n_above_fence", 4095),
    ("key_metrics.json", "score.max", 214.0),
    ("key_metrics.json", "missing.grade_date", 45.51),
    ("key_metrics.json", "missing.grade", 43.22),
    ("key_metrics.json", "missing.score", 14.74),
    ("key_metrics.json", "missing.cuisine_description", 4.06),
    ("tables.json", "borough[Manhattan].median", 12.0),
    ("tables.json", "borough[Bronx].median", 13.0),
    ("tables.json", "borough[Brooklyn].median", 13.0),
    ("tables.json", "borough[Queens].median", 13.0),
    ("tables.json", "borough[Staten Island].median", 13.0),
    ("tables.json", "cuisine[Donuts].median_score", 10.0),
    ("tables.json", "cuisine[Hamburgers].median_score", 10.0),
    ("tables.json", "cuisine[Latin American].median_score", 16.0),
    ("tables.json", "correlation.matrix[0][2]", 0.86),
    ("tables.json", "correlation.matrix[3][4]", -1.0),
    ("key_metrics.json", "visit_kind.initial_graded", 31758),
    ("key_metrics.json", "visit_kind.initial_bc", 0),
    ("key_metrics.json", "visit_kind.reinspection_bc_pct", 32.9),
    ("key_metrics.json", "visit_kind.initial_pct_scored_14_plus", 41.8),
    ("key_metrics.json", "visit_kind.reinspection_pct_scored_14_plus", 37.1),
    ("key_metrics.json", "population.population_bc_pct", 33.8),
    ("key_metrics.json", "population.modeled_bc_pct", 33.8),
    ("key_metrics.json", "zip.zcta_match_pct", 99.6),
]


def lookup(doc, path):
    cur = doc
    for name, key in re.findall(r"([^.\[\]]+)?(?:\[([^\]]+)\])?\.?", path):
        if name:
            cur = cur[name]
        if key:
            if re.fullmatch(r"\d+", key) and isinstance(cur, list) and not isinstance(cur[0], dict):
                cur = cur[int(key)]
            elif re.fullmatch(r"\d+", key) and isinstance(cur, list) and "threshold" not in cur[0]:
                cur = cur[int(key)]
            else:
                cur = next(d for d in cur if any(str(v) == key for v in d.values()))
    return cur


def check_fixtures_only(docs):
    """Fixture rows as (path, spec, export, status) without writing FIXTURES.md."""
    rows, failures, pending = [], [], 0
    for fname, path, expect in FIXTURES:
        got = lookup(docs[fname], path)
        if got is None:
            pending += 1
            continue
        cmp = round(got, 3) if isinstance(got, float) and isinstance(expect, float) else got
        cmp_expect = round(expect, 3) if isinstance(expect, float) else expect
        if cmp != cmp_expect:
            failures.append({"file": fname, "path": path, "spec": expect, "export": got})
    return failures, pending


def check_fixtures(docs):
    lines = ["# Fixture check", "",
             "Exports compared with the values quoted in the build spec (Part 7's acceptance",
             "fixture and the numbers in Part 2). The notebook is the source of truth: a",
             "mismatch means the spec's number is wrong for this notebook run, and a person",
             "decides what changes. Nothing is edited to make a row pass.", "",
             "| File | Field | Spec | Export | Status |", "|---|---|---|---|---|"]
    failures = pending = 0
    for fname, path, expect in FIXTURES:
        got = lookup(docs[fname], path)
        if got is None:
            status, pending = "PENDING (no notebook output)", pending + 1
        else:
            cmp = round(got, 3) if isinstance(got, float) and isinstance(expect, float) else got
            cmp_expect = round(expect, 3) if isinstance(expect, float) else expect
            ok = cmp == cmp_expect
            failures += not ok
            status = "ok" if ok else "**MISMATCH**"
        lines.append(f"| {fname} | `{path}` | {expect} | {got} | {status} |")
    lines += ["", "## Values still pending", ""]
    for p in docs["key_metrics.json"]["pending"]:
        lines.append(f"- `{p['key']}`: {p['reason']}. Run `tools/notebook_export_cell.py` in Colab.")
    lines.append("")
    (DATA / "FIXTURES.md").write_text("\n".join(lines))
    return failures, pending


# ---------------------------------------------------------------- main

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cells = json.loads(NOTEBOOK.read_text())["cells"]
    nb = from_notebook(cells)
    pop = pd.read_csv(MODELING, parse_dates=["inspection_date"])
    if len(pop) != nb["history"]["feature_rows"]:
        sys.exit(f"export failed: modeling_table.csv has {len(pop)} rows, cell 56 printed "
                 f"{nb['history']['feature_rows']}")
    nta = pd.read_csv(NTA)
    if len(nta) != nb["nta"]["neighborhoods"]:
        sys.exit("export failed: nta_risk_table.csv row count differs from cell 40")
    fit = refit(pop)
    verify_refit(nb, fit)
    extra = json.loads(EXTRA.read_text()) if EXTRA.exists() else None

    DATA.mkdir(exist_ok=True)
    mapdata = from_maps(nb["hero"]["zips"])
    extra = normalize_extra(extra, mapdata)
    docs = {name: clean({"as_of": AS_OF, **doc}) for name, doc in build(nb, pop, nta, fit, extra, mapdata).items()}

    if "--check" in sys.argv:
        # verify only: the frozen exports must equal a fresh build (INV-10)
        stale = [n for n, d in docs.items()
                 if not (DATA / n).exists() or (DATA / n).read_text() != json.dumps(d, indent=1, ensure_ascii=False) + "\n"]
        bundle_ok = (DATA / "deck-data.js").exists() and json.loads(
            (DATA / "deck-data.js").read_text().split("window.DECK_DATA = ", 1)[1].rstrip().rstrip(";")) == \
            {n[:-5]: d for n, d in docs.items()}
        failures, pending = check_fixtures_only(docs)
        print(json.dumps({"stale": stale, "bundle_ok": bundle_ok, "fixture_failures": failures,
                          "pending": [p["key"] for p in docs["key_metrics.json"]["pending"]]}))
        return 1 if stale or not bundle_ok or failures else 0
    sources = [NOTEBOOK, MODELING, NTA] + ([RISK_MAP, VISIT_MAP] if mapdata else []) + ([EXTRA] if extra else [])
    manifest = ["# Data manifest", "",
                "Generated by `tools/export_deck_data.py`. Do not edit by hand; re-exporting is a",
                "deliberate, diffed event and re-runs the numbers gate (INV-10).", "",
                f"Data as of {AS_OF_TEXT} (the NYC Open Data file downloaded that day).", "",
                "## Sources", "", "| Source | sha256 |", "|---|---|"]
    manifest += [f"| `{p.relative_to(ROOT)}` | `{sha(p)[:16]}` |" for p in sources]
    if extra and extra.get("provenance"):
        manifest += ["", "`source/deck_exports.json` was supplied by the team: " + extra["provenance"],
                     "Its shares are checked against its own counts and against the per-ZIP map data."]
    manifest += ["", "## Exports", "", "| File | sha256 |", "|---|---|"]
    for name, doc in docs.items():
        path = DATA / name
        path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        manifest.append(f"| `{name}` | `{sha(path)[:16]}` |")
    bundle = DATA / "deck-data.js"
    bundle.write_text("// Generated by tools/export_deck_data.py from data/*.json. Do not edit.\n"
                      "window.DECK_DATA = " + json.dumps({n[:-5]: d for n, d in docs.items()},
                                                         ensure_ascii=False) + ";\n")
    manifest.append(f"| `deck-data.js` (all of the above, as one script) | `{sha(bundle)[:16]}` |")
    manifest += ["", "## Pending", ""]
    manifest += [f"- `{p['key']}`: {p['reason']}" for p in docs["key_metrics.json"]["pending"]] or ["None."]
    manifest.append("")
    (DATA / "MANIFEST.md").write_text("\n".join(manifest))

    failures, pending = check_fixtures(docs)
    for name in docs:
        print("wrote", name)
    print(f"refit reproduces the notebook: {len(fit['rows'])} models, {len(fit['stops'])} threshold stops")
    print(f"fixtures: {len(FIXTURES) - failures - pending} ok, {failures} mismatched, {pending} pending "
          f"(see data/FIXTURES.md)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
