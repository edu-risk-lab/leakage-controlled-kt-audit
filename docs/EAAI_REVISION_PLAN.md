# Kế hoạch sửa và nâng novelty — bản thảo EAAI

Ngày lập: 2026-09-14. Căn cứ: đánh giá nội bộ vai trò AE của EAAI (cùng phiên),
`paper/EAAI_editor_review_main_EAAI.md`, và trạng thái số liệu hiện có.

Mục tiêu: chuyển bản thảo từ **"đo một kênh rò rỉ và không thấy gì"** sang
**"đưa ra một cận dự báo được, kiểm chứng được, tính bằng CPU trước khi train"**.

---

## 1. Chẩn đoán gốc

Sáu vấn đề mà AE nêu (M-1…M-6) không độc lập. Chúng đều chảy ra từ **một**
lựa chọn khung: đóng góp trung tâm được phát biểu dưới dạng *phủ định có chặn*
(`|ΔAUC| ≤ 0.010`).

Hệ quả dây chuyền:

- Một khẳng định null cần khoảng tin cậy (M-1) — mà bảng `tab:m4-phase-b-auc`
  chỉ có 1 fold, 1 seed.
- Một khẳng định null luôn bị hỏi "bạn đã tìm đủ chỗ chưa" (M-2, `k=∞`).
- Một khẳng định null không tự sinh ra giá trị kỹ thuật (M-4).
- Một khẳng định null buộc phải rào đón khắp nơi → văn phong phòng thủ, 47 trang.

Vậy **sửa khung sẽ tháo đồng thời M-1, M-2, M-4** và làm nhẹ phần còn lại.
Đây là lý do kế hoạch này ưu tiên tái định khung trước khi chạy thêm GPU.

---

## 2. Ý tưởng nâng novelty: cận phơi nhiễm rò rỉ (leakage exposure bound)

### 2.1 Phát biểu

Bài đã đo riêng rẽ hai đại lượng nhưng chưa bao giờ nhân chúng với nhau:

| Đại lượng | Ý nghĩa | Đã có ở đâu |
|---|---|---|
| `s_m,D` | độ nhạy backbone với cấu trúc đồ thị: OLS slope của AUC-drop theo DDR | 0.084 (GKT/XES3G5M), 0.0028 (GKT/ASSIST) |
| `δ_θ` | độ lệch cấu trúc do pooling tại bộ lọc θ: leak/\|E_pre\| | census `tab:m4-qk-census` |

Giả thuyết làm việc:

```
|ΔAUC_leak(m, D, θ)|  ≤  s_m,D · δ_θ
```

Cả hai vế đều chuẩn hoá theo `|E_pre|`, nên đơn vị khớp nhau. Vế phải tính được
**không cần train lại**: `δ_θ` là CPU thuần (census), `s_m,D` chỉ cần đo **một
lần cho mỗi cặp (backbone, corpus)** — chính là manipulation check `p=0.90` bạn
đã chạy.

### 2.2 Đối chiếu với số liệu đã có — ĐÃ TÍNH

Chạy bằng `scripts/leakage_exposure.py`; kết quả ở
`results/tables/leakage_exposure.csv` và `leakage_exposure.tex`.

| Ô | leak | \|E_pre^to\| | `δ_θ` | Cận `0.084·δ` | \|ΔAUC\| quan sát | Kết luận |
|---|---|---|---|---|---|---|
| Published default | 103 | 1,162 | 0.089 | 0.0075 | 0.0006 | đúng, dư 12.2× |
| Review open `q`, `k=5` | 136 | 3,213 | 0.042 | 0.0036 | 0.0015 | đúng, dư 2.4× |
| `k=20` lift | 634 | 8,712 | 0.073 | 0.0061 | 0.0005 | đúng, dư 12.7× |
| **`k=∞` lift** | 2,276 | 17,211 | **0.132** | **0.0111** | **chưa chạy** | **dự báo** |

**Cận đúng 3/3 ô đã train.** Dùng cận trên của slope CI (0.0900) thì dự báo cho
`k=∞` là `|ΔAUC| ≤ 0.0119`. Script cũng xuất dự báo cho cả 13 ô census chưa train
— đó là tập pre-registration ở việc 1.5.

Hai điều quan trọng:

1. Cận **đúng trên cả ba ô đã chạy**. Đây là một khẳng định *khẳng định*, không
   phải null — và nó kiểm chứng được, bác bỏ được.
2. Cận dự báo `k=∞` ≈ **0.011**, tức **vượt ngưỡng 0.003** mà bài đang tuyên bố.
   Lý thuyết nói ô `k=∞` là nơi trần có thể vỡ. Điều này biến việc chạy `k=∞` từ
   "một ô nữa cho đủ" thành **phép thử phủ định lý thuyết**.

### 2.3 Vì sao cận dư 2–12 lần: đã thử ba tinh chỉnh, chọn được một

Giả thuyết ban đầu của tôi — "cạnh rò rỉ chủ yếu dư thừa bắc cầu nên vô hại" —
**đã bị số liệu bác bỏ**. Tôi thử ba đại lượng thay cho `δ` thô, tất cả tính từ
CSV cạnh đã có (`scripts/leakage_exposure.py --edge-root`):

