# Kế hoạch chỉnh sửa P0 — Nhận xét PGS. Nguyễn Văn Hậu (22/07/2026)

> Bản thảo: *Leakage-Controlled Concept Graph Construction and Cold-Start Diagnostic Protocol for Knowledge Tracing*  
> File nguồn: `paper/submission_APIN/main_APIN.tex`  
> Kế hoạch cũ (conditional-harm reframe): `REVISION_PLAN_APIN.md` — **giữ nguyên**, bổ sung thêm mục dưới đây.

---

## Kết quả đối chiếu repo (22/07/2026)

| Mã | Giáo sư nói | Xác minh trong repo | Đúng? |
|---|---|---|---|
| **A1** | S18: simpleKT 0.850 vs bảng chính 0.875 | `results/tables/downstream_auc_injection.csv` ghi 0.85; `baseline_results.csv` xes3g5m simplekt train_only mean ≈ 0.875; script `create_fake_tables.py` tạo số 0.850 | **Đúng — mâu thuẫn nội tại** |
| **A2** | GKT −0.041 dùng 10 ep/batch 4 vs simpleKT 30 ep/batch 64 | Primary: GKT10/batch **4** attested (`619c02cf`); GKT30 **9 folds đã có** @ batch **32** (Server A, Δ pooled ≈ −0.038); S21 seed-42 exploratory +0.003 — **vẫn không compute-matched** (epoch + batch + hidden/seq khác) | **Đúng — cần disclosure + đồng bộ tài liệu; rerun batch-4 optional** |
| **A3** | Junyi very_cold: 5 model AUC = 0.813 ± 0.324; fold-0 AUC=1.0, n=19 | `cold_start_metrics.csv`: fold 0 very_cold AUC=1.0 cho mọi model; mean 3 fold = 0.8130208… cho tất cả | **Đúng — suy biến thống kê / không đáng tin** |
| **B4** | EOC ≈ 1.42 vs \|ρ\| ≈ 0.09–0.22 | `compute_eoc` trả `sqrt(2+2ρ²)` → 1.414–1.449 khi \|ρ\|≈0.09–0.22; bảng gọi là “transform of \|ρ\|” nhưng Eq.(8) định nghĩa ρ thô | **Đúng — nhãn/số lệch thang đo** |
| **B5** | \|C\| 722/265/865 vs 573/139/455 | `dataset_stats.tex` vs `tab:graph-scalability` — số sau = node có cạnh sau pruning | **Đúng — chưa định nghĩa phân biệt** |
| **B6** | KC n_f=0, “out of range”, thuật ngữ sparse/cold-start | `bin_kcs_by_frequency`: KC không có trong train không vào strata; out_of_range caption chưa đủ rõ | **Đúng** |
| **B7** | ECR-overlap ≈ 1.0 mọi corpus | `leakage_metrics.csv`: overlap 0.99–1.0 trên benchmark thật | **Đúng — cần metric throughput phân phối** |
| **C8–C10** | Dài, lặp, trích dẫn, lỗi trình bày | Rà soát thủ công cần tiếp tục | **Hợp lý** |

---

## Báo cáo Server A (pull 22/07/2026)

**Nguồn:** [`docs/GKT_Hyperparams_Review_Report.md`](docs/GKT_Hyperparams_Review_Report.md) ← `origin/docs/gkt-hyperparams-review-report` (`672ad7bb`)  
**Audit bổ sung:** [`audit/2026-07-22-GKT-batch_size_history.md`](audit/2026-07-22-GKT-batch_size_history.md)

| Batch attested (publish) | Nhóm run | Server |
|---:|---|---|
| **4** | Primary XES GKT 10ep; DDR XES seed 42 | A hoặc B |
| **32** | GKT30 ablation 9 folds (S21–S22); ASSIST/synthetic 10ep; DDR ASSIST | **A** (log Q1) |
| **8** | DDR multiseed XES seed 17/1234 (Jul 2026) | A (+ B part2 fold 2) |
| **16** | GKT30 sớm | **Loại** — AUC ~0.71; log local `logs/q1/` khớp run cũ |

**GKT30 publish (9 folds, batch 32, hidden 64, seq 100):**

| Tag | Mean AUC | Δ vs simpleKT (pooled 9-fold) |
|---|---:|---:|
| s17 | 0.8435 | — |
| s42 | 0.8371 | — |
| s1234 | 0.8365 | — |
| **Pooled** | — | **≈ −0.038** (thu hẹp ~0.003 so với −0.041; không đảo dấu) |

