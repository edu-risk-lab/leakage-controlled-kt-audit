# Kế hoạch sửa paper APIN — "Conditional Harm" reframe + DDR downstream fix

> Nguồn: nhận xét giáo sư hướng dẫn (hai điểm A4 + A5/C2). Tài liệu này biến nhận
> xét thành một kế hoạch theo dõi, có thể tick dần. Draft text cho paper viết bằng
> tiếng Anh; phần thảo luận bằng tiếng Việt.
>
> File paper: `paper/main_APIN.tex`. Ánh xạ số bảng giáo sư dùng:
> - **"Table 9"** = `tab:graph-ablation` (§4.5, `results/tables/graph_ablation.tex`) — null ≤0.003.
> - **"Table 11"** = `tab:ddr-downstream` (§4.7, `results/tables/ddr_downstream.tex`) — DGEKT-only, r=0.13–0.15.
> - **"§4.3 injection"** = `sec:exp-injection`, bảng phụ S17 (`leak_injection.tex`) + S18 (`downstream_auc_injection.tex`).

---

## 0. Insight gốc: hai nhận xét → một gốc, một thí nghiệm

- **Gốc chung:** Cả hai null-result (≤0.003 và r=0.13) đều xảy ra vì kênh graph bị
  **bóp nghẹt** — hoặc filter gắt (throughput≈0), hoặc backbone trơ (reliance≈0,
  DGEKT). KHÔNG phải vì "leakage vô hại" hay "DDR vô dụng".
- **Lời giải chung:** một thí nghiệm — **GKT (+GIKT) chạy DDR→AUC sweep có positive
  control trên XES3G5M** — vừa lấp nhân tố *reliance* cho mô hình hai nhân tố (A4),
  vừa sửa lỗi "test sai backbone" (A5/C2). Một mũi tên, hai con chim.
- **Dữ liệu chưa khai thác:** bảng S18 (`downstream_auc_injection.tex`) cho thấy
  **GIKT cũng dịch +0.028** dưới injection 20% (0.852→0.880), không chỉ GKT (+0.05).
  ⇒ Đã có **hai** backbone graph-reliant trên trục reliance. Phải tận dụng.

---

## 1. Khung lập luận mới: "Conditional Harm" (mô hình hai nhân tố)

**Luật:** harm lên AUC ≈ **throughput** (held-out mass thực sự lọt vào edge set
được tiêu thụ) × **reliance** (mức backbone dựa vào graph). Một nhân tố ≈ 0 ⇒ harm
≈ 0 dù provenance vẫn có leakage. ⇒ AUC là chuông báo tồi (chỉ kêu khi cả hai cao).

- **Throughput** ← filter (q=0.95, top-k=5, K=5000), loại quan hệ, mật độ/độ dư thừa
  transition. Filter càng gắt ⇒ throughput càng thấp.
- **Reliance** ← backbone: simpleKT≈0, GKT>0, GIKT>0 (S18), DGEKT≈0 (Table 11).

### 1.1. Câu thesis (thả vào cuối Introduction)

```latex
Graph-mediated leakage shifts headline AUC only when two factors are
simultaneously high: the \emph{throughput} of contamination into the consumed
edge set, and the \emph{reliance} of the backbone on graph structure. Because
AUC stays silent at every other configuration, it cannot serve as a leakage
alarm; this is precisely why an audit layer that measures throughput
\emph{independently of accuracy} is necessary.
```

### 1.2. Bảng 2×2 (bằng chứng trung tâm — đặt sau §4.3 hoặc đầu §5.1)

Đã đủ cả 4 ô trong dữ liệu hiện tại:

|                                   | reliance thấp (simpleKT) | reliance cao (GKT, GIKT)            |
|-----------------------------------|--------------------------|-------------------------------------|
| throughput thấp (full-log pooling)| ~0                       | ≤0.003 (Table 9)                    |
| throughput cao (20% test-fold inj)| ~0 (0.850→0.858)         | +0.05 GKT, +0.03 GIKT (S17–S18)     |

LaTeX để chèn:

