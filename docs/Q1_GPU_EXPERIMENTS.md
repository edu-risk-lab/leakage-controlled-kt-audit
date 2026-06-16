# Kịch bản thí nghiệm Q1 trên GPU server (24GB VRAM)

Tài liệu này mô tả **thứ tự chạy**, **ước lượng thời gian**, **cách lấy kết quả**, và **đánh giá run đã pull** cho revision C5 + multi-seed. Mọi run Q1 ghi vào `results/q1/<tag>/` — **không ghi đè** `results/tables/baseline_fold_results.csv` hiện tại.

---

## 0. Chuẩn bị server

```bash
git clone https://github.com/tuanymc/p0_project.git
cd p0_project
git submodule update --init --recursive

python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
pip install -e ".[pykt]"
# PyTorch CUDA — chọn build phù hợp driver, ví dụ cu121:
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Dữ liệu: tải bundle Google Drive (README §3) hoặc copy parquet + raw
# Bắt buộc: data/processed/xes3g5m.parquet
# Khuyến nghị: data/raw/xes3g5m/ (ground-truth DAG cho E_pre)
```

Kiểm tra GPU:

```bash
python -c "import torch; print(torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory/1e9)"
```

**24GB VRAM:** đủ cho GKT XES3G5M; config hiện tại dùng **batch 32** (`configs/xes3g5m_gkt_epochs30.yaml`) sau OOM trên 16GB.

---

## 0.1 Kết quả đã pull (cập nhật sau pull mới nhất)

| Run | Trạng thái | Mean GKT AUC | Δ vs simpleKT | Dùng trong paper? |
|-----|------------|--------------|---------------|-----------------|
| GKT **10ep** primary (seed 42) | ✅ baseline chính | **0.834** | **−0.041** [−0.044, −0.038] | Table S16 |
| GKT **30ep** matched (seed 42) | ✅ hợp lệ (folder `gkt_epochs30_s42/`) | **0.837** | **−0.038** [−0.048, −0.027] | **Table S21** |
| GKT 30ep (seed 17) | 🔄 **đang rerun** — fold 0 aligned **0.842**; fold 1–2 vẫn stale (~0.71) | 0.755* | — | **Chưa** — cần xong 3 fold |
| GKT 30ep (seed 1234) | ⚠️ stale (graph chưa rebuild) | ~0.710 | −0.167 | **Không** |
| Phase 3 `trio_matched_s*` | ✅ merged CSV (18 dòng) | simpleKT ~0.877, GIKT ~0.879 | GIKT +0.002…+0.003 | Supplementary |

\*Mean 3 fold nếu trộn 1 fold mới + 2 fold cũ — **không dùng** cho paper.

**Kết luận paper (không đổi):** seed **42** đủ cho Table S21 (kịch bản B: gap −0.041 → −0.038). Rerun seed 17 **fold 0 = 0.842** xác nhận graph rebuild **đúng hướng**; cần hoàn tất fold 1–2 (seed 17) rồi seed 1234.

Regenerate bảng (local, sau mỗi lần pull):

```bash
python scripts/summarize_q1_experiments.py --sync-cache
python scripts/summarize_q1_phase3.py
python scripts/generate_gkt_epoch_ablation.py
```

**Lưu ý:** `--sync-cache` copy fold-0 cache aligned (`results/cache/*_s17_*`) vào `results/q1/` nếu CSV cũ vẫn ~0.71.

---

## 0.2 ⚠️ Bắt buộc: graph export phải khớp `split_base_seed`

`graph_builder` ghi graph vào `data/processed/xes3g5m/fold_{0,1,2}/` **không có hậu tố seed**. `baseline_runner --split-base-seed N` dùng learner split (N, N+1, N+2) nhưng vẫn đọc graph cũ nếu không rebuild.

**Triệu chứng:** AUC GKT ~0.71 khi seed ≠ 42 trong khi seed 42 ~0.84.

**Quy tắc:** trước mỗi run với `split_base_seed = S`, rebuild graph với **`split.seed: S`** trong config (không chỉ `--seed` CLI — yaml mặc định `seed: 42` ghi đè default).

### Tạo config tạm theo seed

