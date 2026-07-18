# Manuscript Audit Report

## 1. Audit identity

- Project: `p0_project` (Knowledge Tracing graph leakage / cold-start audit protocol)
- Canonical manuscript: `paper/main_APIN.tex`
- SHA-256 (tex): `85517A952CAE70FB537B4596F4DA2EAC09433B9724E638B5DEA0576D2A83F581`
- Companion PDF: `paper/main_APIN.pdf`
- SHA-256 (pdf): `53889464B95DFB844F47AF6A82B5B9E3A5AF8DA862260F6DD34CE4C080A83846`
- Audit timestamp: `2026-07-17-1541` (local); generated UTC recorded in `inventory.json`
- Audit depth: **RAPID**
- Target venue: Applied Intelligence (APIN), Springer Nature (`sn-jnl` + `sn-mathphys-num`)
- Auditor/tool configuration: `skills/audit-research-manuscript` rules + KT profile (relevance only); `manuscript_inventory.py` on `paper/`; scoped hashes for `paper/`, `results/`, `scripts/`, `src/`; PDF text inspect via editor Read; **no source edits**; DOI live-resolve and code re-execution **not** performed

## 2. Executive decision

- Readiness: **NOT READY**
- Critical open: **0**
- High open: **2** (simpleKT epoch-reference conflict; DDR correlation framing conflict across table captions / figure annotation)
- Checks not verified: reference live metadata, claim-support against primary sources, full code/result regeneration, APIN submission-checklist completeness, AI-use factual disclosure vs actual tooling history, dataset licence terms
- Most important next action: Resolve whether Phase~3 / Tables~S21–S22 compare GKT to `simpleKT` at **10** or **30** epochs, align abstract, §Training parity, Table~S15, Table~S21, and Q1 captions to one canonical protocol, then regenerate or re-label dependent $\Delta$AUC claims

## 3. Scope and evidence received

| Artifact | Version/hash | Used for | Status |
|---|---|---|---|
| `paper/main_APIN.tex` | 85517A95…2A83F581 | Canonical prose, macros, structure | Inspected |
| `paper/main_APIN.pdf` | 53889464…80A83846 | Rendered 57-page build (log); title/author page | Inspected (text); layout/figure pixels partially |
| `paper/main_APIN.log` | build 17 Jul 2026 13:42 | Undefined refs, missing inputs | Inspected |
| `paper/refs_APIN.bib` | 51614B85…4E065059 | Bibliography inventory | Inspected (structure only) |
| `results/REFERENCES_AUDIT.md` | prior author log 2026-06-08 | Historical REF cleanup note | Noted; **not** re-verified |
| `results/tables/*` (key headline tables) | see inventory | Number consistency | Inspected |
| `results/figures/fig_ddr_downstream.pdf` | text layer | Figure annotation vs caption | Inspected |
| `paper/submission_APIN/` | key tables SHA match results/ | Flat-package drift check | Spot-checked MATCH |
| `scripts/`, `src/` | inventoried | Lineage existence | Present; execution **NOT VERIFIED** |
| APIN official submission guidelines | web fetch timeout | VEN/AIP | **NOT VERIFIED** (SN AI policy from secondary SN pages only) |

Canonical source selected because the user designated `paper/main_APIN.tex`; PDF matches a successful pdflatex build of that file (57 pages; inputs resolved to project-root `results/`).

## 4. Findings

