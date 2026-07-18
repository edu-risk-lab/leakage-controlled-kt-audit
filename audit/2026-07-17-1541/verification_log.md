# Verification log — RAPID audit `2026-07-17-1541`

Legend: `PASS` | `FAIL` | `NOT VERIFIED` | `NOT APPLICABLE`

Never equate `NOT VERIFIED` with `PASS`.

## Pass A — Deterministic inventory

| Check | Status | Tools/commands/sources | Observed |
|---|---|---|---|
| Audit dir created without overwrite | PASS | `audit/2026-07-17-1541/` | New directory |
| Canonical tex/pdf hashed | PASS | PowerShell `Get-FileHash` SHA256 | tex `85517A95…`; pdf `53889464…` |
| Scoped inventory + hashes | PASS | Python hash over `paper/`,`results/`,`scripts/`,`src/`, skill | 663 files → `inventory.json` |
| LaTeX placeholder/TODO/`??` scan (`paper/`) | PASS | `manuscript_inventory.py --root paper` | warnings `0` |
| Missing `\ref` labels / bib keys (`paper/`) | PASS | same inventory | missing_latex_label `0`; missing_bib_key `0` |
| Full-repo inventory script | PASS (saved) | `inventory_full.json` (23 895 files; 583 warnings) | `main_APIN.tex` warnings **0**; most hits are `tools/miktex/**`, hyphenation data, unrelated `.tex` — not manuscript blockers |
| All `\input`/`\includegraphics` targets exist | PASS | `_scratch_scan` then deleted; 44 paths | missing `0` (resolved via project-root `results/`) |
| `submission_APIN` vs `results/tables` drift (key files) | PASS | SHA256 compare 6 tables | MATCH |
| Build log undefined citations/refs | PASS | `rg` on `main_APIN.log` | No undefined citation/reference warnings; PDF 57 pages |

## Pass B — Structure / internal consistency (rapid)

| Check | Status | Evidence | Observed |
|---|---|---|---|
| Title/abstract/contributions alignment (topic) | PASS | tex L90–163, contributions | Same protocol framing |
| Headline number consistency (core AUC deltas) | FAIL | number_consistency.csv | F-R01, F-R03, F-R11 conflicts |
| DDR correlation consistency | FAIL | captions + figure text layer | F-R02, F-R04 |
| Cross-ref/`??` unresolved in tex | PASS | inventory + grep | None in `main_APIN.tex` |
| Blinded identity leak | NOT APPLICABLE / NOT VERIFIED | Authors printed; APIN blind policy unknown | Journal typically single-blind — policy **NOT VERIFIED** |

## Pass C — References / claim evidence (rapid)

| Check | Status | Evidence | Observed |
|---|---|---|---|
| Bib keys parse; cite keys resolve locally | PASS | inventory 56 bib_keys in paper tree; 0 missing cites in scan | Note: bib file itself has 52 `@` entries |
| DOI live resolve / metadata match | NOT VERIFIED | No Crossref calls this audit | Prior `REFERENCES_AUDIT.md` not re-validated |
| Claim support from primary literature | NOT VERIFIED | Sources not re-read | Mark literature framing NOT VERIFIED |
| Internal claim→table support | FAIL/PARTIAL | claim_evidence_matrix.csv | Several SUPPORTED; C04 CONTRADICTED; C02 PARTIAL |

## Pass D — Methods / data / code (rapid)

| Check | Status | Evidence | Observed |
|---|---|---|---|
| Named scripts exist for key tables | PASS | declarations + `scripts/` inventory | Names present |
| Execute regeneration | NOT VERIFIED | Not run | — |
| Split/leakage code vs prose | NOT VERIFIED | Code not audited line-by-line | KT profile items deferred |
| Test-set tuning / leakage in builder | NOT VERIFIED | Requires code+logs | — |

## Pass E — Statistics (rapid)

