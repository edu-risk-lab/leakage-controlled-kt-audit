# A1 — Kết quả injection verified (Server A GPU, 2026-07-23)

**Branch merged:** `origin/results/injection-s18-verified` → `main`  
**Cache:** `results/cache/xes3g5m_fold_0_{simplekt,gkt,gikt}_s42_inject{00,05,20}_result.json` (9 files)

## Table S18 (fold 0, Table S15 budgets)

| Model | 0% | 5% | 20% | Δ@20% |
|--------|---:|---:|---:|---:|
| simpleKT | 0.8744 | 0.8748 | 0.8748 | +0.0004 |
| GKT | 0.8346 | 0.8255 | 0.8243 | **−0.0103** |
| GIKT | 0.8776 | 0.8778 | 0.8778 | +0.0002 |

## So với placeholder cũ

| | Placeholder narrative | Verified |
|---|----------------------|----------|
| GKT @20% | +0.050 (0.810→0.860) | **−0.010** |
| GIKT @20% | +0.028 | +0.0002 |
| simpleKT @20% | +0.008 | +0.0004 |

## Diễn giải manuscript (§4.3)

- **S17** vẫn đúng: |E_pre| 1162→1417, TBMR tăng, ECR_flag=0.
- **S18:** decoupling — audit metrics phản ứng, AUC retrain **không** tăng theo graph mass; GKT giảm nhẹ.
- Đã cập nhật `main_APIN.tex`, bảng 2×2, caption S18; xóa Configuration note tạm.

## Lệnh thu thập

```bash
python -m scripts.collect_injection_auc
```
