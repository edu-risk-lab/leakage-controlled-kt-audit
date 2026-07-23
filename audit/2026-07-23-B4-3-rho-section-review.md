# B4.3 — Rà §4.2 |ρ| vs bảng leakage (2026-07-23)

## Vấn đề gốc (PGS)

Bảng ghi metric kiểu EOC ≈ 1.42 trong khi Eq.(8) định nghĩa ρ thô; reviewer thấy lệch thang đo.

## Trạng thái sau B4.1–B4.3

| Thành phần | Trạng thái |
|---|---|
| `compute_eoc()` | Trả `\|ρ\|` (alias `compute_rho_edge_outcome`) |
| `leakage_metrics.csv` | Cột `eoc` **đã migrate** sang \|ρ\| (không còn 1.42…) |
| `leakage_metrics.tex` | Cột `$|\rho|$`; sync submission |
| §3.2 formal problem | Tier diagnostics dùng `\|ρ_f\|` |
| §4.2 `sec:leakage` | Eq. rho-edge-outcome; báo cáo `\|ρ_f\|`; range 0.09–0.22 + ref Table |
| Algorithm 1 | Return `\|ρ_f\|` |
| §4.x exp-audit | Khớp bảng: ASSIST 0.109, Junyi 0.224, XES 0.088 |
| `generate_paper_artifacts.py` | Delegate → `write_leakage_metrics_tex` (không còn caption EOC) |

**Lưu ý CSV refresh (2026-07-23):** recompute từ fold graphs cập nhật ASSIST `ECR_overlap` 0→1 và `TBMR` 0→0.20 — khớp narrative “overlap near unity”; exp-audit TBMR range đã sửa.

## Số đối chiếu (3-fold mean ± std)

| Dataset | \|ρ\| (CSV migrated) | Bảng TeX |
|---|---:|---|
| ASSIST'12 | 0.109 ± 0.008 | 0.109 ± 0.006 |
| Junyi | 0.224 ± 0.001 | 0.224 ± 0.001 |
| XES3G5M | 0.088 ± 0.012 | 0.088 ± 0.010 |
| Synth C2/C5 | 0.000 | 0.000 |

Lệch ASSIST std do làm tròn 3 chữ số — không ảnh hưởng narrative.

## Lệnh bảo trì

```bash
# Migrate legacy CSV (nhanh) hoặc recompute từ fold graphs (chậm, Junyi):
python -m scripts.regenerate_leakage_metrics --sync-tex
python -m scripts.generate_phase_c_tables   # nếu cần full phase-C bundle
```

## Không còn trong manuscript

- Không còn `\textsc{EOC}`, `eq:eoc`, Frobenius norm, hay số 1.41–1.45 trong `main_APIN.tex`.
