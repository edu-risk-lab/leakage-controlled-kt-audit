# Runbook — A1 injection downstream: 6 GPU job (XES3G5M, fold 0)

**Ngày:** 2026-07-22  
**Mục tiêu:** Train + eval 3 model × 2 arm leak (`inject05`, `inject20`) → điền Table S18 cột 5%/20%.  
**Cột 0% (clean):** đã có từ fold-0 `train_only` (proxy `inject00`); tùy chọn thêm 3 job `inject00` để sanity-check.

**Chạy trên:** Server B (GPU khuyến nghị). Có thể chạy Server A nếu đủ VRAM (RTX 3090 24GB).

---

## 1. Ma trận 6 job

| # | Model | Graph arm | Cache output |
|---|--------|-----------|--------------|
| 1 | simpleKT | `inject05` | `results/cache/xes3g5m_fold_0_simplekt_s42_inject05_result.json` |
| 2 | simpleKT | `inject20` | `..._inject20_result.json` |
| 3 | GKT | `inject05` | `..._gkt_s42_inject05_result.json` |
| 4 | GKT | `inject20` | `..._gkt_s42_inject20_result.json` |
| 5 | GIKT | `inject05` | `..._gikt_s42_inject05_result.json` |
| 6 | GIKT | `inject20` | `..._gikt_s42_inject20_result.json` |

**Không dùng** `python -m scripts.run_injection_auc` cho bước train — script đó gọi `baseline_runner` **không** có `--models` → sẽ chạy **mọi** baseline enabled (lãng GPU).

---

## 2. Hyperparameters bắt buộc (Table S15 / commit `619c02cf`)

Nguồn attested: `audit/2026-07-17-1541/canonical_training_protocol.yaml` + `configs/xes3g5m.yaml` @ `619c02cf`.

| Model | Epochs (max) | Batch | LR | max_seq_len | Early stop | Graph input | Backend |
|--------|-------------|-------|-----|-------------|------------|-------------|---------|
| **simpleKT** | **30** | **64** | 0.001 | 200 | patience **5** (valid AUC) | không dùng graph | pyKT stock |
| **GKT** | **10** | **4** | 0.001 | 200 | patience **5** | `E_pre` + `E_sim` (inject arm) | pyKT stock |
| **GIKT** | **10** | **8** | 0.001 | 200 | patience **5** | `E_pre` + `E_sim` | native (`src/models/gikt.py`) |

### ⚠️ Kiểm tra HEAD trước khi chạy

File `configs/xes3g5m.yaml` **hiện tại** có thể lệch commit attested:

| Trường | Cần cho injection | HEAD (2026-07-22) | @ `619c02cf` |
|--------|-------------------|-------------------|--------------|
| `baselines[gkt].batch_size` | **4** | 4 ✓ | 4 |
| `baselines[gikt].batch_size` | **8** | **16** ✗ | **8** |
| `pykt.epochs` / simpleKT override | **30** | 30 (fallback) ✓ | 30 |
| `pykt.batch_size` / simpleKT | **64** | 64 ✓ | 64 |

**Bắt buộc sửa trước run:**

```yaml
# configs/xes3g5m.yaml — baselines → gikt → hyperparams
  - name: gikt
    enabled: true
    hyperparams:
      batch_size: 8    # was 16 — must match 619c02cf / primary baseline
      epochs: 10
```

Ghi lại hash config sau sửa: `git rev-parse HEAD` + diff yaml.

### Split & fold (cố định)

| Tham số | Giá trị |
|---------|---------|
| Dataset | `xes3g5m` |
| Split | learner_temporal `[0.7, 0.1, 0.2]` |
| `split.seed` | **42** |
| Fold chạy | **0** only (`--fold-idx 0`) |
| `split_seed` fold 0 | **42** (→ cache `s42`) |
| `experiment_seed` (`--seed`) | **42** (default) |
| Eval split | valid+test |
| `n_eval` mong đợi | **1,922,840** (±0) |

### Graph builder (inject arms)

Từ `configs/xes3g5m.yaml` @ `619c02cf` (phải khớp S17):

| Tham số | Giá trị |
|---------|---------|
| `e_pre_support_quantile` | **0.95** |
| `e_pre_top_k_per_node` | **5** |
| `e_pre_max_edges` | **5000** |
| Inject sample seed | `42 + int(p*100)` → p=0.05 → **47**, p=0.20 → **62** |
| `E_sim` trên inject arms | **rỗng** (chỉ `E_pre`) |

**Sanity S17 sau build graph:**

| Arm | \|E_pre\| retained |
|-----|-------------------|
| inject00 | **1162** |
| inject05 | **1378** |
| inject20 | **1417** |

