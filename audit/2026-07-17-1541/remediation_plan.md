# Remediation plan (read-only audit; no edits applied)

Priority order for authorized remediation. Do not invent missing evidence.

| Priority | Finding | Owner | Action | Evidence required | Acceptance test |
|---|---|---|---|---|---|
| P0 | F-R01 | Authors / experiment owner | Freeze the exact `simpleKT` checkpoint used for S16 vs S21–S22. Align abstract, §Training parity, Table~S15, Table~S21 Epochs column, Q1 caption, and S22 prose to one protocol. If tables used 30-ep `simpleKT`, stop claiming “reference unchanged at 10 epochs”; if deltas used 10-ep Phase-3 trio, fix S21/Q1 labels. | Config YAMLs, run logs, parquet/metrics paths for each seed/fold | Every epoch mention agrees; regenerated $\Delta$ match claimed protocol |
| P0 | F-R02 | Authors | Define correlation subsets (`p≤0.3` core vs +anchors vs all-operator pooled). Recompute $r$/$\rho$ from `ddr_downstream.csv`. Sync `ddr_downstream.tex` caption, GKT table caption, abstract, and figure annotation. | Notebook/script output with checksum of CSV | One definition per reported $r$; figure label matches |
| P1 | F-R03 | Manuscript editor | Replace “$0.003$ AUC/ACC” with AUC-only bound or state ACC max $0.008$. | `graph_ablation.tex` / full S6–S10 | Contribution sentence matches table extrema |
| P1 | F-R11 | Manuscript editor | Soften “unmoved” for `simpleKT` under injection (e.g. “shifts $\ll$ graph-reliant models”). | `downstream_auc_injection.tex` | Abstract matches $+0.008$ vs $+0.05$/~$+0.03$ |
| P1 | F-R04 | Authors | Update Fig.~S3 caption to state models included and meaning of pooled $r{=}0.75$, or regenerate figure without misleading pooled fit. | Plotting script + data slice | Caption ↔ annotation |
| P2 | F-R05 | Authors | Keep observational ranking language; point to single parity table. | S15 + S21–S22 after F-R01 fix | No stronger fairness claim than protocol |
| P2 | F-R06 | Repo maintainer | Document real compile recipe (`paper/` + include path to `results/`, or flat `submission_APIN`). | Successful clean build log | Third party can compile from notes alone |
| P2 | F-R07 | Corresponding author | Attest AI tools used; add SN-compliant disclosure if beyond copy-editing. | Author attestation | Declarations match attestation |
| P2 | F-R08 | Corresponding author | Complete APIN submission checklist from current journal page. | Dated guidelines PDF/HTML | Checklist all PASS/WAIVED |
| P3 | F-R09 | Bibliography owner | Re-resolve DOIs; add missing DOI fields where they exist. | Crossref/publisher records | REF-001 closed or waived |
| P3 | F-R10 | Stats owner | Prefer per-seed CIs; label pooled nine-fold assumption. | S22 text | Reader can see dependence caveat |

## Boundary

This audit did **not** modify `paper/main_APIN.tex`, PDF, tables, figures, or code. Apply changes only after explicit authorization, one finding at a time, with re-audit of affected checks.
