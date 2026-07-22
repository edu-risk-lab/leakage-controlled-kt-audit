# S21 / S22 validity decision (pre-remediation)

**Decision rule applied:** do not discard S21/S22 before scope is fixed; separate *epoch-extension* from *GKT30 vs simpleKT* and from *compute matching*.

## Terminology (required)

| Term | Meaning | Applies here? |
|---|---|---|
| Equal maximum epochs | Both arms trained with the same `max_epochs` | **No** for GKT10 vs GKT30 |
| Epoch-extension sensitivity | Same split/fold; raise GKT `max_epochs` only (10→30) and measure ΔAUC | **Yes** — seed 42, 3 folds |
| Compute matching | Matched wall-clock / FLOPs / batch / steps across models | **No** — do **not** call this compute-matched |

## S21 — GKT epoch-extended ablation (seed 42)

| Question | Answer |
|---|---|
| Is S21 seed 42 × three folds? | **YES** (`generate_gkt_epoch_ablation.py` loads only `gkt_epochs30` @ seed 42; pairs with primary 3 folds) |
| Does the “Epoch gain +0.003” row match valid pairs? | **YES** (recomputed mean +0.003451; CI matches display) |
| Keep S21? | **YES**, with corrected scope label: **targeted three-fold epoch-extension sensitivity check** (seed 42) |
| Fix before publish (later remediation) | Batch columns: primary should be **4** (author+config@AUC), not 16; GKT30 batch needs author confirmation (config@intro **16**, tex **32**). simpleKT reference row is a **vs-simpleKT** contrast, not the +0.003 definition |

## S22 — multi-seed block

| Question | Answer |
|---|---|
| Do nine GKT30 fold AUCs (~0.84) exist? | **YES** (seeds 17, 42, 1234 × 3) |
| Is that a nine-fold **GKT10↔GKT30** extension? | **NO** — no GKT10 for seeds 17/1234 |
| Is “pooled nine-fold” valid for the **+0.003** claim? | **NO** |
| What does current S22 actually pool? | **GKT30 − simpleKT** over 9 folds (`gkt_epoch_ablation_pooled.csv`) — a different estimand |
| Keep S22 as “pooled nine-fold epoch-extension”? | **NO** |
| Keep S22 at all? | **CONDITIONAL** — may remain only if clearly labeled as **multi-seed GKT@30 vs simpleKT observational deltas**, not as epoch-extension pooling; author must confirm those six extra GKT30 runs stay in scope |

## Recommended status (awaiting author OK)

| Table | Recommended status | Label |
|---|---|---|
| S21 | **Retain** | Targeted three-fold epoch-extension sensitivity (seed 42); report mean Δ and CI from three pairs |
| S22 (as epoch-extension nine-fold) | **Do not claim** | Insufficient GKT10 twins |
| S22 (as GKT30 vs simpleKT) | **Author decision** | Artifacts exist; not compute-matched; not equal-max-epochs vs primary GKT |

## Explicit non-actions this turn

- Manuscript not edited.
- No rows deleted from results.
- No automatic drop of S21/S22 files.
