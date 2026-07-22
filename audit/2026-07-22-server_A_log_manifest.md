# Server A — manifest sau pull (2026-07-22)

**Pull git:** `origin/main` — Already up to date  
**Báo cáo chính:** `docs/GKT_Hyperparams_Review_Report.md` ← `origin/docs/gkt-hyperparams-review-report` (`672ad7bb`)

**Server A (theo báo cáo):** máy trạm; đối tác **Server B** = máy chủ GPU

## File log

| File | Size | Mtime | Nội dung chính |
|---|---:|---|---|
| `logs/q1/run.log` | 13 KB | 2026-07-08 | Phase 2 OOM song song → chạy tuần tự; ghi **16GB VRAM** |
| `logs/q1/gkt_epochs30_s17.log` | 18 KB | 2026-06-16 | 30 epoch/fold; valid_auc **~0.71** (run cũ); path `C:\TUAN\p0_project` |
| `logs/q1/gkt_epochs30_s1234.log` | 12 KB | 2026-06-16 | Tương tự s17 |
| `logs/q1/graph_builder.log` | 11 KB | 2026-06-16 | Graph rebuild |
| *(thiếu)* `gkt_epochs30_s42.log` | — | — | Không có log cho run AUC **~0.84** seed 42 |

## Trích dẫn quan trọng

**OOM / VRAM (`run.log`):**
```
Warning: Parallel execution failed (likely CUDA OOM). Falling back to sequential execution...
Running Phase 2 sequentially (16GB VRAM insufficient for parallel GKT)...
```

**Epoch xác nhận từ log (`gkt_epochs30_s1234.log`):**
```
INFO:src.pykt_engine:pyKT epoch 30 train_loss=... valid_auc=0.71224 ...
```

**Batch size:** runner **không in** `batch_size` trong log (schema `baseline_runner.py` / `pykt_engine.py`).

## Đối chiếu log ↔ artefact

| Tag | Log valid_auc (cuối epoch) | CSV AUC (paper) | Khớp? |
|---|---:|---:|---|
| gkt_epochs30_s17 | ~0.71 | ~0.843 | **Không** — log = run cũ; CSV = run sau (batch/graph khác) |
| gkt_epochs30_s1234 | ~0.71 | ~0.836 | **Không** |
| gkt_epochs30_s42 | *(no log)* | ~0.837 | Chỉ có artefact + config@`b02afca9` batch **16** |
