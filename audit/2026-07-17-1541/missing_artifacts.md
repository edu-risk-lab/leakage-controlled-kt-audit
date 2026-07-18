# Missing artifacts blocking EXECUTION_VERIFIED (F-R01 / F-R12)

Read-only inventory. Paths relative to repo root unless noted.

## Critical gaps (paper S15–S22)

| Missing artifact | Needed for | Status |
|---|---|---|
| Training log for primary XES3G5M GKT/simpleKT (3 folds) | Primary epochs/batch | ABSENT |
| `results/cache/xes3g5m_fold_*_{gkt,simplekt}_train_only_result.json` with hp fields | Primary lineage | ABSENT (and schema lacks hp even when present) |
| `logs/q1/gkt_epochs30_s42.log` | S21 GKT30 seed 42 | ABSENT |
| Training logs for **final** GKT30 AUCs (~0.84) | S21/S22 GKT | ABSENT (existing s17/s1234 logs are 0.71-era) |
| `logs/q1/trio_matched_s{17,42,1234}.log` | Phase-3 trio | ABSENT |
| `results/q1/trio_matched_s*/baseline_fold_results.csv` | Trio isolation | ABSENT (rows only in merged CSV) |
| Working-tree `simplekt_s*` cache JSON | S22 simplekt30 | DELETED in `85afe0c8` (recoverable from `004691d3` only) |
| Checkpoints for paper AUCs | Hashable model state | ABSENT in WT; `results/pykt_work/` gitignored |
| MLflow / W&B / ClearML runs | Run ID ↔ hp | ABSENT |
| Config snapshot file written beside each fold result | Immutable hp | ABSENT (only live YAML + git history) |
| Environment lockfile tied to Jun 2026 GPU runs | Reproducibility | Only unrelated `pip_freeze_verify_20260520.txt` |
| Shell/command history of GPU server runs | Exact CLI | ABSENT (wrapper `logs/q1/run.log` incomplete) |

## Present but insufficient

| Artifact | Why insufficient |
|---|---|
| `logs/q1/gkt_epochs30_s17.log`, `s1234.log` | Prove epoch loop to 30 for **stale** ~0.71 AUCs; do not contain final 0.84 metrics |
| `results/tables/training_parity.tex` | Config dump at regeneration time; disagrees with `training_parity.csv` and with primary AUC commit |
| Cache JSON (when present) | No `epochs` / `batch_size` keys |
| Current `configs/xes3g5m.yaml` | Post-dates primary AUCs; GKT batch 8 ≠ historical 4 or S15 16 |

## Recoverable from git (not in working tree)

| Object | Commit | Caution |
|---|---|---|
| `results/cache/xes3g5m_fold_*_simplekt_s*_train_only_result.json` (+ preds) | `004691d3` (deleted `85afe0c8`) | Still no hp fields |
| `results/cache/xes3g5m_fold_0_gkt_s17_train_only_result.json` | `fcb14635` | AUC matches paper fold0 s17; hp not in JSON |
| `.../gkt_p0_protocol_best.ckpt` | `fcb14635` | May not match final multi-fold paper set |

## Intentionally out of scope / empty

- `mlruns/`, `wandb/`, `checkpoints/`, `outputs/` — not used by this project layout.
