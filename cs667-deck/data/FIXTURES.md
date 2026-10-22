# Fixture check

Exports compared with the values quoted in the build spec (Part 7's acceptance
fixture and the numbers in Part 2). The notebook is the source of truth: a
mismatch means the spec's number is wrong for this notebook run, and a person
decides what changes. Nothing is edited to make a row pass.

| File | Field | Spec | Export | Status |
|---|---|---|---|---|
| thresholds.json | `stops[0.3].precision` | 0.338 | 0.338 | ok |
| thresholds.json | `stops[0.3].recall` | 0.988 | 0.988 | ok |
| thresholds.json | `stops[0.4].precision` | 0.359 | 0.359 | ok |
| thresholds.json | `stops[0.4].recall` | 0.918 | 0.918 | ok |
| thresholds.json | `stops[0.45].precision` | 0.376 | 0.376 | ok |
| thresholds.json | `stops[0.45].recall` | 0.822 | 0.822 | ok |
| thresholds.json | `stops[0.5].precision` | 0.402 | 0.402 | ok |
| thresholds.json | `stops[0.5].recall` | 0.71 | 0.71 | ok |
| thresholds.json | `stops[0.6].precision` | 0.474 | 0.474 | ok |
| thresholds.json | `stops[0.6].recall` | 0.453 | 0.453 | ok |
| thresholds.json | `stops[0.7].precision` | 0.576 | 0.576 | ok |
| thresholds.json | `stops[0.7].recall` | 0.232 | 0.232 | ok |
| key_metrics.json | `history.feature_rows` | 18998 | 18998 | ok |
| key_metrics.json | `split.train_rows` | 9111 | 9111 | ok |
| key_metrics.json | `split.test_rows` | 9887 | 9887 | ok |
| key_metrics.json | `model.test_roc_auc` | 0.644 | 0.644 | ok |
| key_metrics.json | `model.test_pr_auc` | 0.496 | 0.496 | ok |
| tables.json | `models[Random forest].train_roc_auc` | 1.0 | 1.0 | ok |
| tables.json | `models[Random forest].test_roc_auc` | 0.64 | 0.641 | **MISMATCH** |
| tables.json | `models[Gradient boosting].train_roc_auc` | 0.87 | 0.87 | ok |
| tables.json | `models[Gradient boosting].test_roc_auc` | 0.637 | 0.636 | **MISMATCH** |
| tables.json | `models[Logistic regression].train_roc_auc` | 0.644 | 0.644 | ok |
| key_metrics.json | `dummy.test_accuracy` | 0.668 | 0.668 | ok |
| key_metrics.json | `dummy.recall` | 0.0 | 0.0 | ok |
| key_metrics.json | `dummy.test_positives` | 3281 | 3284 | **MISMATCH** |
| key_metrics.json | `zip.worst.zip` | 11355 | 11355 | ok |
| key_metrics.json | `zip.worst.pct_bc` | 33.3 | 33.3 | ok |
| key_metrics.json | `zip.worst.graded` | 342 | 342 | ok |
| key_metrics.json | `zip.citywide_pct_bc` | 12.9 | 12.9 | ok |
| key_metrics.json | `nta.worst.name` | Queensboro Hill | Queensboro Hill | ok |
| key_metrics.json | `nta.worst.pct_bc` | 34.0 | 34.0 | ok |
| key_metrics.json | `pca.pc1_pct` | 21.8 | 21.8 | ok |
| key_metrics.json | `pca.pc2_pct` | 16.6 | 16.6 | ok |
| key_metrics.json | `pca.n_for_90pct` | 8 | 8 | ok |
| key_metrics.json | `pca.n_features` | 11 | 11 | ok |
| key_metrics.json | `pca.auc_90pct_components` | 0.631 | 0.631 | ok |
| key_metrics.json | `dataset.raw_rows` | 295356 | 295356 | ok |
| key_metrics.json | `dataset.inspections` | 96897 | 96897 | ok |
| key_metrics.json | `dataset.restaurants` | 31443 | 31443 | ok |
| key_metrics.json | `dataset.same_day_multi_type` | 8456 | None | PENDING (no notebook output) |
| key_metrics.json | `score.median` | 13.0 | 13.0 | ok |
| key_metrics.json | `score.mean` | 17.869195 | 17.869195 | ok |
| key_metrics.json | `score.upper_fence` | 46.5 | 46.5 | ok |
| key_metrics.json | `score.n_above_fence` | 4095 | 4095 | ok |
| key_metrics.json | `score.max` | 214.0 | 214.0 | ok |
| key_metrics.json | `missing.grade_date` | 45.51 | 45.51 | ok |
| key_metrics.json | `missing.grade` | 43.22 | 43.22 | ok |
| key_metrics.json | `missing.score` | 14.74 | 14.74 | ok |
| key_metrics.json | `missing.cuisine_description` | 4.06 | 4.06 | ok |
| tables.json | `borough[Manhattan].median` | 12.0 | 12.0 | ok |
| tables.json | `borough[Bronx].median` | 13.0 | 13.0 | ok |
| tables.json | `borough[Brooklyn].median` | 13.0 | 13.0 | ok |
| tables.json | `borough[Queens].median` | 13.0 | 13.0 | ok |
| tables.json | `borough[Staten Island].median` | 13.0 | 13.0 | ok |
| tables.json | `cuisine[Donuts].median_score` | 10.0 | 10.0 | ok |
| tables.json | `cuisine[Hamburgers].median_score` | 10.0 | 10.0 | ok |
| tables.json | `cuisine[Latin American].median_score` | 16.0 | 16.0 | ok |
| tables.json | `correlation.matrix[0][2]` | 0.86 | 0.86 | ok |
| tables.json | `correlation.matrix[3][4]` | -1.0 | -1.0 | ok |
| key_metrics.json | `visit_kind.initial_graded` | 31758 | 31758 | ok |
| key_metrics.json | `visit_kind.initial_bc` | 0 | 0 | ok |
| key_metrics.json | `visit_kind.reinspection_bc_pct` | 32.9 | 32.9 | ok |
| key_metrics.json | `visit_kind.initial_pct_scored_14_plus` | 41.8 | None | PENDING (no notebook output) |
| key_metrics.json | `visit_kind.reinspection_pct_scored_14_plus` | 37.1 | None | PENDING (no notebook output) |
| key_metrics.json | `population.population_bc_pct` | 33.8 | 33.8 | ok |
| key_metrics.json | `population.modeled_bc_pct` | 33.8 | 33.8 | ok |
| key_metrics.json | `zip.zcta_match_pct` | 99.6 | None | PENDING (no notebook output) |

## Values still pending

- `same_day_multi_type`: described in a markdown cell only; no cell prints it. Run `tools/notebook_export_cell.py` in Colab.
- `visit_kind_scored_14_plus`: cell 13.5 (initial vs re-inspection maps) was saved as 'Output hidden'. Run `tools/notebook_export_cell.py` in Colab.
- `zcta_match_pct`: cell 13.4 (ZIP risk map) was saved as 'Output hidden'. Run `tools/notebook_export_cell.py` in Colab.
