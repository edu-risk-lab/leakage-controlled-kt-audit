# A2.2 — DDR seed 17 fold 0 AUC trùng GKT30 (2026-07-22)

## Phát hiện

| Nguồn | fold | AUC |
|---|---|---:|
| `gkt_epochs30_s17` (GKT30, 30ep, batch 32) | 0 | **0.8422173236026003** |
| `ddr_downstream.csv` / `ddr_downstream_gkt_seed17.csv` `operator=none` | 0 | **0.8422173236026003** (trùng tuyệt đối) |

## Nguyên nhân (đã xác minh)

**Không phải merge CSV nhầm** — là **placeholder hardcode** trong `scripts/eval_existing.py`:

```python
# REMOVED 2026-07-22: inserted GKT30 AUC when fold=0, operator=none
row.update({"auc": 0.8422173236026003, ...})
```

DDR seed 17 fold 0 `none` **không phải** run GKT 10ep batch 8 hợp lệ; giá trị copy từ GKT30 ablation.

## Hệ quả

- Dòng `none` fold 0 trong `ddr_downstream_gkt_seed17.csv` và merged `ddr_downstream.csv` **không dùng được** cho claim DDR baseline seed 17.
- Các operator khác fold 0 (edge/node/prereq) dùng AUC **thấp hơn** (~0.82–0.83) — hợp lý cho perturbed graph.
- Fold 1/2 `none` có AUC khác (~0.835, ~0.844) — có thể từ ckpt thật.

## Hành động

| Mức | Việc | Trạng thái |
|---|---|---|
| Code | Xóa hardcode `eval_existing.py` | **Done** |
| GPU | Rerun DDR GKT seed 17 fold 0 `operator=none` (10ep, batch 8) | **Script ready** — `scripts/run_a2_2b_ddr_seed17_baseline.{sh,ps1}` |
| Data | Cập nhật `ddr_downstream_gkt_seed17.csv` + merge | **Pending rerun** |
| Paper | Không cite fold-0 none seed 17 làm DDR baseline cho đến khi rerun | **Note for authors** |

## Tham chiếu Server A

`docs/GKT_Hyperparams_Review_Report.md` §7.2 đã ghi nhận bất thường; nguyên nhân gốc là placeholder script, không phải training thật.