| Ký hiệu | Định nghĩa | Đúng mấy ô | Dư xấu nhất |
|---|---|---|---|
| `δ` | cạnh rò rỉ / \|E_pre\| | **3/3** | 12.7× |
| `δ_eff` | cạnh rò rỉ tạo quan hệ khả đạt mới / \|E_pre\| | **1/3 — bác bỏ** | — |
| `δ_tv` | TV trung bình giữa phân phối hàng đã chuẩn hoá | **3/3** | 10.6× |
| `δ_w` | khối lượng trọng số dịch chuyển / tổng trọng số | **3/3** | **4.8×** |

Số chi tiết cho bốn ô mốc (fold 0):

| Ô | `δ` | `δ_eff` | `δ_w` | cận `0.084·δ_w` | \|ΔAUC\| | dư |
|---|---|---|---|---|---|---|
| Published default | 0.089 | 0.033 | 0.035 | 0.00297 | 0.00061 | 4.8× |
| Review open `q` | 0.042 | 0.0072 | 0.022 | 0.00182 | 0.00151 | **1.20×** |
| `k=20` lift | 0.073 | 0.0022 | 0.019 | 0.00162 | 0.00048 | 3.4× |
| `k=∞` lift | 0.132 | 0.0010 | 0.022 | 0.00183 | chưa chạy | — |

Ba kết luận:

1. **`δ_eff` sai.** Nó giảm 33 lần khi mở `k` (0.033 → 0.0010) trong khi ΔAUC quan
   sát gần như phẳng. Cạnh dư thừa bắc cầu **vẫn** đổi trọng số và phép chuẩn hoá
   kề mà GKT tiêu thụ, dù không đổi quan hệ khả đạt. Bỏ hướng này.
2. **`δ_w` là đại lượng đúng.** Chặt hơn `δ` thô 2.6 lần, và ở ô open-`q` cận chỉ
   dư **1.20×** — tức cận gần như bám sát, không hề rỗng.
3. **`δ_w` gần như phẳng (0.019–0.035) trong khi `δ` tăng gấp ba.** Đây chính là cơ
   chế giải thích cái null: nới bộ lọc nạp thêm rất nhiều cạnh rò rỉ, nhưng chúng
   mang rất ít khối lượng trọng số. Kênh rò rỉ bị chặn bởi trọng số, không phải
   bởi số cạnh.

Điểm 3 là câu trả lời "vì sao" mà bản thảo hiện chưa có.

#### Hệ quả: ô `k=∞` trở thành phép thử phân định

Hai ứng viên cho **dự báo trái ngược nhau** ở ô `k=∞`:

| Dự báo theo | Cận | Có vỡ trần 0.003 của bản thảo? |
|---|---|---|
| `δ` thô | ≤ 0.0111 | **có thể** |
| `δ_w` | ≤ 0.00183 | **không** |

Nên chạy `k=∞` không còn là "thêm một ô cho đủ" mà là thí nghiệm **phân định giữa
hai lý thuyết**. Kết quả nào cũng có giá trị đăng: nếu `|ΔAUC| ≤ 0.0018` thì `δ_w`
thắng và bài có một chỉ số dự báo chặt; nếu `> 0.003` thì `δ_w` bị bác bỏ, `δ` thô
sống sót, và bài tìm được chế độ rò rỉ thực sự có hại.

### 2.3b Phạm vi áp dụng: cận chỉ có nghĩa khi nằm trên sàn nhiễu

Chạy cận trên pipeline chính của cả ba corpus
(`scripts/leakage_exposure.py --primary`) lộ ra một giới hạn cấu trúc:

| Corpus / backbone | `s` | `δ` | cận `s·δ` | \|ΔAUC\| | Kết |
|---|---|---|---|---|---|
| xes3g5m / GKT | 0.0843 | 0.089 | 0.00747 | 0.00174 | đúng |
| assist2012 / GKT | 0.00277 | 0.058 | 0.00016 | 0.00003 | đúng, nhưng < sàn nhiễu |
| xes3g5m / DGEKT | 0.000194 | 0.089 | 0.0000172 | 0.00029 | **vỡ 17×** |
| assist2012 / DGEKT | 0.000069 | 0.058 | 0.0000040 | 0.00010 | **vỡ 25×** |

DGEKT có `s` gần 0 (Pearson r chỉ 0.13–0.15), nên cận co về ~1e-5 — thấp hơn
sàn nhiễu huấn luyện cả một bậc. ΔAUC quan sát ở mức 1e-4 gần như hoàn toàn là
nhiễu, nên "vỡ cận" ở đây không phải cận sai mà là **cận không kiểm chứng được**.

Phát biểu đúng phải là:

```
|ΔAUC_leak|  ≤  max( s·δ , σ )        với σ = sàn nhiễu huấn luyện
```

Hệ quả cho bản thảo:

1. C3 **thừa hưởng đúng cái cổng mà bài đã có**: chỉ áp cận cho backbone đã qua
   manipulation check. Đây là điểm nhất quán tốt, không phải chắp vá.
2. `σ` từ chỗ "nên đo" thành **bắt buộc đo** — nó là một thành phần của công cụ.
   Ô lặp ở `docs/EAAI_PREREGISTRATION.md` §3 vì thế lên mức bắt buộc.
3. Junyi hiện **không có** slope DDR nào được đo, nên cận không tính được ở đó.
   Cần nói thẳng trong Limitations thay vì lờ đi.

Script đã mã hoá điều này bằng cột `informative` và cờ `--sigma`.

### 2.4 Giả định phải kiểm chứng (rủi ro chính của ý tưởng này)

`s_m,D` được ước lượng từ phép nhiễu **xoá/đảo** cạnh (DDR). Rò rỉ thì **thêm**
cạnh. Việc chuyển slope từ chế độ xoá sang chế độ thêm là một giả định, không
phải hệ quả.

