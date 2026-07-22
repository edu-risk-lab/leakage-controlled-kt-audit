# Prompt cho Cursor — Server A & Server B: kiểm tra lịch sử injection (A1)

> **Cách dùng:** Copy **một** khối PROMPT tương ứng máy bạn đang mở Cursor.  
> Chạy **cả hai** (A rồi B) trước khi quyết định có cần GPU rerun hay không.

| Máy | Vai trò (theo audit) | Prompt |
|-----|----------------------|--------|
| **Server A** | Máy trạm — log Q1, cache ASSIST/synthetic, DDR ckpt Jul 2026 | §1 bên dưới |
| **Server B** | Máy chủ GPU — fold 2, primary XES ckpt, sync `server 2` | §2 bên dưới |

**Bối cảnh chung (dev, 2026-07-22):** Table S18 cũ = placeholder (`create_fake_tables.py`). Git không có `*inject*_result.json`. S17 graph metrics thật. S18 clean đã thay fold-0 thật (simpleKT 0.8744, GKT 0.8346, GIKT 0.8776); 5%/20% pending.

Chi tiết audit dev: `audit/2026-07-22-A1-injection-data-audit.md`

---

## §1 — PROMPT Server A (máy trạm)

```
Bạn đang ở Server A (máy trạm). Repo: p0_project — bài APIN Knowledge Tracing.

## Bối cảnh (đã audit trên máy dev, 2026-07-22)

Table S18 (`downstream_auc_injection.csv`) trong git có số 0.850/0.810/0.852 — nguồn gốc placeholder:
- Commit `6a0b09fc` (2026-06-11): thêm CSV/TEX với số cố định
- Commit `6eadc24b` (2026-06-16): `scripts/create_fake_tables.py` hard-code cùng bộ số
- Toàn bộ git history: **không có** `results/cache/*inject*_result.json`

Trên máy dev:
- S17 (`leak_injection.csv`) **thật** — graph metrics (1162/1378/1417 edges) regenerate khớp
- S18 cột 0% đã thay bằng fold-0 train_only thật: simpleKT 0.8744, GKT 0.8346, GIKT 0.8776
- S18 cột 5%/20%: **pending** — chưa có artifact

Script liên quan:
- `scripts/run_injection_auc.py` — build graph inject + train + collect
- `scripts/run_leak_injection.py` — chỉ graph/leakage metrics (S17)
- `scripts/collect_injection_auc.py` — thu AUC từ cache hoặc fold-0 baseline

Cache naming (baseline_runner):
  results/cache/xes3g5m_fold_{fold}_{model}_s{split_seed}_{graph_construction}_result.json

Injection arms: `inject00`, `inject05`, `inject20`
Models: `simplekt`, `gkt`, `gikt`
Protocol: XES3G5M, fold 0, split_seed=42, hp từ `configs/xes3g5m.yaml`

Graph files (nếu từng build):
  data/processed/xes3g5m/fold_0/e_pre_inject{00,05,20}.csv
  data/processed/xes3g5m/fold_0/e_sim_inject{00,05,20}.csv

## Nhiệm vụ — CHỈ ĐIỀU TRA, chưa chạy GPU trừ khi tôi yêu cầu

Hãy tự chạy lệnh và tìm kiếm trên **toàn bộ ổ đĩa workspace + path log cũ** (repo có thể từng ở `C:\TUAN\p0_project` theo log GKT30):

### 1. Cache & checkpoint
- Tìm mọi file khớp:
  - `*inject*_result.json`, `*inject*_preds.csv`
  - `*inject*.pt`, `*inject*.pth`, checkpoint pyKT liên quan xes3g5m fold 0
- Đọc JSON nếu có — trích AUC/acc/model/arm/timestamp

### 2. Graph inject
- Kiểm tra `data/processed/xes3g5m/fold_0/e_pre_inject*.csv` — có tồn tại? mtime?

### 3. Log
- Quét `logs/`, `logs/q1/`, và mọi `*.log` trong repo
- Tìm keyword: `inject`, `injection`, `inject05`, `inject20`, `run_injection`, `downstream_auc`
- Ghi path, size, mtime, vài dòng AUC/epoch/batch nếu có

### 4. Git local (Server A)
- `git log --all --oneline -- results/cache/*inject* results/tables/downstream_auc_injection.csv`
- `git stash list`; branch chưa push?
- File untracked/ignored trong `results/cache/`?

### 5. Script lịch sử
- Đọc `scripts/create_fake_tables.py`, `scripts/mock_gkt.py` — xác nhận mock vs real
- Có script/notebook khác từng ghi S18 không?

### 6. Đối chiếu số (nếu tìm được artifact)
So với placeholder cũ và baseline fold-0 thật:

| Model | Placeholder S18 | Fold-0 train_only (dev) |
| simpleKT | 0.850 | 0.8744 |
| GKT | 0.810 | 0.8346 |
| GIKT | 0.852 | 0.8776 |

Placeholder deltas: GKT +0.05 @20%, GIKT +0.028, simpleKT +0.008

## Deliverable — báo cáo markdown

Tạo file `audit/2026-07-22-server_A-injection-history-report.md` với:

1. **Tóm tắt 1 đoạn:** có/không có run injection downstream thật trên Server A
2. **Bảng artifact tìm được** (path | loại | mtime | AUC nếu có | khớp arm nào)
3. **Bảng artifact KHÔNG tìm thấy** (pattern đã grep)
4. **Trích log** (≤10 dòng quan trọng nhất)
5. **Khuyến nghị** — chọn MỘT:
   - **A)** Đủ artifact → merge vào repo (`collect_injection_auc.py`) — liệt kê file cần copy/sync sang dev
   - **B)** Không đủ → chuyển sang kiểm Server B hoặc GPU rerun 6 job
   - **C)** Mơ hồ → cần thêm thông tin gì

6. **Mirror checklist:** artifact nào Server A có mà dev chưa có (hoặc ngược lại)

## Ràng buộc
- Không commit/push trừ khi tôi yêu cầu
- Không xóa file
- Không chạy training GPU trừ khi báo cáo kết luận B và tôi confirm
- Ghi rõ path repo thực tế nếu khác `p0_project`
```

---

## §2 — PROMPT Server B (máy chủ GPU)

```
Bạn đang ở Server B (máy chủ GPU). Repo: p0_project — bài APIN Knowledge Tracing.

## Bối cảnh

Theo `docs/GKT_Hyperparams_Review_Report.md` (audit Server A, 2026-07-22):
- **Server B** = máy GPU chính; thường chạy **fold 2** và các job nặng
- **Server A** = máy trạm; có log GKT30, DDR ckpt Jul 2026, cache ASSIST/synthetic
- Git commit `85afe0c8` ("Sync results from server 2") — artifact có thể xuất phát từ **Server B này**
- Trên Server A **thiếu:** ckpt GKT primary XES (`train_only/gkt_p0_protocol_best.ckpt`), DDR XES seed 42 (Jun 2026)

**Vấn đề A1 (injection downstream, Table S18):**
- Số cũ 0.850/0.810/0.852 = placeholder trong git — **chưa xác minh trên GPU server**
- Cần tìm xem Server B từng train/eval với graph arms `inject05`, `inject20` (fold 0) hay không
- Nếu không có → cần **6 GPU job** (3 model × 2 arms leak); cột clean đã có từ fold-0 train_only

## Path & naming cần tìm

### Cache JSON (sau eval)
```
results/cache/xes3g5m_fold_0_{simplekt,gkt,gikt}_s42_inject{00,05,20}_result.json
results/cache/xes3g5m_fold_0_{model}_s42_inject{05,20}_preds.csv
```

### pyKT workdir & checkpoint (sau train)
```
results/pykt_work/xes3g5m/fold_0_seed_42/inject{00,05,20}/
  train_valid_sequences.csv
  test_sequences.csv
  gkt_graph_p0_protocol.npz          # GKT
  {simplekt,gkt,gikt}_p0_protocol_best.ckpt
  gikt_bipartite.csv                 # GIKT
```

### Graph inject (build trước train)
```
data/processed/xes3g5m/fold_0/e_pre_inject{00,05,20}.csv
data/processed/xes3g5m/fold_0/e_sim_inject{00,05,20}.csv
```

### Config hp (Table S15 primary)
- File: `configs/xes3g5m.yaml` @ commit `619c02cf` (attested): GKT **10 ep, batch 4**, lr 0.001, max_seq_len 200
- simpleKT/GIKT: xem `baselines.*` và `pykt.*` trong cùng file
- **Lưu ý:** HEAD hiện có thể batch 8 — ghi rõ batch thực tế nếu log/ckpt cho thấy khác

## Nhiệm vụ — CHỈ ĐIỀU TRA trước; KHÔNG train trừ khi tôi confirm sau báo cáo

Quét **repo + path clone cũ + thư mục kết quả ngoài repo** (nếu từng copy `results/` ra chỗ khác):

### 1. Injection artifact (ưu tiên cao nhất)
- `find`/glob/`rg` toàn repo:
  - `*inject*result.json`, `*inject*preds*`, `e_pre_inject*.csv`
  - `results/pykt_work/**/inject05/**`, `**/inject20/**`
- Với mỗi hit: path, size, mtime, đọc AUC từ JSON hoặc log cuối epoch

### 2. Primary XES baseline ckpt (phụ — liên quan provenance)
- `results/pykt_work/xes3g5m/fold_{0,1,2}_seed_{42,43,44}/train_only/*_best.ckpt`
- GKT fold 0 seed 42 — Server A báo **không còn**; Server B có thể còn

### 3. Log GPU
- `logs/`, `logs/q1/`, `nohup.out`, `*.log`, `screenlog.*`, journal tmux nếu có
- Keyword: `inject`, `graph_construction=inject`, `run_injection`, `valid_auc`, `Saved PyKT checkpoint`, `batch_size`, `CUDA`
- Ghi GPU model (3090/4090…), VRAM, thời gian train nếu log có

### 4. Git & sync history (Server B)
- `git log --oneline -20` — commit nào push/pull với Server A?
- `git log --all --oneline -- results/cache/*inject* results/pykt_work/**/inject*`
- Branch/stash/untracked trong `results/` (thường gitignore)
- Có tarball/zip backup `results/` không?

### 5. Chạy dry-check (KHÔNG train)
Nếu repo + data đủ:
```bash
python -m scripts.collect_injection_auc
```
→ In bảng wide; ghi cột nào `verified` vs `pending`

Nếu thiếu graph inject nhưng có script:
```bash
python -c "from scripts.run_injection_auc import build_injected_graphs; build_injected_graphs()"
```
→ Chỉ build graph, **không** gọi `run_baselines()` trừ khi tôi yêu cầu

### 6. Đối chiếu số

| Model | Placeholder S18 (fake) | Fold-0 clean thật (dev) | Placeholder Δ@20% |
| simpleKT | 0.850 → 0.858 | 0.8744 | +0.008 |
| GKT | 0.810 → 0.860 | 0.8346 | +0.050 |
| GIKT | 0.852 → 0.880 | 0.8776 | +0.028 |

Nếu tìm được AUC inject thật: so Δ@20% vs placeholder; ghi batch/epoch đã dùng.

## Deliverable — báo cáo markdown

Tạo file `audit/2026-07-22-server_B-injection-history-report.md` với:

1. **Tóm tắt:** Server B có/không có run injection downstream thật; mức độ đầy đủ (0/6, 3/6, 6/6 job)
2. **Bảng artifact** (path | arm | model | AUC | mtime | batch/epoch nếu suy ra được)
3. **Bảng THIẾU** — pattern đã grep toàn repo
4. **GPU environment:** card, VRAM, CUDA, path repo thực tế
5. **Trích log** (≤15 dòng quan trọng nhất, có AUC/checkpoint path)
6. **Khuyến nghị** — MỘT trong:
   - **A)** Đủ 6 job inject05/20 → liệt kê file sync về dev + lệnh `collect_injection_auc`
   - **B)** Thiếu toàn bộ → ước lượng rerun: 6 job × ~X phút/job @ batch/epoch Table S15; đề xuất thứ tự chạy
   - **C)** Một phần → job nào còn thiếu; có thể tái dùng ckpt inject00 (=train_only) không
   - **D)** Cần thêm input từ Server A trước khi quyết định

7. **Phụ lục mirror:** ckpt/log primary XES hoặc DDR seed 42 tìm thấy trên B (nếu có) — liên quan audit GKT chung

## Ràng buộc
- **Không** commit/push/xóa file
- **Không** chạy training GPU (pyKT epoch loop) trừ khi tôi reply "OK chạy rerun" sau báo cáo
- Build graph-only (`build_injected_graphs`) được phép nếu cần xác minh |E_pre| khớp S17
- Báo cáo bằng tiếng Việt; path file giữ nguyên tiếng Anh
```

---

## §3 — Sau khi có cả hai báo cáo (dev quyết định)

| Kết quả A + B | Hành động |
|---------------|-----------|
| Cả hai không có inject05/20 | GPU rerun 6 job trên Server B; sync cache → dev → `collect_injection_auc` |
| B có đủ cache | Copy `results/cache/*inject*` (+ `pykt_work/.../inject*` nếu cần re-eval) về dev |
| Chỉ có graph CSV, không ckpt | Rerun train 6 job (graph tái dùng) |
| Có log nhưng không ckpt | Ghi provenance; vẫn cần rerun trừ khi log chứa AUC đủ 6 dòng |

**Manuscript:** Chỉ cập nhật §4.3 / Table S18 leak columns khi có số verified — không ngoại suy từ placeholder.

**Script thu thập (dev):** `python -m scripts.collect_injection_auc`

---

## Ghi chú nội bộ

- Server A prompt: tập trung log local, mock scripts, git history workstation
- Server B prompt: tập trung `pykt_work`, GPU log, ckpt primary thiếu trên A
- Báo cáo GKT batch (`docs/GKT_Hyperparams_Review_Report.md`) **chưa** cover injection — hai báo cáo mới bổ sung phần đó
