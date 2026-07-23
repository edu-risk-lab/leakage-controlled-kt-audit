# Hướng dẫn chạy A3.5 — Cold-start rerun trên GPU server

**Ngày:** 2026-07-23  
**Mục tiêu revision:** A3.5 trong `REVISION_PLAN_APIN_NCS_20260722.md`  
**Vấn đề:** Junyi `very_cold` — mọi model có AUC trùng nhau (artefact từ prediction cap 5000 / skip cold-start pyKT).

---

## 1. Tóm tắt nhanh

| Mục | Giá trị |
|-----|---------|
| Script chính | `scripts/run_a3_cold_start_rerun.sh` (Linux) / `.ps1` (Windows) |
| Dispatcher | `bash scripts/run_gpu_server_pending.sh a3_coldstart` |
| Dataset mặc định | **Junyi** (ưu tiên — artefact very_cold) |
| Thời gian ước lượng | Junyi: **4–12 giờ** (3 folds × ~8 model pyKT; dùng checkpoint nếu đã train) |
| Output chính | `results/tables/cold_start_metrics.csv` + `cold_start_*.tex` |
| GPU RAM khuyến nghị | ≥ 16 GB (Junyi graph models batch 16) |

---

## 2. Chuẩn bị server (lần đầu hoặc sau khi pull)

```bash
cd p0_project
git pull origin main

source .venv/bin/activate          # Linux
# .\.venv\Scripts\Activate.ps1     # Windows PowerShell

pip install -e ".[pykt]"
python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0))"
python -c "import pykt"
```

**Dữ liệu bắt buộc:**

```bash
test -f data/processed/junyi.parquet && echo "OK junyi"
# Tùy chọn nếu chạy --dataset all:
test -f data/processed/xes3g5m.parquet
test -f data/processed/assist2012.parquet
```

Nếu thiếu parquet → xem README §3 (preprocess).

**Checkpoint pyKT (khuyến nghị):** Nếu đã chạy baseline Junyi trước đó, thư mục `results/pykt_work/junyi/` có sẵn → script **load checkpoint**, không train lại từ đầu (nhanh hơn nhiều).

---

## 3. Chạy production (Junyi — khuyến nghị)

### Linux / nohup

```bash
chmod +x scripts/run_a3_cold_start_rerun.sh scripts/run_gpu_server_pending.sh

# Cách 1 — script trực tiếp
nohup bash scripts/run_a3_cold_start_rerun.sh \
  > logs/q1/nohup_a3_coldstart.log 2>&1 &

# Cách 2 — dispatcher
nohup bash scripts/run_gpu_server_pending.sh a3_coldstart \
  > logs/q1/nohup_a3_coldstart.log 2>&1 &

# Theo dõi
tail -f logs/q1/nohup_a3_coldstart.log
# hoặc
tail -f logs/q1/a3_cold_start_junyi.log
```

### Windows Server

```powershell
.\scripts\run_a3_cold_start_rerun.ps1
# hoặc overnight:
Start-Process powershell -ArgumentList '-NoProfile -File scripts/run_a3_cold_start_rerun.ps1' -RedirectStandardOutput logs/q1/nohup_a3_coldstart.log
```

---

## 4. Chạy thử / debug (fold 0 only)

Trước khi chạy full 3 folds, nên thử fold 0 (~1–3 giờ):

```bash
bash scripts/run_a3_cold_start_rerun.sh --fold-idx 0
```

Chỉ chạy vài model (nhanh hơn):

```bash
bash scripts/run_a3_cold_start_rerun.sh --fold-idx 0 --models simplekt,gikt,skt
```

Dry-run (in lệnh, không train):

```bash
bash scripts/run_a3_cold_start_rerun.sh --dry-run
```

---

## 5. Pipeline làm gì?

1. Xóa cache prediction cũ (5000 dòng): `results/cache/junyi_fold_*_*_train_only_preds.csv`
2. Gọi:
   ```bash
   python -m src.baseline_runner \
     --config configs/junyi.yaml \
     --cold-start-only \
     --force-cold-start
   ```
   - `--cold-start-only`: **chỉ** cập nhật `cold_start_metrics.csv`, không ghi đè `baseline_results.csv`
   - `--force-cold-start`: full predictions + valid+test, có `kc_id` cho pyKT
3. Regenerate TeX: `cold_start_summary.tex`, `cold_start_comparison.tex`, `cold_start_metrics.tex`, …
4. In verify `very_cold` theo fold/model ở cuối log

