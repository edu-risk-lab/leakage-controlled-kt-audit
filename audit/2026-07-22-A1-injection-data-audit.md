# A1 — Rà soát dữ liệu injection (Table S17/S18)

**Ngày:** 2026-07-22  
**Phạm vi:** XES3G5M, fold 0, arms `inject00/05/20`, models simpleKT / GKT / GIKT

---

## Kết luận ngắn

| Thành phần | Trạng thái | Nguồn |
|---|---|---|
| **S17** (`leak_injection.csv`) — \|E_pre\|, ECR, TBMR | **Thật** | `scripts/run_leak_injection.py`; regenerate 2026-07-22 khớp số cũ |
| **S18 cột 0% (clean)** | **Thay bằng số thật** | `baseline_fold_results.csv` fold 0, `train_only` (= `inject00` graph) |
| **S18 cột 5% / 20%** | **Không có artifact** | Không log, cache, checkpoint `inject05/20` trong repo/git/server sync |

**Table S18 cũ (0.850 / 0.810 / 0.852…) là placeholder** — commit `6a0b09fc` (2026-06-11); script `create_fake_tables.py` (`6eadc24b`, 2026-06-16) hard-code cùng bộ số. **Không có run GPU injection downstream nào được lưu.**

---

## Truy vết artifact

### 1. Git history — `downstream_auc_injection.csv`

| Commit | Ngày | Ghi chú |
|---|---|---|
| `6a0b09fc` | 2026-06-11 | Thêm CSV/TEX với số 0.850/0.810/0.852 ngay từ đầu |
| `6eadc24b` | 2026-06-16 | Thêm `create_fake_tables.py`, `mock_gkt.py` (mock GKT từ simpleKT−0.041) |

Không commit nào chứa `results/cache/*inject*_result.json`.

### 2. `results/cache/` (toàn bộ lịch sử git)

- Có `*_train_only_*`, `*_full_log_*` cho nhiều dataset.
- **Không có** `*_inject00_*`, `*_inject05_*`, `*_inject20_*` cho bất kỳ model/dataset nào.
- `mock_gkt.py` tạo cache inject với AUC **random** (`0.85 + rand*0.05`) — không dùng cho bảng paper; bảng paper dùng số cố định từ `create_fake_tables.py`.

### 3. Log Server A (`audit/2026-07-22-server_A_log_manifest.md`)

- Không có log injection downstream (chỉ GKT30, graph builder, OOM).

### 4. Checkpoint / `.pt`

- Không có file checkpoint pyKT trong workspace.

### 5. S17 — xác minh lại (2026-07-22)

Chạy `python -m scripts.run_leak_injection` → khớp `leak_injection.csv` hiện có:

| Rate | \|E_pre\| | ECR_overlap | TBMR |
|---:|---:|---:|---:|
| 0% | 1162 | 1.000 | 0.754 |
| 5% | 1378 | 1.000 | 0.776 |
| 20% | 1417 | 1.000 | 0.779 |

→ Phần **graph / metric tiering** của injection **có cơ sở thật**; phần **retrain AUC** thì không.

---

## S18 — đối chiếu số cũ vs số thật (fold 0, clean)

Nguồn thật: `results/tables/baseline_fold_results.csv`, `graph_construction=train_only`  
(`inject00` với p=0 ≡ cùng graph train-only.)

| Model | S18 cũ (placeholder) | Fold-0 primary (thật) | Δ |
|---|---:|---:|---:|
| simpleKT | 0.850 | **0.8744** | +0.024 |
| GKT | 0.810 | **0.8346** | +0.025 |
| GIKT | 0.852 | **0.8776** | +0.026 |

**Sửa audit trước:** GKT 0.810 **không** khớp fold-0 primary (0.8346) — khớp với công thức mock `simpleKT_fake − 0.041 ≈ 0.809`.

Cache git `6eadc24b`: `xes3g5m_fold_0_simplekt_train_only_result.json` → AUC **0.874642** (≈ fold CSV).

---

## S18 — cột 5% / 20% (leak retrain)

**Không tìm thấy** nguồn thay thế:

- Không `results/cache/xes3g5m_fold_0_{model}_s42_inject{05,20}_result.json`
- Không dòng `inject*` trong `baseline_fold_results.csv`
- `run_injection_auc.py` chưa từng hoàn tất pipeline train trên máy dev (thiếu graph inject + cache)

→ Cần **GPU rerun 6 job** (3 model × inject05 + inject20; inject00 = số clean đã có) hoặc **hạ claim** §4.3 / Table S18 cho đến khi có run.

---

## Delta placeholder vs thật (nếu giữ shape cũ — **không khuyến nghị**)

Nếu áp cùng Δ placeholder lên clean thật:

| Model | Δ@5% (cũ) | Δ@20% (cũ) | Clean thật | 20% ngoại suy |
|---|---:|---:|---:|---:|
| simpleKT | +0.002 | +0.008 | 0.8744 | 0.8824 |
| GKT | +0.015 | +0.050 | 0.8346 | 0.8846 |
| GIKT | +0.008 | +0.028 | 0.8776 | 0.9056 |

**Không dùng** cho paper — Δ chưa được đo trên checkpoint thật.

---

## Hành động đã / cần

- [x] Audit toàn repo + git
- [x] Regenerate S17 (xác nhận)
- [x] Cập nhật `downstream_auc_injection.csv` — clean verified; leak `pending`
- [x] Regenerate `downstream_auc_injection.tex` — leak = `---`
- [ ] GPU: 6 run `inject05/20` × 3 model (fold 0, hp Table S15)
- [ ] Cập nhật §4.3 / bảng 2×2 sau khi có leak AUC thật

**Script thu thập:** `python -m scripts.collect_injection_auc`