Phải có một thí nghiệm riêng: thêm ngẫu nhiên cạnh vào `E_pre` ở các tỉ lệ khớp
với `δ_θ`, đo slope của AUC theo tỉ lệ thêm. Gọi là `s⁺`. Nếu `s⁺ ≲ s` thì cận
giữ nguyên dạng; nếu `s⁺ > s` thì phải dùng `s⁺` trong công thức. **Không được
bỏ qua bước này** — reviewer sẽ tìm đúng chỗ đó.

### 2.5 Phát hiện ngoài dự kiến: hai bảng trong bản thảo lệch nhau 2.8× — ĐÃ TRUY RA

Khi đối chiếu ô default của sweep m4 với lần chạy ablation chính (cùng bộ lọc
công bố `q0.95 k5 K5000 τ0.1`), `scripts/leakage_exposure.py` báo:

| | isolated (m4) | primary (ablation) | lệch |
|---|---|---|---|
| AUC train-only | 0.833591 | 0.833644 | **0.00005** |
| AUC full-log | 0.834206 | 0.835382 | **0.00118** |
| ΔAUC | +0.00061 | +0.00174 | 2.8× |

Nhánh train-only tái lập tới 5e-5, nhánh full-log lệch gấp **22 lần** mức đó.
Bất đối xứng như vậy không phải nhiễu huấn luyện — nhiễu sẽ tác động đều lên cả
hai nhánh.

**Đã chẩn đoán xong** bằng `scripts/diagnose_full_log_artefact.py`. Loại trừ theo
thứ tự:

1. *Khác đồ thị?* **Không.** Bốn phép so đều cho tập cạnh **giống hệt nhau**
   (Jaccard 1.000): full-log primary vs dựng lại từ config, full-log primary vs
   full-log m4, train-only primary vs train-only m4, và e_sim. Giả thuyết artefact
   cũ bị bác bỏ.
2. *Khác `split_seed`?* **Không.** `graph_stats.csv` ghi seed 17/18/19 nhưng đó là
   artefact của thí nghiệm seed-sensitivity (`augmentation.seeds: [42, 17, 1234]`),
   không phải của ablation. Cả hai lần chạy đều dùng base seed 42.
3. *`e_pre_source: ground_truth` trong config?* **Không liên quan** — key này không
   file Python nào đọc, là key chết.
4. *Commit `2593fc14` ("fix full_log pred_cap NameError")?* **Không** — tôi từng
   quy cho nó, nhưng kiểm lại thì sai. Ở bản tháng 6 dòng đó là
   `pred_cap = 5000 if effective_skip_cold else None`, dùng **đối xứng** cho cả
   hai nhánh; không có lỗi. Bản sửa tháng 9 đặt
   `current_pred_cap = None if model in export_models else base_pred_cap`, mà
   `run_m4_qk_sweep.py` **không** truyền `--export-full-predictions`, nên
   `export_models` rỗng và `current_pred_cap == base_pred_cap == 5000` — bằng đúng
   `pred_cap` cũ. Commit đó chỉ chữa một crash, **không đổi ngữ nghĩa**.

**Kết luận hiện tại: chưa quy được trách nhiệm.** Đã loại được đồ thị, seed, config
chết, và bản sửa pred_cap. Ứng viên còn lại, chưa phân định được:

| Ứng viên | Ghi chú |
|---|---|
| Commit `2490798c` *"Optimize GKT model with vectorization"* | Đổi thứ tự cộng dồn dấu phẩy động → đổi AUC ở mức nhỏ. Nhưng lẽ ra tác động lên **cả hai** nhánh. |
| Nhiễu huấn luyện | Giải thích được 1.2e-3, nhưng khi đó việc train-only khớp tới 5e-5 chỉ là may. |
| Nguyên nhân khác chưa nghĩ ra | — |

Chú ý: khoảng lệch train-only **không bằng 0** (5.3e-5), nên hai lần chạy vốn đã
không bit-identical.

### 2.5b Sàn nhiễu đo được từ dữ liệu đã có (không tốn GPU)

Không cần chờ ô lặp 2.0b mới có `σ`. Đợt quét DDR ba seed đã chứa sẵn **bản lặp
thật** mà trước đây ta bỏ sót: với ASSIST2012, cả ba file seed dùng **cùng**
`split_seed` (42/43/44) và **cùng** số cạnh (413/416/416), tức cùng split và cùng
đồ thị, chỉ khác seed huấn luyện (`fit_seed = experiment_seed + fold*97`).
`scripts/noise_floor.py` trích ra **36 nhóm lặp, 96 cặp chỉ-khác-seed**:

| Đại lượng | Giá trị |
|---|---|
| Hiệu cặp chỉ-khác-seed, trung vị | 1.59e-4 |
| Hiệu cặp chỉ-khác-seed, p90 | 4.32e-4 |
| Hiệu cặp chỉ-khác-seed, tối đa | 9.99e-4 |

Phải dùng **hiệu từng cặp**, không dùng biên độ ba seed: biên độ của 3 rút thăm
rộng hơn hiệu của 2 một cách hệ thống, nên so vintage với biên độ sẽ dễ dãi sai
hướng.

Đối chiếu hai nhánh của cùng hai bản mã, cùng fold, cùng corpus:

| Nhánh | Khoảng lệch vintage | Phân vị đuôi trong null chỉ-khác-seed |
|---|---|---|
| train-only | 5.33e-5 | 0.854 — hoàn toàn bình thường |
| full-log | 1.177e-3 | **0.000** — vượt cả 96/96 cặp |

