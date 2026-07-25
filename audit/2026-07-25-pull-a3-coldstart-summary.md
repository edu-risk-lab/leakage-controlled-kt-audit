# Pull summary — A3.5 Junyi cold-start GPU (2026-07-25)

**Branch merged:** `origin/results/a3-coldstart-junyi-verified` → `main`  
**Commit:** `bc9ea715` (Server A, 2026-07-25)

## Thay đổi chính

| Artefact | Trước (capped diagnostic) | Sau (full pyKT, 3 folds) |
|----------|----------------------------|---------------------------|
| Junyi very_cold fold~0 $n$ | 19 | **11** |
| Fold~0 AUC mọi model | Trùng $1.0$ (artefact) | **Không còn trùng**; hầu hết suppress (n_disc $<10$) |
| SKT fold~0 very_cold | AUC $1.0$ | ACC $0.545$, n_disc=**9** (gần ngưỡng) |
| warm/hot Junyi | — | simpleKT warm $0.846\pm0.016$; hot $0.982\pm0.000$ |

## Manuscript

- §4.8 / H2: cập nhật prose (n=11/43, A3.5 GPU, bỏ n=19/degenerate 1.0).
- `cold_start_summary.tex`: very_cold + cold Junyi → `---`.
- Fix generator: suppress ô NaN → `---` (`generate_phase_c_tables.py`).

## Code fixes trên server (trong branch)

- `src/pykt_engine.py` — AMP/BCE stability
- `src/models/dygkt.py` — device handling
- `scripts/run_a3_cold_start_rerun.ps1` — hardening Windows

## Việc còn lại

- Junyi cold stratum: AUC NaN (n_disc=0) — có thể do valid+test pyKT alignment; warm/hot OK.
- Rút thêm trang body (38→32–35).
- Checklist nghiệm thu PGS.