---

## 3. Pre-flight checklist (bắt buộc)

```powershell
cd D:\path\to\p0_project   # hoặc path Server B

# 1) Data
Test-Path data/processed/xes3g5m.parquet

# 2) Config GIKT batch = 8 (grep)
Select-String -Path configs/xes3g5m.yaml -Pattern "gikt" -Context 0,4

# 3) GPU + PyTorch
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

# 4) Không còn cache inject cũ (mock/random)
Remove-Item results/cache/xes3g5m_fold_0_*_inject05_* -ErrorAction SilentlyContinue
Remove-Item results/cache/xes3g5m_fold_0_*_inject20_* -ErrorAction SilentlyContinue

# 5) (Tuỳ chọn) Xóa workdir inject cũ để train lại từ đầu
Remove-Item -Recurse -Force results/pykt_work/xes3g5m/fold_0_seed_42/inject05 -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force results/pykt_work/xes3g5m/fold_0_seed_42/inject20 -ErrorAction SilentlyContinue
```

**Không** chạy `--clear-cache` toàn cục (sẽ xóa baseline primary).

---

## 4. Bước A — Build graph inject (CPU, ~vài phút)

```powershell
python -c "from scripts.run_injection_auc import build_injected_graphs; build_injected_graphs()"
```

**Verify:**

```powershell
Get-ChildItem data/processed/xes3g5m/fold_0/e_pre_inject*.csv | Format-Table Name, Length, LastWriteTime
python -m scripts.run_leak_injection   # S17 phải khớp bảng trên
```

---

## 5. Bước B — 6 job GPU (từng lệnh một)

Template (PowerShell / bash):

```bash
python -m src.baseline_runner \
  --config configs/xes3g5m.yaml \
  --baseline-backend pykt \
  --fold-idx 0 \
  --seed 42 \
  --graph-construction inject05 \
  --models simplekt
```

### Lệnh đầy đủ (6 run)

```bash
# 1–2 simpleKT
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt --fold-idx 0 --seed 42 --graph-construction inject05 --models simplekt
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt --fold-idx 0 --seed 42 --graph-construction inject20 --models simplekt

# 3–4 GKT  (batch 4 — chậm nhất, ~2–4 h/arm trên 3090)
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt --fold-idx 0 --seed 42 --graph-construction inject05 --models gkt
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt --fold-idx 0 --seed 42 --graph-construction inject20 --models gkt

# 5–6 GIKT (batch 8)
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt --fold-idx 0 --seed 42 --graph-construction inject05 --models gikt
python -m src.baseline_runner --config configs/xes3g5m.yaml --baseline-backend pykt --fold-idx 0 --seed 42 --graph-construction inject20 --models gikt
```

**Ghi log từng job:**

```bash
python -m src.baseline_runner ... 2>&1 | tee logs/q1/injection_fold0_gkt_inject05_$(date +%Y%m%d_%H%M).log
```

**Thứ tự khuyến nghị:** simpleKT → GIKT → GKT (GKT lâu nhất).

**Ước lượng wall-clock (RTX 3090 24GB):**

| Model | ~thời gian / arm |
|--------|------------------|
| simpleKT | 0.5–3 h |
| GIKT | 0.5–3 h |
| GKT | **2–4 h** |
| **Tổng 6 job** | **~12–24 h** (chạy tuần tự) |

---

## 6. Post-run verification (từng job)

### 6.1 File tồn tại

```powershell
$models = "simplekt","gkt","gikt"
$arms = "inject05","inject20"
foreach ($m in $models) { foreach ($a in $arms) {
  $p = "results/cache/xes3g5m_fold_0_${m}_s42_${a}_result.json"
  if (Test-Path $p) { Get-Content $p | Select-Object -First 15 } else { Write-Warning "MISSING $p" }
}}
```

### 6.2 JSON schema bắt buộc

Mỗi `*_result.json` phải có:

```json
{
  "dataset": "xes3g5m",
  "fold": 0,
  "split_seed": 42,
  "model": "gkt",
  "graph_construction": "inject05",
  "eval_split": "valid+test",
  "auc": 0.xxxx,
  "n_eval": 1922840,
  "status": "pykt_checkpoint"
}
```

| Check | Pass |
|-------|------|
| `graph_construction` | đúng `inject05` / `inject20` |
| `fold` | 0 |
| `split_seed` | 42 |
| `n_eval` | 1_922_840 |
| `auc` | finite, ∈ (0.5, 1.0) |

### 6.3 Checkpoint pyKT

