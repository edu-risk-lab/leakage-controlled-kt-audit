# Server A — Injection Downstream Audit (Table S18)

**Date:** 2026-07-22  
**Machine:** Server A (workstation)  
**Repo path:** `C:\TUAN\p0_project`  
**Old path from LaTeX logs:** `D:\0. NCS\CODE\p0_project` — **not present** on this machine (`Test-Path` → `False`)

---

## 1. Executive summary

**Server A has never completed real downstream AUC training for the injection experiment (Table S18).** On 2026-06-11 the CPU phase ran: injected prerequisite graphs were written (`e_pre_inject{00,05,20}.csv`) and pyKT sequence export for `inject00` started (`dkt/` CSV/pkl only). No `results/cache/*inject*_result.json` exists on disk anywhere under `C:\TUAN`; git history contains only **mock** simpleKT inject cache files (minimal `{"auc": …}` JSON from `scripts/mock_gkt.py`), committed in `004691d` and **deleted** in `85afe0c`. GKT and GIKT inject cache files were **never** committed. Table S18 in the working tree still holds the original placeholder numbers from `6a0b09fc` / `scripts/create_fake_tables.py`. S17 (`leak_injection.csv`) is real and matches expected edge counts (1162 / 1378 / 1417). Fold-0 train_only baseline AUC for the primary trio is attested in `results/tables/baseline_fold_results.csv` and matches dev machine values.

**Recommendation: B** — GPU rerun required for **6 jobs** (inject05 × 3 models + inject20 × 3 models). Column 0% (clean) can be taken from existing fold-0 `train_only` baselines; optional sanity check whether `inject00` graph (Jun-11 build) differs from current `e_pre_train_only.csv` (Jul-02 rebuild).

---

## 2. Artifacts found

| Path | Type | mtime | AUC / metric | Arm / notes |
|------|------|-------|--------------|-------------|
| `data/processed/xes3g5m/fold_0/e_pre_inject00.csv` | Graph (post-prune edges) | 2026-06-11 14:44 | 701 edges on disk | inject00 / clean injection arm |
| `data/processed/xes3g5m/fold_0/e_pre_inject05.csv` | Graph | 2026-06-11 14:45 | 823 edges | inject05 |
| `data/processed/xes3g5m/fold_0/e_pre_inject20.csv` | Graph | 2026-06-11 14:47 | 850 edges | inject20 |
| `data/processed/xes3g5m/fold_0/e_sim_inject{00,05,20}.csv` | Empty sim stub | 2026-06-11 | 29 B each | inject arms |
| `data/processed/xes3g5m/fold_0/e_pre_train_only.csv` | Baseline graph | 2026-07-02 19:47 | 100747 B (≠ inject00) | **Not** inject arm; newer rebuild |
| `results/pykt_work/xes3g5m/fold_0_seed_42/inject00/dkt/` | pyKT CSV/pkl export | 2026-06-11 14:47 | — | Partial preprocess only; **no** GKT/simpleKT/GIKT ckpt |
| `results/tables/leak_injection.csv` | S17 table | (in git) | \|E_pre\| 1162/1378/1417 | Real graph-leakage metrics |
| `results/tables/baseline_fold_results.csv` | Baseline AUC | (in git) | see §6 | fold 0, seed 42, `train_only` |
| `results/tables/downstream_auc_injection.csv` | S18 table | (in git) | 0.850/0.810/0.852 … | **Placeholder** (fake) |
| Git `004691d` (removed `85afe0c`) | Mock inject cache | commit 2026-06-17 | simpleKT fold0: 0.8820 / 0.8847 / 0.8803 | inject00/05/20; **mock** (`{"auc"}` only) |
| `paper/*.log` | LaTeX build | various | — | References old `D:\0. NCS\CODE\p0_project\results/tables/downstream_auc_injection.tex` |

### Git-recovered mock simpleKT inject AUC (`004691d`, deleted `85afe0c`)

| Fold | inject00 | inject05 | inject20 | Verdict |
|------|----------|----------|----------|---------|
| 0 | 0.8820 | 0.8847 | 0.8803 | Mock (`mock_gkt.py` pattern); not pyKT checkpoint JSON |
| 1 | 0.8523 | 0.8724 | 0.8892 | Mock |
| 2 | 0.8643 | 0.8548 | 0.8541 | Mock |

Full pyKT result JSON would include `acc`, `nll`, `status`, `note`, etc.; these files contain only `{"auc": float}`.

---

## 3. Artifacts NOT found

Patterns searched under `C:\TUAN\p0_project` (recursive) and `C:\TUAN` (limited `rglob`):

| Pattern | Result |
|---------|--------|
| `*inject*_result.json` | **0 files** on disk |
| `*inject*_preds.csv` | **0 files** on disk |
| `*inject*.pt` / `*inject*.pth` | **0 files** |
| `results/cache/xes3g5m_fold_0_{simplekt,gkt,gikt}_s42_inject{05,20}_result.json` | Missing |
| `results/cache/xes3g5m_fold_0_{gkt,gikt,simplekt}_s42_train_only_result.json` | Missing on disk (AUC only in aggregated CSV) |
| GKT/GIKT inject cache in **any** git commit | **Never committed** |
| `scripts/collect_injection_auc.py` | **Does not exist**; collection is `collect_results()` inside `scripts/run_injection_auc.py` |
| Training logs mentioning `inject05`, `inject20`, `run_injection` | **None** in `logs/q1/` or any `*.log` under repo |
| Old repo at `D:\0. NCS\CODE\p0_project` | Path absent |

