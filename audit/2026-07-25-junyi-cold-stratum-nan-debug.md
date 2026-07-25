# Junyi cold-stratum AUC NaN debug (A3 follow-up)

**Date:** 2026-07-25  
**Scope:** Junyi `cold` / `very_cold` rows in `results/tables/cold_start_metrics.csv`

## Symptom

40/42 Junyi cold-stratum cells show `AUC=NaN`; 38 have `n_disc=0`. Only two finite-AUC cells (both SKT): `cold` fold 0 (AUC 0.623, n_disc=26) and `very_cold` fold 1 (AUC 0.529, n_disc=12).

## Verdict

**Not a code bug.** Expected statistical degeneracy on a saturated corpus with tiny cold strata.

### Causes (layered)

1. **Structural sparsity:** Junyi has only 4–15 train `very_cold` KCs and 4–8 `cold` KCs per fold vs hundreds–millions of warm/hot eval steps.
2. **AUC suppression (`MIN_DISCORDANT_PAIRS=10`):** `src/cold_start_report.py` returns NaN when labels are single-class or score blocks are label-pure (`n_disc < 10`).
3. **PyKT export coverage:** Metrics use tail-truncated pyKT predictions (`max_seq_len=100`), so CSV `n` is smaller than raw eval (e.g. fold 0 `very_cold`: 11 vs 19).
4. **Historical artefact resolved:** Pre-A3.5 capped path gave identical AUC=1.0 across models; GPU rerun (`bc9ea715`) removed that; NaN now reflects correct suppression.

## Action taken

- Extended hard suppress in `scripts/generate_phase_c_tables.py` to Junyi **`cold`** as well as `very_cold` (summary/comparison already showed `---` via NaN aggregation).
- Manuscript §4.8 already documents suppression for both strata; tables S12–S13 retain ACC/NLL where finite.

## Do not

- Lower `MIN_DISCORDANT_PAIRS` — would surface unreliable AUC on n≈11–56 samples.
- Rerun expecting stable Junyi cold AUC — fold-level mass is insufficient by design.

## Warm/hot contrast

Same code path; fold 0 `hot` n≈6.2M with n_disc in the millions → stable AUC. Junyi role in paper remains **saturated sanity check**, not cold-start benchmark.
