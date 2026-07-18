# Audit summary — RAPID — `2026-07-17-1541`

**Verdict: NOT READY** for submission until High findings are resolved or explicitly waived with evidence.

## Canonical inputs

| File | SHA-256 |
|---|---|
| `paper/main_APIN.tex` | `85517A952CAE70FB537B4596F4DA2EAC09433B9724E638B5DEA0576D2A83F581` |
| `paper/main_APIN.pdf` | `53889464B95DFB844F47AF6A82B5B9E3A5AF8DA862260F6DD34CE4C080A83846` |

Venue: APIN · Depth: RAPID · Source edits: **none**

## What passed (limited to rapid detectors)

- No TODO/FIXME/`??` / missing LaTeX labels or bib keys in `paper/` inventory.
- Build log clean of undefined citations/references; PDF 57 pages; all inspected `\input`/`\includegraphics` targets found under project `results/`.
- Core $\Delta$AUC $-0.041$ / CI and injection $+0.05$/~$+0.03$ match table artifacts.
- Declarations block present; key `submission_APIN` tables match `results/tables` hashes.

## Blocking issues (High)

1. **F-R01** — `simpleKT` reference described as **10 epochs** in abstract/prose/S22 but Table~S21 and Q1 caption say **30**; S15 primary `simpleKT` is also 30. Material for the epoch-ablation claim.
2. **F-R02** — DDR Pearson $r$ framed as $0.93$/$0.99$ vs caption $r{=}0.99,\rho{=}0.93$ vs figure annotation pooled $r{=}0.75$.

## Medium (triage before submit)

- F-R03 ACC bound overclaim (`0.003` vs `0.008`)
- F-R11 “unmoved” `simpleKT` under injection vs $+0.008$ in table
- F-R04 Fig.~S3 caption vs $r{=}0.75$ annotation
- F-R05/F-R06 parity + build-path documentation
- F-R07/F-R08 AI disclosure and full APIN checklist (**NOT VERIFIED**)

## Explicitly NOT VERIFIED

- Live DOI/metadata re-check; literature claim support from primary PDFs
- Code execution / result regeneration / leakage implementation audit
- Full APIN submission guidelines compliance
- Dataset licence legal review; AI tool-use history
- Pixel-level figure QA beyond selective PDF text layers

## Next action

Resolve F-R01 and F-R02 with config/log evidence, then re-run a focused consistency pass on abstract ↔ S15 ↔ S21–S22 ↔ DDR captions/figure.

Deliverables in this folder: `AUDIT_REPORT.md`, `inventory.json`, `inventory_paper.json`, `findings.csv`, `claim_evidence_matrix.csv`, `number_consistency.csv`, `remediation_plan.md`, `verification_log.md`, `audit_summary.md`.
