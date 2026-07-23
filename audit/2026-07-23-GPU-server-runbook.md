# GPU server runbook — pending revision jobs (2026-07-23)

## Chuẩn bị server

```bash
git clone https://github.com/tuanymc/p0_project.git
cd p0_project
git pull origin main

python -m venv .venv
source .venv/bin/activate   # Linux
# .\.venv\Scripts\Activate.ps1   # Windows

pip install -U pip
pip install -r requirements.txt
pip install -e .
pip install -e ".[pykt]"
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Dữ liệu: data/processed/xes3g5m.parquet + raw DAG (README §3)
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

---

## Job ưu tiên: A2.2b — DDR seed-17 baseline rerun

**Vấn đề:** `ddr_downstream_gkt_seed17.csv` fold-0 `operator=none` có AUC **0.842217…** — placeholder copy từ GKT30 (`eval_existing.py`, đã xóa).

**Mục tiêu:** 1 GPU run GKT 10ep, batch **8**, fold 0, split seed 17, graph unperturbed.

| Tham số | Giá trị |
|---------|---------|
| Config graph | `configs/xes3g5m_split17.yaml` (rebuild) |
| Config train | `configs/xes3g5m.yaml` + `--batch-size 8` |
| Output shard | `results/q1/ddr_downstream_gkt/ddr_downstream_gkt_seed17.csv` |
| Thời gian ước lượng | ~30–90 min (1 fold, 1 variant) |

### Chạy (Linux)

```bash
chmod +x scripts/run_a2_2b_ddr_seed17_baseline.sh scripts/run_gpu_server_pending.sh

# Khuyến nghị overnight:
nohup bash scripts/run_a2_2b_ddr_seed17_baseline.sh \
  > logs/q1/nohup_a2_2b.log 2>&1 &
tail -f logs/q1/nohup_a2_2b.log
```

### Chạy (Windows Server A/B)

```powershell
.\scripts\run_a2_2b_ddr_seed17_baseline.ps1
```

### Flags

| Flag | Ý nghĩa |
|------|---------|
| `--dry-run` | In lệnh, không train |
| `--skip-graph-rebuild` | Bỏ `graph_builder` nếu graph seed-17 đã có |
| `--merge-only` | Chỉ merge CSV → `results/tables/ddr_downstream.csv` + regenerate tex |

### Sau khi xong

```bash
python -m scripts.crossref_auc_numbers   # CPU sanity (optional)

# Commit trên server hoặc scp về dev:
git add results/q1/ddr_downstream_gkt/ddr_downstream_gkt_seed17.csv
git add results/tables/ddr_downstream.csv results/tables/ddr_downstream*.tex
git commit -m "fix: rerun DDR GKT seed-17 fold-0 baseline (A2.2b)"
git push origin HEAD
```

**Pass criteria:** fold-0 none AUC **≠** 0.8422173236026003; thường ~0.82–0.84 (thấp hơn các operator perturbed fold-0 nếu placeholder đã làm lệch baseline).

---

## Job phụ: Injection Table S18 (nếu cache thiếu)

Server A đã chạy 2026-07-23. Chỉ rerun nếu thiếu cache:

```bash
bash scripts/run_injection_downstream_batch.sh --collect-only   # nếu đủ cache
bash scripts/run_injection_downstream_batch.sh                  # full 6 GPU jobs
```

Runbook chi tiết: `audit/2026-07-22-A1-injection-rerun-runbook.md`

---

## Dispatcher

```bash
bash scripts/run_gpu_server_pending.sh help
bash scripts/run_gpu_server_pending.sh a2_2b
bash scripts/run_gpu_server_pending.sh all
```

---

## Sync về máy dev

```bash
# Trên dev sau khi pull:
python -m scripts.merge_ddr_downstream \
  --base results/tables/ddr_downstream.csv \
  --append results/q1/ddr_downstream_gkt/ddr_downstream_gkt_seed17.csv

python -m scripts.plot_ddr_downstream
python -m scripts.generate_ddr_downstream_gkt_tex
python -m scripts.generate_phase_c_tables.py

Copy-Item results/tables/ddr_downstream*.tex paper/submission_APIN/
```

---

## A3.5 — Cold-start rerun (optional GPU)

**Mục tiêu:** Rerun cold-start strata với **full predictions** (không cap 5000); pyKT backend + `kc_id` cho per-stratum AUC.

**Script:** `scripts/run_a3_cold_start_rerun.sh` (Linux) / `run_a3_cold_start_rerun.ps1` (Windows)

```bash
# Junyi only (default — artefact very_cold)
bash scripts/run_a3_cold_start_rerun.sh

# Hoặc qua dispatcher
bash scripts/run_gpu_server_pending.sh a3_coldstart

# Debug fold 0
bash scripts/run_a3_cold_start_rerun.sh --fold-idx 0

# Tất cả dataset (nặng — Junyi ~ nhiều giờ GPU)
bash scripts/run_a3_cold_start_rerun.sh --dataset all
```

**Flags pipeline:** `--cold-start-only --force-cold-start` → chỉ cập nhật `cold_start_metrics.csv`, không đụng `baseline_results.csv`.

**Sau khi chạy:** sync `results/tables/cold_start_*` → `paper/submission_APIN/`; kiểm tra verify in cuối log (very_cold không còn AUC trùng mọi model khi n_discordant ≥ 10).

---

## Không chạy trên GPU (đã xong / CPU only)

| Mục | Trạng thái |
|-----|------------|
| A1 injection S18 | ✅ Server A verified 2026-07-23 |
| A1.3 crossref | ✅ `scripts/crossref_auc_numbers.py` |
| A3 Junyi very_cold | ✅ Suppress `---` trong bảng; **A3.5 optional GPU**: `bash scripts/run_a3_cold_start_rerun.sh` |
