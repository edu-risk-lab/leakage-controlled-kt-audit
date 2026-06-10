# Cover Letter — Applied Intelligence (APIN)

**Manuscript title:** Leakage-Controlled Concept Graph Construction and Cold-Start Diagnostic Protocol for Knowledge Tracing

**Corresponding author:** Nguyen Van Hau (nvhau666@gmail.com)

---

Dear Editor,

We submit our manuscript for consideration in *Applied Intelligence* (APIN). The paper presents a **leakage-controlled audit protocol** for knowledge-component (KC) graph construction in graph-enhanced knowledge tracing (KT). It is intentionally **not** a new KT backbone and does not claim state-of-the-art accuracy gains. Instead, it targets APIN’s applied-intelligence readership by reducing **preventable deployment and benchmarking mistakes** in systems that consume inferred concept graphs.

## Why this fits APIN

APIN readers often need methods that improve the **trustworthy deployment** of intelligent systems, not only higher offline scores. Our contribution is a reproducible audit layer with:

- fold-specific graph provenance and DAG validation;
- tiered leakage diagnostics (provenance/GT as primary; scalar ECR/TBMR as sanity/stress);
- a DAG Disruption Rate (DDR) metric for structure-aware augmentation design;
- KC-level cold-start stratification;
- a five-item **practitioner checklist** for graph-KT reporting;
- open scripts and artefact exports (`https://github.com/tuanymc/p0_project`).

The paper reports an **honest boundary result**: on three public benchmarks, deliberate full-log graph pooling shifts headline AUC by at most 0.003. We position leakage control as a **decision-support and reproducibility precondition**, not as a route to large accuracy corrections.

## Applied value (decision shift, not SOTA)

We anchor model-comparison claims on **XES3G5M** (primary benchmark: low KC-repeat, non-saturated AUC). Under leakage-controlled evaluation, deployable backbone ranking changes materially—for example, GKT trails simpleKT by ≈0.041 mean AUC on XES3G5M while GIKT remains competitive (≈0.878 vs 0.875). A team ranking models on near-ceiling Junyi/ASSIST aggregates or on leaky full-log graphs could reach a different shortlist. That **decision shift** is the applied contribution we emphasize for APIN.

## Relation to reviewer concerns addressed in this revision

| Concern | Response in manuscript |
|--------|-------------------------|
| Protocol/null-result vs applied performance | Reframed as deployment audit + checklist + XES case study (§1, Conclusion) |
| Weak 3-fold inferential tests | Claims based on **ΔAUC magnitudes**; p-values relegated to supplement |
| Saturated benchmarks | XES primary; Junyi saturated sanity; ASSIST secondary (Scope, §4) |
| Implementation parity | Training parity paragraph (§4); limitations note pyKT vs native fork |
| DDR downstream overclaim | Explicitly **DGEKT-only, exploratory**; no extrapolation to all backbones |
| Degenerate leakage scalars | Three-tier audit interpretation + TBMR redefined as within-train stress |
| “Multi-relational” overclaim | Prerequisite-first wording; \|E_sim\|=0 on ASSIST reported explicitly |

## Suggested reviewers

We respectfully suggest reviewers with expertise in educational data mining, knowledge tracing benchmark discipline, graph-based machine learning reproducibility, and intelligent tutoring system evaluation.

## Declarations

- No funding received.
- No competing interests.
- All data are public benchmarks (Junyi Academy, ASSISTments 2012, XES3G5M).
- Code and reproduction artefacts are available in the companion repository.

Thank you for considering our submission.

Sincerely,

Nguyen Van Hau (on behalf of all authors)
