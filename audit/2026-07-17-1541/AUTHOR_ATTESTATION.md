# Author attestation (locked for remediation 2026-07-17)

Source: author decisions in authorized remediation request. No experiments were re-run.

## Confirmed protocols

### Primary GKT (XES3G5M)
- max_epochs: 10
- batch_size: 4
- Evidence: SERVER_ATTESTED + HISTORICAL_CONFIG at commit `619c02cf`
- Not EXECUTION_VERIFIED (no matching training log)

### Targeted extended-training GKT (seed 42, S21 exploratory)
- XES3G5M, experiment seed 42, folds 0–2
- max_epochs: 30, batch_size: **32** (also hidden_dim 64, max_seq_len 100 vs primary)
- Evidence: SERVER_A_REPORT `672ad7bb` + CONFIG @ `fcb14635` / `85afe0c8`
- Not EXECUTION_VERIFIED (no batch in result JSON; s42 log absent on dev machine)
- Not epoch-only controlled ablation; configuration sensitivity only

### GKT30 ablation publish (S21–S22 nine-fold context, not +0.003 claim)
- XES3G5M, seeds 17, 42, 1234 × 3 folds
- max_epochs: 30, batch_size: **32**, hidden_dim 64, max_seq_len 100
- Evidence: SERVER_A_REPORT + `results/q1/gkt_epochs30_s*/`
- Pooled Δ vs simpleKT@30 ≈ −0.038 (artefact); excluded from S21 +0.003451 pairing

### DDR downstream GKT
- max_epochs: 10
- batch_size: **4** for seed 42 XES (primary budget)
- batch_size: **8** for multiseed XES seeds 17/1234 (Jul 2026, config `955a820+`)
- batch_size: **32** for ASSIST2012
- Use: robustness/DDR only; not evidence for GKT30 epoch gain

### simpleKT reference
- max_epochs: 30
- batch_size: 64
- Any “simpleKT at 10 epochs” description is incorrect

## Confirmed fold deltas (unchanged artifacts)

| Fold | GKT10 | GKT30 | Delta |
|---:|---:|---:|---:|
| 0 | 0.834557 | 0.840181 | +0.005624 |
| 1 | 0.833752 | 0.838300 | +0.004547 |
| 2 | 0.832624 | 0.832804 | +0.000181 |

Mean delta = +0.003451; approx. 95% CI [−0.004, +0.011] includes 0.

Seeds 17 and 1234 GKT30 artifacts are **LEGACY_UNPAIRED_GKT30_ARTIFACTS** and must not enter the +0.003451 claim.