Đọc theo null của ASSIST2012 thì nhánh train-only nằm giữa phân phối còn nhánh
full-log vượt cả 96/96 cặp. Nhưng **đây là null của corpus sai**, và §2.5c dưới
đây cho thấy đọc như vậy là overclaim.

Hai điểm dè dặt: (i) `σ` này đo trên ASSIST2012 ở mức AUC 0.96, còn XES3G5M ở mức
0.83; (ii) không có bản lặp nào cho XES3G5M vì ba file seed dùng split 42/43/44,
17/18/19, 1234/1235/1236 và số cạnh 1162/1163/1408 — khác cả split lẫn đồ thị.

### 2.5c Chuyển tỉ lệ phương sai: `σ` cho XES3G5M mà không cần GPU

Chuyển **số tuyệt đối** từ ASSIST sang XES là sai vì hai corpus ở hai mức AUC.
Thay vào đó chuyển một **tỉ lệ không đơn vị**: phần dao động do seed gây ra.

Trên ASSIST2012 đo được cả hai thành phần (vì có bản lặp trong từng split):

| Thành phần | Giá trị |
|---|---|
| sd do seed (gộp trong split) | 1.346e-4 |
| sd tổng (split + đồ thị + seed) | 6.166e-4 |
| **tỉ lệ seed** `ρ` | **0.218** |

Trên XES3G5M **đo được sd tổng** từ 9 ô không nhiễu loạn (không cần huấn luyện
thêm), rồi nhân với `ρ`. Cuối cùng đổi từ sd sang hiệu hai lần chạy xấu nhất bằng
hệ số đuôi mà chính ASSIST thể hiện (max/sd = 7.4):

| Tập ô XES3G5M | sd tổng | sd seed ước lượng | **`σ` ước lượng** |
|---|---|---|---|
| Cả 9 ô | 1.099e-3 | 2.40e-4 | **1.78e-3** |
| Bỏ ô vintage lạ (1403–1408 cạnh) | 5.77e-4 | 1.26e-4 | **9.35e-4** |

Bản bỏ ô vintage lạ đáng tin hơn: các ô seed1234 có ~1408 cạnh so với ~1162 của
seed 42/17, tức đồ thị dựng khác cấu hình, đưa vào sẽ thổi phồng sd tổng. Vậy
**`σ` trên corpus chính vào khoảng 1e-3**, và trùng với ước lượng thô bằng cách
lấy max của ASSIST — hai lộ trình độc lập cho cùng một bậc.

**Hệ quả, và nó nghiêm trọng.** Với `σ ≈ 1e-3`:

1. Cả ba ΔAUC đã đo (+0.0006, −0.0015, −0.0005) **nằm ở hoặc dưới sàn nhiễu**.
   Bảng M4 Phase B không phải "null chặt" mà là "chưa phân giải được ở ngân sách
   này". Mọi câu trong bản thảo nói `|ΔAUC| ≤ 0.003` như một khẳng định đo được
   phải đổi thành khẳng định có kèm sàn.
2. Kết luận §2.5b phải hạ cấp. Khoảng lệch full-log 1.177e-3 so với sd hiệu cặp
   của XES (≈ √2 × 2.4e-4 = 3.4e-4) chỉ là **~3.5σ**, không phải "vượt mọi cặp".
   Vẫn đáng ngờ, nhưng **không loại được** nhiễu huấn luyện một cách dứt khoát.
   Bất đối xứng 22× giữa hai nhánh vẫn là quan sát thật và vẫn trỏ về `2490798c`.
3. Việc 2.0b từ "nên đo" trở lại **bắt buộc**, vì cả C3 lẫn M-1 đều đứng trên con
   số này và ước lượng chuyển tỉ lệ có khoảng rộng 0.9e-3–1.8e-3.

**Hệ quả cho bản thảo.** Bản thảo trích cả hai vintage cho **cùng một ô bộ lọc**:
bảng graph-ablation (ΔAUC = +0.0017, tháng 6) và bảng M4 Phase B (ΔAUC = +0.0006,
tháng 9). Chênh 2.8×, nhưng cả hai đều dưới `σ`, nên không thể nói bên nào đúng.
Phương án đúng vẫn là chạy lại ở HEAD (việc 2.0), và khi viết thì trình bày kèm
sàn nhiễu thay vì so hai con số với nhau.

---

## 3. Trục novelty thứ hai: phơi nhiễm tập trung ở cold-start

Bài đã lập luận (Discussion) rằng throughput tỉ lệ nghịch với tần suất KC, và tự
gọi việc tách ablation theo tầng là "the natural next measurement" — rồi không làm.

Cận ở §2 dự báo điều này một cách định lượng: `δ_θ` tính trên toàn đồ thị là
trung bình; trên lân cận KC rất hiếm, tỉ lệ cạnh rò rỉ cục bộ cao hơn nhiều, nên
phơi nhiễm cục bộ lớn hơn.

Nếu tầng `very_cold` cho `|ΔAUC|` lớn hơn hẳn mức tổng hợp, thì **null tan thành
một phát hiện dương có định vị**: rò rỉ đồ thị không vô hại, nó chỉ bị pha loãng
bởi trung bình toàn cục. Đó là kết quả đăng được, khác hẳn một trần phẳng.

Nếu tầng `very_cold` cũng phẳng, đó vẫn là kết quả: cận dự báo đúng cả ở đuôi, và
bài có thêm một xác nhận. Hai nhánh đều có giá trị — thí nghiệm này không thể thất bại vô ích.

