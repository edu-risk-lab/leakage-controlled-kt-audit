# Báo cáo Hyperparameters GKT theo từng Run — Review nội bộ

| Trường | Giá trị |
|--------|---------|
| **Máy lập báo cáo** | **Server A** (máy trạm — repo local hiện tại) |
| **Đối tác** | Server B (máy chủ GPU) |
| **Ngày rà soát** | 2026-07-22 |
| **Phạm vi** | Toàn bộ run GKT đã publish hoặc có artifact trong repo |
| **Mục đích** | Gửi review — xác nhận hyperparams **đã cấu hình lúc chạy**, phân công Server A/B, và các điểm cần đính chính |

---

## 1. Tóm tắt cho reviewer

Pipeline đọc hyperparams theo thứ tự ưu tiên:

1. `configs/<dataset>.yaml` → `baselines[name=gkt].hyperparams` (override)
2. Fallback: `configs/<dataset>.yaml` → `pykt.*`
3. Fallback code (`src/pykt_engine.py`): kiến trúc GKT mặc định pyKT

**Lưu ý quan trọng:** `result.json` / checkpoint `.ckpt` **không ghi** `batch_size`. Báo cáo này suy ra batch/epoch từ **git commit tại thời điểm chạy**, log (`logs/q1/`), và khớp AUC với CSV publish.

| Batch đã chạy (attested) | Số nhóm run publish | Ghi chú |
|--------------------------|---------------------|---------|
| **4** | Primary XES 10ep; DDR XES seed 42 | Commit `619c02cf` / `91b2fee` |
| **32** | ASSIST/synthetic 10ep; GKT epoch-matched 30ep (9 folds); DDR ASSIST | Cache + log + yaml `gkt_epochs30` |
| **8** | DDR multiseed XES (seed 17, 1234) — Jul 2026 | Config `955a820+`; ckpt còn trên Server A |
| **16** | Run sớm GKT-30ep (đã **loại**) | AUC ~0.71; không dùng trong paper cuối |
| **8 (config only)** | Chưa publish | `xes3g5m.yaml` HEAD — **không** phản ánh run paper |

---

## 2. Hyperparams mặc định GKT (pyKT branch)

Áp dụng khi yaml **không** ghi đè:

| Tham số | Giá trị mặc định | Nguồn code |
|---------|------------------|------------|
| `hidden_dim` | 100 | `src/pykt_engine.py` |
| `emb_size` | 100 (= hidden_dim) | idem |
| `dropout` | 0.5 | idem |
| `lr` | 0.001 | `pykt.lr` trong config |
| `patience` (early stopping) | 3 | idem |
| `selection_metric` | Valid AUC (best ckpt) | idem |
| `graph_input` | `E_pre` + `E_sim` | graph builder P0 |
| `gkt_graph_tag` | `p0_protocol` | `pykt.gkt_graph_tag` |
| `codebase` | pyKT stock `gkt` | `baseline_backend: pykt` |
| `max_degree` | Theo paper GKT gốc / pyKT | không đổi trong P0 |

---

## 3. Bảng tổng hợp — mọi Run GKT

### 3.1 Baseline chính (Table S16 / `baseline_fold_results.csv`)

| Run ID | Mục đích | Config file | Dataset | Epochs | Batch | LR | hidden/emb | max_seq_len | Split seeds | Folds | Graph | Server | Bằng chứng |
|--------|----------|-------------|---------|--------|-------|-----|------------|-------------|-------------|-------|-------|--------|------------|
| **GKT-P01** | Primary release | `configs/xes3g5m.yaml` @ `619c02cf` | XES3G5M | **10** | **4** | 0.001 | 100 / 100 | 200 | 42→42,43,44 | 3 | train_only | A hoặc B† | AUC 0.8336 mean; `training_parity.csv` |
| **GKT-P02** | Cross-dataset baseline | `configs/assist2012.yaml` @ `de5b896` | ASSIST2012 | **10** | **32** | 0.001 | 100 / 100 | 200 | 42 | 3 | train_only + full_log | **A**‡ | `results/cache/assist2012_fold_*_gkt_*` (May 19–25) |
| **GKT-P03** | Synthetic sanity | `configs/synthetic_c2.yaml` @ `e18dca7` | synthetic_c2 | **10** | **32** | 0.001 | 100 / 100 | 200 | 42 | 3 | train_only + full_log | **A**‡ | cache May 19 |
| **GKT-P04** | Synthetic sanity | `configs/synthetic_c5.yaml` @ `e18dca7` | synthetic_c5 | **10** | **32** | 0.001 | 100 / 100 | 200 | 42 | 3 | train_only + full_log | **A**‡ | cache May 19 |