```latex
\begin{table}[t]
\centering
\caption{Two-factor interaction: graph-mediated leakage shifts AUC only in the
high-throughput $\times$ high-reliance cell. Rows are contamination
\emph{throughput} into the consumed edge set; columns are backbone
\emph{reliance} on the graph. Entries are observed $\Delta$AUC on XES3G5M.}
\label{tab:two-factor}
\footnotesize
\begin{tabularx}{\linewidth}{@{} >{\RaggedRight\arraybackslash}p{0.34\linewidth}
  >{\centering\arraybackslash}X >{\centering\arraybackslash}X @{}}
\toprule
 & low reliance (\textit{simpleKT}) & high reliance (GKT, GIKT) \\
\midrule
low throughput (train-only vs.\ full-log pooling) &
  $\approx 0$ &
  ${\leq}0.003$ (Table~\ref{tab:graph-ablation}) \\
high throughput (20\% test-fold injection) &
  $\approx 0$ ($0.850{\to}0.858$) &
  $+0.05$ GKT, $+0.03$ GIKT (Tables~S17--S18) \\
\bottomrule
\end{tabularx}
\end{table}
```

Điểm mạnh phải viết rõ: **cùng backbone GKT cho ~0 dưới pooling thật nhưng +0.05
dưới injection** ⇒ throughput là "knob" thật; điểm vận hành thực tế rơi vào hàng
throughput-thấp **vì filter gắt**, không phải vì leakage vô hại theo quy luật.

### 1.3. Mỗi null-result cũ → bằng chứng dưới khung mới

- **≤0.003 (§4.5):** không còn "leakage vô hại" mà là **phép đo định vị** — 3
  benchmark ở ô throughput-thấp, **vì filter bóp nghẹt kênh**. Output hữu ích cho
  practitioner: "rủi ro thấp ở đây, có bằng chứng".
- **§4.3 injection:** từ "metric-sensitivity check" → **bằng chứng trung tâm**.
  TBMR + builder-mass tăng đơn điệu theo throughput trong khi ECRflag=0 câm ⇒ audit
  phát hiện trước, AUC mù.
- **Table 11 (DGEKT):** sau khi sửa → **mỏ neo reliance≈0**, không phải kết luận về DDR.

---

## 2. Thí nghiệm BẮT BUỘC (lấp đồng thời A4-reliance + A5/C2)

### 2.1. Thiết kế cốt lõi

| Thành phần | Spec |
|---|---|
| Backbone chính | **GKT** trên **XES3G5M** (đã biết graph-sensitive qua §4.3) |
| Backbone lượt hai | **GIKT** (S18 gợi ý graph-reliant) |
| Operator | **edge_drop / prereq_preserve / node_drop** |
| Strength p | {0.10, 0.20, 0.30} |
| Seeds | ≥3, **retrain** (giữ retrain để so được với Table 11) |
| Báo cáo | AUC ≥4 chữ số + **CI giữa seed**; nói thẳng nếu drop chìm dưới noise floor |

Code liên quan: `scripts/plot_ddr_downstream.py`, `scripts/generate_phase_c_tables.py`,
operator §S4 (`sec:supp-operators`).

### 2.2. Positive control / manipulation check — QUAN TRỌNG NHẤT

Thêm **hai mỏ neo** cho mỗi backbone:
1. Graph sạch, DDR=0 → AUC baseline (mỏ neo trên).
2. Graph phá gần hoàn toàn → mỏ neo dưới. Chọn ≥1: `Epre` rỗng / DAG ngẫu nhiên cùng
   kích thước / `node_drop` p rất cao (0.7–0.9).

**Quy tắc diễn giải (định trước):**
- AUC **không động** ngay cả ở mỏ neo dưới ⇒ backbone graph-inert ⇒ lặp lại lỗi
  DGEKT ⇒ báo cáo là **Kết cục C**.
- AUC **dịch rõ** ở mỏ neo dưới ⇒ backbone "đọc" graph ⇒ mới được diễn giải tương quan.

GKT gần như chắc qua (injection +0.05). GIKT chưa chắc — để check tự nói.

### 2.3. Phép so quyết định (thay tương quan gộp)

Contrast paired theo fold, matched budget p:
> "Ở cùng ngân sách xóa cạnh, `prereq_preserve` có làm tụt AUC **ít hơn**
> `edge_drop` không?" — báo `prereq_preserve` vs `edge_drop` vs `node_drop` tại từng
> p, paired theo fold, kèm CI. Đây mới là bằng chứng C2 đang thiếu.

### 2.4. Ghép A6 — reachability disruption

Chạy song song hai tương quan: (DDR thô) vs AUC-drop, và (`1 − reachability-F1`) vs
AUC-drop. Nếu reachability-disruption dự báo tốt hơn DDR thô ⇒ phát hiện có giá trị
(model quan tâm thuộc tính cấu trúc nào) ⇒ trả lời cả A5 lẫn A6.

