# DDR correlation recomputation report (F-R02)

- Generated (UTC): 2026-07-17T09:43:37.996273+00:00
- Input: `D:/0. NCS/CODE/p0_project/results/tables/ddr_downstream.csv`
- SHA-256: `c2e1bcdcdc83d314377318ee742994e4fbc0b706263f1f844966e6b12be8214d`
- Bootstrap: n=10000, seed=20260717, percentile 2.5/97.5
- Manuscript / figures: **not modified**

## Filters mirrored

### `generate_ddr_downstream_gkt_tex.py` (stats a, b)

1. `model == 'gkt'` and `operator != 'none'`
2. drop rows with NA `auc_drop` (CSV column)
3. `p = float(p).round(4)`
4. (a) `dataset == 'xes3g5m'` and `p <= 0.3 + 1e-9`
5. (b) `dataset == 'xes3g5m'` (all remaining p, including anchors)
6. Pearson on finite `(ddr, auc_drop)` via `scipy.stats.pearsonr`

### `plot_ddr_downstream.py` (stats c, d)

1. Keep rows with non-null `auc`
2. Recompute `baseline_auc` from `operator == 'none'` keyed by `(dataset, model, fold, split_seed)`
3. `auc_drop = baseline_auc - auc` (script path; not the stored column)
4. `pert = operator != 'none'`
5. (c) group cell `xes3g5m`/`gkt`: Spearman on finite `(ddr, auc_drop)`
6. (d) global: Pearson on all finite pert `(ddr, auc_drop)`

- Max |CSV `auc_drop` − recomputed| on XES/GKT pert rows: `9.801188e-17`

## Results

| ID | Filter | n | Stat | Value | p-value | Boot 95% CI | Reported | Match |
|---|---|---:|---|---:|---:|---|---:|---|
| a_xes_gkt_pearson_core | operator!=none; auc_drop notna; p.round(4)<=0.3;… | 81 | pearson_r | 0.931037 | 2.489e-36 | [0.8906, 0.9561] | 0.93 | **PASS_ROUNDING** |
| b_xes_gkt_pearson_all_p | operator!=none; auc_drop notna; all p incl ancho… | 99 | pearson_r | 0.985133 | 5.129e-76 | [0.9781, 0.9898] | 0.99 | **PASS_ROUNDING** |
| c_xes_gkt_spearman_full | operator!=none; finite ddr & recomputed auc_drop… | 99 | spearman_rho | 0.927730 | 2.651e-43 | [0.8677, 0.9623] | 0.93 | **PASS_ROUNDING** |
| d_global_pearson_all_pert | operator!=none; finite ddr & recomputed auc_drop… | 186 | pearson_r | 0.746624 | 2.102e-34 | [0.6175, 0.8467] | 0.75 | **PASS_ROUNDING** |

## Comparison detail

### a_xes_gkt_pearson_core
- Recomputed: `0.9310366656` → display 2 d.p. = `0.93`
- Reported target: `0.93` (abstract/GKT-caption Pearson r≈0.93 core)
- Match: **PASS_ROUNDING**
- n=81; p=2.489499e-36; CI=[0.890560, 0.956127]

### b_xes_gkt_pearson_all_p
- Recomputed: `0.9851325655` → display 2 d.p. = `0.99`
- Reported target: `0.99` (abstract/GKT-caption Pearson r≈0.99 with anchors; ddr_downstream.tex r=0.99)
- Match: **PASS_ROUNDING**
- n=99; p=5.129156e-76; CI=[0.978051, 0.989838]

### c_xes_gkt_spearman_full
- Recomputed: `0.9277303649` → display 2 d.p. = `0.93`
- Reported target: `0.93` (ddr_downstream.tex caption rho=0.93 for xes3g5m/gkt)
- Match: **PASS_ROUNDING**
- n=99; p=2.651003e-43; CI=[0.867729, 0.962312]

### d_global_pearson_all_pert
- Recomputed: `0.7466243641` → display 2 d.p. = `0.75`
- Reported target: `0.75` (fig_ddr_downstream.pdf pooled Pearson r=0.75)
- Match: **PASS_ROUNDING**
- n=186; p=2.102452e-34; CI=[0.617467, 0.846675]

## Findings from recomputation

No substantive mismatches. All four targets match at 2-decimal display rounding (`PASS_ROUNDING` or `PASS_EXACT_OR_TIGHT`). **No new CON finding opened.**

## Companion (not a headline target)

- XES/GKT Pearson on the same full pool as Spearman (plot_ddr caption `r`): `0.9851325655` (2 d.p. = `0.99`), p=`5.129e-76`, n=`99` — expected to align with reported `r=0.99` in `ddr_downstream.tex` caption.
- Match vs 0.99: **PASS_ROUNDING**

