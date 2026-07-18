# Proposed canonical values (evidence-gated)

Rule: a value is **canonical** only when backed by config and/or immutable run artifact. Prose majority does **not** decide. Missing run logs → leave **NOT VERIFIED**.

## F-R01 — Epoch budgets

| Quantity | Proposed canonical | Evidence gate | Status |
|---|---|---|---|
| Primary `simpleKT` epochs (XES3G5M, `configs/xes3g5m.yaml`) | **30** | `pykt.epochs: 30`; model has no `hyperparams.epochs` override; `src/baseline_runner.py` L733–735 falls back to `pykt.epochs`; S15 emitted by `generate_training_parity.py` from that config | **CONFIG-CANONICAL**; actual executed epochs on GPU **NOT VERIFIED** (no log / no epoch field in `baseline_fold_results.csv`) |
| Primary `simpleKT` batch | **64** | `pykt.batch_size: 64` in `configs/xes3g5m.yaml` | **CONFIG-CANONICAL**; run **NOT VERIFIED** |
| Primary GKT epochs | **10** | `baselines.gkt.hyperparams.epochs: 10` in `configs/xes3g5m.yaml` | **CONFIG-CANONICAL**; run **NOT VERIFIED** |
| Primary GKT batch | **NOT VERIFIED** | S15 prints 16; current yaml has `batch_size: 8` | Do not canonicalize |
| Epoch-ablation GKT | **30 epochs, batch 32** | `configs/xes3g5m_gkt_epochs30.yaml` `pykt.epochs/batch_size`; runner `run_gkt_epochs30`; artifacts `results/q1/gkt_epochs30_s*` | **CONFIG + ARTIFACT tag**; training-loop epoch count in log **NOT VERIFIED** |
| Phase-3 / S22 `simpleKT` reference epochs | **30** (config/script intent), **not 10** | `xes3g5m_primary_trio_matched.yaml` `pykt.epochs: 30`; `run_q1_gpu_experiments.sh` L61 labels “30ep”; Q1 caption “30 epochs from cache”; S21 generator hardcodes 30 | **CONFIG/SCRIPT-CANONICAL against manuscript “10”**; cache JSON files for `simplekt30` **ABSENT** locally → executed epochs still **NOT VERIFIED** |
| Manuscript claim “`simpleKT` reference at 10 epochs” | **Reject as unsupported** | No config sets `simplekt` → 10; contradicted by configs/scripts above | **NOT VERIFIED as fact**; treat as documentation error pending author attestation + logs |

### Pairing canonicals (what $\Delta$ actually used)

| Table / claim | GKT source | simpleKT source | Canonical pairing statement |
|---|---|---|---|
| S16 / primary $\Delta\approx-0.041$ | `baseline_fold_results.csv` gkt | same CSV simplekt | Primary release pair; epochs from config resolution (GKT10 vs simpleKT30) — **fairness caveat remains** |
| S21 seed-42 $\Delta$ | `q1` `gkt_epochs30_s42` | **`baseline_fold_results` simplekt** (not `simplekt30`) | Generator L54–66; delta $-0.037625$ matches that pairing |
| S22 / pooled $\Delta$ | `gkt_epochs30_*` | prefer `simplekt30_*` else `trio_matched_*` | Generator `_pooled_nine_fold`; AUCs of `simplekt30`≡`trio_matched` on shared folds |

Do **not** canonicalize “S21 and S22 use the same simpleKT run” — evidence shows S21 uses primary baseline simpleKT.

## F-R02 — DDR correlations

| Quantity | Proposed canonical meaning | Evidence gate | Status |
|---|---|---|---|
| Headline Pearson $r{=}0.93$ | **XES3G5M / GKT / Pearson / $p\le0.3$ core / row-level** | `generate_ddr_downstream_gkt_tex.py` `_corr(..., 0.3)`; subset size $n{=}81$ matches prose L1643 | **DEFINITION-CANONICAL**; numeric recompute **not performed** (per audit scope) |
| Headline Pearson $r{=}0.99$ | **XES3G5M / GKT / Pearson / all $p$ incl. anchors / row-level** | same script `_corr(..., None)`; $n{=}99$ | **DEFINITION-CANONICAL**; recompute withheld |
| Caption $\rho{=}0.93$ on `ddr_downstream.tex` | **Spearman** on full XES3G5M/GKT pool ($n{=}99$), **not** the core Pearson | `plot_ddr_downstream.py` L113–115; caption string | **DEFINITION-CANONICAL**; do not equate to headline $r{=}0.93$ without label |
| Figure pooled $r{=}0.75$ | **Global Pearson** over all finite pert rows (both datasets × both models), $n{=}186$ | `plot_ddr_downstream.py` L121–129; figure text layer | **DEFINITION-CANONICAL**; different scope — **not** a contradiction of $0.99$ if disclosed |

### Contradiction vs under-specification

| Pair | Verdict |
|---|---|
| $0.93$ (core Pearson) vs $0.99$ (all-$p$ Pearson) | **Different scopes**, both defined in GKT table generator — OK if prose keeps both definitions |
| $0.93$ (core Pearson) vs $0.93$ (Spearman $\rho$ in `ddr_downstream` caption) | **Different statistics, same digit** — under-specified if reader collapses them |
| $0.99$ (XES/GKT) vs $0.75$ (global figure pool) | **Different pools** — not numerical conflict; figure caption currently **under-describes** (claims DGEKT-focused story while annotation is global pooled $r$) |

## What must remain NOT VERIFIED until logs/cache return

1. Wall-clock training epoch counts actually executed for primary / trio / `simplekt30` / GKT30.
2. Recomputed floating-point $r$/$\rho$ from `ddr_downstream.csv` (intentionally not recomputed in this pass).
3. Whether S15 GKT batch 16 matches the primary run that produced `baseline_fold_results.csv`.