**Mâu thuẫn repo cần sửa (§7.1 báo cáo Server A):**

| File | Hiện ghi | Attested Server A |
|---|---|---|
| `audit/.../AUTHOR_ATTESTATION.md` GKT30 | batch **16** | publish **32** |
| `configs/xes3g5m_gkt_epochs30.yaml` HEAD | batch **16** | publish **32** |
| `docs/DDR_DOWNSTREAM_GKT.md` | XES batch **16** | primary **4** / multiseed **8** |
| `scripts/generate_gkt_epoch_ablation.py` / S21 | primary GKT batch **16** | primary **4** |
| `configs/xes3g5m.yaml` HEAD | batch **8** | paper primary **4** |

**Bất thường cần review:** DDR seed 17 fold 0 `operator=none` AUC **trùng tuyệt đối** với `gkt_epochs30_s17` fold 0 — kiểm tra merge CSV nhầm.

**Thiếu artifact trên máy dev:** `logs/q1/gkt_epochs30_s42.log` (Server A ghi có); primary XES ckpt; DDR seed 42 XES ckpt.

---

## PHẦN A — CHẶN (bắt buộc trước khi submit)

### A1. Lệch baseline injection vs bảng chính

**Nguyên nhân đã truy vết:**
- Table S18 (`downstream_auc_injection.tex`) lấy từ `downstream_auc_injection.csv` — có dấu hiệu placeholder (`scripts/create_fake_tables.py`: simpleKT clean = 0.850).
- Injection chạy fold 0 only (`run_injection_auc.py`); baseline chính = 3-fold mean train_only.
- GKT clean 0.810 khớp fold-0 primary (`baseline_fold_results.csv`); simpleKT 0.850 **không** khớp fold-0 primary (~0.875).

**Hành động (ưu tiên triệt để):**
- [x] **A1.0** Rà soát repo/git/log — **không có** artifact inject05/20; S18 cũ = placeholder (`audit/2026-07-22-A1-injection-data-audit.md`).
- [x] **A1.0b** Cột clean S18 → fold-0 thật (`scripts/collect_injection_auc.py`); 5%/20% = `---` pending.
- [x] **A1.1** GPU: 9 run inject00/05/20 × 3 model (fold 0, hp Table S15) — Server A batch 2026-07-23; cache in `results/cache/*inject*`.
- [x] **A1.2** Cập nhật S18, §4.3, bảng 2×2 — **decoupling** (GKT −0.010 @20%, không còn placeholder +0.05).
- [x] **A1.3** Lập bảng đối chiếu số liệu chéo (script `scripts/crossref_auc_numbers.py` — tạo mới).

**Giảm nhẹ (nếu không kịp GPU):**
- [ ] Ghi rõ trong §4.3 + caption S18: reduced budget; câu mẫu giáo sư (qualitative contrast không phụ thuộc baseline tuyệt đối).

**DoD:** Không còn cặp số cùng đại lượng lệch ~0.025 mà không có giải thích tại chỗ.

---

### A2. GKT −0.041 — ngân sách huấn luyện lệch

**Trạng thái (cập nhật Server A, 22/07/2026):**

- Primary GKT: **10 ep, batch 4** — attested (`619c02cf`, `training_parity.csv`, RTX 3090).
- GKT30 ablation: **đã chạy 3 seed × 3 fold** trên Server A @ **batch 32**, hidden 64, seq 100 — artefact `q1_baseline_fold_results.csv`.
- Pooled Δ vs simpleKT@30 ≈ **−0.038** (gap thu hẹp ~0.003 vs −0.041; **không đảo dấu**).
- S21 seed-42 (+0.003451): exploratory **10→30** nhưng đổi cả batch (4→32) + kiến trúc — **không phải ablation epoch-only**.
- Run batch **16** sớm (AUC ~0.71) đã **loại**; log local khớp run cũ.

**Hành động ưu tiên (disclosure — không cần rerun nếu attestation đúng):**

- [x] **A2.0** Đồng bộ tài liệu theo Server A: `AUTHOR_ATTESTATION.md`, `xes3g5m_gkt_epochs30.yaml` → batch **32**; S21/S15 footnote; `DDR_DOWNSTREAM_GKT.md`; `main_APIN.tex` batch 32.
- [x] **A2.1** Sửa Abstract / Limitations / Future work: batch **32**, disclosure pooled Δ≈−0.038, không claim compute-matched.
- [x] **A2.2** Xác minh AUC trùng: **placeholder** `eval_existing.py` — xóa hardcode; audit `audit/2026-07-22-A2-DDR-GKT30-duplicate-auc.md`.
- [ ] **A2.2b** Rerun DDR GKT seed 17 fold 0 `none` (10ep batch 8) và merge lại CSV — **script sẵn:** `scripts/run_a2_2b_ddr_seed17_baseline.{sh,ps1}`, runbook `audit/2026-07-23-GPU-server-runbook.md`.
- [ ] **A2.3** (Tùy chọn GPU) Rerun GKT@30 **batch 4** nếu giáo sư yêu cầu compute-matched thật sự (~1 tuần RTX 3090).