| ID | Rule | Severity | Confidence | Location | Summary | Status |
|---|---|---|---|---|---|---|
| F-R01 | CON-001 | HIGH | HIGH | Abstract L140–146; §Training parity L1459–1469; App. L2465–2486; `gkt_epoch_ablation.tex`; `training_parity.tex`; `q1_gkt_epochs30_ablation.tex` caption | `simpleKT` reference epoch is **10** in prose/abstract/S22 narrative but **30** in Table~S21 row and Q1 caption; S15 lists primary `simpleKT` at 30 epochs | OPEN |
| F-R02 | CON-001 | HIGH | MEDIUM | Abstract L131–133; `ddr_downstream.tex` caption; `ddr_downstream_gkt.tex` caption; `fig_ddr_downstream.pdf` | Pearson $r$ for XES3G5M/GKT stated as $0.93$ (core) / $0.99$ (anchors) vs pooled caption $r{=}0.99,\rho{=}0.93$; figure text layer shows pooled $r{=}0.75$ | OPEN |
| F-R03 | CON-001 | MEDIUM | HIGH | Contributions L460 vs `graph_ablation.tex` | Claim “at most $0.003$ AUC/ACC” conflicts with max $\|\Delta$ACC$\|{=}0.008$ (Junyi) | OPEN |
| F-R04 | FIG-002 | MEDIUM | MEDIUM | App. Fig.~S3 caption L2357 vs figure annotation | Caption describes DGEKT sensitivity; figure annotation reports pooled Pearson $r{=}0.75$ without matching prose explanation | OPEN |
| F-R05 | MTH-002 | MEDIUM | MEDIUM | §Training parity; Tables~S15/S21 | Primary release compares sequence@30ep vs graph@10ep; paper discloses partial parity, but F-R01 muddies whether the epoch-extended ablation holds the reference fixed | OPEN |
| F-R06 | REP-001 | MEDIUM | HIGH | Build notes L10–13 vs compile cwd `paper/` | Build notes say place tex at project root; actual build from `paper/` loads `../results` (log shows absolute `p0_project/results/...`). Reproducers may miss path setup | OPEN |
| F-R07 | AIP-001 | MEDIUM | LOW | Declarations L2559–2618 | No AI-assistance disclosure statement; SN policy requires disclosure for generative LLM content beyond copy-editing. Actual AI use history **NOT VERIFIED** | OPEN |
| F-R08 | VEN-001 | MEDIUM | LOW | Venue package | Full APIN submission-guideline checklist (limits, sections, anonymity) **NOT VERIFIED** (guidelines fetch timed out) | OPEN |
| F-R09 | REF-001 | LOW | LOW | `refs_APIN.bib` | 5 entries lack DOI fields; live DOI/title resolve not re-run this audit (prior `REFERENCES_AUDIT.md` exists) | OPEN / NOT VERIFIED |
| F-R10 | STA-003 | LOW | MEDIUM | DDR multi-seed / nine-fold pooling | Nine folds from three split seeds treated as pooled paired-$t$ sample; paper is relatively careful, but independence justification is thin | OPEN |
| F-R11 | CON-001 | MEDIUM | HIGH | Abstract L154–156 vs `downstream_auc_injection.tex` | “Sequence-only baseline is unmoved” vs `simpleKT` $+0.008$ AUC at 20% leak | OPEN |

Detailed finding blocks: see `remediation_plan.md` and `findings.csv`.

## 5. Claim–evidence coverage

| Claim | Location | Evidence | Support | Verification |
|---|---|---|---|---|
| GKT trails simpleKT by $\approx 0.041$ AUC on XES3G5M (CI $[-0.044,-0.038]$) | Abstract; Table~S16 | `bootstrap_auc_ci.tex`; baseline GKT $0.834$ vs simpleKT $0.875$ | SUPPORTED (internal tables) | Artifact inspected; regeneration **NOT VERIFIED** |
| Epoch-extended GKT recovers $\approx{+}0.003$, pooled $\Delta\approx{-}0.038$ | Abstract; S21–S22 | `gkt_epoch_ablation.tex`; pooled table | PARTIAL — numbers match tables, but reference-epoch labeling conflicts (F-R01) | Conflict OPEN |
| Full-log vs train-only moves AUC by $\le 0.003$ on public benchmarks | Abstract; ablation | `graph_ablation.tex` max $\|\Delta$AUC$\|$ | SUPPORTED for AUC | ACC overclaim at L460 (F-R03) |
| Leak injection: GKT $\approx{+}0.05$, GIKT $\approx{+}0.03$ | Abstract | `downstream_auc_injection.tex` ($0.810\to0.860$; $0.852\to0.880$) | SUPPORTED (internal) | Regeneration **NOT VERIFIED** |
| DDR predicts AUC loss, $r\approx0.93$ / $0.99$ (GKT/XES3G5M) | Abstract; GKT DDR table | `ddr_downstream_gkt.tex` caption | PARTIAL vs other captions/figure (F-R02) | Correlation recomputation **NOT VERIFIED** |
| Graph-inert cells move AUC by $\le0.003$ under total destruction | Abstract | ASSIST GKT rows in `ddr_downstream_gkt.tex` | SUPPORTED (table values) | **NOT VERIFIED** beyond table |
| Literature leakage / KT citations support framing | Intro | `refs_APIN.bib` + prior audit note | NOT VERIFIED | Primary-source claim support not re-read |
| Protocol yields acyclic train-only graphs on all corpora | Abstract | `dag_audit_summary.tex` present | NOT VERIFIED | Table not fully cross-walked in rapid pass |

