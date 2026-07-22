# LEGACY_UNPAIRED_GKT30_ARTIFACTS

Status (author attestation, remediation 2026-07-17):

- `gkt_epochs30_s17/` and `gkt_epochs30_s1234/` contain GKT30 fold artefacts
  without matched primary GKT10 twins for the same fold/split_seed pairs used
  in the seed-42 sensitivity check.
- Keep artefacts in the repository for audit/history.
- Do **not** use them in:
  - Table S21 generator (`scripts/generate_gkt_epoch_ablation.py`)
  - manuscript submission claims for +0.003451
  - any nine-fold / pooled GKT10→GKT30 paired analysis

Canonical paired check: seed 42, folds 0–2 only
(`audit/2026-07-17-1541/canonical_training_protocol.yaml`).
