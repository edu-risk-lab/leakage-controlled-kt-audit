# Pull & tổng hợp kết quả — 2026-07-23 ~21:30

**Git:** merged `origin/results/a2-2b-ddr-seed17-verified` → `main` (`65c24e43`, pushed)

---

## 1. A2.2b — DDR GKT seed-17 baseline (Server A GPU)

| | Placeholder (cũ) | Verified (mới) |
|---|--:|--:|
| XES3G5M, GKT, fold 0, seed 17, `operator=none` | **0.842217** | **0.834468** |
| Nguồn lỗi | Hardcode copy GKT30 trong `eval_existing.py` | Training GPU thật (batch script A2.2b) |

**Ý nghĩa:** Baseline fold-0 seed-17 giờ khớp primary GKT (~0.8346), không còn inflate ~+0.008 so với các seed khác.

**DDR downstream (XES/GKT, pooled 9 folds sau merge):**

| Operator | p | DDR mean | AUC drop mean |
|----------|---:|---:|---:|
| edge_drop | 0.3 | 0.298 | 0.0124 |
| node_drop | 0.9 | 0.990 | 0.0877 |
| prereq_preserve | 0.3 | 0.237 | 0.0096 |

**Correlation DDR↔AUC drop (regenerated):** Pearson **r=0.989** (n=99), Spearman ρ=0.957 — narrative manipulation-check **giữ nguyên hướng**.

**Artefacts cập nhật:** `ddr_downstream.csv/.tex`, `ddr_downstream_gkt.tex`, `fig_ddr_downstream.pdf`, shard `ddr_downstream_gkt_seed17.csv`

---

## 2. B7 — Junyi edge share (local/server run, merged CSV)

Trước đó Junyi `---` trong Table leakage; giờ đã merge vào `edge_share_summary.csv`:

| Dataset | Edges >50% (mean) | Share p90 (mean) |
|---------|--:|--:|
| XES3G5M | 7.9% | 0.339 |
| ASSIST'12 | 0% | 0.334 |
| **Junyi** | **0.5%** | **0.355** |

`leakage_metrics.tex` (submission) — Junyi row đã có cột `$>50%$` và `p90`.

---

## 3. Đã có trên main (không cần pull thêm)

| Mục | Commit | Trạng thái |
|-----|--------|------------|
| A1 S18 injection verified | `0e440b33` / `f8cd815f` | decoupling GKT −0.010 @20% |
| B4 \|ρ\| + B7 XES/ASSIST | `80935c47` | leakage table migrated |
| Scan placeholder +0.05 | `af042678` | seminar scripts aligned |
| C8.1/C9/C10 | `80935c47` | Limitations, refs, Fig captions |

---

## 4. Còn pending

| Mục | Ghi chú |
|-----|---------|
| A2.2b-merge §4.6 prose | Kiểm tra §4.6/main text có cần cập nhật số correlation sau baseline fix (optional — pooled r≈0.99 giữ) |
| A3.5 / A3.3 | Cold-start GPU reruns |
| C8.3 | Rút trang Eq/Fig.5 |
| Sync `paper/results/tables/` | Một số file bị IDE lock lúc copy — submission_APIN đã sync |

---

## 5. Lệnh reproduce

```bash
git pull origin main
python -m scripts.plot_ddr_downstream
python -m scripts.generate_ddr_downstream_gkt_tex
python -m scripts.crossref_auc_numbers   # sanity trước submit
```