```powershell
Get-ChildItem results/pykt_work/xes3g5m/fold_0_seed_42/inject05 -Filter *_best.ckpt
Get-ChildItem results/pykt_work/xes3g5m/fold_0_seed_42/inject20 -Filter *_best.ckpt
```

Path mẫu:

```
results/pykt_work/xes3g5m/fold_0_seed_42/inject05/gkt_p0_protocol_best.ckpt
results/pykt_work/xes3g5m/fold_0_seed_42/inject05/gikt_p0_protocol_best.ckpt
results/pykt_work/xes3g5m/fold_0_seed_42/inject05/simplekt_p0_protocol_best.ckpt
```

Log train phải có dòng kiểu: `Saved PyKT checkpoint to ...` và `valid_auc=...`.

### 6.4 Đối chiếu clean baseline (fold 0, train_only)

| Model | AUC clean đã publish | Nguồn |
|--------|---------------------|--------|
| simpleKT | **0.8744** | `baseline_fold_results.csv` |
| GKT | **0.8346** | idem |
| GIKT | **0.8776** | idem |

**Kỳ vọng hướng (không phải số cũ placeholder):**

- **simpleKT:** ΔAUC @20% **nhỏ** vs GKT/GIKT (placeholder cũ +0.008 — chỉ tham khảo hướng)
- **GKT, GIKT:** AUC **tăng** từ inject05 → inject20 (graph throughput tăng)
- inject05 AUC ≥ clean − 0.01 (thường tăng với graph models)

**Fail nếu:**

- AUC trùng tuyệt đối giữa inject05 và inject20 (có thể dùng nhầm graph)
- AUC = số placeholder cũ (0.810, 0.860, …) — nghi cache/mock
- `n_eval` ≠ 1_922_840

### 6.5 (Tuỳ chọn) Sanity inject00 — 3 job thêm

Nếu chạy thêm `inject00`, AUC phải **≈ train_only** (|Δ| < 0.002):

```bash
python -m src.baseline_runner ... --graph-construction inject00 --models simplekt
python -m src.baseline_runner ... --graph-construction inject00 --models gkt
python -m src.baseline_runner ... --graph-construction inject00 --models gikt
```

---

## 7. Bước C — Gom bảng S18

Trên máy có đủ 6 cache (hoặc sau sync từ Server B → dev):

```bash
python -m scripts.collect_injection_auc
```

**Verify output:**

- `results/tables/downstream_auc_injection.csv` — cột 5%/20% **không** rỗng; `leak*_status` ≠ `pending_gpu_rerun`
- `results/tables/downstream_auc_injection.tex` — không còn `---` ở cột 5%/20%

Sync sang paper:

```powershell
Copy-Item results/tables/downstream_auc_injection.* paper/submission_APIN/
```

Cập nhật §4.3 `main_APIN.tex`: thay số placeholder (0.850→0.858, 0.810→0.860, …) bằng số mới + ghi protocol fold 0 / hp Table S15.

---

## 8. Sync Server B → dev

Copy tối thiểu:

```
results/cache/xes3g5m_fold_0_{simplekt,gkt,gikt}_s42_inject{05,20}_result.json
results/cache/xes3g5m_fold_0_{simplekt,gkt,gikt}_s42_inject{05,20}_preds.csv
logs/q1/injection_*.log
```

(Tuỳ chọn provenance: `results/pykt_work/xes3g5m/fold_0_seed_42/inject{05,20}/`)

---

## 9. Troubleshooting

| Triệu chứng | Nguyên nhân | Xử lý |
|-------------|-------------|--------|
| OOM CUDA | batch GKT=4 vẫn nặng | Chạy tuần tự; đóng process GPU khác |
| Cache hit số cũ | JSON preds đã tồn tại | Xóa cặp `*_inject05_*` / `*_inject20_*` rồi rerun |
| \|E_pre\| ≠ 1162/1378/1417 | sai graph yaml hoặc chưa build | Chạy lại `build_injected_graphs()` |
| GIKT AUC lệch primary | batch 16 thay vì 8 | Sửa yaml → xóa workdir inject → rerun |
| `run_injection_auc` chạy hàng chục model | thiếu `--models` | Dùng lệnh §5, không gọi `run_baselines()` |

---

## 10. DoD — coi là xong khi

- [ ] 6 file `*_inject{05,20}_result.json` pass checklist §6
- [ ] Log mỗi job ghi epoch/batch/valid_auc cuối
- [ ] `collect_injection_auc` → S18 đủ 9 ô AUC (3 model × 3 arm; inject00 từ cache hoặc train_only proxy)
- [ ] Δ@20% graph models >> simpleKT (claim §4.3)
- [ ] Manuscript cập nhật; xóa *Configuration note* tạm nếu số đã verified