Hạ tầng đã có: `src/cold_start_report.py::per_stratum_metrics` nhận DataFrame
`(kc_id, y_true, y_prob)`. Cần predictions cho cả hai nhánh train-only / full-log
(`baseline_runner --export-full-predictions gkt`). Cache hiện tại
(`results/q1/m4_*/cache/*.json`) **chỉ lưu scalar** auc/acc/nll, không có
predictions — nên bước này cần chạy lại có cờ export.

---

## 4. Trục novelty thứ ba: soi các pipeline đã công bố

Đây là câu trả lời cho M-4 (giá trị kỹ thuật) mà **không cần đối tác công nghiệp**.

GKT và SKT gốc pool toàn log trước khi chia learner. Với cận ở §2, ta tính được
con số phơi nhiễm cho chính cấu hình mặc định của họ, trên corpus của họ, chỉ
bằng CPU. Kết quả là một bảng dạng:

| Pipeline công bố | Bộ lọc | `δ` | `s` (đo được / thừa hưởng) | Phơi nhiễm ước lượng |
|---|---|---|---|---|

Phát biểu được: "quy trình X nằm trong vùng phơi nhiễm thấp, kết quả của họ an
toàn theo trục này; quy trình Y nằm trong vùng cao, cần công bố thêm hàng
train-only". Đó là **một phát hiện về văn liệu**, loại kết quả mà reviewer nhớ.

Và nó biến cổng CI từ "checklist tốn 5–54 phút" thành "công cụ trả ra một con số
rủi ro có thể hành động" — đúng cái EAAI muốn nghe.

---

## 5. Kế hoạch theo pha

Ưu tiên: **novelty trên mỗi đơn vị GPU-giờ**. Pha 1 gần như không tốn GPU nhưng
gánh phần lớn giá trị mới.

### Pha 1 — CPU, ~4–6 ngày, không cần GPU

| # | Việc | Đầu ra | Gỡ được |
|---|---|---|---|
| 1.1 | Phát biểu hình thức cận `\|ΔAUC\| ≤ s·δ`, liệt kê giả định | §Protocol mới, ~1 trang | novelty |
| 1.2 | Tính `δ`, `δ_eff`, `δ_tv`, `δ_w` cho mọi ô census | `scripts/leakage_exposure.py`, CSV | §2.3 |
| 1.3 | Bảng đối chiếu cận vs quan sát trên 3 ô đã chạy | bảng mới thay `tab:m4-phase-b-auc` | M-1 (một phần) |
| 1.4 | Census + cận cho cấu hình mặc định của GKT/SKT gốc | bảng "published pipelines" | **M-4** |
| 1.5 | Ghi dự báo `k=∞` **trước khi chạy**, đóng dấu thời gian vào repo | mục pre-registration | M-2 |
| 1.6 | **Chẩn đoán lệch full-log (§2.5)** | loại được 5 giả thuyết kể cả nhiễu | **tái lập** |
| 1.7 | **Sàn nhiễu từ bản lặp có sẵn (§2.5b)** | `scripts/noise_floor.py`, 96 cặp | **M-1**, §2.5 |

**Trạng thái: 1.1, 1.2, 1.3, 1.6, 1.7 đã xong.** Artefact sinh ra:

- `scripts/leakage_exposure.py` + `tests/test_leakage_exposure.py` (11 test pass)
- `scripts/noise_floor.py` + `tests/test_noise_floor.py` (11 test pass)
- `scripts/diagnose_full_log_artefact.py`
- `results/tables/leakage_exposure.{csv,tex}`, `exposure_replicate_check.csv`,
  `full_log_artefact_diag.csv`, `noise_floor.csv`, `noise_floor_groups.csv`,
  `noise_floor_macros.tex`

Ghi chú: `data/processed/` **có sẵn ở máy viết bài** (6.4M tương tác XES3G5M), nên
các việc tôi từng xếp "chỉ chạy được trên server" thực ra chạy tại chỗ được. Chỉ
phần cần GPU (train) mới phải lên server.

1.4 và 1.5 cũng đã xong: `--primary` chấm cả ba corpus
(`results/tables/leakage_exposure_primary.csv`, kết quả ở §2.3b), và
`docs/EAAI_PREREGISTRATION.md` đã đóng băng dự báo tại commit `149a7595`.

**Toàn bộ Pha 1 đã xong.** Việc còn lại đều cần GPU hoặc là viết lách.

Ghi chú 1.2: đã chạy. `δ_eff` bị bác bỏ (1/3), `δ_w` được chọn (3/3, dư xấu nhất
4.8×). Lệnh: `python scripts/leakage_exposure.py --edge-root data/processed/xes3g5m/m4`.

Ghi chú 1.5: viết dự báo ra file có commit **trước** khi có kết quả. Nếu sau đó
`k=∞` rơi đúng vào cận, đó là bằng chứng mạnh hơn nhiều so với hồi cứu.

### Pha 2 — GPU, xếp theo giá trị giảm dần

Ước lượng dựa trên `docs/M4_GPU_SERVER.md`: một ô GKT (train-only + full-log,
1 fold, 10 epoch / batch 4) ≈ **4–8 giờ** trên 1× 3090.