### `results/cache/` on Server A (xes3g5m)

54 tracked/ignored cache files exist for folds 0–2, but **only** secondary models (akt, bkt, dkt, skt, dygkt, dgekt) with `train_only` / `full_log`. **No** simpleKT, GKT, GIKT, and **no** inject tags.

---

## 4. Log excerpts (most relevant ≤10 lines)

No injection **training** logs exist. Only manuscript build and planning references:

```
# paper/main_APIN.log (build on D:\0. NCS\CODE\p0_project)
(D:\0. NCS\CODE\p0_project\results/tables/leak_injection.tex)
(D:\0. NCS\CODE\p0_project\results/tables/downstream_auc_injection.tex)

# prompt.txt (task spec, not run log)
# R2. Downstream AUC on injected graphs (XES3G5M fold 0)
#   Output: results/tables/leak_injection_auc.csv + .tex

# scripts/create_fake_tables.py (source of S18 placeholders)
{"Model": "simplekt", "Clean AUC": 0.850, "Leak 5% AUC": 0.852, "Leak 20% AUC": 0.858}
{"Model": "gkt",      "Clean AUC": 0.810, "Leak 5% AUC": 0.825, "Leak 20% AUC": 0.860}
{"Model": "gikt",     "Clean AUC": 0.852, "Leak 5% AUC": 0.860, "Leak 20% AUC": 0.880}

# scripts/mock_gkt.py
json.dump({"auc": 0.85 + (np.random.random() * 0.05)}, f)  # skip-training stub
```

`logs/q1/` contains GKT/simpleKT epoch-30 and graph_builder logs (Jun–Jul 2026); **zero** matches for `inject`, `injection`, `inject05`, `inject20`.

---

## 5. Git local state (Server A)

```
Branch: main @ 672ad7b (ahead 1, behind 5 vs origin/main)
```

### History touching inject cache / S18

| Commit | Date | Action |
|--------|------|--------|
| `6a0b09fc` | 2026-06-11 | Added `downstream_auc_injection.csv/.tex` with fixed placeholder AUCs |
| `6eadc24b` | 2026-06-16 | Added `scripts/create_fake_tables.py` (same hard-coded S18 numbers) |
| `004691d` | 2026-06-17 | Committed mock simpleKT inject cache (9 folds×arms, old naming without `s42`) |
| `85afe0c` | later | **Deleted** all 18 simpleKT inject cache files from git |

`git log --all -- results/cache/*inject*`: only `85afe0c`, `004691d` (no gkt/gikt inject ever).

### Stash

7 stashes present; none recoverable inject cache via `git show stash@{N}:...` (exit 128 on Windows). Stash@{4} message references seed-42 DDR work, not injection downstream.

### Untracked / ignored

No inject files under `results/cache/` (ignored or absent). Primary trio XES caches not on disk locally.

---

## 6. Script provenance (mock vs real)

| Script | Role | Real downstream AUC? |
|--------|------|----------------------|
| `scripts/create_fake_tables.py` | Hard-codes S18 + bootstrap CI tables | **No** — explicit placeholders |
| `scripts/mock_gkt.py` | Mock GKT/GIKT parquets + inject cache JSON if missing | **No** — random AUC ≈ 0.85–0.90 |
| `scripts/run_leak_injection.py` | S17 graph/leakage metrics only | N/A (no model training) |
| `scripts/run_injection_auc.py` | Build graphs → `baseline_runner` → `collect_results()` | **Real if GPU runs**; never completed here |
| `scripts/master_run.py` | Lists `run_injection_auc.py` in pipeline | Orchestration only |

No notebook or other script writes S18 except `create_fake_tables.py` and `run_injection_auc.py:collect_results()`.

**Naming note:** Current `baseline_runner` cache path is  
`results/cache/{dataset}_fold_{fold}_{model}_s{split_seed}_{graph_construction}_result.json`  
(e.g. `xes3g5m_fold_0_gkt_s42_inject05_result.json`). Git mock files used old form without `s42`: `xes3g5m_fold_0_simplekt_inject05_result.json`.

**Rerun caveat:** `run_injection_auc.py` does not pass `--models simplekt,gkt,gikt`; default runs **all** enabled baselines per arm. For the 6-job plan, invoke `baseline_runner` with `--models` filter per job.

---

## 7. Number cross-check

### S18 placeholder vs fold-0 train_only (real, Server A = dev)

| Model | Placeholder S18 (0%) | Fold-0 train_only (real) | Δ |
|-------|---------------------|--------------------------|---|
| simpleKT | 0.850 | **0.8744** | +0.024 |
| GKT | 0.810 | **0.8346** | +0.025 |
| GIKT | 0.852 | **0.8776** | +0.026 |

