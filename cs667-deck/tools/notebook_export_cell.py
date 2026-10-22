# ---------------------------------------------------------------------------
# Cell 15: deck export.
#
# Paste this as the LAST cell of the notebook and run it after a full
# top-to-bottom run (Runtime > Run all). It prints nothing new about the
# analysis; it only writes deck_exports.json, the values the presentation
# needs that no saved output holds: the visit-kind numbers and per-ZIP
# panels from the hidden map cell 13.5, the ZIP boundary match and polygons
# from the hidden cell 13.4, and the same-day count from cell 4's notes.
# (Curves, threshold confusion counts and coefficients are NOT needed here:
# tools/export_deck_data.py re-fits them from modeling_table.csv.)
#
# Then upload deck_exports.json to cs667-deck/source/ and re-run
# tools/export_deck_data.py.
#
# It refuses to export if the downloaded file is not the October 21, 2026
# file the rest of the deck describes: NYC Open Data updates daily, and a
# newer file would quietly change every number on every slide.
# ---------------------------------------------------------------------------

import json

import numpy as np
import pandas as pd

EXPECTED_RECORD_DATE = "10/21/2026"
EXPECTED_RAW_ROWS = 295356

record_dates = sorted(df_raw["RECORD DATE"].astype(str).unique())
assert record_dates == [EXPECTED_RECORD_DATE], (
    f"This run used the file published {record_dates}, not {EXPECTED_RECORD_DATE}. "
    "Every number in the deck describes the October 21 file; stop and re-plan.")
assert len(df_raw) == EXPECTED_RAW_ROWS, f"raw rows {len(df_raw)} != {EXPECTED_RAW_ROWS}"

out = {"record_date": record_dates[0], "raw_rows": int(len(df_raw))}


def r(x, n=6):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


# --- aggregation: restaurant-days carrying more than one inspection type ----
dated = df[df["inspection_date"] > pd.Timestamp("1900-01-01")]
types_per_day = dated.groupby(["camis", "inspection_date"])["inspection_type"].nunique()
out["same_day_multi_type"] = int((types_per_day > 1).sum())

# --- visit kind (the hidden map cell 13.5), rebuilt from df_insp ------------
# Same cleaning as cell 13.1; map_df was redefined by cell 13.7, so it is
# rebuilt here rather than reused.
vk = df_insp.copy()
vk["zip5"] = pd.to_numeric(vk["zipcode"], errors="coerce").map(
    lambda v: f"{int(v):05d}" if pd.notna(v) else np.nan)
ok = (vk["latitude"].notna() & vk["longitude"].notna()
      & (vk["latitude"] != 0) & (vk["longitude"] != 0)
      & vk["latitude"].between(40.49, 40.92) & vk["longitude"].between(-74.26, -73.69))
vk = vk[ok].copy()
vk["visit"] = np.where(
    vk["inspection_type"].str.endswith("Initial Inspection", na=False), "initial",
    np.where(vk["inspection_type"].str.endswith("Re-inspection", na=False),
             "reinspection", "other"))

visit = {}
for kind in ["initial", "reinspection"]:
    f = vk[vk["visit"] == kind]
    gr = f[f["grade"].isin(["A", "B", "C"])]
    sc = f.dropna(subset=["score"])
    visit[kind] = {
        "inspections": int(len(f)),
        "graded": int(len(gr)),
        "graded_A": int((gr["grade"] == "A").sum()),
        "graded_B": int((gr["grade"] == "B").sum()),
        "graded_C": int((gr["grade"] == "C").sum()),
        "pct_bc_of_graded": r(100 * gr["grade"].isin(["B", "C"]).mean(), 3),
        "scored": int(len(sc)),
        "scored_14_plus": int((sc["score"] >= 14).sum()),
        "pct_scored_14_plus": r(100 * (sc["score"] >= 14).mean(), 3),
    }
out["visit_kind"] = visit

# per-ZIP panels for the visit-type toggle (cell 13.5's FLOOR of 20 scored)
panels = {}
for kind in ["initial", "reinspection"]:
    sc = vk[(vk["visit"] == kind)].dropna(subset=["score", "zip5"])
    g = sc.groupby("zip5")
    t = pd.DataFrame({"scored": g.size(),
                      "high": g["score"].apply(lambda s: int((s >= 14).sum())),
                      "median_score": g["score"].median()}).reset_index()
    t = t[t["zip5"].isin(zcta_ids)]
    panels[kind] = [{"zip": z.zip5, "scored": int(z.scored), "high": int(z.high),
                     "pct_high": r(100 * z.high / z.scored, 3),
                     "median_score": r(z.median_score, 1),
                     "reliable": bool(z.scored >= 20)} for z in t.itertuples()]
out["visit_kind_zip_panels"] = {"floor_scored": 20, "panels": panels}

# --- ZIP boundary match (the hidden cell 13.4) and simplified polygons ------
with_zip = vk.dropna(subset=["zip5"])
matched = with_zip["zip5"].isin(zcta_ids)
out["zcta_match"] = {
    "inspections_matched": int(matched.sum()),
    "inspections_with_zip": int(len(with_zip)),
    "pct_matched": r(100 * matched.mean(), 3),
    "zips_in_data": int(with_zip["zip5"].nunique()),
    "zips_matched": int(with_zip.loc[matched, "zip5"].nunique()),
}
try:
    from shapely.geometry import mapping, shape
    shapes = {}
    for feat in zcta_geojson["features"]:
        z = feat["properties"]["zcta5"]
        geom = shape(feat["geometry"]).simplify(0.0006, preserve_topology=True)
        gj = mapping(geom)
        gj = json.loads(json.dumps(gj), parse_float=lambda v: round(float(v), 4))
        shapes[z] = gj
    out["zcta_shapes"] = shapes
except Exception as exc:  # the deck falls back to ZIP centroids
    print("ZCTA shapes not exported:", exc)

with open("deck_exports.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("Saved deck_exports.json")
print(f"  same-day restaurant-days with more than one type: {out['same_day_multi_type']:,}")
for kind, v in visit.items():
    print(f"  {kind}: B or C {v['pct_bc_of_graded']:.1f}% of {v['graded']:,} graded; "
          f"14+ points {v['pct_scored_14_plus']:.1f}% of {v['scored']:,} scored")
print(f"  ZIP boundary match: {out['zcta_match']['pct_matched']:.1f}%")

try:
    from google.colab import files
    files.download("deck_exports.json")
except ImportError:
    pass
