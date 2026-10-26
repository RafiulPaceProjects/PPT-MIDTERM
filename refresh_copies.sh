#!/bin/bash
# Re-copies every showcase file from its source with cp -p, then regenerates
# reports/MANIFEST.md. Sources are only read; nothing outside this folder is written.
set -euo pipefail

ROOT=/Users/rafiulhaider/Documents/Misinformation
OUT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$OUT/reports/MANIFEST.md"
MAX_BYTES=$((5 * 1024 * 1024))

# Each entry: showcase path (relative to OUT) | source path
ENTRIES=(
  "reports/baseline/BASELINE_CLAIMS_2026-10-25.md|$ROOT/data/reports/baseline_study/BASELINE_CLAIMS_2026-10-25.md"
  "reports/baseline/BASELINE_REPORT_DRAFT_2026-10-25.md|$ROOT/data/reports/baseline_study/BASELINE_REPORT_DRAFT_2026-10-25.md"
  "reports/baseline/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md|$ROOT/data/reports/baseline_study/MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md"
  "reports/baseline/MMFAKEBENCH_TEST_ABLATION_2026-10-25.md|$ROOT/data/reports/baseline_study/MMFAKEBENCH_TEST_ABLATION_2026-10-25.md"
  "reports/baseline/NCP_STREAM_METHOD_2026-10-25.md|$ROOT/data/reports/baseline_study/NCP_STREAM_METHOD_2026-10-25.md"
  "reports/baseline/VERITE_IMAGE_ROOT_DISCREPANCY_2026-10-25.md|$ROOT/data/reports/baseline_study/VERITE_IMAGE_ROOT_DISCREPANCY_2026-10-25.md"
  "reports/baseline/published_comparison_2026-10-18.md|$ROOT/data/reports/baseline_study/published_comparison_2026-10-18.md"
  "reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md|$ROOT/data/reports/transfer_probe/NCP_TRANSFER_PROBE_PROTOCOL_v1_2026-10-25.md"
  "reports/transfer_probe/PILOT_REPORT_ncp_transfer_probe_v1_2026-10-25.md|$ROOT/data/reports/transfer_probe/PILOT_REPORT_ncp_transfer_probe_v1_2026-10-25.md"
  "reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md|$ROOT/data/reports/transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md"
  "reports/planning/POS_DEVIATION_2026-10-25.md|$ROOT/data/reports/baseline_study/POS_DEVIATION_2026-10-25.md"
  "reports/planning/POS_DEVIATION_ADDENDUM_DRAFT_2026-10-25.md|$ROOT/data/reports/baseline_study/POS_DEVIATION_ADDENDUM_DRAFT_2026-10-25.md"
  "reports/planning/POS_GAP_PLAN_2026-10-25.md|$ROOT/data/reports/baseline_study/POS_GAP_PLAN_2026-10-25.md"
  "reports/planning/FINETUNE_PREREGISTRATION_DRAFT_2026-10-25.md|$ROOT/data/reports/FINETUNE_PREREGISTRATION_DRAFT_2026-10-25.md"
  "reports/planning/FINETUNE_HANDOFF_2026-10-25.md|$ROOT/data/reports/baseline_study/FINETUNE_HANDOFF_2026-10-25.md"
  "data_summaries/results.json|$ROOT/dashboard/results.json"
  "data_summaries/eda.json|$ROOT/dashboard/eda.json"
  "data_summaries/published_supplement.json|$ROOT/dashboard/published_supplement.json"
  "data_summaries/published_references.json|$ROOT/data/workflows/baseline_study/published_references.json"
  "data_summaries/mmfakebench_source_pair_effect_2026-10-25.json|$ROOT/data/reports/baseline_study/mmfakebench_source_pair_effect_2026-10-25.json"
  "data_summaries/mmfakebench_test_ablation_2026-10-25.json|$ROOT/data/reports/baseline_study/mmfakebench_test_ablation_2026-10-25.json"
  "data_summaries/ncp_metrics_2026-10-25.json|$ROOT/data/reports/baseline_study/ncp_metrics_2026-10-25.json"
  "data_summaries/full_probe.json|$ROOT/data/processed/protocol/ncp_transfer_probe_v1/full_probe.json"
  "data_summaries/pilot_probe.json|$ROOT/data/processed/protocol/ncp_transfer_probe_v1/pilot_probe.json"
  "reference/POS_final.pdf|/Users/rafiulhaider/Downloads/POS_final.pdf"
  "reference/mmfakebench-ontology.md|$ROOT/data/ontology/mmfakebench-ontology.md"
  "reference/mmfakebench-ontology-3d.html|$ROOT/data/ontology/mmfakebench-ontology-3d.html"
  "notebooks/eda_original/dataset_eda.ipynb|$ROOT/data/notebooks/dataset_eda.ipynb"
  "notebooks/eda_original/VERITE_deep_EDA.ipynb|$ROOT/main/data/notebooks/VERITE_deep_EDA.ipynb"
  "notebooks/eda_original/mmfakebench_deep_eda_colab.ipynb|$ROOT/main/data/notebooks/mmfakebench_deep_eda_colab.ipynb"
  "notebooks/eda_original/newsclippings_deep_eda_colab.ipynb|$ROOT/main/data/notebooks/newsclippings_deep_eda_colab.ipynb"
)

