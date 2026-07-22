# Human verification checklist

Do **not** treat READY FOR HUMAN VERIFICATION as CLOSED until you accept the diffs and PDF.

## Sentences / paragraphs to re-read

1. **Abstract** — primary GKT/simpleKT budgets; one cautious ~0.003 configuration-sensitivity sentence; simpleKT +0.008 under injection; DDR r with n=81/99.
2. **Contribution C5** — seed-42 three-fold check; +0.003451; CI includes 0; batch also changed; split AUC/ACC ablation bounds.
3. **§ Baseline / Training parity** — GKT batch **4**, maximum 10 epochs; simpleKT maximum 30 / batch 64; S21 exploratory wording.
4. **§ Injection** — “changed only modestly, by +0.008 AUC”.
5. **§ DDR downstream** — Pearson 0.93 (n=81) vs 0.99 (n=99) vs Spearman 0.93 (n=99).
6. **Limitations** — primary GKT max 10 vs simpleKT max 30; seed-42 check max 30 with batch 16; +0.003451 as configuration sensitivity; not fully compute-matched.
7. **Conclusion** — cautious ~0.003; AUC≤0.003 and ACC≤0.008 ablation bounds.

## Tables / captions to check

| Item | What to verify |
|---|---|
| **Table S15** | GKT Max epochs=10, Batch=4; simpleKT 30/64; footnote matches attestation |
| **Table S16** | Unchanged primary Δ intervals; prose no longer cites nine-fold pool |
| **Table S21** | Fold AUCs exactly 0.834557/0.840181, 0.833752/0.838300, 0.832624/0.832804; Mean Δ=+0.003451 |
| **S21 caption** | XES3G5M; seed 42; folds 0–2; primary 10/4; extended 30/16; exploratory; CI includes 0; epochs+batch both changed |
| **Former S22** | Absent from PDF |
| **ddr_downstream / ddr_downstream_gkt captions** | Distinct estimands + sample sizes |
| **Fig. S3 caption** | r≈0.75 = global pooled Pearson n=186 |

## Numbers to confirm

- Mean Δ = (0.005624+0.004547+0.000181)/3 = **0.003451**
- Approx. 95% CI **[−0.004, +0.011]** includes 0
- Injection simpleKT **0.850 → 0.858 = +0.008**
- Ablation max |ΔAUC| **0.003**, max |ΔACC| **0.008**

## Findings you may close (after accepting PDF)

| Finding | Close only if… |
|---|---|
| F-R01 | All epoch/max-epoch claims match attested scopes |
| F-R02 | Every DDR statistic carries type/scope/n |
| F-R03 | AUC and ACC bounds never merged incorrectly |
| F-R04 | Fig. S3 caption matches your reading of the figure |
| F-R11 | No “unmoved/unchanged” for simpleKT under injection |
| F-R12 | Primary GKT 10/4; targeted GKT30 30/16 seed42 folds0–2 |

**F-R05** — do **not** close as “parity achieved”; keep as disclosed limitation.

## Still NOT VERIFIED

- Historical **executed** epoch counts after early stopping (logs missing / mismatched)
- EXECUTION_VERIFIED lineage for paper AUC rows (~0.84) vs stale ~0.71 logs
- Full compute-matched GKT↔simpleKT experiment (not performed; not claimed)
