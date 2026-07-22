# Rà soát vết: GKT batch=4 trên RTX 3090 24GB (2026-07-22)

> **Cập nhật 2026-07-22 (pull lần 2):** Đã pull [`docs/GKT_Hyperparams_Review_Report.md`](../docs/GKT_Hyperparams_Review_Report.md) từ `origin/docs/gkt-hyperparams-review-report` (`672ad7bb`).  
> Lịch sử batch: [`2026-07-22-GKT-batch_size_history.md`](2026-07-22-GKT-batch_size_history.md).  
> Log local: [`2026-07-22-server_A_log_manifest.md`](2026-07-22-server_A_log_manifest.md).

**Câu hỏi:** Có cơ sở khẳng định mọi run GPU GKT đều dùng `batch_size=4` (3090 24GB không chạy được batch lớn hơn)?

**Kết luận ngắn (sau Server A):**

| Nhóm run | Batch=4 — mức tin cậy | Ghi chú |
|---|---|---|
| Primary GKT 10ep (baseline chính, −0.041) | **Cao** (config @619c02cf + attestation + S15) | Không có training log |
| DDR downstream GKT | **Cao** (author attestation) | Riêng mục đích DDR |
| GKT30 9 folds (S21–S22) | **Batch 32 attested (Server A report)** | Log cũ ~0.71 = run batch **16** đã loại |
| GKT30 seed 42 (S21 Δ +0.003) | **Exploratory only** — không dùng 9-fold pooled | Attestation cũ batch 16 **superseded** |

**Server A report:** Primary XES **batch 4**; GKT30 publish **batch 32** (hidden 64, seq 100); DDR multiseed XES **batch 8**.

→ **Không** khẳng định “mọi GKT batch 4”. Cần đính chính `AUTHOR_ATTESTATION.md` và yaml GKT30 → batch **32** cho khớp báo cáo Server A.

---

## 1. Cơ sở ủng hộ batch=4 (GKT primary)

| Nguồn | Nội dung |
|---|---|
| `configs/xes3g5m.yaml` @ commit `619c02cf` (2026-06-03, lúc khóa AUC primary) | `baselines[gkt].hyperparams.batch_size: 4`, `epochs: 10` |
| `audit/2026-07-17-1541/AUTHOR_ATTESTATION.md` | Primary GKT: **10 ep, batch 4** — SERVER_ATTESTED |
| `results/tables/training_parity.csv` | GKT: 10 ep, **batch 4**, HW **NVIDIA RTX 3090 24GB** |
| `src/baseline_runner.py` L733–735 | `batch_size = hp.get("batch_size", pykt.batch_size)` — không clamp về 4 |

**AUC primary (3 fold):** 0.834557 / 0.833752 / 0.832624 — artefact `baseline_fold_results.csv`.

---

## 2. Cơ sở **mâu thuẫn** batch≠4 (GKT30 / Q1)

### 2.1 Lịch sử git `configs/xes3g5m_gkt_epochs30.yaml`

| Commit | Ngày | batch trong yaml | Sự kiện |
|---|---:|---:|---|
| `c0365119` | Q1 pipeline | **64** | Khởi tạo |
| `b8b4fa2b` | Phase 1 xong | **16** (giảm từ 32) | "complete Phase 1 experiments" |
| `b02afca9` | Seed 42 artefact | **16** | Lưu `gkt_epochs30_s42` AUC ~0.84 |
| `fcb14635` | Seed 17 fold 0 | **32** (tăng từ 16) | Commit message: *"set GKT batch_size to 32"* |
| `a1b42ef1` (HEAD) | Hiện tại | **16** (comment *was 32*) | |

→ Repo **ghi nhận có ý định/thay đổi** batch 16 và 32 cho GKT30; **không có commit nào** đặt GKT30 yaml về batch 4.

### 2.2 Attestation & generator hiện tại

