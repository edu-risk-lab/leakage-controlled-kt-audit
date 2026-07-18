# Focused evidence audit — F-R01 & F-R02

- Audit folder: `audit/2026-07-17-1541/`
- Depth: focused evidence (read-only)
- Canonical manuscript: `paper/main_APIN.tex` (unchanged)
- Constraint: no edits to manuscript, code, config, results, or figures; **no correlation recomputation**

Companion files: `epoch_evidence_matrix.csv`, `ddr_correlation_evidence_matrix.csv`, `proposed_canonical_values.md`, `verification_log.md` (section appended).

---

## F-R01 — simpleKT 10 vs 30 epochs

### 1. All manuscript / table locations stating 10 or 30 for simpleKT / training budgets

| Epochs claim | Role | Locator |
|---|---|---|
| simpleKT reference **10** ep, batch 64 | Ablation reference | `paper/main_APIN.tex` abstract L140–141; L342; L416–417; L1427–1428; L2111–2113; L2427–2428; L2485–2486 |
| Sequence checkpoints **30** ep, batch 64 (includes simpleKT family) | Primary parity prose | `paper/main_APIN.tex` L1446–1448; L1459–1460 |
| Phase-3 trio simpleKT **10** ep, batch 64 | Ablation pairing prose | `paper/main_APIN.tex` L1463; L2112 |
| Full 30-ep simpleKT parity **remains open** | Limitations | `paper/main_APIN.tex` L2164–2165 |
| S15 simpleKT **30** / 64 | Table | `results/tables/training_parity.tex` L7–8 |
| S21 simpleKT reference **30** / 64 | Table | `results/tables/gkt_epoch_ablation.tex` L8 |
| Q1/S22 caption: simpleKT **30** ep from cache else Phase-3 | Caption | `results/tables/q1_gkt_epochs30_ablation.tex` L4 |
| GKT primary **10**; ablation **30**/batch 32 | GKT side | abstract L138–140; L2466–2467; `xes3g5m_gkt_epochs30.yaml` |

### 2–3. Lineage by run role

#### A. Primary release (baseline CV / S16)

| Field | Evidence |
|---|---|
| Config | `configs/xes3g5m.yaml`: `simplekt` has **no** `hyperparams`; `pykt.epochs: 30`, `pykt.batch_size: 64` (L87–91); `gkt.hyperparams.epochs: 10` (L56–58) |
| Resolution code | `src/baseline_runner.py` L733–735: `epochs = hp.get("epochs", py_all.get("epochs", 30))` |
| Metrics artifact | `results/tables/baseline_fold_results.csv` — XES3G5M `train_only` simplekt/gkt folds 0–2 (no epoch column) |
| S15 emitter | `scripts/generate_training_parity.py` L36–42, L56–60 → writes simpleKT **30**/64 |
| Command / log / run_id | **NOT VERIFIED** — `logs/experiment_log.csv` has no baseline training rows; no `results/pykt_work/`; no per-run logs |

**Config-canonical primary simpleKT epochs = 30**, not 10. Executed epochs **NOT VERIFIED**.

#### B. Epoch-ablation GKT (S21–S22 GKT side)

| Field | Evidence |
|---|---|
| Config | `configs/xes3g5m_gkt_epochs30.yaml` L42–43, L55–56: epochs 30, batch 32 |
| Command | `scripts/run_q1_gpu_experiments.sh` L41–55: `python -m src.baseline_runner --config configs/xes3g5m_gkt_epochs30.yaml --split-base-seed … --isolated-results gkt_epochs30_s{seed}` |
| Artifacts | `results/q1/gkt_epochs30_s17|s42|s1234/baseline_fold_results.csv`; merged into `results/tables/q1_baseline_fold_results.csv` tags `gkt_epochs30_*` |
| Log files | `gkt_epochs30_*.log` **ABSENT** on disk |

#### C. Reference simpleKT for ablation (S21 vs S22 — different sources)

