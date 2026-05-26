# reproduction_log.md — P0 baseline & protocol reproduction

| Field | Value |
|-------|--------|
| **NCS** | Dao Minh Tuan |
| **Repository** | `p0_project` / https://github.com/tuanymc/p0_project.git |
| **Purpose** | Reproduce protocol artefacts + verify pyKT baselines against `reference.txt` |
| **Started** | 2026-05-20 |
| **Last updated** | 2026-05-20 |

---

## 1. Code revisions

| Component | Commit / pin |
|-----------|----------------|
| **p0_project (this repo)** | `de5b8967de1efaed283aa84a4280c9e5de38a154` — *lần 14* (2026-05-20 09:41 +0700) |
| **pykt-toolkit submodule** | `4db3fbe681e2bca3e44ea92863a7168234267b92` (`third_party/pykt-toolkit`) |

```bash
git rev-parse HEAD
git -C third_party/pykt-toolkit rev-parse HEAD
```

---

## 2. Environment

### 2.1 Intended (README)

- Python **3.10 / 3.11** (tested)
- OS: Linux, macOS, Windows (PowerShell + Git Bash for shell scripts)

### 2.2 Recorded on 2026-05-20 (machine that updated this log)

```
Python 3.14.2
networkx==3.6.1
numpy==2.4.0
pandas==2.3.3
scipy==1.16.3
torch==2.12.0
```

> **Action:** For supervisor verify, re-run on Python 3.10/3.11 and append full `pip freeze` below.

<details>
<summary>pip freeze (partial — expand after clean venv)</summary>

```
# TODO: pip install -r requirements.txt && pip install -e ".[pykt]"
# pip freeze > logs/pip_freeze_verify_YYYYMMDD.txt
```

</details>

### 2.3 Install commands

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

git submodule update --init --recursive
pip install -e ".[pykt]"
```

---

## 3. Data provenance

| Dataset | Raw path (config) | In git? | Notes |
|---------|-------------------|---------|-------|
| ASSISTments 2012 | `data/raw/assist2012/2012-2013-data-with-predictions-4-final.csv` | No | Neo for baseline verify |
| Junyi | `data/raw/junyi/junyi_ProblemLog_original.csv` + DAG | No | GT CV optional |
| XES3G5M | per `configs/xes3g5m.yaml` | No | |

**Bundle (optional):** [Google Drive P0 data](https://drive.google.com/drive/folders/1eQNSTV0pVDeB79Mx--vnPml_YPYwVzDP?usp=sharing)

| Field | Value |
|-------|--------|
| Download date | *TODO: YYYY-MM-DD* |
| Who downloaded | *TODO* |
| Checksum / size | *TODO* |

---

## 4. Standard pipeline (per dataset)

Run from **repository root** with venv active.

### 4.1 ASSISTments 2012 (neo — baseline verify)

```bash
# 1. Preprocess
python -m src.preprocess --config configs/assist2012.yaml

# 2. Split audit (must pass)
python -m src.split_checker --config configs/assist2012.yaml

# 3. Train-only graphs (all folds)
python -m src.graph_builder --config configs/assist2012.yaml

# 4. DAG audit + DDR + cold-start (protocol)
python -m src.dag_audit --config configs/assist2012.yaml
python -m src.dag_disruption --config configs/assist2012.yaml
python -m src.cold_start_report --config configs/assist2012.yaml

# 5. Baselines — pyKT backend (VERIFY RUN)
python -m src.baseline_runner --config configs/assist2012.yaml --baseline-backend pykt

