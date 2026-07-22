# Final language remediation diff

Authorized final-remediation after focused audit of `main_APIN(2).pdf`.
No experiments. No result-artefact edits. S21 fold values unchanged.

## Task A — Baseline Diagnostic grammar

**Before (broken two-subject comma splice):**  
“…(Table S21), the extended-training GKT configuration (…), the observed mean AUC was…”

**After:**  
“…(Table S21), the observed mean AUC under the extended-training GKT configuration (maximum 30 epochs, batch size 16) was 0.003451 higher than under the primary GKT configuration (maximum 10 epochs, batch size 4); however, the approximate 95% CI [−0.004, 0.011] included zero. Because both the maximum epoch budget and batch size changed, this exploratory comparison does not isolate the effect of epochs.”

## Task B — AI declaration

Removed overstrong “independently reviewed and verified…”.

Replaced with review-against-available-sources wording; authors make final decisions; AI not listed as author. ChatGPT + Cursor retained.

## Task C — Limitations S21 wording

Removed “Therefore …; however …” double hedge.

Now: observed +0.003451, but CI includes zero; because batch size also differed (already disclosed in prior sentence: 4 vs 16); exploratory configuration sensitivity; not a fully compute-matched comparison.

## Unchanged

- Protocols 10/4, 30/64, targeted 30/16 seed 42  
- S21 fold table + CI  
- No S22  
- Funding / Competing interests / Ethics / Consent / Data / Code / Author contributions  