```bash
python - <<'PY'
from pathlib import Path
import yaml

base = yaml.safe_load(Path("configs/xes3g5m.yaml").read_text())
for s in (42, 17, 1234):
    cfg = dict(base)
    cfg["split"] = dict(base["split"])
    cfg["split"]["seed"] = s
    out = Path(f"configs/xes3g5m_split{s}.yaml")
    out.write_text(yaml.dump(cfg, sort_keys=False), encoding="utf-8")
    print("Wrote", out)
PY
```

### Rebuild graph + train GKT 30ep (một seed)

```bash
SEED=17   # hoặc 42, 1234

python -m src.graph_builder --config configs/xes3g5m_split${SEED}.yaml

python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt

python -m src.baseline_runner \
  --config configs/xes3g5m_gkt_epochs30.yaml \
  --split-base-seed ${SEED} \
  --isolated-results gkt_epochs30_s${SEED} \
  --log-level INFO
```

**Phase 2 không chạy song song** các seed khác nhau trên cùng máy nếu dùng chung thư mục `fold_*` — phải **tuần tự**: rebuild graph seed 17 → train → rebuild seed 1234 → train.

Sau khi hoàn tất multi-seed hợp lệ:

```bash
python scripts/summarize_q1_experiments.py
python scripts/generate_gkt_epoch_ablation.py   # nếu mở rộng bảng S21
```

---

## 1. Ba phase thí nghiệm

| Phase | Mục tiêu | Config | Split seeds | Runs GKT | Thời gian ước lượng* |
|-------|----------|--------|-------------|----------|----------------------|
| **1** | **C5 core** — GKT epoch-matched | `configs/xes3g5m_gkt_epochs30.yaml` | 42 | 3 fold | **4–8 h** |
| **2** | Multi-seed inferential | cùng config + **graph rebuild/seed** | 17, 1234 | 6 fold | **+10–20 h**† |
| **3** | Primary trio matched | `configs/experiments/xes3g5m_primary_trio_matched.yaml` | 42, 17, 1234 | 9×3 models | **+24–48 h** |

\*Trên GPU tương đương RTX 3090 / A5000 24GB.  
†Bao gồm ~2× graph_builder + train tuần tự (§0.2).

### Chạy từng phase (khuyến nghị)

```bash
chmod +x scripts/run_q1_gpu_experiments.sh

# Phase 1 — seed 42 (graph mặc định configs/xes3g5m.yaml đã khớp seed 42)
./scripts/run_q1_gpu_experiments.sh phase1

# Phase 2 — BẮT BUỘC rebuild graph từng seed (§0.2); KHÔNG chạy parallel trên cùng repo
for S in 17 1234; do
  python -m src.graph_builder --config configs/xes3g5m_split${S}.yaml
  python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt
  python -m src.baseline_runner \
    --config configs/xes3g5m_gkt_epochs30.yaml \
    --split-base-seed ${S} \
    --isolated-results gkt_epochs30_s${S} \
    --log-level INFO
done
python scripts/summarize_q1_experiments.py

# Phase 3 — optional: trio matched × 3 seeds (rebuild graph trước mỗi seed)
./scripts/run_q1_gpu_experiments.sh phase3   # cần sửa script: gọi graph_builder theo seed

# Gộp bảng
./scripts/run_q1_gpu_experiments.sh summarize
```

Chạy tất cả (overnight):

```bash
nohup ./scripts/run_q1_gpu_experiments.sh all > logs/q1/nohup.log 2>&1 &
tail -f logs/q1/nohup.log
```

> **Lưu ý:** `run_q1_gpu_experiments.sh` hiện **bỏ qua** graph rebuild khi `fold_0/e_pre_train_only.csv` đã tồn tại. Phase 2+ phải rebuild thủ công theo §0.2 (hoặc xóa exports cũ trước khi chạy seed mới).

---

## 2. Cấu trúc output

```
results/q1/
  gkt_epochs30_s42/baseline_fold_results.csv   # Phase 1 ✅ (cần pull folder)
  gkt_epochs30_s17/...                         # ⚠️ cần chạy lại sau graph rebuild
  gkt_epochs30_s1234/...
  trio_matched_s42/...                         # Phase 3 — chỉ merged CSV trên git (folder gitignored)

results/tables/
  q1_baseline_fold_results.csv                 # merged (có thể chứa s42 từ merge tay)
  q1_gkt_vs_simplekt.csv
  gkt_epoch_ablation.tex                       # Table S21 (paper)
  gkt_epoch_ablation.csv

logs/q1/
  run.log, gkt_epochs30_s42.log, ...
```

