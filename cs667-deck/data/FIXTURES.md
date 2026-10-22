# Fixture check

Exports compared with the values quoted in the build spec. The notebook is the
source of truth: a mismatch means the slide text in the spec must change, not
the export.

| File | Field | Spec | Notebook | Status |
|---|---|---|---|---|
| dataset.json | `raw_rows` | 295356 | 295356 | ok |
| dataset.json | `inspections` | 96897 | 96897 | ok |
| dataset.json | `restaurants` | 31443 | 31443 | ok |
| score.json | `median` | 13.0 | 13.0 | ok |
| score.json | `mean` | 17.9 | 17.869195 | ok |
| score.json | `upper_fence` | 46.5 | 46.5 | ok |
| score.json | `n_above_fence` | 4095 | 4095 | ok |
| score.json | `max` | 214.0 | 214.0 | ok |
| missingness.json | `columns[grade_date].pct_missing` | 45.5 | 45.51 | ok |
| missingness.json | `columns[grade].pct_missing` | 43.2 | 43.22 | ok |
| missingness.json | `columns[score].pct_missing` | 14.7 | 14.74 | ok |
| missingness.json | `columns[cuisine_description].pct_missing` | 4.1 | 4.06 | ok |
| borough.json | `boroughs[Manhattan].median` | 12.0 | 12.0 | ok |
| borough.json | `boroughs[Bronx].median` | 13.0 | 13.0 | ok |
| borough.json | `boroughs[Brooklyn].median` | 13.0 | 13.0 | ok |
| borough.json | `boroughs[Queens].median` | 13.0 | 13.0 | ok |
| borough.json | `boroughs[Staten Island].median` | 13.0 | 13.0 | ok |
| cuisine.json | `top_cuisines[Donuts].median_score` | 10.0 | 10.0 | ok |
| cuisine.json | `top_cuisines[Hamburgers].median_score` | 10.0 | 10.0 | ok |
| cuisine.json | `top_cuisines[Latin American].median_score` | 16.0 | 16.0 | ok |
| correlation.json | `traps[0].r` | 0.86 | 0.86 | ok |
| correlation.json | `traps[1].r` | -1.0 | -1.0 | ok |
| population.json | `crosstab.initial.A` | 31758 | 31758 | ok |
| population.json | `crosstab.initial.BC` | 0 | 0 | ok |
| history.json | `feature_table_rows` | 18998 | 18998 | ok |
| history.json | `split.train.rows` | 9111 | 9111 | ok |
| history.json | `split.test.rows` | 9887 | 9887 | ok |
| population.json | `modeling_bc_pct` | 33.8 | 33.8 | ok |
| pca.json | `components[PC1].variance_pct` | 21.8 | 21.8 | ok |
| pca.json | `components[PC2].variance_pct` | 16.6 | 16.6 | ok |
| pca.json | `n_for_90pct` | 8 | 8 | ok |
| pca.json | `n_features` | 11 | 11 | ok |
| pca.json | `logreg_90pct_components_auc` | 0.631 | 0.631 | ok |
| pca.json | `logreg_original_features_auc` | 0.644 | 0.644 | ok |
| models.json | `models[Logistic regression].test_roc_auc` | 0.644 | 0.644 | ok |
| models.json | `models[Logistic regression].train_roc_auc` | 0.644 | 0.644 | ok |
| models.json | `models[Random forest].test_roc_auc` | 0.64 | 0.641 | **MISMATCH** |
| models.json | `models[Random forest].train_roc_auc` | 1.0 | 1.0 | ok |
| models.json | `models[Gradient boosting].test_roc_auc` | 0.637 | 0.636 | **MISMATCH** |
| models.json | `models[Gradient boosting].train_roc_auc` | 0.87 | 0.87 | ok |
| models.json | `models[Dummy (always A)].test_roc_auc` | 0.5 | 0.5 | ok |
| models.json | `models[Dummy (always A)].test_accuracy` | 0.668 | 0.668 | ok |
| thresholds.json | `default_threshold` | 0.45 | 0.45 | ok |
| summary.json | `recall_at_threshold` | 0.822 | 0.822 | ok |
| summary.json | `precision_at_threshold` | 0.376 | 0.376 | ok |
| zip_risk.json | `highest_bc_reliable[0].pct_bc` | 33.3 | 33.3 | ok |
| zip_risk.json | `citywide_pct_bc` | 12.9 | 12.9 | ok |

## Quoted in the spec, absent from every notebook output

These cannot appear on a slide under INV-1 until the notebook prints them.

- **32.9% of graded re-inspections end B or C (slide 9)** — cell 38 (initial vs re-inspection map) was saved as 'Output hidden'; cell 52 only prints 'all other inspections' (6,497 of 19,242 = 33.8%), which is not the same population.
- **8,456 same-day restaurant pairs (slide 3 beat)** — described in a markdown cell as a one-off check; no cell prints it.
- **confusion counts per threshold stop (slide 13 slider)** — cell 60 prints precision/recall/F1 only; counts at 0.5 exist only inside pred_confusion.png.
- **ROC / PR curve points (curves.json for the native rebuild)** — cell 60 draws the curves into pred_curves.png but prints no points.