# 6. Paper tables
python scripts/generate_paper_artifacts.py
```

**Minimal script:** `bash scripts/run_assist_minimal.sh` (if present and data ready)

**Expected outputs:**

- `results/tables/baseline_fold_results.csv`
- `results/tables/baseline_results.csv`
- `data/processed/assist2012/fold_*/e_pre_train_only.csv`

### 4.2 Full three-benchmark protocol

```bash
./scripts/run_all_datasets_full.sh --server
# Windows: .\scripts\run_all_datasets_full.ps1 -ServerProfile
python scripts/generate_paper_artifacts.py
```

### 4.3 Graph ablation (train-only vs full log)

```bash
./scripts/run_graph_ablation_experiment.sh
# Windows: .\scripts\run_graph_ablation_experiment.ps1 -ServerProfile
```

See `scripts/GRAPH_ABLATION_EXPERIMENT.md`.

---

## 5. Runs logged

| Run ID | Date | Dataset | Command summary | Commit | Status | Artefacts |
|--------|------|---------|-----------------|--------|--------|-----------|
| R0 | 2026-05-20 | multi | Prior development runs (paper v9/v10) | `de5b896` | partial | `results/tables/*.csv` |
| R1 | *TODO* | assist2012 | Full pyKT verify, `n_folds=3`, seed 42–44 | *TODO* | planned | baseline_results.csv |
| R2 | *TODO* | assist2012 | Fill `reference.txt` paper column from pyKT official | *TODO* | planned | reference.txt |

### 5.1 Snapshot — last known NCS metrics (assist2012, pyKT)

From `results/tables/baseline_results.csv` (`status=pykt_checkpoint`, `n_folds=1.0` — **incomplete for final**):

| Model | AUC | ACC | n_eval |
|-------|-----|-----|--------|
| GKT | 0.9603 | 0.9063 | 816951 |
| DKT | 0.9615 | 0.9081 | 816951 |
| AKT | 0.9675 | 0.9144 | 816951 |
| simpleKT | 0.9674 | 0.9147 | 816951 |
| BKT (EM) | 0.6710 | 0.7112 | 816951 |

### 5.2 Snapshot — diagnostic backend (paper main tables)

| Dataset | Backend | Best AUC (simpleKT) | GKT AUC |
|---------|---------|---------------------|---------|
| Junyi | diagnostic | 0.719 | 0.704 |
| ASSISTments | diagnostic | 0.697 | 0.604 |
| XES3G5M | diagnostic | 0.718 | 0.608 |

*Source: `results/tables/baseline_results.tex` / CSV, `graph_construction=train_only`.*

---

## 6. Issues and resolutions

| ID | Issue | Cause | Resolution | Status |
|----|-------|-------|------------|--------|
| I1 | `GIKT` ≠ GIKT paper | pyKT has no GIKT | Map `gikt` → `akt`; document in CSV `note` | accepted limitation |
| I2 | Junyi OOM on full cold-start | Large interaction count | `run_junyi_minimal.sh` uses `--skip-cold-start` for baseline only | documented README |
| I3 | ASSISTments no `e_sim` | 100% single-skill Q-matrix | Expected; report in paper §cold-start | not a bug |
| I4 | NCS AUC >> pyKT AS2009 table | Different dataset (2012 vs 2009) + P0 split/preprocess | Fill assist2012 paper column from pyKT assist2012 benchmark; do not use AS2009 as neo | open |
| I5 | `reference.txt` paper column empty | assist2012 not in NeurIPS 2022 Table 2 | Run pyKT official assist2012 recipe or supervisor sign-off | open |
| I6 | Mixed backends in CSV | Historical runs diagnostic + pykt | Filter `status` column; verify only `pykt_checkpoint` | open |

---

## 7. Verification checklist linkage

| Step | File / evidence |
|------|-----------------|
| Anchor spec | `reference.txt` §A–B |
| Paper vs NCS table | `reference.txt` §D (paper column TODO) |
| Supervisor checklist | `checked.md` |
| Unit tests | `pytest -q` |

**PASS criteria (neo):** After R1, all models in `reference.txt` §D have `|delta_pct| <= 5` on overall AUC (cold-start ≤15%).

---

## 8. Next actions (NCS)

1. [ ] Clean venv Python 3.11 + full `pip freeze` → `logs/pip_freeze_verify.txt`
2. [ ] Run R1: `baseline_runner` assist2012, 3 folds, pykt backend
3. [ ] Obtain assist2012 GKT/DKT/AKT/simpleKT AUC from pyKT official benchmark → update `reference.txt` §D
4. [ ] Compute delta_pct; if FAIL, one controlled fix (document in §6) and re-run R1
5. [ ] Update `checked.md` decision to PASS or THẢO LUẬN

---

*End of log — append new runs at §5 (new rows), never delete history.*