# Entries whose source was missing or too large during this run (bash 3.2 safe).
MISSING_LINES=()

# Step A: copy each source with cp -p (sources are read only).
for entry in "${ENTRIES[@]}"; do
  rel="${entry%%|*}"
  src="${entry#*|}"
  dest="$OUT/$rel"
  if [ ! -f "$src" ]; then
    echo "WARNING: source missing, not copied: $src" >&2
    MISSING_LINES+=("- \`$rel\`: source missing at refresh time ($src). Existing copy, if any, left unchanged.")
    continue
  fi
  size=$(stat -f %z "$src")
  if [ "$size" -gt "$MAX_BYTES" ]; then
    echo "WARNING: too large (over 5 MB), not copied: $src" >&2
    MISSING_LINES+=("- \`$rel\`: too large, see source path ($src).")
    continue
  fi
  mkdir -p "$(dirname "$dest")"
  cp -p "$src" "$dest"
  if ! cmp -s "$src" "$dest"; then
    echo "ERROR: copy does not match source: $dest" >&2
    exit 1
  fi
  echo "copied $rel"
done

# Step B: regenerate the manifest from the copies present in this folder.
mkdir -p "$(dirname "$MANIFEST")"
{
  echo "Copied on $(date '+%Y-%m-%d %H:%M:%S %Z'). These are copies; run refresh_copies.sh to update them from their sources."
  echo
  echo "# MIDTERM_PRETRAINED_BASELINE copy manifest"
  echo
  echo "| showcase path | source path | size (bytes) | sha256 (first 12 hex) | source modified |"
  echo "|---|---|---:|---|---|"
  for entry in "${ENTRIES[@]}"; do
    rel="${entry%%|*}"
    src="${entry#*|}"
    dest="$OUT/$rel"
    [ -f "$dest" ] || continue
    if [ -f "$src" ]; then
      mtime=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$src")
    else
      mtime="source missing"
    fi
    echo "| \`$rel\` | \`$src\` | $(stat -f %z "$dest") | $(shasum -a 256 "$dest" | cut -c1-12) | $mtime |"
  done
  echo
  echo "## Missing or skipped"
  echo
  echo "- Notebooks: the same-named files in \`$ROOT/data/notebooks/\` (\`VERITE_deep_EDA.ipynb\`, \`mmfakebench_deep_eda_colab.ipynb\`, \`newsclippings_deep_eda_colab.ipynb\`) were not copied. The versions in \`$ROOT/main/data/notebooks/\` have newer modification times (2026-10-19 11:54:20 versus 2026-10-14 18:26), so those were copied instead."
  if [ ${#MISSING_LINES[@]} -eq 0 ]; then
    echo "- No other source files were missing or skipped during this refresh."
  else
    for line in "${MISSING_LINES[@]}"; do
      echo "$line"
    done
  fi
} > "$MANIFEST"

echo "Manifest regenerated: $MANIFEST"