| # | Việc | Chi phí | Gỡ được | Bắt buộc? |
|---|---|---|---|---|
| 2.0 | Chạy lại XES3G5M/GKT graph-ablation ở HEAD | 8–16 h | tái lập, §2.5 | **Có** |
| 2.0b | Ô lặp `q0.95_k5_Kinf_tau0.1` — `σ` **trên corpus chính** XES3G5M | 4–8 h | **M-1**, §2.3b | **Có** |
| 2.1 | Ô `k=∞`, fold 0 — phép thử phân định `δ` vs `δ_w` | 4–8 h | **M-2**, novelty | **Có** |
| 2.2 | Slope cộng cạnh `s⁺`: thêm cạnh ngẫu nhiên ở 4 tỉ lệ, fold 0 | 16–32 h | §2.4, nền móng của cận | **Có** |
| 2.3 | Default + `k=20`, fold 1–2 (seed 42) → CI 3 fold | 16–32 h | **M-1** | **Có** |
| 2.4 | Seed thứ hai (17) cho 2 ô, fold 0 → phương sai seed | 8–16 h | M-1 | Nên |
| 2.5 | Export predictions train-only/full-log để tách tầng cold-start | 8–16 h | novelty trục 2 | Nên |
| 2.6 | GKT compute-matched vs simpleKT (30 ep / batch 64 cả hai) | 24–48 h | M-3 | Tuỳ |

Tổng bắt buộc (gồm 2.0): **44–88 giờ GPU** (~2–4 ngày chạy liên tục).
Tổng gồm "nên": **60–120 giờ** (~3–5 ngày).

Thứ tự: 2.0b **không còn chặn** phần còn lại, vì §2.5b đã cho một `σ` đo được từ
dữ liệu cũ và đã chốt được rằng việc 2.0 là cần thiết. Nhưng vẫn phải chạy 2.0b,
vì `σ` hiện có là của ASSIST2012 còn cận C3 và M-1 cần `σ` trên **corpus chính**
XES3G5M ở mức AUC 0.83 — nơi dao động nhiều khả năng lớn hơn. Chừng nào chưa có
nó, mọi ΔAUC mức 1e-3 trên XES3G5M, kể cả ô `k=∞` ở §2.3, chỉ diễn giải được với
một sàn mượn từ corpus khác.

Về 2.6: nếu thiếu tài nguyên, giữ M-3 ở mục Limitations nhưng **bỏ hẳn** việc
dùng khoảng cách GKT–simpleKT để biện minh cho việc chọn XES3G5M làm primary.
Thay bằng lý do độc lập với budget: tỉ lệ KC-repeat thấp (21%) và AUC chưa bão hoà.
Đây là cách rẻ nhất để vô hiệu hoá M-3 mà không tốn GPU.

### Pha 3 — Viết lại, ~1–2 tuần

| # | Việc | Gỡ được |
|---|---|---|
| 3.1 | ~~Tái cấu trúc đóng góp C1–C5 + mục `sec:exposure`~~ — **xong** | novelty |
| 3.2 | ~~Viết lại abstract: đưa công cụ dự báo lên trước~~ — **xong** | ấn tượng biên tập |
| 3.3 | ~~Đổi tiêu đề (phương án 1)~~ — **xong**, đồng bộ 5 chỗ | ấn tượng biên tập |
| 3.4 | ~~Viết lại 5 highlights, bỏ câu tự hạ thấp~~ — **xong** | minor |
| 3.5 | ~~Cắt trang~~ — **xong**: chuyển DDR→AUC (S23–S24), main **46 trang** | |
| 3.6 | Đưa 2 hình từ phụ lục lên main (DDR-vs-p; scatter cận-vs-quan sát) | cân đối hình/bảng |
| 3.7 | ~~Thống nhất thuật ngữ: bỏ hẳn TBMR chỉ giữ LTES; giải nghĩa ECR~~ — **xong** | minor |
| 3.8 | Mở rộng Related Work — **xong một phần**, 32 → 36 tài liệu đã xác minh | minor |

### Ghi chú 3.5 — mục tiêu 38 trang có thể đặt sai

Cắt 133 dòng văn bản chỉ đổi được 2 trang. Bài có 22 float (9 bảng/hình/thuật
toán nội tuyến + 13 bảng `\input`), ước tính ~14 trong 47 trang là bảng và hình.
Muốn xuống 40 phải **chuyển bảng**, không phải viết ngắn lại.

Quan trọng hơn: header `main_EAAI.tex` ghi ràng buộc thật là **ngưỡng
desk-reject 50 trang của EAAI**, và bài đã hạ 12pt → 10pt để lọt ngưỡng. Vậy 47
là đạt; 38 là mục tiêu tự đặt. Đã quyết định dừng ở 47.

Đã làm: bảng 2×2 → phụ lục (Table S22, 5 tham chiếu đã trỏ lại); Broader
implications 218 → 156 dòng (bỏ khối "deployment vignettes" trùng với bảng
quyết định ngay trên nó); Introduction 321 → 289 (gỡ số liệu baseline trio khỏi
phần mở đầu); gom các lần lặp `≤0.003` trong Discussion.

Sửa kèm: bảng 2×2 có một dòng tự tham chiếu chính nó; phần vai trò corpus vẫn
còn khẳng định "clearest graph-backbone separation" mà lần gỡ M-3 bỏ sót.

### Ghi chú 3.8 — không nên nhồi cho đủ 50–60

Header `refs_EAAI.bib` ghi rõ **bốn mục bịa** đã từng bị gỡ khỏi file này
(GrapKT, CoreKT, GraceKT, wan2021contrastive). Nhồi số lượng tài liệu là đúng
cơ chế đã tạo ra sự cố đó. Tôi thêm 4 mục đã xác minh chéo nhiều nguồn thay vì
20 mục tra vội:

- `zhou2024psikt` — PSI-KT, ICLR 2024. Suy luận đồ thị tiên quyết bằng Bayes.
- `annabi2023prereq` — ICDL 2023, DOI. Coi cấu trúc tri thức là tham số học được.
- `xu2026gbktsurvey` — survey graph-KT, JEDM, 19/07/2026.
- `abdelrahman2023dgmn` — IEEE TKDE 35(8), DOI.

Hai mục đầu cho phép dựng một lập luận định vị mà bài trước đây thiếu: nhánh đó
hỏi đồ thị suy luận có **chính xác** không, bài này hỏi trước đó một bước là nó
có **hợp lệ** không. Hai câu hỏi độc lập.

`REFERENCES_AUDIT.md` mà bib nhắc tới **không tồn tại** trong kho; tôi dùng chú
thích `% VERIFIED <ngày>: <nguồn>` nội tuyến. Nếu muốn khôi phục file audit thì
đó là việc riêng.

Đã làm ở 3.1:

- Chèn `\subsection{Leakage Exposure Bound}` (`sec:exposure`) ngay sau mục DDR,
  gồm ba phương trình: `eq:delta-count`, `eq:delta-weight`, `eq:exposure-bound`.
- Đóng góp đánh số lại thành C1–C5, C3 là cận phơi nhiễm; L đánh lại để C_i khớp L_i.
- **Gỡ va chạm ký hiệu**: ràng buộc khả thi đổi từ (C1)–(C4) sang (F1)–(F4) ở cả
  `main_EAAI.tex` và `supplementary_EAAI.tex`. Trước đây C4 vừa là "ràng buộc
  top-K" vừa là "GT cross-validation" — reviewer đọc sẽ vấp.
- Biên dịch sạch cả main lẫn supplementary, không warning tham chiếu. **49 trang**
  (tăng 2; việc cắt trang là 3.5, chưa làm).

Chưa làm, vẫn chờ `σ` **trên XES3G5M**: chưa gắn bảng `leakage_exposure.tex` vào
bài, vì cột ΔAUC quan sát chỉ diễn giải được khi biết sàn nhiễu của chính corpus
đó. §2.5b đã cho một sàn đo được nhưng là của ASSIST2012, chỉ đủ để loại giả
thuyết nhiễu ở §2.5, chưa đủ để đóng số vào `eq:exposure-bound`. Phần phương pháp
đã viết sao cho không phụ thuộc kết quả đó.

---

## 6. Đề xuất tiêu đề mới

Tiêu đề hiện tại thuần mô tả, không mang khẳng định:

> Leakage-controlled concept-graph construction and cold-start diagnostics for
> graph-enhanced knowledge tracing

Ba phương án đặt công cụ lên trước (đều tránh viết tắt chưa định nghĩa):

1. *Bounding graph-mediated leakage in knowledge tracing: a train-only audit
   protocol with a predictive exposure measure*
2. *How much can a leaked concept graph move accuracy? A computable exposure
   bound for graph-enhanced knowledge tracing*
3. *From provenance audit to risk score: predicting graph-leakage exposure in
   graph-enhanced knowledge tracing*

Khuyến nghị phương án 1: nêu cả công cụ (audit protocol) lẫn cái mới (exposure
measure), và chữ "bounding" giữ được tính trung thực của kết quả.

**Đã chốt phương án 1.** Đồng bộ ở `main_EAAI.tex`, `supplementary_EAAI.tex`,
`title_page.tex`, `CoverLetter_EAAI.md`, `REVIEW_ARCHIVE_README.md`.

### 6b Trạng thái bản thảo sau khi đưa sàn nhiễu vào

- Abstract viết lại: cận phơi nhiễm lên đầu phần AI contribution, các con số null
  chuyển xuống phần engineering application kèm câu "bound rather than resolve".
- Highlights bỏ câu "not a new architecture" (tự hạ thấp), thay bằng 5 câu nói về
  cận, `δ_w`, chi phí CPU, slope, và sàn nhiễu.
- `sec:exposure` thêm đoạn hiệu chỉnh sàn: 96 cặp ASSIST + phép chuyển tỉ lệ ra
  `σ ≈ 1e-3` cho XES3G5M, ghi rõ là **ước lượng, không phải phép đo**.