| Check | Status | Evidence | Observed |
|---|---|---|---|
| “Significant” without test | PASS (rapid) | grep significant/Wilcoxon | Paper flags Wilcoxon underpower; uses paired-$t$ CI |
| Seed pooling as independent samples | FAIL (soft) | S22 nine-fold pool | F-R10 LOW |
| Recompute CIs/correlations | NOT VERIFIED | Not executed | — |

## Pass F — Integrity / privacy / licence / venue (rapid)

| Check | Status | Evidence | Observed |
|---|---|---|---|
| Declarations present | PASS | L2559–2618 | Funding, COI, ethics, data, code, authors |
| AI disclosure | NOT VERIFIED | Absent text; use history unknown | F-R07 |
| APIN mandatory checklist | NOT VERIFIED | Guidelines fetch timeout | F-R08 |
| Dataset/code licences | NOT VERIFIED | Declarations only | — |
| Privacy / restricted data exposure | NOT VERIFIED | Public-dataset claim only | No secrets scanned beyond rapid grep |

## PDF / visual

| Check | Status | Evidence | Observed |
|---|---|---|---|
| PDF opens; title/authors render | PASS | Read `main_APIN.pdf` text | Title + authors visible |
| Figure S3 annotation | FAIL (clarity) | Read `fig_ddr_downstream.pdf` | Burned-in `pooled Pearson r=0.75` |
| Full page-by-page layout QA | NOT VERIFIED | Not done | — |

## Environment notes

- Host: Windows; MiKTeX build log dated 17 Jul 2026 13:42.
- No manuscript source files modified.
- Internet: used for SN AI policy search; APIN guidelines page timed out.

---

## Focused evidence pass — F-R01 & F-R02 (read-only)

Deliverables: `focused_FR01_FR02.md`, `epoch_evidence_matrix.csv`, `ddr_correlation_evidence_matrix.csv`, `proposed_canonical_values.md`.

### F-R01 checks

| Check | Status | Tools/sources | Observed |
|---|---|---|---|
| Enumerate 10/30 claims in `main_APIN.tex` + tables | PASS | ripgrep + file reads | 10ep claim in abstract/prose/S22 narrative; 30ep in S15/S21/Q1 caption |
| Config resolution for primary simpleKT | PASS | `configs/xes3g5m.yaml`; `baseline_runner.py` L733–735 | Defaults to `pykt.epochs=30` |
| Config for Phase-3 trio simpleKT | PASS | `configs/experiments/xes3g5m_primary_trio_matched.yaml` L58; `run_q1_gpu_experiments.sh` L61 | `pykt.epochs: 30`; shell string “30ep” |
| Config for GKT ablation | PASS | `configs/xes3g5m_gkt_epochs30.yaml` | epochs 30, batch 32 |
| Manuscript “simpleKT @ 10ep” supported by config | FAIL | no yaml sets simplekt epochs:10 | Prose-only; contradicted |
| Trace S21 pairing to CSV | PASS | `generate_gkt_epoch_ablation.py` L54–97; fold CSVs | S21 uses **primary** simpleKT; label hardcoded 30; $\Delta=-0.037625$ |
| Trace S22/pooled pairing | PASS | same script `_pooled_nine_fold`; `q1_gkt_vs_simplekt.csv` | Prefers `simplekt30` then `trio_matched`; $\Delta$ s42 $=-0.037529$ |
| `simplekt30` cache JSON present | FAIL / NOT VERIFIED | glob `results/cache/xes3g5m_fold_*_simplekt_s*_…` | **0** files |
| Training logs / run_id for trio & gkt30 | NOT VERIFIED | glob `*gkt_epochs30*.log`, `*trio_matched*.log`; `experiment_log.csv` | Logs absent |
| Canonical epoch without majority vote | PASS (method) | see `proposed_canonical_values.md` | Config-canonical simpleKT=30; executed epochs NOT VERIFIED |

### F-R02 checks

