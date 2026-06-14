# Kịch bản thí nghiệm Q1 trên GPU server (24GB VRAM)

Tài liệu này mô tả **thứ tự chạy**, **ước lượng thời gian**, và **cách lấy kết quả** cho revision C5 + multi-seed. Mọi run Q1 ghi vào `results/q1/<tag>/` — **không ghi đè** `results/tables/baseline_fold_results.csv` hiện tại.

---

## 0. Chuẩn bị server

```bash
git clone https://github.com/tuanymc/p0_project.git
cd p0_project
git submodule update --init --recursive

python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
pip install -e ".[pykt]"
# PyTorch CUDA — chọn build phù hợp driver, ví dụ cu121:
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Dữ liệu: tải bundle Google Drive (README §3) hoặc copy parquet + raw
# Bắt buộc: data/processed/xes3g5m.parquet
# Khuyến nghị: data/raw/xes3g5m/ (ground-truth DAG cho E_pre)
```

Kiểm tra GPU:

```bash
python -c "import torch; print(torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory/1e9)"
```

**24GB VRAM:** đủ cho GKT XES3G5M batch 64 (epochs30 config). Nếu OOM → sửa tạm `batch_size: 32` trong `configs/xes3g5m_gkt_epochs30.yaml`.

---

## 1. Ba phase thí nghiệm

| Phase | Mục tiêu | Config | Split seeds | Runs GKT | Thời gian ước lượng* |
|-------|----------|--------|-------------|----------|----------------------|
| **1** | **C5 core** — GKT epoch-matched | `configs/xes3g5m_gkt_epochs30.yaml` | 42 | 3 fold | **4–8 h** |
| **2** | Multi-seed inferential | cùng config | 17, 1234 | 6 fold | **+8–16 h** |
| **3** | Primary trio matched | `configs/experiments/xes3g5m_primary_trio_matched.yaml` | 42, 17, 1234 | 9×3 models | **+24–48 h** |

\*Trên GPU tương đương RTX 3090 / A5000 24GB.

### Chạy từng phase (khuyến nghị)

```bash
chmod +x scripts/run_q1_gpu_experiments.sh

# Phase 1 — chạy trước, đủ để cập nhật C5 trong paper
./scripts/run_q1_gpu_experiments.sh phase1

# Xem kết quả sơ bộ
cat results/tables/q1_gkt_vs_simplekt.csv

# Phase 2 — thêm 2 split seeds (chỉ GKT epochs30)
./scripts/run_q1_gpu_experiments.sh phase2

# Phase 3 — optional Q1: cả trio (simpleKT + GKT30 + GIKT) × 3 seeds
./scripts/run_q1_gpu_experiments.sh phase3

# Gộp bảng LaTeX
./scripts/run_q1_gpu_experiments.sh summarize
```

Chạy tất cả (overnight):

```bash
nohup ./scripts/run_q1_gpu_experiments.sh all > logs/q1/nohup.log 2>&1 &
tail -f logs/q1/nohup.log
```

---

## 2. Cấu trúc output

```
results/q1/
  gkt_epochs30_s42/baseline_fold_results.csv   # Phase 1
  gkt_epochs30_s17/...
  gkt_epochs30_s1234/...
  trio_matched_s42/...                           # Phase 3

results/tables/
  q1_baseline_fold_results.csv                 # merged
  q1_gkt_vs_simplekt.csv                       # ΔAUC per tag/seed
  q1_gkt_epochs30_ablation.tex                 # bảng cho paper

logs/q1/
  run.log, gkt_epochs30_s42.log, ...
```

Cột mới trong CSV: `experiment_tag`, `split_base_seed`.

---

## 3. Calibrate một fold (smoke test ~1–2h)

```bash
python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt --dry-run
python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt

python -m src.baseline_runner \
  --config configs/xes3g5m_gkt_epochs30.yaml \
  --split-base-seed 42 \
  --fold-idx 0 \
  --isolated-results gkt_epochs30_s42_fold0_smoke \
  --log-level INFO
```

---

## 4. Sau khi có số — cập nhật paper

1. Mở `results/tables/q1_gkt_vs_simplekt.csv` → lấy `delta_mean` cho tag `gkt_epochs30_s42` (so với baseline cũ −0.041).
2. Nếu gap thu hẹp / giữ nguyên → chỉnh abstract C5 theo kịch bản A/B (đã thảo luận).
3. (Tuỳ chọn) `\input{results/tables/q1_gkt_epochs30_ablation.tex}` vào supplementary.
4. Chạy lại bootstrap nếu merge vào main CSV:

```bash
# Chỉ khi bạn đã quyết định promote Q1 rows vào main tables
python scripts/summarize_q1_experiments.py
# rồi merge thủ công hoặc mở rộng bootstrap_auc_ci.py cho 9 fold
```

---

## 5. Resume / lỗi thường gặp

| Vấn đề | Xử lý |
|--------|--------|
| Run dở giữa chừng | Chạy lại cùng phase; cache GKT được xóa trước mỗi run |
| OOM 24GB | `batch_size: 32` trong yaml GKT; hoặc `--fold-idx N` từng fold |
| Cache cũ 10 epoch | `python scripts/clear_baseline_cache.py --models gkt` |
| Không có CUDA | Script `check_env` sẽ fail sớm |

---

## 6. Lệnh thủ công tương đương (Phase 1)

```bash
python -m src.graph_builder --config configs/xes3g5m.yaml   # nếu thiếu exports
python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt
python -m src.baseline_runner \
  --config configs/xes3g5m_gkt_epochs30.yaml \
  --split-base-seed 42 \
  --isolated-results gkt_epochs30_s42
python scripts/summarize_q1_experiments.py
```

---

## 7. Checklist trước khi push kết quả về máy local

- [ ] `results/q1/*/baseline_fold_results.csv` tồn tại
- [ ] `results/tables/q1_gkt_vs_simplekt.csv` có dòng `gkt_epochs30_s42`
- [ ] `logs/q1/run.log` không có traceback
- [ ] (Phase 3) đủ 3 tag `trio_matched_s*`

Scp về local:

```bash
scp -r user@server:~/p0_project/results/q1 ./results/
scp user@server:~/p0_project/results/tables/q1_* ./results/tables/
```