† Primary XES: không còn ckpt/cache GKT trên Server A; provenance git `619c02cf`.  
‡ Cache GKT ASSIST/synthetic hiện có trên Server A.

**Mean AUC publish (train_only):**

| Run | Fold 0 | Fold 1 | Fold 2 | Mean |
|-----|--------|--------|--------|------|
| GKT-P01 XES | 0.8346 | 0.8338 | 0.8326 | **0.8336** |
| GKT-P02 ASSIST | 0.9603 | 0.9610 | 0.9617 | **0.9610** |

---

### 3.2 Epoch-matched ablation (Table S21–S22 / `q1_baseline_fold_results.csv`)

| Run ID | Tag CSV | Config file | Split base seed | Epochs | Batch | LR | hidden/emb | max_seq_len | Folds | Server | Bằng chứng |
|--------|---------|-------------|-----------------|--------|-------|-----|------------|-------------|-------|--------|------------|
| **GKT-E17** | `gkt_epochs30_s17` | `configs/xes3g5m_gkt_epochs30.yaml` | 17 | **30** | **32** | 0.001 | **64 / 64** | **100** | 3 | **A** | `logs/q1/gkt_epochs30_s17.log`; ckpt đã xóa |
| **GKT-E42** | `gkt_epochs30_s42` | idem @ `0982891+` | 42 | **30** | **32** | 0.001 | **64 / 64** | **100** | 3 | **A** | `logs/q1/gkt_epochs30_s42.log` |
| **GKT-E1234** | `gkt_epochs30_s1234` | idem | 1234 | **30** | **32** | 0.001 | **64 / 64** | **100** | 3 | **A** | `logs/q1/gkt_epochs30_s1234.log` |

**Run đã loại (không publish):**

| Run ID | Batch | AUC mean | Lý do loại |
|--------|-------|----------|------------|
| GKT-E17-early | 16 | ~0.712 | OOM / graph chưa rebuild; thay bằng GKT-E17 @ batch 32 |
| GKT-E1234-early | 16 | ~0.710 | idem; rerun → AUC ~0.836 |

**Mean AUC publish (9 folds pooled Δ vs simpleKT ≈ −0.038):**

| Tag | Fold AUC (0,1,2) | Mean |
|-----|------------------|------|
| GKT-E17 | 0.8422, 0.8435, 0.8448 | 0.8435 |
| GKT-E42 | 0.8402, 0.8383, 0.8328 | 0.8371 |
| GKT-E1234 | 0.8357, 0.8341, 0.8397 | 0.8365 |

---

### 3.3 DDR → downstream GKT (`ddr_downstream.csv` + `results/q1/ddr_downstream_gkt/`)

Script: `scripts/ddr_downstream.py` hoặc `scripts/run_ddr_downstream_gkt_multiseed.ps1`  
Đọc HP từ `baselines[gkt].hyperparams` của config được truyền vào.

| Run ID | Config @ thời điểm chạy | Dataset | Exp seed | Epochs | Batch | Operators × p | Runs | Server | Artifact Server A |
|--------|-------------------------|---------|----------|--------|-------|---------------|------|--------|-------------------|
| **GKT-D42-XES** | `xes3g5m.yaml` @ `91b2fee` | XES3G5M | 42 | 10 | **4** | none + 3×(edge/node/prereq)×(0.1,0.2,0.3) | 36 | B† | Không còn ckpt (Jun 2026) |
| **GKT-D42-ASSIST** | `assist2012.yaml` | ASSIST2012 | 42 | 10 | **32** | idem | 36 | **A** | 4 ckpt Jul 2–3 |
| **GKT-D17-XES** | `xes3g5m.yaml` @ `955a820+` | XES3G5M | 17 | 10 | **8** | grid + anchor p=0.9 | 36+ | **A** | 11 ckpt Jul 9–12 |
| **GKT-D1234-XES** | idem | XES3G5M | 1234 | 10 | **8** | grid + anchor p=0.9 | 36+ | A + B§ | 7 ckpt Jul 9–16 trên A |
| **GKT-D1234-P2** | `xes3g5m.yaml` (Part 2) | XES3G5M | 1234 | 10 | **4**¶ | node_drop/prereq_preserve + anchor 0.9 | partial | **A + B** | CSV `part2.csv`; xem §4 |

† DDR seed 42 XES chạy ~Jun 2026 trước khi config đổi batch 8.  
§ Phân công Fold 2 → Server B (xem §4).  
¶ Theo audit git `619c02cf` cho primary; **cần xác nhận** với Server B nếu Part 2 chạy sau `955a820` (có thể là batch 8).