| Check | Status | Tools/sources | Observed |
|---|---|---|---|
| Inventory $r$/$\rho$ in prose/captions/figure | PASS | grep + Read PDF text layer | 0.93/0.99/0.75 + caption $\rho$ values |
| Map each value to script definition | PASS | `generate_ddr_downstream_gkt_tex.py`; `plot_ddr_downstream.py` | Core Pearson / all-$p$ Pearson / Spearman / global Pearson |
| Subset sizes $n$ without recomputing $r$ | PASS | read `ddr_downstream.csv` | XES/GKT core 81; all-$p$ 99; global finite 186 |
| Manuscript $n{=}81,99$ vs CSV | PASS | `main_APIN.tex` L1643 vs sizes | Match |
| Recompute Pearson/Spearman floats | NOT VERIFIED | intentionally not run | Per user constraint |
| Regenerate / edit figure | NOT APPLICABLE | read-only | — |
| $0.93$ vs $0.99$ vs $0.75$ same estimand? | FAIL (as same estimand) / PASS (as scoped family) | definitions above | Different scopes; labeling debt on $\rho$ and figure |

### Integrity

- No writes to `paper/`, `configs/`, `scripts/`, `src/`, `results/`, figures.
- Scratch helpers deleted after use; outputs only under `audit/2026-07-17-1541/`.

---

## F-R02 deterministic recomputation

| Check | Status | Source | Observed |
|---|---|---|---|
| Recompute a–d from `ddr_downstream.csv` | PASS | `recompute_ddr_correlations.py` | See `ddr_recomputed.csv` |
| a Pearson core vs 0.93 | PASS_ROUNDING | n=81, r=0.931037 | display 0.93 |
| b Pearson all-p vs 0.99 | PASS_ROUNDING | n=99, r=0.985133 | display 0.99; p=5.129e-76 matches caption |
| c Spearman full vs ρ=0.93 | PASS_ROUNDING | n=99, ρ=0.927730 | display 0.93 |
| d global Pearson vs 0.75 | PASS_ROUNDING | n=186, r=0.746624 | display 0.75; p=2.102e-34 |
| New substantive finding | NOT APPLICABLE | — | No FAIL; numbers not rewritten |
| Manuscript/figure edits | NOT APPLICABLE | — | None |

---

## Experiment provenance recovery — F-R01 & F-R12

Deliverables: `experiment_provenance_matrix.csv`, `FR01_FR12_evidence_report.md`, `missing_artifacts.md`, `rerun_requirements.md`.

| Check | Status | Evidence | Observed |
|---|---|---|---|
| Search logs/ckpts/mlflow/cache/git | PASS (search) | See report §Search coverage | MLflow absent; q1 logs partial; cache gitignored/deleted |
| Treat HEAD YAML as execution proof | FAIL (rejected) | Policy | Current GKT batch 8 not used as primary evidence |
| Primary AUC ↔ config@`619c02cf` | PASS | git show | GKT 10/4; simpleKT 30/64 intended |
| S15 batch 16 vs primary commit | FAIL (consistency) | tex@a288d4a0 vs yaml@619c02cf | F-R12: S15 regenerated under batch 16; AUCs from batch-4 era |
| `training_parity.csv` vs `.tex` | FAIL | csv batch 4; tex batch 16 | Dual S15 artifacts |
| GKT30 final AUCs ↔ on-disk logs | FAIL | logs ~0.71; CSV ~0.84 | Stale logs only |
| GKT30 seed42 config@intro | PASS | `b02afca9` yaml | epochs 30 batch **16** (not 32) |
| simplekt30 cache in WT | FAIL | deleted `85afe0c8` | Recoverable from `004691d3` only; no hp fields |
| trio_matched isolated runs | FAIL | no q1 folders/logs | ARTIFACT_TAG_ONLY |
| Any paper S15–S22 row EXECUTION_VERIFIED for epochs+batch | FAIL | matrix | None |
| Stale GKT30 logs epoch=30 | PASS | `logs/q1/gkt_epochs30_s17.log` | EXECUTION_VERIFIED for superseded 0.71 runs only |
| Source tree unmodified | PASS | audit-only writes | manuscript/config/results untouched |
