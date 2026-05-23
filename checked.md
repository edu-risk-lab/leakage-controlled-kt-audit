# CHECKLIST SUPERVISOR REVIEW — VERIFY BASELINE

| Trường | Giá trị |
|--------|---------|
| **Baseline (đang verify)** | **pyKT toolkit** (`GKT`, `DKT`, `AKT`, `simpleKT`); alias `GIKT`→`AKT` |
| **Dataset neo (ưu tiên)** | **ASSISTments 2012** (có số liệu `pykt_checkpoint` trong repo) |
| **NCS** | Dao Minh Tuan |
| **Repo** | `p0_project` — protocol paper *Leakage-Controlled Concept Graph…* |
| **Commit ghi nhận** | `de5b8967de1efaed283aa84a4280c9e5de38a154` (2026-05-20) |
| **Ngày điền checklist** | 2026-05-20 |

> **Lưu ý quan trọng:** Bài P0 **không** nhằm tái tạo SOTA từng paper GKT/GIKT. Có **hai backend** baseline:
> - `diagnostic` — ensemble tuyến tính (số trong `paper/main.tex` Table baseline, Junyi/XES/ASSIST diagnostic).
> - `pykt` — huấn luyện checkpoint thật qua `pykt-toolkit` (một phần dataset đã chạy).
>
> Checklist supervisor **chỉ PASS** khi so khớp **`pykt`** với paper gốc trên **dataset neo**. Không dùng số `diagnostic` để claim verify paper GKT.

---

## BƯỚC 1 — DATASET NEO

