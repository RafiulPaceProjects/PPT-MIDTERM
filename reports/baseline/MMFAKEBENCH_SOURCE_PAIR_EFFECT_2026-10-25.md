# MMFakeBench test: image effect by source pair

**Date:** 2026-10-25
**Question:** the pooled paired − text-only accuracy difference (−1.51 pp) is pooled across source pairs. Is it a consistent image effect, or a mix of different effects in different sources?
**Scope:** saved predictions only; no inference, training, or downloads. MMFakeBench official test, post-hoc (the split was inspected before evaluation). One checkpoint (`f2fe3c12…`), same rows in both arms.
**Artifacts:** `mmfakebench_source_pair_effect_2026-10-25.json` (sha256 `d7efc829…`), produced by `data/workflows/analysis/mmfakebench_source_pair_effect_20261025.py`.

## Method

- Rows: the 9,999 test rows usable in both the paired (image + text) and text-only (`vision_text`) arms. Source pair = (`text_source`, `image_source`) from `MMFakeBench_test.json`; 14 pairs including one with empty metadata (100 rows).
- Difference: paired accuracy minus text-only accuracy on the same rows.
- Ranges: 95% bootstrap ranges, 2,000 resamples, seed 20261018, clusters = exact image bytes. Descriptive, not confirmatory.
- Check: the script recomputes the pooled difference with the original algorithm and stops unless it matches `mmfakebench_test_ablation_2026-10-25.json` exactly. It matched: −1.51 pp [−2.44, −0.54], 9,999 rows, 9,716 clusters.

## Result

| text_source | image_source | n | gold label | paired acc | text-only acc | difference (pp) | 95% range (pp) |
|---|---|---|---|---|---|---|---|
| VisualNews | VisualNews | 2,000 | original | 13.5% | 18.6% | −5.10 | [−7.10, −3.15] |
| Newsclipings | Newsclipings | 1,500 | mismatch | 12.5% | 18.3% | −5.80 | [−8.12, −3.52] |
| Fakeddit | Fakeddit | 1,000 | original 500 / visual 500 | 7.6% | 10.4% | −2.80 | [−5.01, −0.50] |
| COCO-Counterfactuals | COCO-Counterfactuals | 1,000 | mismatch | 16.6% | 6.2% | +10.40 | [+7.70, +13.20] |
| Fever | AI-generated Image | 999 | textual | 24.3% | 23.9% | +0.40 | [−3.10, +3.70] |
| Fakenewsnet | Repurposed Image | 750 | textual | 81.3% | 83.3% | −2.00 | [−5.53, +1.32] |
| MS-COCO | MS-COCO | 500 | original | 60.4% | 42.0% | +18.40 | [+12.92, +24.10] |
| GPT-generated Rumor | Repurposed Image | 500 | textual | 74.0% | 72.0% | +2.00 | [−3.09, +6.95] |
| GPT-generated Rumor | AI-generated Image | 500 | textual | 33.4% | 51.2% | −17.80 | [−23.00, −12.80] |
| DGM4 | DGM4 | 500 | mismatch | 10.2% | 7.8% | +2.40 | [−0.80, +5.60] |
| MS-COCO | AI-generated Image | 350 | visual | 4.9% | 2.9% | +2.00 | [−0.86, +4.86] |
| Gossipcop | AI-generated Image | 250 | textual | 72.4% | 90.4% | −18.00 | [−23.60, −12.00] |
| (empty) | (empty) | 100 | visual | 0.0% | 5.0% | −5.00 | [−10.00, −1.00] |
| VisualNews | AI-generated Image | 50 | visual | 2.0% | 20.0% | −18.00 | [−30.00, −6.00] |

Across pairs:

- 7 of 14 pair ranges lie below zero, 2 lie above zero, 5 span zero.
- n-weighted mean of the within-pair differences: −1.51 pp. This is identical to the pooled value by construction, because both arms are scored on the same rows.
- Equal-weight mean (each pair counts once): −2.78 pp, 95% range [−4.20, −1.47].

## Reading

1. **The pooled −1.51 pp is an average of large, opposite effects.** Within-pair differences run from −18.0 pp to +18.4 pp. The pooled number describes the mix of sources in this test split, not a typical per-item image effect.
2. **The caveat needs refining.** In a same-row design, conditioning on source pair does not change the weighted mean; it reveals the spread. The accurate statement is "pooled across source pairs; the effect varies widely by pair (−18.0 to +18.4 pp)".
3. **Because 13 of 14 pairs are label-pure, a within-pair difference is mostly a change in how often the model predicts that pair's one label.** The image moves the predicted-label mix in source-specific directions (`predicted_share_*` in the JSON):
   - MS-COCO image sources: predicted "original" rises from 42.0% to 60.4% (MS-COCO pair) and from 38.9% to 60.9% (AI-generated image pair).
   - Gossipcop / AI-generated: predicted "textual" falls from 90.4% to 72.4%, and "mismatch" rises from 3.2% to 25.2%.
   - Overall (n = 9,999): predicted "visual distortion" falls from 3.9% to 1.0%, and "mismatch" rises from 13.4% to 19.0%.

   The positive pairs are pairs where that shift happens to land on the pair's label. That is a different claim from "the image helped the model judge the item".
4. **Where the label varies within a source, the image does not help separate it.** Fakeddit is the only mixed pair (500 original / 500 visual distortion). Within-pair macro-F1 over those two labels is 11.2% paired vs 14.2% text-only.
5. **AI-generated images are not flagged as visual distortion.** In the two visual-distortion pairs with AI-generated images (MS-COCO 350, VisualNews 50), the paired arm predicts "visual distortion" in at most 4.9% of rows. With MS-COCO text, the image instead raises "original" to 60.9%.

## Limits

- Post-hoc test diagnostics, one checkpoint, zero-shot. No claim about images in general.
- 14 per-pair ranges were read at once; with this many, some will exclude zero by chance. The large effects (|difference| ≥ 10 pp) are well outside that concern; the small ones are not.
- 36 image-byte clusters span more than one pair. The per-pair and equal-weight bootstraps resample them within each pair.
- Within-pair accuracy on a label-pure pair is that class's recall in that pair. It is not a discrimination measure.

## Reproduce (read-only)

```bash
D=data/processed/protocol/dataset_native_baseline_20261025_test_ablation_v1
data/.venv-eda/bin/python -I data/workflows/analysis/mmfakebench_source_pair_effect_20261025.py \
  --paired $D/mmfakebench_test_paired/paired.predictions.jsonl \
  --text $D/mmfakebench_test_vision_text/vision_text.predictions.jsonl \
  --manifest $D/mmfakebench_test_paired/manifest.json \
  --annotations data/raw/MMFakeBench/MMFakeBench_test.json \
  --reference data/reports/baseline_study/mmfakebench_test_ablation_2026-10-25.json \
  --output data/reports/baseline_study/mmfakebench_source_pair_effect_2026-10-25.json
```