### 2.5. Ba kết cục — định trước, mỗi cái buộc bài làm gì

- **A** — graph-sensitive: DDR cao → AUC-drop lớn (đơn điệu, ý nghĩa) + `prereq_preserve`
  tụt ít hơn `edge_drop` ở matched budget ⇒ claim C2 chứng thực; "DDR as design target"
  (§4.6) chính đáng. **Mạnh.**
- **B** — qua manipulation check NHƯNG DDR không dự báo / `prereq_preserve` ≈ `edge_drop`
  ⇒ **null hợp lệ, công bố được**; hạ giọng: "DDR là hạ tầng cấu trúc/reproducibility;
  không tìm thấy hệ quả accuracy trên backbone đã test" — **gỡ "design target"**.
- **C** — GKT/GIKT cũng graph-inert ⇒ **phát hiện meta**: graph-KT model trên benchmark
  này không dùng graph prerequisite ⇒ **giải thích luôn null ≤0.003 của A4** ⇒ định
  hình lại toàn bài. Phải kiểm chứ không né.

### 2.6. Phạm vi tối thiểu khả thi

GKT trên XES3G5M, 3 operator, 3 p, 2 mỏ neo manipulation-check, ≥3 seeds, retrain.
GKT-trên-Junyi bỏ được (graph dày). GIKT là lượt hai.

### 2.7. Trạng thái: ĐANG CHẠY trên GPU server qua `docs/DDR_DOWNSTREAM_GKT.md`

`scripts/ddr_downstream.py` + playbook `docs/DDR_DOWNSTREAM_GKT.md` CHÍNH LÀ hiện
thực 2.x. Đã sửa đúng lỗi "test sai backbone" (chạy `--model gkt` thay DGEKT).

**Đã khớp:** GKT, XES3G5M+ASSIST, edge/node/prereq, p=0.10/0.20/0.30, baseline
DDR=0 (mỏ neo TRÊN), retrain, tương quan + paired contrast, reliance profile cho A4.

**Còn thiếu so với yêu cầu giáo sư (cần bổ sung TRƯỚC khi server xong, kẻo chạy lại 12–24h):**
- [x] **Mỏ neo DƯỚI / positive control (QUAN TRỌNG NHẤT):** ĐÃ thêm anchor `edge_drop`
  & `node_drop` @ p=0.90 (≈ Epre rỗng = graph-inert check) trong
  `scripts/run_ddr_downstream_gkt_multiseed.sh`. KHÔNG cần sửa code lõi.
- [x] **≥3 seeds (CI + noise floor + power ANOVA 6.1):** ĐÃ làm — runner mới loop
  seed {42,17,1234}, mỗi seed một CSV riêng `..._seed<NN>.csv` (tránh footgun
  `_load_done` dedupe không có seed). Aggregate offline theo seed×fold.
- [x] **Reachability-disruption (A6):** ĐÃ viết `scripts/reachability_disruption.py`
  (offline, reconstruct từ `e_pre_train_only.csv`, self-check DDR, in tương quan
  DDR-vs-AUC và reach-vs-AUC cạnh nhau). Helper `reachability_f1` thêm vào
  `src/dag_disruption.py`. KHÔNG cần GPU/retrain.
- [ ] **GIKT KHÔNG chạy được qua DDR sweep** (tiêu thụ bipartite Q–C, không đọc Epre →
  script từ chối). Reliance của GIKT lấy từ injection S18 (0.852→0.880); ghi rõ là GIKT
  không nằm trong DDR table. Backbone thứ hai trong sweep nếu cần: skt/dygkt (có thể inert).

**Deliverables vừa tạo (Bước "tiếp tục"):**
- `scripts/run_ddr_downstream_gkt_multiseed.sh` — runner đa-seed + anchor (gửi lên server).
- `scripts/reachability_disruption.py` — A6 offline + bảng tương quan.
- `src/dag_disruption.py` — thêm `reachability_pairs`, `reachability_f1`.
- **Lệnh server:** `bash scripts/run_ddr_downstream_gkt_multiseed.sh`
  (hoặc `DATASETS="configs/xes3g5m.yaml" bash ...` cho primary trước).
- **Lưu ý compute:** thêm anchor + 3 seeds tăng tổng số run; nếu hạn chế GPU, chạy
  XES3G5M trước (primary), ASSIST sau.