| Table | simpleKT source used by generator | Epoch label printed | Evidence |
|---|---|---|---|
| **S21** (seed 42) | `baseline_fold_results.csv` primary simplekt | Hardcoded **30** / 64 | `scripts/generate_gkt_epoch_ablation.py` L54–66, L97 |
| **S22 / pooled** | Prefer `simplekt30_*` else `trio_matched_*` in `q1_baseline_fold_results.csv` | Caption/tag **30** | same file L37–45; `summarize_q1_experiments.py` L47–80, L100–107 |

Measured pairing deltas (read-only check against CSVs):

| Pairing | $\Delta$ mean |
|---|---|
| S21 logic: GKT30@s42 − primary simpleKT | $-0.037625$ (= `gkt_epoch_ablation.csv` `epoch_matched_seed42`) |
| S22 logic: GKT30@s42 − simplekt30 | $-0.037529` (= `q1_gkt_vs_simplekt.csv` seed 42) |

So S21 and S22 are **not** the same simpleKT artifact, even though both are labeled “30”.

#### D. Phase-3 trio (`trio_matched_*`)

| Field | Evidence |
|---|---|
| Config | `configs/experiments/xes3g5m_primary_trio_matched.yaml`: comment L1–2; `simplekt` enabled without epoch override; `pykt.epochs: 30` (L58) |
| Shell label | `run_q1_gpu_experiments.sh` L61: **“Primary trio (GKT+simpleKT+GIKT 30ep)”** |
| Artifacts | Rows in `q1_baseline_fold_results.csv` with `trio_matched_s*`; **no** `results/q1/trio_matched_*` folders locally |
| Cache for `simplekt30` | Pattern `results/cache/xes3g5m_fold_*_simplekt_s*_train_only_result.json` → **0 files** |
| Manuscript “10 epochs” | **No supporting config**; contradicted by config + shell string |

### 4. What is canonical (gated)

See `proposed_canonical_values.md`.

Short form:

- **Canonical (config): primary & Phase-3-intended simpleKT = 30 epochs.**
- **Manuscript “simpleKT reference = 10 epochs” = unsupported / contradicted by available configs and runner labels.**
- **Executed epoch counts on the machine that produced AUCs = NOT VERIFIED** (logs/cache missing).
- **Do not pick 10 because the abstract repeats it.**

### 5. F-R01 conclusion

| Question | Answer |
|---|---|
| Is there an internal 10 vs 30 conflict? | **Yes** — prose/abstract/S22 narrative say 10; S15/S21/Q1 caption/configs/shell say 30 |
| Which side has run/config evidence? | **30** has config + generator + shell evidence; **10** has prose only |
| Are S21/S22 deltas interchangeable? | **No** — different simpleKT sources (primary vs simplekt30/trio) |
| Can we certify GPU epoch counts? | **NOT VERIFIED** |

---

## F-R02 — DDR Pearson $r$ / Spearman $\rho$

### 1–2. Inventory of reported values (with scope)

Full matrix: `ddr_correlation_evidence_matrix.csv`.

| Value | Statistic | Dataset/model | Scope | $n$ (CSV subset, not recomputed $r$) | Producer |
|---|---|---|---|---|---|
| **0.93** | Pearson $r$ | xes3g5m / gkt | $p\le0.3$ core | **81** | `generate_ddr_downstream_gkt_tex.py` `_corr(..., 0.3)` → `ddr_downstream_gkt.tex` |
| **0.99** | Pearson $r$ | xes3g5m / gkt | all $p$ incl. 0.9 anchors | **99** | same script `_corr(..., None)`; also `plot_ddr_downstream.py` per-(ds,model) → `ddr_downstream.tex` caption |
| **0.93** | Spearman $\rho$ | xes3g5m / gkt | full pert pool (no core filter) | **99** | `plot_ddr_downstream.py` L114 → caption `$\rho$=0.93` |
| **0.75** | Pearson $r$ | **all** rows (assist+xes × dgekt+gkt) | global pool | **186** finite | `plot_ddr_downstream.py` L128–129 → `fig_ddr_downstream.pdf` annotation |
| 0.97 / 0.95 | $r$ / $\rho$ | assist2012 / gkt | full cell | 33 | `plot_ddr_downstream.py` |
| 0.15 / 0.18 | $r$ / $\rho$ | assist2012 / dgekt | full cell | 27 | same |
| 0.13 / 0.18 | $r$ / $\rho$ | xes3g5m / dgekt | full cell | 27 | same |

Input artifact for all of the above: `results/tables/ddr_downstream.csv` (210 rows; pert 192; models `gkt`,`dgekt`).

Manuscript $n{=}81$ and $99$ (`paper/main_APIN.tex` L1642–1643) **matches** CSV subset sizes for XES/GKT core and all-$p$ — supports that D01/D02 definitions are the intended ones.

### 3. Text vs caption vs annotation vs table

| Channel | What it states | Gap |
|---|---|---|
| Abstract L132 | Pearson $r\approx0.93$ on $p\le0.3$ core, $r\approx0.99$ with anchors | Aligns with GKT table generator definitions |
| Body L1642–1643 | Same + $n{=}81$ and $99$ | Aligns with subset sizes |
| `ddr_downstream_gkt.tex` caption | Pearson $r{=}0.93$ core, $0.99$ including anchors | Aligns with abstract |
| `ddr_downstream.tex` caption | xes3g5m/gkt: $r{=}0.99$, $\rho{=}0.93$ | **$\rho{=}0.93$ is Spearman on full pool** — same digit as core Pearson, different statistic |
| `fig_ddr_downstream.pdf` | annotation `pooled Pearson r=0.75` | Global pool $n{=}186$ |
| App Fig S3 caption (`main_APIN.tex` L2357) | “DGEKT sensitivity…” — **no** $r{=}0.75$, **no** model pool disclosure | Under-specified vs annotation |

### 4. Contradiction or different scopes?

**Verdict: primarily different scopes / statistics, with labeling debt — not three incompatible estimates of one parameter.**

1. **$0.93$ (Pearson, core)** and **$0.99$ (Pearson, all $p$)** are two intentional subsets in `generate_ddr_downstream_gkt_tex.py`. Compatible if both definitions stay visible.
2. **$0.93$ (Spearman $\rho$, full XES/GKT)** in `ddr_downstream.tex` is **not** the core Pearson. Treating caption $\rho$ as the abstract’s $r{=}0.93$ would be a false conflict or false agreement.
3. **$0.75$** is a **global** pooled Pearson over both models/datasets. It does **not** refute $0.99$ for XES/GKT alone. The failure mode is **omitted scope** in the figure caption (and caption’s DGEKT-only framing vs multi-model plot).

Numeric values were **not recomputed** in this pass; definitions and $n$ were verified from scripts + CSV structure + existing emitted captions/annotations.

### 5. F-R02 conclusion

| Question | Answer |
|---|---|
| Same estimand thrice? | **No** |
| Are $0.99$, $0.93$, $0.75$ mutually exclusive? | **No**, if scopes above are kept |
| Is presentation adequate? | **No** — caption $\rho{=}0.93$ and figure $r{=}0.75$ lack explicit scope next to the abstract’s Pearson pair |
| Recompute / regenerate figure? | **Deferred** until authors accept these input definitions (`ddr_downstream.csv` + two scripts) |

---

## Cross-cutting gaps (both findings)

| Missing evidence | Impact |
|---|---|
| Training logs (`*.log`), `results/pykt_work/`, `simplekt30` cache JSON | Cannot certify executed epochs |
| `results/q1/trio_matched_*` folders | Trio AUCs only in merged CSV |
| Correlation recompute | $r$/$\rho$ floats trusted from prior emission, not re-derived here |

---

## Recommended documentation fixes (not applied)

1. Replace every “simpleKT reference at **10** epochs” with **30** (or attach logs proving 10).
2. State explicitly that S21 pairs GKT30 against **primary** simpleKT, S22 against **simplekt30/trio**.
3. In DDR captions: label Pearson-core / Pearson-all / Spearman-full / Pearson-global separately; put $n$ and pool on Fig S3.
4. Resolve limitations L2164–2165 vs tables that already claim 30-ep simpleKT.