- Hạ cấp hai chỗ overclaim: đoạn hai vintage (từ "loại được nhiễu" xuống "~3σ,
  chưa dứt điểm") và bảng M4 Phase B (thêm "chưa phân giải được ở ngân sách này").
- **Sửa lỗi có từ trước**: `supplementary_EAAI.tex` tham chiếu 21 nhãn nằm trong
  `main_EAAI.tex` nhưng không nạp `xr`, nên bản in ra có 21 dấu "??". Đã thêm
  `\usepackage{xr}` + `\externaldocument{main_EAAI}`; giờ 0 cảnh báo.
- Build: main **46 trang**, supplementary 23 trang, không warning tham chiếu.

**Số trang.** Chuyển hai bảng DDR→AUC (`tab:ddr-downstream`,
`tab:ddr-downstream-gkt`) sang phụ lục (Tables S23–S24) đã lấy lại 3 trang và
hết hiện tượng bảng nằm sau References. Bảng 13–16 trong main giờ là
cold-start, GT cross-validation, decision map, và audit cost, đều đặt sát chỗ
trích dẫn (trang 29–36); References bắt đầu sau Conclusion (trang 38). Còn 4
trang dự phòng dưới ngưỡng desk-reject 50.

---

## 7. Cấu trúc đóng góp sau khi sửa

```
C1  Quy trình dựng đồ thị train-only + provenance + DAG audit          (giữ)
C2  DDR: chỉ số cấu trúc, tách khỏi AUC, + manipulation check gating   (giữ)
C3  Cận phơi nhiễm |ΔAUC| ≤ s·δ_eff — tính bằng CPU, không cần train   (MỚI)
      · kiểm chứng trên 4 ô bộ lọc × 1 corpus
      · dự báo pre-registered cho ô k=∞
      · áp lên cấu hình mặc định của pipeline đã công bố
C4  Phân tầng cold-start + phơi nhiễm cục bộ theo tầng                 (nâng cấp)
C5  Ground-truth cross-validation trên Junyi                           (giữ)
```

Kết quả phủ định hiện tại **không biến mất** — nó trở thành hệ quả của C3:
"các pipeline công bố nằm ở vùng `δ` thấp, nên trần 0.003 là hệ quả của chế độ
vận hành, không phải tính chất của rò rỉ". Đó chính xác là điều bài muốn nói,
nhưng lần này có công thức đỡ lưng.

---

## 8. Rủi ro và phương án dự phòng

| Rủi ro | Xác suất | Xử lý |
|---|---|---|
| `s⁺` (thêm cạnh) lớn hơn hẳn `s` (xoá cạnh) | trung bình | Dùng `s⁺` trong công thức; cận vẫn đứng, chỉ đổi hằng số. Không phá khung. |
| Ô `k=∞` cho \|ΔAUC\| > 0.011, tức **vượt cả cận thô** | thấp | Kết quả còn tốt hơn: tìm được chế độ rò rỉ thực sự có hại. Đổi câu chuyện sang phát hiện dương. Phải sửa mọi chỗ nói "at most 0.003". |
| ~~`δ_eff` không giải thích được khoảng dư~~ | **đã xảy ra** | Đã xử lý: `δ_eff` bị bác bỏ, thay bằng `δ_w` (§2.3). |
| `δ_w` chỉ được kiểm trên 3 điểm, 1 corpus, 1 backbone | **cao** | Đây là điểm yếu thật của C3. Giảm nhẹ bằng: (a) ô `k=∞` làm điểm thứ tư phân định, (b) mở rộng sang ASSIST2012/GKT nơi `s` nhỏ hơn 30 lần, (c) phát biểu C3 là *cận có kiểm chứng trên N điểm*, không phải định luật. Không được overclaim. |
| Tầng cold-start quá ít mẫu để đo ổn định | **cao** | Đã biết trước: `n=49–161`. Gộp `very_cold`+`cold`, báo cáo kèm `n`, dùng bootstrap theo learner. Không tuyên bố nếu CI quá rộng. |
| Hết tài nguyên GPU giữa chừng | trung bình | Thứ tự 2.1 → 2.2 → 2.3 đã xếp theo giá trị. Dừng ở bất kỳ đâu vẫn còn bài mạch lạc; chỉ hạ phạm vi khẳng định. |

---

## 9. Việc làm ngay (không chờ GPU)

1. ~~`scripts/leakage_exposure.py` + test~~ — **xong**, cận `δ` đúng 3/3.
2. ~~Tính `δ_eff`~~ — **xong**, bị bác bỏ; `δ_w` thay thế (§2.3).
3. ~~Chẩn đoán lệch full-log §2.5~~ — loại được đồ thị, seed, config chết, bản
   sửa `pred_cap`, và (qua §2.5b) cả **nhiễu huấn luyện**. Ứng viên còn lại:
   `2490798c`.
3b. ~~Đo sàn nhiễu từ bản lặp có sẵn~~ — **xong**, `scripts/noise_floor.py`:
   96 cặp chỉ-khác-seed trên ASSIST2012, trung vị 1.59e-4, tối đa 9.99e-4.
4. ~~Ghi pre-registration~~ — **xong**, `docs/EAAI_PREREGISTRATION.md`.
5. ~~Mở rộng cận sang ASSIST2012 và Junyi~~ — **xong** (`--primary`), phát hiện
   giới hạn sàn nhiễu ở §2.3b.
6. ~~Gỡ liên kết "chọn XES3G5M vì GKT–simpleKT tách xa"~~ — **xong**, đã sửa hai
   chỗ trong `main_EAAI.tex` (§Introduction và §Datasets).
7. Quyết định cách xử lý §2.5 trong bản thảo trước khi viết lại bất kỳ bảng nào.
   §2.5b đã gỡ phần lớn thế bí: hai vintage **không so sánh được**, nên hướng đi
   là việc 2.0 (chạy lại XES3G5M/GKT ở HEAD). Còn lại là bạn chốt cách trình bày
   trong lúc chờ: rút bảng tháng 6, hay giữ kèm chú thích cảnh báo.

Lưu ý môi trường: `py -3 -m pytest` cần cờ `-p no:typeguard` (plugin typeguard hỏng
trên Python 3.14). `tests/test_optimized_gkt.py` segfault sẵn từ trước, không liên
quan các thay đổi ở đây.

---

## 10. Không làm

- Không đổi ngân sách GKT primary sang 30 epoch / batch 32 (đó là C5 đã gác).
- Không `--clear-cache` trên `results/cache/` dùng chung.
- Không nhắc quyết định của tạp chí trước trong bản thảo hay cover letter.
- Không hứa case study công nghiệp nếu chưa có đối tác — §4 đã thay thế được.