- [x] **Đã xác định dataset neo** (paper gốc có báo cáo)  
  - **Neo:** ASSISTments 2012-13 (`assist2012`, Baker et al.) — ghi trong [`reference.txt`](reference.txt) §A.  
  - **Nguồn số paper:** pyKT toolkit (Liu et al., NeurIPS 2022) + benchmark assistments2012 trên [pykt.org](https://pykt.org/assist2012).  
  - **Lưu ý:** Bảng Table 2 paper pyKT 2022 chỉ có ASSISTments**2009**, không có 2012 — cột `paper` trong `reference.txt` vẫn **VERIFY_REQUIRED**.

- [x] **Đã ghi rõ split, metric, hyperparameter trong `reference.txt`**  
  - **File:** [`reference.txt`](reference.txt) §B (split/metric/hyperparams), §D (bảng so sánh), §F (AS2009 tham chiếu chéo).  
  - **Cột Paper AUC:** chưa điền — chờ run pyKT official hoặc supervisor.  
  - **Tóm tắt config NCS** (`configs/assist2012.yaml`):
    | Mục | Giá trị P0 |
    |-----|------------|
    | Split | Learner-based temporal, ratios `0.7 / 0.1 / 0.2` |
    | Seed | `42` (fold seeds: `42, 43, 44` khi `n_folds: 3`) |
    | Metric | AUC, ACC, NLL trên **valid+test** (sequence positions) |
    | pyKT | `max_seq_len: 200`, `epochs: 30`, `batch_size: 64`, `lr: 0.001` |
    | GKT graph | Adjacency từ `e_pre_train_only.csv` / P0 export (`gkt_graph_tag: p0_protocol`) |

**Hành động tiếp:** Điền cột `paper` trong `reference.txt` §D sau khi có số assist2012 chính thức từ pyKT (không copy AS2009 0.7424 trừ khi supervisor đồng ý).

---

## BƯỚC 2 — MÔI TRƯỜNG

- [x] **Code từ GitHub repo chính thức (hoặc note thay thế)**  
  - Upstream: [pykt-team/pykt-toolkit](https://github.com/pykt-team/pykt-toolkit) — submodule `third_party/pykt-toolkit` @ `4db3fbe681e2bca3e44ea92863a7168234267b92`.  
  - P0 pipeline: `https://github.com/tuanymc/p0_project.git` (local path hiện tại).  
  - **Note thay thế:** `GIKT` không có trong pyKT → map `gikt` → `akt` (ghi trong `baseline_results.csv` cột `note`). `SKT`/`DyGKT`/`DGEKT` dùng config tương tự GKT trong `pykt_engine.py` (không phải paper gốc đầy đủ).

- [x] **`requirements.txt` có pin version**  
  - Có khoảng phiên bản: `numpy>=1.24,<2.0`, `pandas>=2.0,<3.0`, `torch>=2.1,<3.0`, …  
  - **Thiếu:** lock file đầy đủ (`pip freeze`) trong log — nên bổ sung vào `reproduction_log.md`.

- [ ] **Dataset đúng phiên bản**  
  - Raw data **không** có trong git (`data/raw/` chỉ `.gitkeep`).  
  - Cần xác nhận: ASSISTments **2012** (skill-builder), Junyi PSLC DataShop, XES3G5M NeurIPS 2023 — đúng file tên trong `configs/*.yaml`.  
  - Google Drive bundle (README §3) nếu dùng phải ghi version/ngày tải trong log.

---

## BƯỚC 3–4 — VERIFY TRÊN NEO

- [ ] **Đã chạy với hyperparameter mặc định (KHÔNG tinh chỉnh)**  
  - ASSISTments / synthetic_c2 / một phần assist: `status=pykt_checkpoint`, hyperparams từ YAML/pyKT defaults.  
  - **Junyi, XES3G5M (bảng paper chính):** vẫn `status=diagnostic` trong `results/tables/baseline_results.csv` — **chưa verify pyKT trên neo cho 2 dataset này**.

- [ ] **Bảng so sánh có đủ 3 cột: paper | NCS | sai lệch**  
  - Xem bảng dưới (ASSISTments 2012, fold mean / 1 fold — **cần điền cột Paper từ `reference.txt`**).

- [ ] **Mọi metric overall trong ±5%** (cold-start trong ±15%)  
  - **Chưa đánh giá** — thiếu số paper chuẩn.

### Bảng so sánh (ASSISTments 2012 — pyKT backend, train-only graph)

| Model | Paper AUC | NCS AUC | Sai lệch | Paper ACC | NCS ACC | Ghi chú |
|-------|-----------|---------|----------|-----------|---------|---------|
| GKT | *TBD* | 0.9603 | *TBD* | *TBD* | 0.9063 | `n_folds=1` trong CSV dòng mới nhất |
| DKT | *TBD* | 0.9615 | *TBD* | *TBD* | 0.9081 | |
| AKT | *TBD* | 0.9675 | *TBD* | *TBD* | 0.9144 | |
| simpleKT | *TBD* | 0.9674 | *TBD* | *TBD* | 0.9147 | |
| BKT | *TBD* | 0.6710 | *TBD* | *TBD* | 0.7112 | classical BKT EM, không phải pyKT |
| GIKT | *TBD* | 0.9676 | *TBD* | *TBD* | 0.9146 | thực chất = AKT (alias) |

**Cảnh báo:** AUC NCS ~0.96 có thể **cao hơn** paper do khác preprocess/split/đánh giá trên toàn bộ val+test sequence — **bắt buộc** đối chiếu cùng protocol pyKT gốc trước khi kết luận PASS.

### Bảng diagnostic (không dùng để verify paper — chỉ protocol P0)

| Dataset | Backend | simpleKT AUC (NCS) | GKT AUC (NCS) | Mục đích |
|---------|---------|-------------------|---------------|----------|
| Junyi | diagnostic | 0.719 | 0.704 | Bảng `tab:baseline-results` trong paper |
| ASSISTments | diagnostic | 0.697 | 0.604 | Khác hẳn pyKT row ở trên |
| XES3G5M | diagnostic | 0.718 | 0.608 | |

---

## BƯỚC 5 — DIAGNOSTIC (nếu cần)

- [ ] **Nếu FAIL: đã thử fix một nguyên nhân một lần**  
  - Chưa vào vòng FAIL chính thức (chưa có cột Paper).

- [ ] **Đã xác định nguyên nhân thực sự gây sai lệch**  
  - **Ứng viên cần kiểm:** (1) learner split P0 vs paper; (2) `max_seq_len=200`; (3) graph P0 train-only vs graph paper; (4) GIKT≠GIKT paper; (5) diagnostic vs pyKT nhầm lẫn khi đọc bảng.

- [ ] **Sau fix, đã chạy lại Bước 3 và PASS**

---

## BƯỚC 6 — EXTEND

- [x] **Đã chạy trên đủ dataset của bài hiện tại**  
  - Junyi, ASSISTments 2012, XES3G5M (+ synthetic C2/C5 cho test pipeline).  
  - Graph: train-only + full_log ablation (`results/tables/graph_ablation_summary.csv`).

- [x] **Sanity check pass: kết quả hợp lý**  
  - `pytest -q` (unit tests leakage/graph).  
  - DAG audit acyclic; `ECR_flag=0`; cold-start strata exported.  
  - Diagnostic ordering: simpleKT ≥ GKT trên 3 benchmark (đúng narrative paper).

- [ ] **Số seed phù hợp giai đoạn**  
  - Split seeds: 3 folds (`42, 43, 44`) — **đạt cho protocol**.  
  - Augmentation DDR: seeds `[42, 17, 1234]` × 3 folds.  
  - **Verify baseline paper:** ASSIST pyKT hiện `n_folds=1.0` — **chưa đủ 5 seed cho final**; Junyi/XES pyKT full run **chưa hoàn**.

---

## BƯỚC 7 — DOCUMENT

- [x] **`reproduction_log.md` đầy đủ và update** (khung + snapshot hiện tại)  
  - **File:** [`reproduction_log.md`](reproduction_log.md) — commit hash, lệnh chuẩn, issues §6, run R1 *TODO*.  
  - **Thiếu:** `pip freeze` đầy đủ trên Python 3.10/3.11; hoàn tất run R1 (3 folds pyKT neo).

- [x] **Code đã commit, có hash trong log**  
  - Hash: `de5b8967de1efaed283aa84a4280c9e5de38a154`  
  - Submodule pyKT: `4db3fbe681e2bca3e44ea92863a7168234267b92`

- [x] **Vấn đề và cách giải quyết được ghi rõ (một phần)**  
  - README §8 Troubleshooting; `scripts/GRAPH_ABLATION_EXPERIMENT.md`; `baseline_runner.py` docstring (diagnostic vs pykt, GIKT alias).  
  - **Thiếu:** log tập trung một file `reproduction_log.md`.

---

## TÀI LIỆU THAM CHIẾU TRONG REPO

| Artefact | Đường dẫn |
|----------|-----------|
| **Anchor / verify spec** | [`reference.txt`](reference.txt) |
| **Reproduction log** | [`reproduction_log.md`](reproduction_log.md) |
| Kết quả baseline | `results/tables/baseline_results.csv`, `baseline_fold_results.csv` |
| Bảng paper | `results/tables/baseline_results.tex` |
| Graph ablation | `results/tables/graph_ablation_summary.csv` |
| Cold-start | `results/tables/cold_start_metrics.csv` |
| Config | `configs/junyi.yaml`, `assist2012.yaml`, `xes3g5m.yaml` |
| Báo cáo tổng hợp | `results/reports/p0_diagnostic_report.md` |

---

## QUYẾT ĐỊNH

- [ ] **PASS** — chuyển sang baseline tiếp theo  
- [x] **CẦN ĐIỀU CHỈNH** — NCS làm lại theo feedback  
- [ ] **CẦN THẢO LUẬN** — họp supervisor để cùng quyết định  

### Lý do chọn *CẦN ĐIỀU CHỈNH*

1. Cột **paper** trong `reference.txt` §D chưa điền (VERIFY_REQUIRED).  
2. Chưa tính **sai lệch %** và PASS ±5% trên neo.  
3. Verify pyKT trên neo (ASSISTments) chưa đối chiếu ±5%; Junyi/XES chưa chạy pyKT cho bảng verify.  
4. `n_folds=1` cho một số run ASSIST pyKT — chưa đủ cho giai đoạn final (5 seed).  
5. Cần tách rõ khi báo cáo supervisor: **diagnostic** (protocol) vs **pyKT** (verify paper).

### Việc làm tiếp theo (đề xuất thứ tự)

1. Điền cột `paper` trong `reference.txt` §D từ pyKT assist2012 benchmark (xem `reproduction_log.md` §8).  
2. Chạy **R1** trong `reproduction_log.md`: `baseline_runner` assist2012, `n_folds: 3`, pykt backend.  
3. Điền bảng sai lệch; nếu FAIL >5%, fix **một** nguyên nhân (ví dụ chỉ `max_seq_len` hoặc chỉ split) rồi chạy lại.  
4. Lặp cho `simpleKT`, `GKT` trên neo; sau đó mở rộng Junyi/XES nếu supervisor yêu cầu.  
5. Khi PASS neo → tick PASS và chuyển baseline tiếp (ví dụ GKT paper gốc nếu khác pyKT config).

---

*Checklist generated from repository state on 2026-05-20. Cập nhật lại sau mỗi lần chạy verify.*
