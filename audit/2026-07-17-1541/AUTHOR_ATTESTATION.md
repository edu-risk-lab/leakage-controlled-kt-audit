# Author attestation (locked for remediation 2026-07-17)

Source: author decisions in authorized remediation request. No experiments were re-run.

## Confirmed protocols

### Primary GKT (XES3G5M)
- max_epochs: 10
- batch_size: 4
- Evidence: SERVER_ATTESTED + HISTORICAL_CONFIG at commit `619c02cf`
- Not EXECUTION_VERIFIED (no matching training log)

### DDR downstream GKT
- max_epochs: 10
- batch_size: 4
- experiment_seed 1234 includes folds 0–2
- Use: robustness/DDR only; not evidence for GKT30

### simpleKT reference
- max_epochs: 30
- batch_size: 64
- Any “simpleKT at 10 epochs” description is incorrect

### Targeted extended-training GKT
- XES3G5M, experiment seed 42, folds 0–2
- max_epochs: 30, batch_size: 16
- Evidence: CONFIG_AND_ARTIFACT_SUPPORTED + SERVER_ATTESTED
- Not EXECUTION_VERIFIED
- Not a full rerun, not compute-matched, not epoch-only controlled ablation

## Confirmed fold deltas (unchanged artifacts)

| Fold | GKT10 | GKT30 | Delta |
|---:|---:|---:|---:|
| 0 | 0.834557 | 0.840181 | +0.005624 |
| 1 | 0.833752 | 0.838300 | +0.004547 |
| 2 | 0.832624 | 0.832804 | +0.000181 |

Mean delta = +0.003451; approx. 95% CI [−0.004, +0.011] includes 0.

Seeds 17 and 1234 GKT30 artifacts are **LEGACY_UNPAIRED_GKT30_ARTIFACTS** and must not enter the +0.003451 claim.