**Hyperparams bổ sung cho mọi run DDR:**

| Tham số | Giá trị |
|---------|---------|
| `perturb_seed` | = `experiment_seed` (42 / 17 / 1234) |
| `fit_seed` | `experiment_seed + fold × 97` |
| `graph_tag` (ckpt) | `{operator}_{p:.2f}_seed{experiment_seed}` |
| `lr` | 0.001 |
| `hidden/emb/dropout` | 100 / 100 / 0.5 (default pyKT) |
| `max_seq_len` | 200 (XES), 200 (ASSIST) |

---

## 4. Phân công Server A / Server B

Theo `Training_Configuration.md` (DDR Downstream GKT — Seed 1234 Part 2):

| Server | Vai trò | Fold / nhiệm vụ |
|--------|---------|-----------------|
| **Server A** (máy trạm) | Chạy chính | Fold **0**, Fold **1**; hỗ trợ thêm `node_drop p=0.9` Fold **2** |
| **Server B** (máy chủ) | Chạy chính | Fold **2** (các cấu hình còn lại) |
| **Đồng bộ** | Git | `results/q1/ddr_downstream_gkt/ddr_downstream_gkt_seed1234_part2.csv` |

**Artifact xác nhận trên Server A (audit 2026-07-22):**

| Loại | Đường dẫn | Ghi chú |
|------|-----------|---------|
| Log Q1 GKT-30ep | `logs/q1/gkt_epochs30_s{17,42,1234}.log` | Config `xes3g5m_gkt_epochs30.yaml` |
| Kết quả Q1 | `results/q1/gkt_epochs30_s*/baseline_fold_results.csv` | 9 folds |
| DDR multiseed CSV | `results/q1/ddr_downstream_gkt/*.csv` | seed 17, 42, 1234 |
| Checkpoint DDR XES | `results/pykt_work/xes3g5m/fold_*_seed_{17,1234,1235,1236}/ddr_downstream/gkt/*.ckpt` | **50 file** (Jul 2026) |
| Checkpoint DDR ASSIST | `results/pykt_work/assist2012/.../ddr_downstream/gkt/*.ckpt` | **4 file** |
| Cache baseline | `results/cache/*_gkt_*_result.json` | ASSIST + synthetic (18 file); **không** có XES GKT |

**Không có trên Server A:** ckpt GKT primary XES (`train_only/gkt_p0_protocol_best.ckpt`); ckpt DDR XES seed 42 (Jun 2026).

---

## 5. Chi tiết cấu hình yaml (tham chiếu)

### 5.1 Primary — `configs/xes3g5m.yaml`

| Trường | **Đã chạy (attested)** | **File hiện tại (HEAD)** |
|--------|------------------------|---------------------------|
| `baselines[gkt].batch_size` | **4** @ `619c02cf` | **8** ⚠️ |
| `baselines[gkt].epochs` | **10** | 10 |
| `pykt.lr` | 0.001 | 0.001 |
| `pykt.max_seq_len` | 200 | 200 |
| `pykt.batch_size` (fallback) | 64 (không dùng vì có override GKT) | 64 |

### 5.2 Epoch-matched — `configs/xes3g5m_gkt_epochs30.yaml`

| Trường | Giá trị publish |
|--------|-----------------|
| `baselines[gkt].batch_size` | **32** |
| `baselines[gkt].epochs` | **30** |
| `baselines[gkt].hidden_dim` | **64** |
| `baselines[gkt].emb_size` | **64** |
| `pykt.max_seq_len` | **100** |
| `pykt.lr` | 0.001 |
| `graph_ablation.enabled` | false |

### 5.3 ASSIST2012 — `configs/assist2012.yaml`

| Trường | Giá trị |
|--------|---------|
| `baselines[gkt].batch_size` | **32** |
| `baselines[gkt].epochs` | **10** |
| `pykt.max_seq_len` | 200 |
| `pykt.lr` | 0.001 |

---

## 6. Ma trận Run × Hyperparameter (compact)

