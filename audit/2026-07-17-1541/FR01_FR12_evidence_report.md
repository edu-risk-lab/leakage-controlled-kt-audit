# Experiment provenance recovery — F-R01 & F-R12

- Audit dir: `audit/2026-07-17-1541/`
- Mode: read-only (no edits to manuscript, config, tables, or results)
- Rule: **current YAML is not historical execution evidence**
- Companion: `experiment_provenance_matrix.csv`, `missing_artifacts.md`, `rerun_requirements.md`

**F-R01** = simpleKT / GKT epoch labeling for S15–S22.  
**F-R12** = GKT batch conflict (S15 = 16 vs current YAML = 8 vs config@primary-AUC-commit = 4).

---

## Search coverage

| Class | Found? | Notes |
|---|---|---|
| Training logs | Partial | `logs/q1/gkt_epochs30_s17.log`, `s1234.log`, `run.log`; assist baselines only. **No** xes primary / simplekt30 / trio / gkt_epochs30_s42 logs |
| Checkpoints | Absent in WT | Historically `gkt_p0_protocol_best.ckpt` committed under `results/pykt_work/...` (fcb14635); `results/pykt_work/` gitignored; no xes ckpt in working tree now |
| MLflow / W&B | Absent | No `mlruns/`, `wandb/` |
| Command history | Partial | `logs/q1/run.log` wrapper; no shell history file |
| Result JSON/CSV | Partial | Primary: `baseline_fold_results.csv`. Q1: `results/q1/gkt_epochs30_s*/`. `simplekt30` cache JSON **deleted** from HEAD (recoverable at `004691d3`) |
| Config snapshots | Via git | Historical blobs for `xes3g5m.yaml`, `xes3g5m_gkt_epochs30.yaml`, trio yaml |
| Environment manifest | Weak | `logs/pip_freeze_verify_20260520.txt` (May 20; not tied to Jun runs) |
| Timestamps | Yes | Artifact mtimes + git commit dates |
| Git commit/tag | Yes | See matrix |
| Seed/fold IDs | Yes | In CSV columns |

Result JSON schema (`src/baseline_runner.py` cache dump) stores AUC/status/note only — **never epochs or batch_size**.

---

## Lineage summaries

### 1. Primary GKT (feeds S16; S15 row)

| Item | Evidence |
|---|---|
| AUC artifact | `results/tables/baseline_fold_results.csv` (git blob unchanged since `619c02cf`, 2026-06-03) |
| Config **at that commit** | `gkt.hyperparams.epochs: 10`, `batch_size: 4` |
| S15 tex today | Epochs 10, **Batch 16** (`training_parity.tex`, regenerated `a288d4a0` when YAML had batch 16) |
| S15 csv leftover | Still lists GKT **batch 4** (`training_parity.csv`, mtime 2026-06-10) |
| Current YAML | batch **8** since `955a8202` (2026-06-24) |
| Log / ckpt | **ABSENT** for xes primary |
| Strength | **CONFIG_INTENDED_ONLY** for epochs=10 & batch=4 at AUC commit; S15 batch 16 is **not** execution-verified; current batch 8 is **irrelevant** to those AUCs |

### 2. Primary simpleKT (feeds S16; S15 row; S21 pairing baseline)

| Item | Evidence |
|---|---|
| AUC artifact | same `baseline_fold_results.csv` @`619c02cf` |
| Config at commit | no model hp → `pykt.epochs: 30`, `pykt.batch_size: 64` |
| Prose “10 epochs” | **No** config/log/artifact supports it |
| Strength | **CONFIG_INTENDED_ONLY** for 30/64; prose 10 = **NOT VERIFIED** (contradicted by historical config) |

### 3. `gkt_epochs30` (S21/S22 GKT side)

| Item | Evidence |
|---|---|
| Final AUC CSV | `results/q1/gkt_epochs30_s{42,17,1234}/baseline_fold_results.csv` (~0.83–0.84) |
| Seed 42 intro commit | `b02afca9` — config then **epochs 30, batch 16** |
| Seed 17/1234 final | after `fcb14635` batch→**32**; config @`0982891d`/`007f621f` = 30/32 |
| Logs on disk | `logs/q1/gkt_epochs30_s17.log` & `s1234.log` show **pyKT epoch … 30** and YAML load — but AUCs in those runs (~0.71) match **superseded** `d9efa271`, **not** paper CSVs |
| Strength for **paper** AUCs | **ARTIFACT_TAG_ONLY** (+ **CONFIG_INTENDED_ONLY** at the commit that first stored each final AUC). Epochs/batch of the 0.84 runs are **NOT EXECUTION_VERIFIED** |
| Stale-log strength | **EXECUTION_VERIFIED** for epochs=30 on the *early* 0.71 runs only |

### 4. `simplekt30` (S22 preferred reference)

| Item | Evidence |
|---|---|
| Commit | `004691d3` “run simpleKT 30 epochs on 9 folds…” added cache JSONs |
| JSON fields | AUC etc.; **no epochs/batch** |
| Working tree | Files **deleted** in `85afe0c8` (still recoverable from git) |
| Logs | **ABSENT** |
| Strength | **ARTIFACT_TAG_ONLY** (tag + commit message). Executed epochs/batch **NOT VERIFIED** |

### 5. `trio_matched`

| Item | Evidence |
|---|---|
| Rows | Only in `q1_baseline_fold_results.csv` |
| Folders / logs | **No** `results/q1/trio_matched_*`; **no** logs |
| Config intent @Phase3 | `xes3g5m_primary_trio_matched.yaml`: `pykt.epochs: 30`, `pykt.batch_size: 32`; shell string “30ep” |
| AUC vs simplekt30 | Identical on shared folds |
| Strength | **ARTIFACT_TAG_ONLY** / **CONFIG_INTENDED_ONLY**; not a separately verified execution |

---

## Targeted checks (item 5)

| Claim | Verdict |
|---|---|
| GKT batch **16** in S15 | Regenerated table from YAML when batch was 16 (`a288d4a0`). **Not** proven as primary-run batch. Primary AUC commit had batch **4**. |
| GKT batch **8** in current YAML | Post-hoc workspace state (`955a8202`). **Not** evidence for S15/S16/S21 AUCs. |
| simpleKT **10** in prose | **NOT VERIFIED**; contradicted by historical + current configs (30). |
| simpleKT **30** in configs/tables | **CONFIG_INTENDED_ONLY** (primary/S15/tags); execution **NOT VERIFIED**. |

---

## Classification legend (applied)

| Label | Meaning here |
|---|---|
| `EXECUTION_VERIFIED` | Log (or equivalent) shows the hyperparameter for the **same** AUC artifact |
| `CONFIG_INTENDED_ONLY` | Historical config blob at the commit that introduced the AUC |
| `ARTIFACT_TAG_ONLY` | Tag/filename/commit message without hp in payload or matching log |
| `NOT VERIFIED` | No admissible evidence |

**No paper S15–S22 AUC row reaches `EXECUTION_VERIFIED` for both epochs and batch.**

---

## Implications (no auto-correction)

1. Do **not** “fix” S15 GKT batch to 8 because HEAD YAML says 8.
2. Do **not** treat S15 batch 16 as proven execution for primary GKT.
3. Strongest historical pointer for primary GKT batch is **4** (config@`619c02cf` + `training_parity.csv`), still only `CONFIG_INTENDED_ONLY`.
4. GKT30 paper runs: seed42 likely intended batch **16**; later seeds intended **32** — mixed; needs logged reruns to certify.
5. F-R01 prose “simpleKT @ 10” remains unsupported after provenance recovery.

