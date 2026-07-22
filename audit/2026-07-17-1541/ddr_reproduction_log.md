# DDR recomputation reproduction log

- UTC: 2026-07-17T09:43:37.997326+00:00
- Python: 3.14.2 (CPython)
- Platform: Windows-11-10.0.26100-SP0
- numpy: 2.4.0; pandas: 2.3.3; scipy: scipy.stats
- scipy version: 1.16.3
- Input CSV: `D:\0. NCS\CODE\p0_project\results\tables\ddr_downstream.csv`
- Input SHA-256: `c2e1bcdcdc83d314377318ee742994e4fbc0b706263f1f844966e6b12be8214d`
- Input size bytes: 38103
- Bootstrap seed: 20260717; n_resamples: 10000
- Working directory intent: read `D:\0. NCS\CODE\p0_project\results\tables\ddr_downstream.csv`, write only under `D:\0. NCS\CODE\p0_project\audit\2026-07-17-1541`

## Commands

```
python "D:\0. NCS\CODE\p0_project\audit\2026-07-17-1541\recompute_ddr_correlations.py"
```

## Outputs

- `D:\0. NCS\CODE\p0_project\audit\2026-07-17-1541\ddr_recomputed.csv`
- `D:\0. NCS\CODE\p0_project\audit\2026-07-17-1541\ddr_recomputation_report.md`
- `D:\0. NCS\CODE\p0_project\audit\2026-07-17-1541\ddr_reproduction_log.md`

## Observed summary

- a_xes_gkt_pearson_core: n=81 pearson_r=0.931037 p=2.489e-36 CI=[0.8906,0.9561] vs 0.93 → PASS_ROUNDING
- b_xes_gkt_pearson_all_p: n=99 pearson_r=0.985133 p=5.129e-76 CI=[0.9781,0.9898] vs 0.99 → PASS_ROUNDING
- c_xes_gkt_spearman_full: n=99 spearman_rho=0.927730 p=2.651e-43 CI=[0.8677,0.9623] vs 0.93 → PASS_ROUNDING
- d_global_pearson_all_pert: n=186 pearson_r=0.746624 p=2.102e-34 CI=[0.6175,0.8467] vs 0.75 → PASS_ROUNDING

- max_abs auc_drop CSV vs recomputed (XES/GKT): 9.801188e-17
- companion XES/GKT Pearson full pool: 0.985133 → PASS_ROUNDING

## Non-actions

- Did not modify manuscript, `results/`, or figures.
- Did not rewrite reported manuscript numbers.
