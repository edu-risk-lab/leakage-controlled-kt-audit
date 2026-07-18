# Remediation verification log

Date: 2026-07-17  
Mode: authorized remediation (no experiments)  
Canonical manuscript: `paper/main_APIN.tex`

## Invariants checked

| Check | Result |
|---|---|
| No training / GPU / new predictions | PASS — no train scripts invoked |
| No edits to historical fold AUC/ACC CSVs | PASS — `baseline_fold_results.csv` and `gkt_epochs30_s*/` fold values untouched |
| S21 values match locked fold AUCs | PASS — generator fail-closed vs EXPECTED constants |
| Mean Δ = mean of three fold deltas | PASS — 0.003451 |
| S22 not in submission tex/PDF | PASS — 0 hits for Table S22 / sec:supp-gkt-multiseed |
| Forbidden phrase scan (key files) | PASS — see post_remediation_audit.md |
| Findings auto-closed? | PASS — only READY FOR HUMAN VERIFICATION / retained limitation |

## Generators

1. `python scripts/generate_gkt_epoch_ablation.py`  
   - Wrote S21 tabular; stubbed pooled tex; macros retire GKTthirty*  
   - Mean Δ=+0.003451; CI≈[−0.003710,+0.010611] → rounded [−0.004,+0.011]
2. `python scripts/generate_training_parity.py`  
   - S15 from `canonical_training_protocol.yaml` (GKT 10/4; simpleKT 30/64)
3. `python scripts/generate_ddr_downstream_gkt_tex.py`  
   - Caption scopes: r_core n=81; r_all/rho n=99
4. `scripts/plot_ddr_downstream.py` caption template updated (not re-run figure; avoids regenerating plot/CSV)

## Build

- Engine: MiKTeX pdflatex (+ bibtex + 2 reruns earlier; final pass after S15 fix)
- Junction: `paper/results` → `../results` (path resolution per build notes)
- Output: `paper/main_APIN.pdf` (57 pages)
- Log: no undefined citations/references; residual Overfull \hbox at TikZ (~32pt) and S15 table (~64pt)
- PDF text: Table S21 present with 0.834557/0.840181/…; Table S22 absent

## Impact note (generators)

- Changing `generate_training_parity.py` affects **S15 only** (and any package that copies it).
- Changing `generate_gkt_epoch_ablation.py` affects **S21 + macros**; pooled file is a non-submission stub.
- DDR script caption changes affect **ddr_downstream*.tex** only when those scripts are re-run; body rows unchanged.
