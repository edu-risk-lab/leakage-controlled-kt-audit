# Final remediation diff summary

## Tracked code / manuscript / table changes (`git diff --stat`)

```
paper/main_APIN.tex                          | 266 +++---
results/tables/ddr_downstream.tex            |   2 +-
results/tables/ddr_downstream_gkt.tex        |  18 +-
results/tables/gkt_epoch_ablation.tex        |  17 +-
results/tables/gkt_epoch_ablation_macros.tex |  13 +-
results/tables/gkt_epoch_ablation_pooled.tex |  12 +-
results/tables/training_parity.tex           |   9 +-
scripts/generate_ddr_downstream_gkt_tex.py   |  37 +-
scripts/generate_gkt_epoch_ablation.py       | 216 +++---
scripts/generate_paper_artifacts.py          |   1 +
scripts/generate_training_parity.py          |  50 +-
scripts/plot_ddr_downstream.py               |  13 +-
12 files changed, 370 insertions(+), 284 deletions(-)
```

Also updated: `paper/main_APIN.pdf` (rebuild).

## New audit / helper artefacts (untracked under `audit/2026-07-17-1541/`)

- `AUTHOR_ATTESTATION.md`
- `canonical_training_protocol.yaml`
- `final_remediation_diff.md` (this file)
- `affected_locations.csv`
- `invalidated_or_removed_claims.md`
- `retained_claims.md`
- `updated_findings.csv`
- `updated_number_consistency.csv`
- `updated_claim_evidence_matrix.csv`
- `remediation_verification_log.md`
- `post_remediation_audit.md`
- `HUMAN_VERIFICATION_CHECKLIST.md`
- plus prior audit products from earlier phases

## Other new files

- `scripts/_remediate_fr01_manuscript.py` — one-shot patch applicator (audit trail)
- `results/q1/LEGACY_UNPAIRED_GKT30_ARTIFACTS.md` — bars seeds 17/1234 from S21 claim
- `results/tables/gkt_epoch_ablation_seed42_pairs.csv` — audit CSV from S21 generator (not a historical fold CSV rewrite)

## Intentionally unchanged

- `results/tables/baseline_fold_results.csv`
- `results/q1/gkt_epochs30_s*/baseline_fold_results.csv` fold AUC/ACC values
- Figure PDF binary `fig_ddr_downstream.pdf` (caption clarified in manuscript; figure not regenerated)

## Build path note

Created junction `paper/results` → `../results` so `\input{results/...}` resolves when compiling from `paper/`.