**Export predictions (A3.3 audit):**  
`results/predictions/junyi/fold_<k>/<model>.parquet`

---

## 6. Pass criteria (kiểm tra sau khi chạy)

Cuối log script có block:

```
--- junyi very_cold (post A3 rerun) ---
fold 0: n=19, models=8, unique_AUC=...
```

| Kiểm tra | Kỳ vọng |
|----------|---------|
| Script exit 0 | Không OOM / không ImportError |
| `cold_start_metrics.csv` cập nhật | Timestamp mới, dataset=junyi |
| Fold 0 very_cold n=19 | AUC có thể vẫn bị suppress (`---` trong TeX) nếu `n_discordant < 10` — **đúng theo A3.1** |
| Fold 1+ very_cold | **Không** còn mọi model AUC trùng đến 7 chữ số (trừ khi vẫn suy biến thống kê) |
| Parquet fold 0 | Tồn tại cho từng model đã chạy |

Kiểm tra tay:

```bash
python - <<'PY'
import pandas as pd
df = pd.read_csv("results/tables/cold_start_metrics.csv")
sub = df[(df.dataset=="junyi") & (df.stratum=="very_cold")]
print(sub.groupby(["fold","model"])[["n","auc","n_discordant"]].first().head(20))
PY
```

---

## 7. OOM / fallback

**Junyi OOM:**

```bash
# Chạy từng model
for m in dkt simplekt akt gikt skt dygkt dgekt; do
  bash scripts/run_a3_cold_start_rerun.sh --models "$m" || break
done
```

**Không có GPU:**

```bash
FORCE_CPU=1 bash scripts/run_a3_cold_start_rerun.sh --fold-idx 0
# Rất chậm — chỉ dùng debug
```

**Chỉ regenerate bảng (đã có CSV từ server khác):**

```bash
bash scripts/run_a3_cold_start_rerun.sh --tables-only
```

---

## 8. Đẩy kết quả về repo / máy dev

### Trên GPU server (sau khi pass)

```bash
git add results/tables/cold_start_metrics.csv
git add results/tables/cold_start_*.tex
git add results/predictions/junyi/   # optional — parquet lớn, có thể scp riêng

git checkout -b results/a3-coldstart-junyi-$(date +%Y%m%d)
git commit -m "$(cat <<'EOF'
results: A3.5 Junyi cold-start rerun with full pyKT predictions.

Regenerates cold_start_metrics and TeX; supports very_cold audit (A3.3).
EOF
)"
git push -u origin HEAD
```

### Trên máy dev (sau merge/pull)

```powershell
Copy-Item results/tables/cold_start_*.tex paper/submission_APIN/ -Force
Copy-Item results/tables/cold_start_metrics.csv paper/submission_APIN/ -Force
# Rebuild PDF manuscript
```

Chạy crossref nếu cần (cold-start không nằm trong crossref AUC 12/12):

```bash
python -m scripts.crossref_auc_numbers
```

---

## 9. Tùy chọn — chạy thêm XES / ASSIST

```bash
bash scripts/run_a3_cold_start_rerun.sh --dataset xes3g5m
bash scripts/run_a3_cold_start_rerun.sh --dataset assist2012
# hoặc cả ba (rất lâu):
bash scripts/run_a3_cold_start_rerun.sh --dataset all
```

---

## 10. Liên hệ tài liệu

| File | Nội dung |
|------|----------|
| `REVISION_PLAN_APIN_NCS_20260722.md` §A3 | Bối cảnh revision |
| `audit/2026-07-22-A1-A3-trace.md` | Trace artefact very_cold |
| `audit/2026-07-23-GPU-server-runbook.md` | Runbook tổng GPU |
| `scripts/run_a3_cold_start_rerun.sh` | Script executable |

---

## Checklist operator

- [ ] `git pull origin main` (commit có script A3)
- [ ] `data/processed/junyi.parquet` tồn tại
- [ ] CUDA + pykt OK
- [ ] (Khuyến nghị) Thử `--fold-idx 0` trước
- [ ] Chạy full: `nohup bash scripts/run_a3_cold_start_rerun.sh ...`
- [ ] Verify log + `cold_start_metrics.csv`
- [ ] Push branch kết quả hoặc scp về dev
- [ ] Sync TeX → `paper/submission_APIN/`