**Map kết cục → cột "Kịch bản" trong playbook §8:** A = r>0.3 & drop theo DDR; B = qua
manipulation-check nhưng null; C = GKT cũng inert (chỉ kết luận được khi CÓ mỏ neo dưới).

---

## 3. Sửa từng phần của bài (checklist + draft text)

### 3.1. Abstract — [ ]
Xóa câu kết "A deliberate full-log graph variant shifts headline metrics by at most
$0.003$... not as a route to higher headline accuracy." Thay bằng:

```latex
We find that graph-mediated leakage shifts headline AUC only when contamination
\emph{throughput} into the consumed edge set and backbone \emph{reliance} on the
graph are simultaneously high. On the three public benchmarks, an aggressive
support filter holds throughput low, so a deliberate full-log variant moves AUC
by at most $0.003$; a controlled injection that raises throughput shifts a
graph-reliant backbone (GKT) by ${\approx}0.05$ while a sequence-only baseline
is unmoved. Because AUC is silent in three of four throughput$\times$reliance
regimes, it is an unreliable leakage alarm; the audit instead measures
throughput directly (builder mass, $\mathrm{TBMR}$) and reports which regime a
corpus occupies before accuracy could reveal it.
```

### 3.2. Introduction — [ ]
- Sửa motivation (dòng ~166–180): leakage là vấn đề **có điều kiện**, protocol là dụng
  cụ đo điều kiện (không khẳng định "graph leakage là vấn đề reproducibility" như sự
  thật chung).
- Thêm câu thesis (1.1) vào cuối phần đặt vấn đề (~dòng 204–206).

### 3.3. §4.3 Controlled injection — nâng lên "kết quả trung tâm" — [ ]
- Đổi câu mở "To verify that the audit metrics respond..." → đóng khung là **màn trình
  diễn có kiểm soát của ô nguy hiểm** trong bảng 2×2.
- **Thêm GIKT** vào kết luận (0.852→0.880) — trục reliance mạnh gấp đôi.
- Câu thêm:

```latex
This experiment is the controlled realisation of the high-throughput cell in
Table~\ref{tab:two-factor}: both graph-reliant backbones move (GKT
$0.810{\to}0.860$, GIKT $0.852{\to}0.880$) while the sequence-only baseline does
not ($0.850{\to}0.858$). Crucially, builder mass ($|\Epre|\,1162{\to}1417$) and
$\mathrm{TBMR}_f$ ($0.754{\to}0.779$) rise monotonically with throughput while
$\mathrm{ECR}^{\mathrm{flag}}_f$ stays at $0$: the structural audit detects the
contamination channel before AUC does, and the learner-disjoint flag never fires.
```

### 3.4. §4.5 Graph ablation — reframe "throughput thấp do filter" — [ ]
Thay câu kết "Train-only construction is therefore *not* penalising..." bằng:

```latex
We read this null shift as a \emph{measurement of operating regime}, not as
evidence that leakage is harmless. Under our support filter ($q{=}0.95$,
top-$k{=}5$, $K{=}5000$), most edges that survive full-log pooling already
survive train-only construction, so held-out mass has low \emph{throughput} into
the consumed edge set. The ${\leq}0.003$ shift therefore places these three
benchmarks in the low-throughput row of Table~\ref{tab:two-factor}; it is the
filter that throttles the channel here, not a general property of leakage. The
same channel carries ${\approx}0.05$ AUC once throughput is raised by injection
(Section~\ref{sec:exp-injection}).
```

### 3.5. §4.6 DDR "design target" — có điều kiện theo kết cục — [ ]
- Tạm hạ "DDR can therefore serve as a concrete design target" → "structural design
  lever, subject to backbone-specific downstream confirmation (§4.7)".
- Sau thí nghiệm: giữ (A) / gỡ "design target" (B/C).

### 3.6. §4.7 DDR Downstream — viết lại hoàn toàn — [ ] (CHỜ SỐ GPU)
Kéo future-work §5.4 vào đây + mở rộng. Cấu trúc mới:
1. Manipulation check trước (reliance profile từng backbone).
2. Giữ DGEKT như **mỏ neo reliance≈0** (đổi vai, không xóa).
3. Kết quả GKT/GIKT: tương quan DDR↔AUC-drop + contrast paired + reachability (A6).
4. Kết luận theo A/B/C đã định trước.

Câu chuyển vai DGEKT:

```latex
The DGEKT sweep (Table~\ref{tab:ddr-downstream}) is best read as the
\emph{low-reliance anchor}: destroying $>$50\% of structure
(\texttt{node\_drop}, DDR$=0.555$) moves DGEKT AUC by $0.0001$, so DGEKT's
predictions are effectively independent of the prerequisite graph on these
corpora. A backbone this inert cannot distinguish ``DDR does not predict AUC''
from ``this backbone ignores the graph''; we therefore re-run the same
DDR$\to$AUC protocol on a graph-reliant backbone (GKT) that passes the
manipulation check below.
```

### 3.7. §5.1 Discussion — tổ chức lại H1/H2/H3 quanh hai nhân tố — [ ]
- H1 (leakage) → **throughput hypothesis** (≤0.003 vì throughput thấp do filter).
- H3 (strong-backbone) → **reliance hypothesis** (simpleKT reliance≈0).
- "Why this strengthens the protocol" → lập luận **leading indicator** (xem 3.9).

### 3.8. §5.3 Threats — thêm guardrail trung thực — [ ] (xem Phần 4)

### 3.9. Conclusion — chốt câu cụ thể (leading indicator) — [ ]
Thay "we position the protocol as reproducibility infrastructure" bằng:

```latex
Leakage control is a deployment precondition precisely because AUC is an
unreliable alarm: it moves only when contamination throughput and backbone
reliance are jointly high, and even then it inflates ($0.810{\to}0.860$) rather
than distinguishing inflation from genuine gain. The audit's throughput
indicators (builder mass, $\mathrm{TBMR}$) fire regardless of backbone reliance,
giving practitioners a leading indicator before a contaminated graph is mistaken
for a SOTA improvement.
```

---

## 4. Guardrail — tránh overclaim mới (BẮT BUỘC trong §5.3)

```latex
Two limits bound the conditional-harm claim. First, the high-throughput cell is
reached only by controlled injection; we have not exhibited a natural workflow
(absent deliberate contamination) that raises throughput on these corpora, so
the cell is demonstrated, not shown to be common. Second, the reliance factor
rests on GKT and GIKT (positive) versus \textit{simpleKT} and DGEKT
(${\approx}0$); the interaction is an illustration backed by two graph-reliant
backbones rather than an exhaustive characterisation.
```

Hai giới hạn phải nói thẳng:
1. Chưa có workflow thực tế (không injection) rơi vào ô throughput cao. Muốn kín:
   filter lỏng-phổ-biến, dataset graph dày hơn, hoặc tái dựng pipeline graph-KT cũ.
2. Reliance mới có GKT(+GIKT) dương, simpleKT/DGEKT≈0. Muốn interaction *chắc* cần ≥2
   graph-reliant backbone chạy ở cả hai mức throughput (chính là thí nghiệm 2.x).

---

## 5. Thứ tự thực hiện

- [ ] **B1. Chạy thí nghiệm 2.x trước** (GKT/XES3G5M + manipulation check). Quyết định
  Kết cục A/B/C. KHÔNG viết §4.6/§4.7/§5.1 kết luận trước khi có số.
- [ ] **B2. Viết phần an toàn với mọi kết cục** (làm song song khi chờ GPU): Abstract
  (3.1), thesis (3.2), bảng 2×2 (1.2), §4.3 (3.3), §4.5 (3.4), Conclusion (3.9),
  guardrail §5.3 (4). ~70% khối lượng text, an toàn.
- [ ] **B3. Có số → điền §4.7 (3.6), chốt §4.6 (3.5), hoàn thiện §5.1 (3.7).**
- [ ] **B4. Thêm GIKT (lượt hai)** nếu compute cho phép → củng cố trục reliance.
- [ ] **B5. Cập nhật bảng** `ddr_downstream.tex` + bảng reliance/manipulation-check +
  figure DDR↔AUC cho GKT.

---

## 6. Yêu cầu Giáo sư 2 (ANOVA / ví dụ / leakage↔cold-start / mã giả)

Cả 4 đều đáp ứng được. ANOVA + leakage↔cold-start phục vụ bởi đúng thí nghiệm 2.x
(không phát sinh compute mới); ví dụ + mã giả thuần viết (0 compute).

### 6.1. Thêm kiểm định ANOVA — [ ]
- Hiện trạng: đã có S19–S20 (`anova_baseline.tex`, `anova_ddr_downstream.tex`) nhưng
  *exploratory*, n=3 folds/ô → underpowered (bài tự hạ xuống "descriptive").