| File | GKT30 extended batch |
|---|---|
| `AUTHOR_ATTESTATION.md` | **16** |
| `canonical_training_protocol.yaml` | `gkt_extended.batch_size: **16**` |
| `gkt_epoch_ablation.tex` comment | `extended max_epochs=30 batch=**16**` |
| `docs/Q1_GPU_EXPERIMENTS.md` L34, L235 | Gợi ý batch **32** trên 24GB (sau OOM 16GB) |

### 2.3 Artefact không lưu batch thực thi

`src/baseline_runner.py` cache JSON chỉ có: `dataset, fold, model, auc, acc, nll, status, note` — **không có `batch_size` hay `epochs`**.

Ví dụ `fcb14635:.../xes3g5m_fold_0_gk s17_train_only_result.json`: AUC=0.842217, không metadata HP.

→ **Không thể** chứng minh batch runtime từ CSV/JSON đã commit.

### 2.4 Log training

Theo `audit/2026-07-17-1541/FR01_FR12_evidence_report.md`:

- **Không có** log cho `gkt_epochs30_s42` (run tạo AUC 0.84 cuối).
- Log `gkt_epochs30_s17/s1234` tồn tại nhưng gắn AUC ~**0.71** (run cũ `d9efa271`), **không** khớp AUC paper ~0.84.

---

## 3. Số liệu GKT30 đã có (bất kể batch runtime)

Nguồn: `paper/results/tables/q1_baseline_fold_results.csv`

| Seed | Mean GKT30 AUC | Δ vs simpleKT (3 fold) |
|---:|---:|---:|
| 42 | 0.8371 | −0.0375 |
| 17 | 0.8435 | −0.0343 |
| 1234 | 0.8365 | −0.0407 |
| **Pooled 9-fold** | — | **−0.0375** |

So với primary GKT10 (−0.041): gap **thu hẹp ~0.003–0.004**, **không đảo dấu**.

---

## 4. Diễn giải thống nhất với nhận định “3090 chỉ chạy batch 4”

**Giả thuyết hợp lý:** Mọi run thực tế trên 3090 đều batch 4; các giá trị 16/32 trong yaml là **drift khi tune/profile** (`scripts/profile_gkt.py` dùng batch 16 cho benchmark; `fcb14635` ghi batch 32 cho lần chạy sau) **không phản ánh** batch đã dùng khi tạo AUC 0.84.

**Điều kiện để khẳng định an toàn trước reviewer:**

1. **Attestation bằng văn bản** (bổ sung `AUTHOR_ATTESTATION.md`): xác nhận mọi run GKT trên XES3G5M thực thi batch=4 trên 3090 24GB, kể cả GKT30.
2. **Sửa yaml** `xes3g5m_gkt_epochs30.yaml` → batch 4 (cả `baselines` và `pykt`).
3. **Sửa** `canonical_training_protocol.yaml`, comment S21, `Q1_GPU_EXPERIMENTS.md` (xóa gợi ý batch 32).
4. **Tùy chọn mạnh:** lưu 1 dòng log mẫu / screenshot `nvidia-smi` + dòng `batch_size` từ runner log cho 1 fold GKT30.
5. **Không cần rerun** nếu attestation đúng — AUC đã có; chỉ sửa **provenance**.

**Nếu không attestation:** reviewer có thể dùng yaml git (16/32) để phản biện “compute không matched” — đúng như mục A2 giáo sư.

---

## 5. Khuyến nghị trả lời giáo sư (A2)

**Phương án A (nếu xác nhận batch 4 thực thi):**

> GKT@30 đã chạy 3×3 fold trên XES3G5M với cùng batch=4 bắt buộc trên RTX 3090 24GB; chỉ epoch tăng 10→30. Pooled Δ vs simpleKT@30 = −0.038. Khoảng cách thu hẹp so với GKT@10 (−0.041) nhưng không đảo dấu. Config yaml 16/32 là drift tài liệu — đã sửa.

**Phương án B (nếu không chắc batch runtime):**

> Cần rerun GKT@30 với batch=4 ghi log, hoặc hạ −0.041 khỏi Abstract.
