# Proposed epoch-claim wording (draft only — no manuscript edit)

Await author confirmation of the run matrix before applying.

## Claims to prefer

### Primary protocol

> Under the primary release protocol on XES3G5M (learner-temporal three-fold, train-only graphs), GKT is trained with **maximum 10 epochs** and **batch size 4**; *simpleKT* uses **maximum 30 epochs** and **batch size 64**.

### Targeted epoch-extension sensitivity (S21)

> As a **targeted epoch-extension sensitivity check** on **split seed 42** (three folds)—not a re-run of the full primary multi-seed pipeline—we increased only GKT’s maximum epoch budget from 10 to 30. Mean test AUC rose by **≈ +0.003** (fold deltas +0.0056, +0.0045, +0.0002; paired-*t* 95% CI approximately [−0.004, +0.011]). This is an **epoch-extension sensitivity** result, **not** a compute-matched comparison and **not** equal maximum epochs versus *simpleKT*.

### What not to say

| Avoid | Why |
|---|---|
| “Epoch-matched ablation” / “compute-matched” | Implies matched compute or equal epoch caps across models |
| “simpleKT reference unchanged at 10 epochs” | Contradicts attestation and primary config (30) |
| “Pooled nine-fold” for the +0.003 GKT10→GKT30 gain | Only three paired folds exist |
| Primary GKT “batch 16” (current S15/S21) | Attestation + config@primary AUC = **4** |
| Using seeds 17/1234 to justify +0.003 | No GKT10 twins |

### Optional S22 (only if author keeps multi-seed GKT30)

> Separately, GKT checkpoints trained with a 30-epoch budget on split seeds 17, 42, and 1234 (nine folds) can be compared to *simpleKT* on the same splits; those deltas answer a **multi-seed GKT@30 vs *simpleKT*** question and **must not** be described as a pooled epoch-extension from the 10-epoch primary GKT.

If that optional block is not wanted, drop S22’s pooled extension language entirely and keep S21 only.

### DDR (side note)

> DDR downstream GKT sweeps use the primary GKT training budget (**10 epochs, batch 4**), not the 30-epoch targeted check.

---

**STOP:** Confirm `targeted_gkt30_run_matrix.csv` before remediation edits to `main_APIN.tex`.