| Run ID | Server | Config | ep | bs | lr | hid | emb | seq | split seed(s) |
|--------|--------|--------|----|----|----|-----|-----|-----|---------------|
| GKT-P01 | A/B | xes3g5m.yaml | 10 | **4** | 1e-3 | 100 | 100 | 200 | 42 |
| GKT-P02 | A | assist2012.yaml | 10 | **32** | 1e-3 | 100 | 100 | 200 | 42 |
| GKT-P03/04 | A | synthetic_*.yaml | 10 | **32** | 1e-3 | 100 | 100 | 200 | 42 |
| GKT-E17 | A | gkt_epochs30.yaml | 30 | **32** | 1e-3 | 64 | 64 | 100 | 17 |
| GKT-E42 | A | gkt_epochs30.yaml | 30 | **32** | 1e-3 | 64 | 64 | 100 | 42 |
| GKT-E1234 | A | gkt_epochs30.yaml | 30 | **32** | 1e-3 | 64 | 64 | 100 | 1234 |
| GKT-D42-XES | B | xes3g5m.yaml | 10 | **4** | 1e-3 | 100 | 100 | 200 | 42 |
| GKT-D42-ASSIST | A | assist2012.yaml | 10 | **32** | 1e-3 | 100 | 100 | 200 | 42 |
| GKT-D17-XES | A | xes3g5m.yaml | 10 | **8** | 1e-3 | 100 | 100 | 200 | 17 |
| GKT-D1234-XES | A+B | xes3g5m.yaml | 10 | **8**† | 1e-3 | 100 | 100 | 200 | 1234 |
| GKT-D1234-P2 | A+B | xes3g5m.yaml | 10 | **4**‡ | 1e-3 | 100 | 100 | 200 | 1234 |

† Config `955a820` (2026-06-24) đổi batch 4→8; run Jul 2026 trên Server A khớp batch **8**.  
‡ Part 2 ghi batch 4 trong `Training_Configuration.md` — **reviewer cần xác nhận** với log Server B.

---

## 7. Các điểm cần review / hành động

### 7.1 Đính chính tài liệu

| Tài liệu | Nội dung sai/lệch | Giá trị attested |
|----------|-------------------|------------------|
| `docs/DDR_DOWNSTREAM_GKT.md` | XES batch **16** | Primary/D42: **4**; multiseed Jul: **8** |
| `scripts/generate_gkt_epoch_ablation.py` (Table S21) | Primary GKT batch **16** | Primary: **4** |
| `configs/xes3g5m.yaml` HEAD | batch **8** | Paper primary: **4** |
| `Training_Configuration.md` Part 2 | batch **4** | Khớp primary; **xác nhận** nếu Part 2 chạy sau Jun 24 |

### 7.2 Bất thường dữ liệu

- **DDR seed 17, fold 0, operator=none** có AUC **trùng tuyệt đối** với `gkt_epochs30_s17` fold 0 (`0.8422173236026003`) dù khác epoch (10 vs 30). Reviewer nên xác minh không có merge CSV nhầm.

### 7.3 Đề xuất cải thiện pipeline

1. Ghi `batch_size`, `epochs`, `config_path`, `git_sha` vào mỗi `*_result.json`.
2. Không dùng `configs/xes3g5m.yaml` HEAD để rerun mà không chỉnh batch về **4** (primary) hoặc **32** (ablation).
3. Server B cung cấp mirror checklist: ckpt/log còn thiếu trên A (primary XES, DDR seed 42 XES).

---

## 8. Phụ lục — Git provenance chính

| Commit | Ngày | Sự kiện | GKT batch (XES) |
|--------|------|---------|-----------------|
| `619c02cf` | trước May 2026 | Primary baseline publish | **4** |
| `de5b896` | 2026-05-20 | ASSIST/synthetic cache | **4** (XES), **32** (ASSIST) |
| `91b2fee` | 2026-06-03 | DDR XES seed 42 | **4** |
| `d9efa27` | 2026-06-16 | GKT-30ep phase 2 (sớm) | **16→32** |
| `fcb1463` | 2026-06-16 | Đặt batch 32 cho gkt_epochs30 | ablation **32** |
| `955a820` | 2026-06-24 | DDR multiseed script | xes primary yaml → **8** |
| `85afe0c` | 2026-06-17+ | Sync Q1 9-fold cuối | ablation **32** |
| `1f457ab` | 2026-07-07 | DDR multiseed hoàn tất | **8** (XES Jul runs) |

---

## 9. Xác nhận reviewer

| Hạng mục | Server A | Server B | Ngày |
|----------|----------|----------|------|
| Primary XES batch=4, 10ep | ☐ | ☐ | |
| GKT-30ep batch=32, 9 folds | ☐ | ☐ | |
| DDR seed 42 XES batch=4 | ☐ | ☐ | |
| DDR multiseed XES batch=8 | ☐ | ☐ | |
| DDR ASSIST batch=32 | ☐ | ☐ | |
| Phân công fold Part 2 (§4) | ☐ | ☐ | |

**Người lập báo cáo (Server A):** ___________________  
**Reviewer / Server B:** ___________________

---

*Báo cáo được tạo tự động từ audit artifact local Server A + git history. File cấu hình hiện tại có thể khác giá trị đã chạy — luôn ưu tiên cột "attested" trong bảng trên.*