## 6. Number consistency

| Concept/metric | Locations and values | Canonical source | Status |
|---|---|---|---|
| $\Delta$AUC GKT−simpleKT (10ep release) | Abstract $\approx0.041$; macro `-0.041`; S16 `-0.041` CI $[-0.044,-0.038]$; baseline $0.834$ vs $0.875$ | `bootstrap_auc_ci.tex` / macros | CONSISTENT |
| Pooled epoch-ext $\Delta$ | Abstract `-0.038` CI $[-0.040,-0.035]$; pooled table same | `gkt_epoch_ablation_pooled.tex` | CONSISTENT (numbers) |
| simpleKT epochs in S21–S22 reference | Prose: **10**; S21 table: **30**; Q1 caption: **30**; S15 primary simpleKT: **30** | Conflicting | **CONFLICT** |
| Full-log max $\|\Delta$AUC$\|$ | Abstract/concl. $0.003$; ablation table $0.003$ | `graph_ablation.tex` | CONSISTENT (AUC) |
| Full-log max $\|\Delta$ACC$\|$ | L460 claims $0.003$ AUC/ACC; table $0.008$ Junyi | `graph_ablation.tex` | **CONFLICT** |
| Injection deltas | Abstract $+0.05$/ $+0.03$; table $+0.050$/ $+0.028$ | `downstream_auc_injection.tex` | CONSISTENT (rounded) |
| DDR $r$ (GKT/XES) | $0.93$/$0.99$ vs caption $r{=}0.99,\rho{=}0.93$ vs fig $0.75$ | Multiple | **CONFLICT / clarify** |

## 7. Reproducibility and lineage

| Reported result | Dataset | Commit/config/run | Artifact/script | Status |
|---|---|---|---|---|
| Table~S16 $\Delta$AUC CI | XES3G5M | Named `scripts/bootstrap_auc_ci.py` | `results/tables/bootstrap_auc_ci.tex` | Artifact present; run **NOT VERIFIED** |
| Tables~S21–S22 | XES3G5M | `configs/xes3g5m_gkt_epochs30.yaml`; `generate_gkt_epoch_ablation.py` | `gkt_epoch_ablation*.tex` | Artifact present; run **NOT VERIFIED** |
| DDR downstream | XES/ASSIST | `ddr_downstream.csv` | `ddr_downstream*.tex` | CSV present; correlation recomputation **NOT VERIFIED** |
| Baseline CV | Public benches | `significance_testing.py` | `baseline_cv_template.tex` | Artifact present; run **NOT VERIFIED** |
| GitHub URL in declarations | — | `https://github.com/tuanymc/p0_project.git` | Remote freshness / tag | **NOT VERIFIED** |

## 8. Venue, privacy, license and AI policy

| Check | Evidence/source/date | Status | Action |
|---|---|---|---|
| Template `sn-jnl` + numbered mathphys | tex header; class file present | PASS (local) | Keep |
| Declarations block (funding, COI, ethics, data, code, authors) | L2559–2618 | PASS (present) | Confirm against APIN checklist |
| Author identities visible (non-blinded) | title page / PDF | Likely OK for journal SN; anonymity policy **NOT VERIFIED** | Confirm APIN blind policy |
| AI disclosure | Absent in manuscript | NOT VERIFIED / possible AIP gap | Add disclosure if generative LLM used beyond copy-edit |
| Dataset licences | Declarations point to public datasets | NOT VERIFIED | Confirm each licence allows stated redistribution of derived graphs |
| ORCID links | Present on authors | PASS (format) | — |

## 9. Remediation plan

See `remediation_plan.md`.

## 10. Verification limitations

- RAPID scope: no full Pass D/E execution; no statistical recomputation; no primary-source citation reading.
- Full-repo inventory hashing was aborted for time; `inventory.json` covers `paper/`, `results/`, `scripts/`, `src/`, skill tree (663 files).
- APIN submission guidelines page fetch timed out; venue checks beyond local template are **NOT VERIFIED**.
- DOI resolution and Crossref/metadata match not re-run; do not treat prior `REFERENCES_AUDIT.md` as this audit’s PASS.
- Figure visual QA limited to PDF text-layer extraction for `fig_ddr_downstream.pdf` and manuscript PDF text; pixel-level axis/legibility audit incomplete.
- Code and experiment regeneration not executed.
- Absence of TODO/`??`/undefined LaTeX refs in the current build is a PASS for those detectors only.
