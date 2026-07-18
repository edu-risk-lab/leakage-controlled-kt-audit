# Revised F-R01 finding (post author attestation + targeted pairing)

## Finding ID

**F-R01** (revised) — Epoch / batch narrative for primary GKT, simpleKT, and targeted GKT30 extension  
Related: **F-R12** (GKT batch labels in S15 vs historical config vs HEAD)

## Severity / confidence

- Severity: **HIGH** (affects how S21/S22 and abstract epoch claims must be worded)  
- Confidence: **HIGH** for scope of +0.003 pairs; **MEDIUM** for GKT30 batch (16 vs 32)

## Status

**OPEN — awaiting author confirmation of `targeted_gkt30_run_matrix.csv` before remediation**

## What changed after attestation

| Claim | Prior audit stance | Revised stance |
|---|---|---|
| Primary GKT 10 / batch 4 | CONFIG_INTENDED_ONLY @`619c02cf` | **SERVER_ATTESTED + CONFIG_AND_ARTIFACT_SUPPORTED** |
| simpleKT 30 / 64 | CONFIG_INTENDED_ONLY | **SERVER_ATTESTED + CONFIG_AND_ARTIFACT_SUPPORTED** |
| Prose “simpleKT reference @ 10 ep” | Unsupported | Still **unsupported** (contradicts attestation + config) |
| +0.003 | Suspected from S21 macros | **Recomputed from 3 valid seed-42 pairs** (+0.003451) |
| S22 nine-fold extension | Ambiguous | **Not valid as GKT10↔GKT30 pool**; optional separate vs-simpleKT story |
| Full primary re-run @ 30 | Feared by some wording | Author: **not done**; treat GKT30 as **targeted check only** |

## Observed evidence (locators)

1. Author attestation (chat, this session): primary GKT 10/4; simpleKT 30/64; targeted 10→30; +0.003; not full primary@30.  
2. Valid pairs: `paired_gkt10_gkt30_deltas.csv` (P42-0..2).  
3. S21 generator: `scripts/generate_gkt_epoch_ablation.py` L63–71, L99–100 (seed-42 gain).  
4. GKT30 seed42 artifact: `results/q1/gkt_epochs30_s42/baseline_fold_results.csv`.  
5. Primary artifact: `results/tables/baseline_fold_results.csv` @ content from `619c02cf`.  
6. Stale logs ~0.71: **excluded** from proving ~0.84 AUCs.

## Why it matters

Abstract/S21–S22 currently mix (a) epoch-extension sensitivity on seed 42, (b) multi-seed GKT30 vs simpleKT, and (c) batch labels that disagree with attestation (primary batch 16 in S15/S21 vs 4). Readers may infer compute-matched or equal-epoch redesigns that were not run.

## Required verification (author)

Confirm run matrix questions in `gkt30_scope_verification.md` §6.

## Recommended remediation (not applied)

1. Rewrite +0.003 as **targeted three-fold epoch-extension sensitivity (seed 42)** only.  
2. Stop calling S22 a pooled nine-fold **extension**; either reframe or remove that claim.  
3. Align batch labels with attestation (GKT10=4) and confirmed GKT30 batch.  
4. Remove “simpleKT @ 10 epochs” wherever it remains.  
5. Use vocabulary: epoch-extension sensitivity ≠ compute matching.

## Acceptance test

- Every +0.003 mention points only to the three seed-42 pairs (or regenerated equivalent with logs).  
- No “nine-fold” language attached to GKT10→GKT30.  
- No “compute-matched” / “epoch-matched” wording that implies equal compute or equal max epochs across families.  
- S15/S21 batch for primary GKT = 4 (or re-attested otherwise with logs).
