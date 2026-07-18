# Final-fix remediation diff (2026-07-17)

Authorized final-remediation of `paper/main_APIN.tex` + flat submission package.
No experiments rerun. No historical result CSV fold values changed.

## Canonical manuscript

| Area | Change |
|---|---|
| Table ?? / S15 | Label `tab:training_configurations` inside caption; prose uses `Table~\ref{...}` → PDF shows **Table S15 (Table 32)** |
| Parity terminology | “Training parity” → “Training-configuration disclosure”; removed “Full epoch/batch parity” / “hyperparameter parity” |
| +0.003451 wording | “observed mean AUC was 0.003451 higher… CI included zero” + non-isolation caveat |
| Abstract | Observed mean AUC difference ≈ +0.003; uncertainty includes zero |
| Generative AI | New section *Declaration of generative AI-assisted work* (ChatGPT + Cursor) before Declarations |
| Retired macros | `\GKTthirty*` placeholders no longer use `??` |

## Generators / helpers

- `scripts/generate_gkt_epoch_ablation.py` — retired macros use `\texttt{n/a}`
- `scripts/build_submission_APIN_flat.py` — **new** flat packager
- `scripts/_final_remediation_patch.py` — one-shot text patch applicator

## Flat package

- Created `paper/submission_APIN_flat/` (no subfolders for deps)
- Clean-room build PASS → `paper/submission_APIN_flat/main_APIN.pdf` (58 pages)

## Intentionally unchanged

- S21 fold AUCs / mean 0.003451
- No S22
- Primary protocol 10/4, simpleKT 30/64, targeted 30/16 seed 42
- Historical result artefacts
