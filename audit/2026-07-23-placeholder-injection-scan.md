# Placeholder injection scan (CPU high-priority)

**Date:** 2026-07-23  
**Scope:** Quét repo tìm số injection placeholder cũ (+0.05 GKT, 0.850→0.858, …) sau A1 verified.

## Verified ground truth (Table S18, fold 0)

| Model | Δ@20% | Source |
|-------|------:|--------|
| simpleKT | +0.0004 | `results/tables/downstream_auc_injection.csv` |
| GKT | **−0.0103** | same |
| GIKT | +0.0002 | same |

## Files updated (active code / exports)

| File | Change |
|------|--------|
| `scripts/build_seminar_pptx.py` | 2×2 table + takeaway → verified decoupling |
| `scripts/build_seminar_pptx_vi.py` | 2×2 table + speaker notes slide 15 |
| `scripts/create_fake_tables.py` | **Deprecated** — exits with pointer to `collect_injection_auc` |
| `scripts/export_baocao_sua_word.py` | §5 bullets → decoupling narrative |
| `scripts/_remediate_fr01_manuscript.py` | Header note: injection patches superseded |

## Left unchanged (historical audit only)

These retain placeholder numbers **on purpose** as audit trail:

- `audit/2026-07-17-1541/*`, `audit/2026-07-22-A1-*`, `audit/2026-07-22-server_A-*`
- `REVISION_PLAN_APIN.md` (superseded plan; see `REVISION_PLAN_APIN_NCS_20260722.md`)

## Manuscript / submission

- `paper/submission_APIN/main_APIN.tex` — Table~\ref{tab:two-factor} and §4.3 already use verified numbers (commit `80935c47` batch).

## Regenerate seminar decks (optional)

```bash
python scripts/build_seminar_pptx.py
python scripts/build_seminar_pptx_vi.py
```

## Residual grep hits (benign)

- `0.05` in DDR perturbation budgets (`p=0.05`), significance stars, dropout hyperparams — **not** injection AUC.
- `mock_gkt.py` random stub — documented; not used for paper tables.
