# Lịch sử batch_size GKT — cập nhật sau pull Server A (2026-07-22)

**Nguồn chính:** [`docs/GKT_Hyperparams_Review_Report.md`](../docs/GKT_Hyperparams_Review_Report.md)  
(pull từ `origin/docs/gkt-hyperparams-review-report`, commit `672ad7bb`)

CSV sự kiện: [`2026-07-22-GKT-batch_size_history.csv`](2026-07-22-GKT-batch_size_history.csv)

---

## Kết luận attested (Server A/B review)

| Batch | Nhóm run publish | Server |
|---:|---|---|
| **4** | Primary XES 10ep; DDR XES seed 42 | A hoặc B |
| **32** | ASSIST/synthetic 10ep; **GKT30 9 folds**; DDR ASSIST | **A** (Q1 logs) |
| **8** | DDR multiseed XES (seed 17, 1234) — Jul 2026 | **A** (+ B part2) |
| **16** | GKT30 sớm | **Loại** — AUC ~0.71, thay bằng batch 32 |

→ **Không phải mọi GKT đều batch 4.** Primary XES = **4**; epoch-matched ablation publish = **32** (không phải 16).

---

## Bảng run publish (rút gọn từ báo cáo Server A)

### Primary (S16)

| Run | Dataset | ep | batch | Mean AUC |
|---|---|---:|---:|---:|
| GKT-P01 | XES3G5M | 10 | **4** | 0.8336 |
| GKT-P02 | ASSIST2012 | 10 | **32** | 0.9610 |

### GKT30 ablation (S21–S22)

| Tag | ep | batch | Mean AUC | Server |
|---|---:|---:|---:|---|
| gkt_epochs30_s17 | 30 | **32** | 0.8435 | A |
| gkt_epochs30_s42 | 30 | **32** | 0.8371 | A |
| gkt_epochs30_s1234 | 30 | **32** | 0.8365 | A |

**Run loại:** batch **16**, AUC ~0.712 / ~0.710 — khớp log local cũ (`logs/q1/gkt_epochs30_s17.log`).

### DDR downstream

| Run | ep | batch | Server |
|---|---:|---:|---|
| DDR seed 42 XES | 10 | **4** | B |
| DDR seed 42 ASSIST | 10 | **32** | A |
| DDR seed 17/1234 XES | 10 | **8** | A (+ B part2) |

---

## Git timeline (XES GKT batch)

| Commit | Ngày | batch XES GKT |
|---|---|---:|
| `619c02cf` | trước May 2026 | **4** (primary) |
| `d9efa271` | 2026-06-16 | 16→32 (GKT30 sớm) |
| `fcb14635` | 2026-06-16 | ablation **32** |
| `955a8202` | 2026-06-24 | primary yaml → **8** (DDR multiseed) |
| `a1b42ef1` | 2026-07-19 | primary yaml → **4** (remediation) |

---

## Mâu thuẫn cần sửa trong repo

| File | Hiện ghi | Attested (Server A) |
|---|---|---|
| `AUTHOR_ATTESTATION.md` GKT30 | batch **16** | publish **32** |
| `xes3g5m_gkt_epochs30.yaml` HEAD | batch **16** | publish **32** |
| `docs/DDR_DOWNSTREAM_GKT.md` | batch **16** XES | **4** (primary) / **8** (multiseed) |
| `generate_gkt_epoch_ablation.py` / S21 | primary batch **16** | primary **4** |

---

## Log local (`logs/q1/`)

| File | Trạng thái | Ghi chú |
|---|---|---|
| `gkt_epochs30_s17.log` | Có | Run cũ batch ~16, AUC~0.71 |
| `gkt_epochs30_s1234.log` | Có | Run cũ batch ~16, AUC~0.71 |
| `gkt_epochs30_s42.log` | **Thiếu** local | Báo cáo Server A ghi có trên máy A |

Pull git: `Already up to date` trên `main`; báo cáo lấy từ nhánh `docs/gkt-hyperparams-review-report`.
