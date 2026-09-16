# M4 Phase B trên GPU server

Phase A (census đồ thị) đã chạy trên máy CPU. Server GPU chỉ cần **rebuild đồ thị cô lập** rồi **train GKT** train-only vs full-log. Không ghi đè `data/processed/xes3g5m/fold_*` hay `results/tables/graph_ablation*.csv`.

Nhánh: `feat/m4-qk-sweep`.

---

## 1. Kéo code

```bash
cd /path/to/leakage-controlled-kt-audit
git fetch origin
git checkout feat/m4-qk-sweep
git pull origin feat/m4-qk-sweep

# Nếu repo mới:
# git clone https://github.com/edu-risk-lab/leakage-controlled-kt-audit.git
# cd leakage-controlled-kt-audit
# git checkout feat/m4-qk-sweep
# git submodule update --init --recursive
```

Môi trường (như `docs/Q1_GPU_EXPERIMENTS.md`):

```bash
source .venv/bin/activate   # hoặc tạo mới: python -m venv .venv
pip install -r requirements.txt
pip install -e .
pip install -e ".[pykt]"
python -c "import torch; print(torch.cuda.get_device_name(0), torch.cuda.is_available())"
```

Bắt buộc có `data/processed/xes3g5m.parquet`. Đồ thị `m4/` **không** nằm trên git (`data/processed/**` bị ignore) — phải chạy Phase A trên server.

---

## 2. Phase A trên server (CPU, ~10–20 phút)

Tái tạo 16 ô × 3 fold vào `data/processed/xes3g5m/m4/` và `results/m4/`.

```bash
python scripts/run_m4_qk_sweep.py --phase a --log-level INFO
```

Chỉ fold 0 nếu muốn Phase B sanity trước:

```bash
python scripts/run_m4_qk_sweep.py --phase a --fold-idx 0
```

Kiểm tra:

```bash
test -f data/processed/xes3g5m/m4/q0.95_k5_K5000_tau0.1/fold_0/e_pre_train_only.csv
python scripts/run_m4_qk_sweep.py --phase b --cells default --dry-run
```

---

## 3. Phase B — GKT (10 epoch / batch 4, ngân sách primary)

`tmux` hoặc `screen`. Mỗi ô: train-only + full-log, cache/`pykt_work` dưới `results/q1/m4_<tag>/`.

### 3.1 Ô default trước (sanity, ~4–8 giờ / 1× 3090)

Kỳ vọng ΔAUC gần **+0.002** như bảng ablation đã nộp.

```bash
python scripts/run_m4_qk_sweep.py --phase b --cells default --fold-idx 0
```

Xong: `results/q1/m4_q0.95_k5_K5000_tau0.1/baseline_fold_results.csv`

### 3.2 Tám ô recommended (fold 0)

Chạy **sau** khi default khớp. Ước lượng **1–2 ngày** nếu không gộp thêm.

```bash
python scripts/run_m4_qk_sweep.py --phase b --cells recommended --fold-idx 0
```

Thứ tự trong `results/m4/phase_b_jobs.json`:

1. `q0.95_k5_K5000_tau0.1` — published default  
2. `q0.95_k5_K1000_tau0.1` — `K` binds  
3. `q0.8_k5_K5000_tau0.1` — mid `q`  
4. `q0.5_k5_Kinf_tau0.1` — góc review (`k` vẫn bind)  
5. `q0.5_k20_Kinf_tau0.1` — **mở kênh**  
6. `q0.5_kinf_Kinf_tau0.1` — **mở mạnh**  
7. `q0.95_k5_K5000_tau0.05` — τ  
8. `q0.95_k5_K5000_tau0.2` — τ  

Một ô lẻ:

```bash
python scripts/run_m4_qk_sweep.py --phase b --cells q0.5_k20_Kinf_tau0.1 --fold-idx 0
```

### 3.3 Ba fold (chỉ sau khi fold 0 của ô mở nhất xong)

```bash
python scripts/run_m4_qk_sweep.py --phase b --cells default --fold-idx -1
```

`--fold-idx -1` = không giới hạn fold (cả 3). Chỉ dùng cho landmark: default, mid, góc mở / `k`-lift nếu `|ΔAUC|` vượt 0.003.

### 3.4 Bản lặp σ (bắt buộc; seed huấn luyện khác, split giữ nguyên)

Ô `q0.95_k5_Kinf_tau0.1` (seed 42) đã trùng bit với mặc định `K=5000`. Đó xác nhận
đồ thị giống nhau và huấn luyện **cùng seed** là xác định; **không** đo được `σ`.
`σ` cần cùng đồ thị, cùng learner split, **khác experiment seed**. Kết quả ghi vào
`results/q1/m4_q0.95_k5_K5000_tau0.1_seed17/` — không đè ô seed 42.

```bash
python scripts/run_m4_qk_sweep.py --phase b --cells default --fold-idx 0 \
  --seed 17 --split-base-seed 42
```

Kỳ vọng: `|AUC_seed17 − AUC_seed42|` trên từng nhánh (train-only và full-log) là
một quan sát của sàn nhiễu. Không đổi `--graph-root`; không `--clear-cache` trên
ô seed 42.

---

## 4. An toàn

| Được | Không được |
|---|---|
| `--graph-root data/processed/xes3g5m/m4/<tag>` | Ghi vào `fold_0/e_pre_train_only.csv` primary |
| `--isolated-results m4_<tag>` | `--clear-cache` trên `results/cache/` dùng chung |
| Overlay `results/m4/overlays/<tag>.yaml` | Sửa `configs/xes3g5m.yaml` |

Nếu cache primary bị đụng: **dừng**, không `--clear-cache` toàn cục. Phase B chỉ xóa `results/q1/m4_*/cache` khi bạn truyền `--clear-cache` cùng `--isolated-results`.

---

## 5. Lấy kết quả về máy viết bài

```bash
# trên máy local
rsync -avz USER@GPU:PATH/leakage-controlled-kt-audit/results/q1/m4_ ./results/q1/
rsync -avz USER@GPU:PATH/leakage-controlled-kt-audit/results/m4/builder_census.csv ./results/m4/
```

Cột cần: `auc`, `graph_construction` (`train_only` / `full_log`), `fold`, `model=gkt`.  
ΔAUC = AUC(full-log) − AUC(train-only).

---

## 6. Nếu OOM

GKT primary là batch **4**, 10 epoch — không đổi sang 32/30 (đó là C5, đã gác). OOM: `--fold-idx 0` từng ô; không tăng batch. Junyi GKT không chạy.
