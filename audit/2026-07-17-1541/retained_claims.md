# Retained and narrowed claims

## Primary protocol (SERVER_ATTESTED_HISTORICAL_CONFIG @ 619c02cf)

- Primary GKT (XES3G5M): **maximum 10 epochs**, **batch 4**
- simpleKT: **maximum 30 epochs**, **batch 64**
- Not claimed as EXECUTION_VERIFIED (no matching training logs for paper AUC rows)

## Primary ranking (unchanged fold artefacts)

- On XES3G5M, GKT trails simpleKT by ≈0.041 AUC (95% CI from Table S16 macros)
- GIKT remains competitive under the same protocol
- Observational under attested maximum-epoch budgets; not causal proof that graphs are useless

## Targeted extended-training sensitivity (narrowed)

- Seed **42**, folds **0–2** only
- Primary GKT AUC vs extended GKT (max 30 epochs, batch **16**)
- Mean ΔAUC = **+0.003451**; approx. 95% CI **[−0.004, +0.011]** includes 0
- Scope: **EXPLORATORY_THREE_FOLD_CONFIGURATION_SENSITIVITY**
- Both max epochs and batch size changed → not an isolated epoch effect; study is not fully compute-matched

## Leakage ablation bounds (narrowed)

- Max |ΔAUC| ≤ **0.003**
- Max |ΔACC| ≤ **0.008**
  (from graph ablation summary; not a single combined AUC/ACC bound)

## Injection (F-R11 narrowed)

- simpleKT changed by **+0.008 AUC** (0.850→0.858) at 20% injection (Table S18)

## DDR correlations (scope-labeled)

| Statistic | Scope | n |
|---|---|---:|
| Pearson r≈0.93 | XES3G5M/GKT, p≤0.3 core | 81 |
| Pearson r≈0.99 | XES3G5M/GKT, all p incl. anchors | 99 |
| Spearman ρ≈0.93 | XES3G5M/GKT full pool | 99 |
| Pearson r≈0.75 | Global pooled (both datasets × both models); Fig. S3 annotation | 186 |

## F-R05

- Retained as disclosed limitation: no claim of full training-budget / compute parity between GKT and simpleKT
