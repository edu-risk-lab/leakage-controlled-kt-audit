# Rerun requirements to reach EXECUTION_VERIFIED

Do **not** patch manuscript numbers from current YAML alone. To certify epochs/batch for each AUC in S15–S22, produce the following (or equivalent immutable provenance).

## Common instrumentation (all families)

For every fold result, write **alongside** the metrics CSV/JSON:

1. `epochs`, `batch_size`, `lr`, `max_seq_len`, `early_stopping_patience`
2. Resolved config path + **SHA-256 of the exact YAML bytes** used
3. `git_sha` (`git rev-parse HEAD`) and dirty flag
4. `split_base_seed`, `fold`, `split_seed`, `experiment_tag`
5. Full training log path; log must include per-epoch lines through the configured max epoch (or early-stop reason)
6. Checkpoint path + file SHA-256 (optional but preferred)
7. Environment: `pip freeze` or lockfile hash at run start

Extend `baseline_runner` cache JSON schema accordingly (today it omits hp).

## Family-specific reruns

### A. Primary release (S15/S16)

| Field | Requirement |
|---|---|
| Models | `gkt`, `simplekt` on XES3G5M, `train_only`, 3 folds, base seed 42 |
| Freeze config | Snapshot YAML **before** run; do not edit mid-campaign |
| Decision needed | Choose and document one GKT batch {4, 16, 8} as the **release** protocol; rerun all three folds under that freeze |
| simpleKT | Document resolved `pykt.epochs` / `batch_size` (expected 30/64 if defaults unchanged) |
| Acceptance | New AUC table + logs; manuscript S15 must match the freeze (not HEAD drift) |

### B. GKT epoch-extended (S21/S22)

| Field | Requirement |
|---|---|
| Config | Single freeze of `xes3g5m_gkt_epochs30.yaml` (pick batch **16 or 32**, not both across seeds) |
| Seeds | 17, 42, 1234 × 3 folds with fold-aligned graphs |
| Logs | One log file per `experiment_tag` containing epoch 1…N and final test metrics matching CSV |
| Acceptance | Paper AUCs regenerable within tolerance; S21 batch column = freeze |

### C. simpleKT reference for S22

| Field | Requirement |
|---|---|
| Tags | Either regenerate `simplekt30_*` **or** `trio_matched_*`, not an undocumented mix |
| Epochs/batch | Explicit in config + log (resolve prose “10” vs config “30” **before** rerun) |
| Cache | Keep `results/cache/..._simplekt_s{seed}_...` under provenance (or upload as release assets) |
| Acceptance | S22 pairing script points at tagged rows whose JSON/logs show the same hp |

## What not to do

- Do not set S15 GKT batch to 8 merely because HEAD YAML is 8.
- Do not cite stale `logs/q1/gkt_epochs30_s17.log` (0.71-era) as proof for 0.84 AUCs.
- Do not treat deleted cache recovery alone as EXECUTION_VERIFIED for epochs.

## Minimal acceptance tests

1. For each paper AUC row, a log line or sidecar JSON states `epochs=` and `batch_size=` used.
2. Config blob hash in the sidecar equals the frozen YAML hash.
3. Regenerating S15 from that freeze reproduces the published epoch/batch columns.
4. Classification upgrades from `CONFIG_INTENDED_ONLY` / `ARTIFACT_TAG_ONLY` to `EXECUTION_VERIFIED` in a follow-up audit.
