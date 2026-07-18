# FINAL HUMAN VERIFICATION CHECKLIST

Do **not** treat READY FOR HUMAN VERIFICATION as CLOSED until you accept the PDF and package.

Please confirm each item:

1. **Table ?? gone** — Appendix K reads `Table S15 (Table 32)` (or whatever current float number `\ref` yields); no `??` anywhere in the PDF.
2. **Parity → configuration disclosure** — headings/captions/prose no longer claim epoch/batch “parity” for primary models.
3. **AI declaration matches reality** — ChatGPT and Cursor were used as described (language refinement, consistency checking, manuscript-quality auditing).
4. **AI tools list** — no tool wrongly listed or omitted; AI is not an author; AI did not independently verify results or run experiments.
5. **S21 intact** — folds 0–2 values unchanged (0.834557/0.840181, 0.833752/0.838300, 0.832624/0.832804; mean +0.003451).
6. **No S22 nine-fold** — absent from PDF and flat package.
7. **No result-artefact edits** — AUC/ACC/NLL/CI CSVs untouched in this pass.
8. **Flat package builds independently** — `paper/submission_APIN_flat` compiles without parent-repo paths.
9. **Final PDF is the intended submission** — `paper/main_APIN.pdf` (canonical) and/or flat PDF match what you intend to upload.
10. **Findings may be closed only after you read the PDF** — F-N01, F-R05, F-R06, F-R07, and prior F-R01/02/03/04/11/12.

## Still NOT VERIFIED until you say so

- Completeness of AI-tool disclosure.
- Any venue-specific APIN upload checklist items beyond this package.