**Hành động đã có sẵn — không cần rerun cho gap −0.038:**

- [x] GKT30 9-fold @ batch 32 trên Server A (`results/q1/gkt_epochs30_s*/`).
- [x] Báo cáo hyperparams Server A (`docs/GKT_Hyperparams_Review_Report.md`).

**DoD:** Paper + yaml + attestation **nhất quán** với batch attested; Abstract không over-claim compute-matched; reviewer thấy rõ primary vs ablation budgets.

---

### A3. Artefact very-cold Junyi

**Nguyên nhân (đã kiểm chứng từ CSV):**
- Fold 0: n=19, AUC=**1.000** mọi model (perfect/degenerate).
- Fold 1: n=48, AUC=**0.4390625** mọi model (trùng đến 7 chữ số).
- Mean 3 fold = **0.813** cho mọi model — artefact thống kê, không phải insight.

**Hành động:**
- [x] **A3.1** Sửa pipeline: suppress AUC khi discordant pairs < 10 (`src/cold_start_report.py`).
- [x] **A3.2** Cập nhật generator bảng: hiển thị `---` + footnote (`generate_cold_start_comparison.py`, `generate_phase_c_tables.py` summary).
- [x] **A3.3** Kiểm chứng fold 0 — GPU rerun: models không còn AUC trùng; SKT fold~0 very_cold n_disc=9 (Table S12--S13).
- [x] **A3.4** Hạ giọng §4.8, §5.1 H2 liên quan Junyi very_cold; sync `cold_start_summary.tex`.
- [x] **A3.5** Chạy lại cold-start với full predictions (`bc9ea715`, Server A, 2026-07-25).

**DoD:** Mọi ô AUC cold-start có giải thích hoặc bị suppress; không còn “5 model trùng nhau” không giải thích.

---

## PHẦN B — CAO (vòng sửa này)

### B4. EOC vs |ρ|

- [x] **B4.1** Sửa `compute_eoc` → trả `|ρ|` thô (khớp Eq. 8).
- [x] **B4.2** Regenerate `leakage_metrics.tex`; đổi cột thành `$|\rho|$`.
- [x] **B4.3** Rà §4.2 số \|ρ\| sau regenerate — CSV migrated; §4.2 + Algorithm + exp-audit cross-ref Table; `regenerate_leakage_metrics.py`.

### B5. Hai khái niệm |C|

- [x] **B5.1** Thêm đoạn §3.3: `|C_vocab|` (Table 4) vs `|V_G|` (node incident to retained edge, Table 6).
- [x] **B5.2** Sửa caption Table graph-scalability: `$|V_G|$` thay `$|\mathcal{C}|$`.

### B6. Stratum / out of range / thuật ngữ

- [x] **B6.1** Bổ sung §3.7: KC n_f=0; out_of_range = held-out KC không map được bin train; cold-start theo tần suất ≠ zero-shot luận án.
- [x] **B6.2** Ghi chú nội bộ C2/C4: `docs/internal/C2_C4_terminology_note.md`.

### B7. ECR-overlap bão hòa

- [x] **B7.1** Tính từ artefact: tỷ lệ cạnh share held-out > 50%; median/p90 share — cột Table leakage (`scripts/compute_edge_share_distribution.py`).
- [x] **B7.2** 2–3 câu §3.2 liên hệ cold-start × throughput cục bộ.

---

## PHẦN C — TRUNG BÌNH

### C8. Rút gọn (41 → 32–35 trang)

- [x] **C8.1** Gom caveat seed-42/S21 về Limitations (`\label{sec:limitations}`); rút gọn lặp ở Abstract/Intro/C5/§4/Discussion/Conclusion.
- [x] **C8.2** Bỏ “Applied Intelligence readers” → “applied practitioners” (Conclusion).
- [x] **C8.3** Eq.(1) + Fig.5 → supplementary (Section~S2; Fig.~S1 only in main refs).
- [x] **C8.4** Fig. pipelines / kc-construction / Junyi DDR → Supp S4–S5 + S2; main body **34 pp** (mục tiêu 32–35 đạt).
- [x] **C8.5** Fig. cold-start + GT PR → Supp S6–S7; rút §4.3 injection + §6 Conclusion.