- Cách làm: thí nghiệm 2.x (GKT/GIKT, ≥3 seeds × 3 folds = 9 obs/ô) → ANOVA **có power**:
  DV = AUC-drop; factors = `operator × strength(p) × backbone`. Là kiểm định cho phép so
  `prereq_preserve` vs `edge_drop`. Thêm định lượng interaction throughput × reliance
  (bảng 2×2). Lưu ý: chỉ có nghĩa khi có manipulation-check anchors.
- Liên kết: trùng khít thí nghiệm 2.x của Giáo sư 1.

### 6.2. Thêm ví dụ — [ ] (0 compute)
- Worked example một cạnh leak `c_i→c_j` với support count (throughput cấp cạnh).
- Injection như case study đi từng bước (|Epre| 1162→1417, GKT 0.810→0.860; S17/S18).
- Ví dụ cold-start × leakage (xem 6.3).

### 6.3. Liên hệ Leakage ↔ cold-start — [ ]
- Hiện trạng: hai diagnostic đang tách rời, chưa nối.
- Lý luận nối: KC cold-start = ít tương tác train ⇒ neighbourhood thưa ⇒ mỗi cạnh leak
  từ test-fold có trọng số tương đối lớn hơn ⇒ **throughput cục bộ cao nhất ở KC cold-start**.
  Cold-start là nơi leakage *bite* mạnh nhất ⇒ củng cố khung conditional-harm.
- Cách làm:
  - Tối thiểu (0 compute): 1 subsection lý luận + 1 ví dụ nối hai khái niệm.
  - Mạnh (ít compute, tái dùng injection): phân tích **ΔAUC dưới injection theo stratum
    cold/warm/hot**; kỳ vọng dịch chuyển tập trung ở stratum cold.

### 6.4. Thêm mã giả (pseudocode) — [ ] (0 compute)
- Hiện trạng: KHÔNG có algorithm nào (chưa load `algorithm`/`algpseudocode`).
- Thêm: Alg 1 = train-only fold-specific graph construction + DAG audit (Johnson cycle
  pruning); Alg 2 = leakage audit (ECR^flag, ECR^overlap, TBMR); Alg 3 = DDR (Eq. sẵn có).

---

## 7. Tiến độ

| Mục | Trạng thái |
|---|---|
| Thí nghiệm 2.x (GKT) | **ĐANG CHẠY** trên GPU server (`docs/DDR_DOWNSTREAM_GKT.md`) — 1 seed, thiếu mỏ neo dưới |
| Thí nghiệm 2.x (GIKT) | KHÔNG khả thi qua DDR sweep (bipartite Q–C); reliance lấy từ injection S18 |
| Manipulation check anchors | **SCRIPT SẴN SÀNG** (`run_ddr_downstream_gkt_multiseed.sh`, anchor p=0.90) — chờ chạy server |
| Multi-seed (≥3) | **SCRIPT SẴN SÀNG** (seed 42/17/1234, CSV riêng mỗi seed) — chờ chạy server |
| Reachability-disruption (A6) | **SCRIPT SẴN SÀNG** (`reachability_disruption.py`, offline) — chờ data 2.x |
| Text B2 (an toàn) | **ĐÃ XONG** (Abstract, thesis, bảng 2×2, §4.3, §4.5, Conclusion, guardrail §5.3) |
| Text B3 (phụ thuộc kết cục) | chờ số |
| ANOVA có power (6.1) | chờ số 2.x |
| Ví dụ (6.2) | **ĐÃ XONG** (worked edge-leak ở Intro + injection case study ở §4.3) |
| Leakage↔cold-start (6.3) | **ĐÃ XONG mức lý luận** (§5.2 paragraph + ví dụ số); phân tích ΔAUC-theo-stratum vẫn chờ |
| Mã giả (6.4) | **ĐÃ XONG** (Alg 1 graph build+DAG audit, Alg 2 leakage audit, Alg 3 DDR) |

### Ghi chú build
- Đã thêm `\usepackage{algorithm}` + `\usepackage{algpseudocode}` (sau `float`).
- Chưa compile được trong môi trường này (shell không trả output). Cần chạy
  `pdflatex → bibtex → pdflatex → pdflatex` để kiểm tra, đặc biệt tương thích
  `algorithm` với `sn-jnl.cls` và các forward-ref `tab:two-factor` / `tab:graph-ablation`.
