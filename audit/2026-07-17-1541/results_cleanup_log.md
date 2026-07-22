# results/ cleanup log (2026-07-17)

Freed approximately **880 MB** (925 MB → 45 MB).

## Removed (junk / old copies)

| Path | Reason |
|---|---|
| `results/main_APIN.tex` | Misplaced old manuscript copy (canonical: `paper/main_APIN.tex`) |
| `results/refs_APIN.bib` | Misplaced bibliography copy |
| `results/CHANGES_APIN.md` | Draft notes |
| `results/REFERENCES_AUDIT.md` | Draft notes |
| `results/REVIEW_APIN.md` | Draft notes |
| `results/cache/` | Regenerable prediction cache (~40 MB) |
| `results/pykt_work/` | pyKT scratch working directory (~795 MB) |
| `results/predictions/*_diagnostic_predictions_sample.csv` | Diagnostic samples (~45 MB) |
| `results/figures/*.png` | PNG previews; paper uses PDF |
| `results/tables/q1_gkt_epochs30_ablation*.tex` | Obsolete S22 LaTeX (removed from submission) |

Empty placeholders restored: `cache/.gitkeep`, `pykt_work/.gitkeep`.

## Kept (paper / audit critical)

- `results/tables/` fold CSVs and paper-facing `.tex`
- `results/figures/*.pdf`
- `results/q1/` including LEGACY unpaired GKT30 seeds 17/1234 and seed 42
- `results/predictions/xes3g5m/**/*.parquet` (optional bootstrap)
- `results/reports/`, `results/gt_validation/`

## Legacy manuscript stems removed from `paper/` (2026-07-17)

Removed 47 files for stems: `main_APIN_build*`, `main_APIN_s1`, `main_APIN_version2`, `main_export`, `main_gikt_fixed`, `main_ieee`, `main`, `main_vi` (`.tex`/`.pdf` + LaTeX aux).

Kept: `paper/main_APIN.tex`, `paper/main_APIN.pdf` (+ current build aux for main_APIN).