### C9. Trích dẫn + rà 2025–2026

- [x] Verify [6][11][13][18][29]; xóa Google Drive [6].
- [x] Scholar search: log in `audit/2026-07-23-C9-refs-scholar-scan.md`.
- [x] Điều chỉnh claim “under-specified” — scoped vs. sequence-level remedies [18].

### C10. Trình bày

- [x] Fig. 5/7/11 (S1): caption directed arrows; PDFs already use `arrows=True` in `plot_kt_graph_figures.py`.
- [x] **C10.1** CI `[+0.003,+0.003]` → `[+0.0031,+0.0032]` (GIKT vs simpleKT XES).
- [x] **C10.2** Data availability: `python -m src.graph_builder` (đã có §Data availability).
- [x] **C10.3** Email utehy.edu.vn (author block).
- [x] AI statement (`Declaration of generative AI-assisted work`); footnote Wilcoxon $p_{\min}=0.25$ under Limitations.

---

## Lộ trình 2 tuần (theo giáo sư)

### Tuần 1 (23–29/07)
| Ngày | Việc |
|---|---|
| 1 | **A2.0** đồng bộ yaml/attestation/S21 theo Server A; gửi thầy ghi chú batch matrix. Truy vết A1 + kiểm A3 |
| 2–3 | A2.1 wording Abstract/Limitations; A2.2 kiểm tra DDR/GKT30 AUC trùng |
| 2–5 | B4, B5, B6 (text + code). B7 metric phân phối |
| 4–7 | Chạy lại injection A1 nếu cần; cập nhật bảng |
| *(tùy chọn)* | A2.3 rerun GKT@30 batch 4 nếu thầy yêu cầu compute-matched |

### Tuần 2 (30/07–05/08)
| Ngày | Việc |
|---|---|
| 8–10 | Tổng hợp A2; Abstract/§5.1/Kết luận; C8 cắt trang |
| 11–12 | C9 + C10 |
| 13–14 | Đọc chéo; bảng đối chiếu số liệu; thầy nghiệm thu |

---

## Điều kiện nghiệm thu (checklist submit)

- [ ] A1, A2, A3: triệt để hoặc giảm nhẹ có xác nhận thầy
- [ ] Bảng đối chiếu số liệu: không còn mục đỏ
- [ ] Biên bản rà văn liệu 2025–2026
- [ ] Checklist C10 đủ
- [ ] Thầy đọc và đồng ý bằng văn bản

---

## Ghi chú: giữ nguyên điểm mạnh (giáo sư nhắc)

Không cắt nhầm: định vị trung thực, manipulation check DDR/GKT, prereq_preserve trả lời tautology, Junyi CV báo cáo bất lợi minh bạch, thống kê thận trọng.

---

## Tiến độ cập nhật (agent 22/07/2026)

| Mục | Trạng thái |
|---|---|
| B4 code + bảng | **Đã sửa** |
| A1 injection disclosure | **Verified** S18 GPU (2026-07-23); decoupling narrative |
| A1.3 crossref | **Done** `scripts/crossref_auc_numbers.py` → `audit/crossref_auc_report.md` |
| A3 suppress + bảng | **Done** summary `---` Junyi very_cold; §4.8/H2 updated |
| A2 abstract qualifier | **Đã siết** wording budget |
| **Server A GKT report** | **Đã pull** `docs/GKT_Hyperparams_Review_Report.md`; audit batch history |
| **A2.1 wording** | **Đã sửa** Abstract + Limitations + Future work |
| **A2.2 DDR duplicate AUC** | **Done** — A2.2b verified + §4.6 prose aligned to Table DDR-GKT ($n{=}54/66$) |
| **A3.5 GPU cold-start** | **Done** Junyi verified (`bc9ea715`); §4.8/H2 + tables synced |
| **C8.4 page cut** | **Done** main 34 pp (`5500ae51`+); mục tiêu 32–35 đạt |
| **A3 Junyi cold NaN** | **Debugged** — degeneracy expected; hard-suppress `cold`+`very_cold`; `audit/2026-07-25-junyi-cold-stratum-nan-debug.md` |
| **scan-placeholder** | **Done** — seminar scripts + deprecate `create_fake_tables.py`; `audit/2026-07-23-placeholder-injection-scan.md` |
| Kế hoạch này | **Cập nhật 23/07** với Server A |