Cột mới trong CSV: `experiment_tag`, `split_base_seed`.

---

## 3. Calibrate một fold (smoke test ~1–2h)

```bash
python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt --dry-run
python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt

python -m src.baseline_runner \
  --config configs/xes3g5m_gkt_epochs30.yaml \
  --split-base-seed 42 \
  --fold-idx 0 \
  --isolated-results gkt_epochs30_s42_fold0_smoke \
  --log-level INFO
```

---

## 4. Cập nhật paper (đã làm trên local)

| Bước | Trạng thái |
|------|-----------|
| Table S21 epoch ablation (`generate_gkt_epoch_ablation.py`) | ✅ |
| Abstract / C5 / §4.2 / Discussion / Conclusion | ✅ |
| Supplementary index + §S21 | ✅ |
| Cover letter (`paper/cover_letter_APIN.md`) | ✅ |
| Bootstrap S16 (vẫn 10ep primary −0.041) | ✅ giữ nguyên — S21 bổ sung 30ep |

Khi có **multi-seed hợp lệ** (9 fold × seed 42/17/1234):

1. Merge vào `q1_baseline_fold_results.csv` qua `summarize_q1_experiments.py`.
2. Mở rộng `scripts/generate_gkt_epoch_ablation.py` hoặc `bootstrap_auc_ci.py` cho 9 điểm fold-level.
3. Cập nhật Limitations: bỏ “single seed” nếu đủ 3 seed aligned.

Compile PDF (từ repo root):

```bash
pdflatex -interaction=nonstopmode -output-directory=paper paper/main_APIN.tex
pdflatex -interaction=nonstopmode -output-directory=paper paper/supplementary.tex
```

---

## 5. Resume / lỗi thường gặp

| Vấn đề | Xử lý |
|--------|--------|
| Run dở giữa chừng | Chạy lại cùng phase; cache GKT được xóa trước mỗi run |
| OOM 24GB | `batch_size: 32` trong yaml GKT; hoặc `--fold-idx N` từng fold |
| Cache cũ 10 epoch | `python scripts/clear_baseline_cache.py --models gkt` |
| Không có CUDA | Script `check_env` sẽ fail sớm |
| **AUC GKT ~0.71 với seed 17/1234** | Graph chưa rebuild — xem §0.2 |
| Phase 2 parallel 2 GPU cùng repo | Tránh: graph path không tách seed |

---

## 6. Lệnh thủ công tương đương (Phase 1, seed 42)

```bash
python -m src.graph_builder --config configs/xes3g5m_split42.yaml
python scripts/clear_baseline_cache.py --dataset xes3g5m --models gkt
python -m src.baseline_runner \
  --config configs/xes3g5m_gkt_epochs30.yaml \
  --split-base-seed 42 \
  --isolated-results gkt_epochs30_s42
python scripts/summarize_q1_experiments.py
python scripts/generate_gkt_epoch_ablation.py
```

---

## 7. Checklist trước khi push kết quả về máy local

- [ ] `results/q1/gkt_epochs30_s42/baseline_fold_results.csv` tồn tại (Phase 1)
- [ ] Phase 2: AUC GKT **~0.83+** (không ~0.71) sau graph rebuild
- [ ] `results/tables/gkt_epoch_ablation.tex` / `gkt_epoch_ablation.csv` có dòng 30ep
- [ ] `logs/q1/run.log` không có traceback
- [x] Phase 3: `q1_baseline_fold_results.csv` có 18 dòng `trio_matched_s*` (simpleKT + GIKT × 3 seeds)
- [ ] Phase 2 hợp lệ seed 17/1234: GKT mean AUC **~0.83+** (hiện ~0.71 — cần rerun với graph rebuild)

Scp về local:

```bash
scp -r user@server:~/p0_project/results/q1 ./results/
scp user@server:~/p0_project/results/tables/q1_* ./results/tables/
scp user@server:~/p0_project/results/tables/gkt_epoch_ablation.* ./results/tables/
```

Sau pull:

```bash
python scripts/generate_gkt_epoch_ablation.py
pdflatex -interaction=nonstopmode -output-directory=paper paper/main_APIN.tex
```