Placeholder **deltas** (manuscript narrative): simpleKT +0.008 @20%, GKT +0.050 @20%, GIKT +0.028 @20% — all unsupported by any real inject run on Server A.

### S17 vs on-disk inject graphs

| Arm | S17 \|E_pre\| (`leak_injection.csv`) | `e_pre_inject*.csv` row count (post-prune) |
|-----|--------------------------------------|---------------------------------------------|
| 0% | 1162 | 701 (inject00) |
| 5% | 1378 | 823 |
| 20% | 1417 | 850 |

S17 counts pre-prune candidate edges (`run_leak_injection.py`); saved CSVs are post-`prune_cycles` (`run_injection_auc.py`). Edge **ratios** across arms are consistent; absolute counts differ by pipeline stage. **`e_pre_train_only.csv` (Jul-02) is a separate, newer graph** and should not be assumed identical to `e_pre_inject00.csv` (Jun-11).

---

## 8. Recommendation

### **B — Insufficient artifacts; GPU rerun required**

**Runbook (canonical, pulled from origin):** [`audit/2026-07-22-A1-injection-rerun-runbook.md`](2026-07-22-A1-injection-rerun-runbook.md)

**Batch script (Server A / Server B):**

```powershell
# Full pipeline: preflight → build graphs → 6 GPU jobs → collect S18
.\scripts\run_injection_downstream_batch.ps1

# Options
.\scripts\run_injection_downstream_batch.ps1 -SkipGraphs -CollectOnly
.\scripts\run_injection_downstream_batch.ps1 -ClearCache   # force retrain inject05/20
```

Linux: `bash scripts/run_injection_downstream_batch.sh` (same flags with `--` prefix).

Collect table only (after sync cache from GPU machine):

```bash
python -m scripts.collect_injection_auc
```

| Job | Model | Graph arm | Cache target |
|-----|-------|-----------|--------------|
| 1 | simpleKT | inject05 | `xes3g5m_fold_0_simplekt_s42_inject05_result.json` |
| 2 | GKT | inject05 | `xes3g5m_fold_0_gkt_s42_inject05_result.json` |
| 3 | GIKT | inject05 | `xes3g5m_fold_0_gikt_s42_inject05_result.json` |
| 4 | simpleKT | inject20 | `…_inject20_result.json` |
| 5 | GKT | inject20 | `…_inject20_result.json` |
| 6 | GIKT | inject20 | `…_inject20_result.json` |

**0% column:** use existing fold-0 `train_only` from `baseline_fold_results.csv` (or rerun inject00 if protocol requires matching Jun-11 graph — recommend **regenerating all inject graphs** with current `configs/xes3g5m.yaml` before training).

**Not option A:** no recoverable real inject downstream cache on Server A (git mocks are invalid).

**Not option C:** evidence is conclusive.

### Suggested rerun commands (after user confirms GPU)

```powershell
# 1) Regenerate graphs (CPU, ~minutes)
python scripts/run_injection_auc.py  # only build_injected_graphs() if split script; or run_leak_injection for S17 refresh

# 2) Per job (example inject05 + GKT)
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt `
  --fold-idx 0 --graph-construction inject05 --models gkt --split-base-seed 42

# 3) Collect table
python -c "from scripts.run_injection_auc import collect_results; collect_results()"
```

---

## 9. GPU time estimate (if B)

From `configs/xes3g5m.yaml` (pyKT backend):

| Model | Epochs | Batch size | Source |
|-------|--------|------------|--------|
| simpleKT | 30 | 64 | `pykt:` global defaults |
| GKT | 10 | 8 | `baselines.gkt.hyperparams` |
| GIKT | 10 | 16 | `baselines.gikt.hyperparams` |

Dataset: XES3G5M fold 0 (~4.49M train interactions, eval ~1.92M positions).

| Job | Rough wall time (single local GPU, RTX-class) |
|-----|-----------------------------------------------|
| simpleKT × inject arm | 25–45 min |
| GKT × inject arm | 20–40 min |
| GIKT × inject arm | 15–30 min |

**6 jobs sequential:** ~2.5–4.5 h  
**3 parallel streams (one model family):** ~1.5–2.5 h  

Preprocessing (pyKT CSV export) adds ~5–10 min per new inject arm if `results/pykt_work/.../inject05` / `inject20` dirs are missing.

---

## 10. Investigation commands run

- File search: `*inject*_result.json`, `*inject*.pt`, graph CSVs, `logs/q1/*.log`
- `git log --all --oneline -- results/cache/*inject* results/tables/downstream_auc_injection.csv`
- `git show 004691d:results/cache/xes3g5m_fold_0_simplekt_inject*_result.json`
- `git diff 004691d..85afe0c -- results/cache/*inject*`
- Read: `create_fake_tables.py`, `mock_gkt.py`, `run_injection_auc.py`, `run_leak_injection.py`, `configs/xes3g5m.yaml`
- `Test-Path D:\0. NCS\CODE\p0_project` → False

---

*Report generated on Server A, 2026-07-22. No files deleted; no GPU jobs launched; no git commit.*
