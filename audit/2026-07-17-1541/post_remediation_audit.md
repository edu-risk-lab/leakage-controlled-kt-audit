# Post-remediation focused audit

Scope: abstract, contributions, experimental setup, S15, S16, S21, former S22 locus, DDR captions, Fig. S3, limitations, conclusion + repo phrase scan.

## Phrase / claim scan (submission sources)

| Needle | Result |
|---|---|
| simpleKT 10 epochs / reference at 10 epochs | ABSENT in `main_APIN.tex` |
| GKT batch 8 as primary | ABSENT |
| GKT batch 32 / S21 batch 32 | ABSENT |
| GKT batch 16 outside targeted seed-42 check | Only targeted extended / GIKT native batch 16 (native models unchanged) |
| epoch-matched | ABSENT |
| nine-fold epoch extension / Table S22 | ABSENT |
| unmoved (simpleKT) | ABSENT; remaining “AUC unmoved” is manipulation-check inert-backbone row |
| 0.003 AUC/ACC | ABSENT; split into 0.003 AUC and 0.008 ACC |
| unsupported pooled Δ/CI (GKTthirty*) | Macros retired; unused in prose |

## Section verdicts

| Area | Verdict |
|---|---|
| Abstract | PASS_FOCUSED — cautious ~0.003 sentence; primary budgets; injection +0.008; DDR n labeled |
| Contributions C5 | PASS_FOCUSED — config sensitivity; no S22 |
| Experimental setup / training parity | PASS_FOCUSED — GKT 10/4; simpleKT 30/64 max epochs |
| S15 | PASS_FOCUSED — regenerated from canonical yaml |
| S16 prose | PASS_FOCUSED — no nine-fold residual |
| S21 | PASS_FOCUSED — fold table + exploratory caption |
| Former S22 | REMOVED |
| DDR captions / Fig S3 | PASS_FOCUSED — estimands scoped |
| Limitations | PASS_FOCUSED — author-required compute/config paragraph present |
| Conclusion | PASS_FOCUSED — narrowed |

## Remaining NOT VERIFIED (unchanged class)

- Exact **executed** epoch counts after early stopping for historical primary/GKT30 runs (no matching logs) → protocol described as **maximum epochs** only.
- EXECUTION_VERIFIED training-loop provenance for paper S15–S21 AUC rows.
- Full compute-matched GKT vs simpleKT comparison (explicitly not claimed).
- Whether HEAD `configs/xes3g5m.yaml` batch matches historical primary (it does not; manuscript no longer uses HEAD for primary GKT).

## Finding status after re-audit

All of F-R01, F-R02, F-R03, F-R04, F-R11, F-R12 → **READY FOR HUMAN VERIFICATION** (not CLOSED).  
F-R05 → retained disclosed limitation.
