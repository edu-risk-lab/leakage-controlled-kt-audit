---
name: audit-research-manuscript
description: Audit scientific manuscripts and their supporting references, data, code, experiment outputs, figures, tables, and supplementary files without silently rewriting them. Use when asked to review, inspect, validate, quality-check, pre-submit check, find AI-caused errors, verify citations or claims, assess reproducibility, compare manuscript sections, or produce an evidence-backed remediation plan for PDF, DOCX, LaTeX, Markdown, BibTeX, CSV, XLSX, code repositories, and experiment artifacts.
---

# Audit Research Manuscript

Perform an evidence-first scientific audit. Treat AI output as a suspicion, not proof. Keep the source manuscript unchanged unless the user separately authorizes edits.

## 1. Establish the audit contract

Determine from available files:

- canonical manuscript and version;
- authors/blinded/supplementary relationship;
- target venue and declared study type;
- available references, PDFs, data, code, logs, results and figures;
- requested scope: rapid, standard, or full audit.

If target venue or supporting artifacts are absent, continue with applicable checks and label dependent checks `NOT VERIFIED`. Do not invent requirements or evidence.

Create outputs under `audit/YYYY-MM-DD-HHMM/`. Do not overwrite a previous audit.

## 2. Preserve evidence

Before analysis:

1. List input files, sizes, modified times and SHA-256 hashes.
2. Record the canonical source selected and why.
3. Run `scripts/manuscript_inventory.py --root <project> --output <audit-dir>/inventory.json` when local files are available.
4. Never modify raw data, original manuscripts, reference PDFs, logs or result files.
5. Cite exact file, page/section/table/figure/line or structured locator for every finding.

For PDF/DOCX, inspect rendered pages when layout, formulas, tables or figures matter. Text extraction alone is not sufficient for visual claims.

## 3. Select audit depth

### Rapid audit

Check blocking and high-risk issues: unresolved placeholders, missing files, broken cross-references, reference existence/metadata, obvious claim–result conflicts, inconsistent headline numbers, blinded leaks and absent evidence.

### Standard audit

Run rapid checks plus all manuscript-level categories in `references/audit-rules.md`, citation mapping, internal consistency, claim strength, methods completeness, statistics reporting and venue-readiness.

### Full audit

Run standard checks plus data/code/experiment lineage, leakage, reproducibility, result regeneration, statistical verification, license/privacy and main–supplementary synchronization. Only mark a check verified when the necessary artifact was inspected or executed.

## 4. Execute in ordered passes

### Pass A — Deterministic inventory

- Inventory files and hashes.
- Detect TODO/FIXME, `??`, unresolved LaTeX references/citations, missing figures/tables and duplicate identifiers.
- Identify manuscript versions and supporting artifacts.
- Build a list of all tables, figures, equations, datasets, models, metrics, seeds and headline numbers.

### Pass B — Structure and internal consistency

- Compare title, abstract, contributions, RQs, methods, results, limitations and conclusion.
- Trace every headline number across abstract, tables, text, conclusion and supplementary material.
- Verify terminology, notation, acronyms, table/figure numbering and cross-references.
- Flag conclusions not directly supported by results.

### Pass C — References and claim evidence

- Parse in-text citations and bibliography.
- Separate `identifier/metadata verified` from `claim support verified`.
- Verify DOI/title/authors/year/venue using authoritative metadata when internet access is authorized.
- For claim support, inspect the original source section/page; abstract-only evidence is insufficient for strong claims.
- Classify support as `SUPPORTED`, `PARTIAL`, `CONTRADICTED`, `UNCLEAR`, or `NOT VERIFIED`.
- Never fabricate a replacement reference.

### Pass D — Methods, data and code

- Map prose → formula/pseudocode → code/config.
- Check dataset version, preprocessing order, split unit, leakage boundaries and test-set use.
- Check seed policy, checkpoint selection, metric implementation and baseline fairness.
- Require lineage from table/figure to result artifact and generating script where available.
- Execute code only when safe, in scope and dependencies are available; report commands and actual results.

### Pass E — Statistics and interpretation

- Check analysis unit, paired/unpaired design, sample size, uncertainty, effect size and multiple comparisons.
- Do not accept `significant` without appropriate evidence.
- Do not treat repeated seeds as automatically independent samples.
- Flag cherry-picking, best-seed reporting, overclaim, causal language unsupported by design and generalization beyond studied data.

### Pass F — Integrity, privacy, license and venue

- Check disclosure of AI use against the verified venue policy.
- Check authorship, acknowledgments, funding and conflicts.
- Check anonymization and blinded metadata.
- Check dataset/code/figure/table licenses and attribution.
- Flag privacy risks and restricted data exposure without reproducing sensitive content.

## 5. Classify findings

Use IDs from `references/audit-rules.md` and severities:

- `CRITICAL`: invalidates evidence or creates serious integrity/privacy/compliance risk; blocks release.
- `HIGH`: may materially alter conclusions or reproducibility; must resolve or receive documented waiver.
- `MEDIUM`: weakens clarity, transparency or rigor; triage before submission.
- `LOW`: editorial or optional improvement.

Assign confidence separately: `HIGH`, `MEDIUM`, `LOW`. Severity is impact; confidence is certainty. Never inflate severity because confidence is high.

Every finding must include:

```text
Finding ID and rule
Severity and confidence
Status
Exact location
Observed evidence
Why it matters
Required verification
Recommended remediation
Acceptance test
```

Do not report generic advice as a finding. Merge duplicate symptoms when they share one root cause.

## 6. Produce auditable outputs

Copy `assets/AUDIT_REPORT_TEMPLATE.md` to the audit directory and fill it. Also create:

- `inventory.json`;
- `findings.csv`;
- `claim_evidence_matrix.csv`;
- `number_consistency.csv`;
- `remediation_plan.md`;
- `verification_log.md`;
- `audit_summary.md`.

In `verification_log.md`, distinguish `PASS`, `FAIL`, `NOT VERIFIED`, and `NOT APPLICABLE`. Record tools/commands/sources and observed output. Never equate `NOT VERIFIED` with `PASS`.

Calculate readiness only after findings are formed:

- `BLOCKED`: any open Critical, untraceable headline result, or mandatory venue failure.
- `NOT READY`: no Critical but open High issues materially affect conclusions.
- `CONDITIONALLY READY`: only bounded Medium/Low issues remain.
- `READY FOR HUMAN PRE-SUBMISSION REVIEW`: audit checks pass; this is not an acceptance guarantee.

## 7. Remediation boundary

During audit, propose changes but do not apply them. If the user authorizes remediation:

1. create a new branch/version;
2. apply one finding at a time;
3. preserve meaning unless evidence requires correction;
4. show diff;
5. rerun affected checks;
6. never replace missing evidence with invented content;
7. keep Critical findings open until an authorized human reviewer accepts evidence.

## 8. Domain profiles

Use the general rules for every paper. For Knowledge Tracing or Educational Data Mining, additionally read `references/knowledge-tracing-profile.md` and apply it only when relevant.

## 9. Stop conditions

Stop and report a blocker rather than guess when:

- the canonical manuscript cannot be identified;
- an encrypted/corrupt file prevents required inspection;
- a strong claim needs a source that is unavailable;
- results require data/code not provided;
- external access or execution would exceed authorization;
- a requested automatic correction would fabricate evidence or conceal an issue.
