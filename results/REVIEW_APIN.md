# Peer Review — Applied Intelligence (Springer)

**Manuscript:** *Leakage-Controlled Concept Graph Construction and Cold-Start
Diagnostic Protocol for Knowledge Tracing*
**Type:** Methodology / resource paper
**Reviewer recommendation:** **Major Revision**

> Simulated single-blind review written from the perspective of an APIN referee.
> It is intended to help the authors anticipate and pre-empt referee objections.

---

## 1. Summary of the manuscript

The paper proposes a *protocol* (not a new model) for constructing and auditing
knowledge-component (KC) concept graphs used by graph-augmented knowledge-tracing
(KT) models, with the goal of preventing information leakage from held-out data
into the graph. The protocol bundles: (i) learner-based temporal splits with
train-only edge inference; (ii) a DAG audit with cycle pruning; (iii) four scalar
leakage diagnostics (ECR-flag, ECR-overlap, EOC, TBVR); (iv) a *DAG Disruption
Rate* (DDR) that quantifies how graph augmentations damage prerequisite structure,
plus a structure-aware operator that shows DDR is not tautological; (v) a KC-level
cold-start stratification; and (vi) a ground-truth cross-validation of inferred
vs. expert prerequisite edges on Junyi. Experiments span Junyi, ASSISTments 2012,
XES3G5M and two synthetic logs. Headline empirical findings are largely
*diagnostic / negative*: under leakage control the benefit of an explicit concept
graph is model-specific (GKT does not beat simpleKT/AKT, GIKT stays competitive);
DDR does not predict downstream AUC drop for DGEKT; a train-only vs. full-log
ablation moves AUC by <0.001 on public data; and benchmark autocorrelation
explains inflated (~0.98) absolute AUC.

---

## 2. Scorecard (1 = poor, 5 = excellent)

| Criterion | Score | Note |
|---|---|---|
| Originality | 4 | Leakage-in-graph-construction is genuinely under-studied in KT |
| Significance / impact | 3 | Methodologically valuable but mostly negative/diagnostic results |
| Technical soundness | 3 | Solid pipeline, but statistical power and implementation parity are weak |
| Clarity / organisation | 3 | Comprehensive but long and dense; experiments sprawl over 9 subsections |
| Reproducibility | 5 | Public data, code repo, provenance logs, self-reported bug fix — exemplary |
| Fit for *Applied Intelligence* | 3 | Scope fit is the central risk (see Major Point 1) |

---

## 3. Strengths

1. **Timely, real problem.** Leakage introduced *through the auxiliary graph*
   (rather than the KT loss) is rarely audited; formalising fold-conditioned graph
   construction is a worthwhile methodological contribution.
2. **Exemplary reproducibility and scientific honesty.** Edge provenance logging,
   a public repository, three-fold bootstrap CIs, and — notably — the authors'
   disclosure of a one-step label-peek bug they found in their own GIKT head
   (Sec. 4 / Threats to Validity) is the kind of transparency reviewers reward.
3. **DDR is well-formalised and shown to be non-trivial.** The
   `prereq_preserve` operator (less disruptive than `edge_drop` at matched budget)
   convincingly demonstrates DDR discriminates structure-aware design rather than
   restating edge counts.
4. **The ground-truth cross-validation finding is interesting in its own right:**
   behavioural inference and expert curation agree at the node level (Jaccard
   ≈0.63) but not the edge level (F1 ≈0.18, direction ≈0.26). This is an
   actionable, publishable observation.
5. **Careful, non-overclaiming framing** throughout; hypotheses (H1–H3) are clearly
   labelled as non-exclusive.

---

## 4. Major points (must be addressed)

**M1. Scope/positioning for Applied Intelligence.**
APIN typically publishes *applied AI methods with demonstrated performance gains*.
This is explicitly a protocol/resource paper whose headline results are negative or
null. The authors should (a) sharpen the **actionable, applied payoff** — e.g., a
concrete checklist/tool practitioners can run, quantified cost, and at least one
case where the audit *changes a modelling decision* — and (b) state plainly why
APIN (vs. a benchmarks/resources venue) is the right home. Without this, an editor
may desk-question fit.

**M2. Statistical power is insufficient for the central claims.**
With only three folds the authors concede Wilcoxon cannot drop below p=0.25 and
fall back on paired t-tests over n=3. Claims such as "GKT trails simpleKT by 0.007,
p<0.001" are driven by vanishingly small fold variance, not by robust evidence; an
n=3 t-test is fragile. Please add: more folds and/or seeds (≥5–10), and a
prediction-level test appropriate to AUC (e.g., **DeLong** — already in your
bibliography — or bootstrap over students). The C5 conclusion hinges on this.

**M3. Benchmark saturation undermines external validity.**
Absolute AUC ≈0.98 on Junyi/ASSISTments, explained well by your autocorrelation
analysis, also means these corpora are poor instruments for measuring graph
contribution. The "graph benefit is model-specific" claim then rests largely on
near-saturated data plus one low-repeat corpus (XES3G5M). Please (a) foreground
XES3G5M (and consider a de-duplicated/repeat-controlled variant of the others), and
(b) temper conclusions accordingly.

**M4. Implementation parity confounds the model comparison (C5).**
GKT/AKT/DKT/simpleKT are stock pyKT, whereas GIKT/SKT/DyGKT/DGEKT are native
re-implementations in your fork. The GIKT bug you caught is direct evidence that
cross-implementation comparisons are risky. Please document hyperparameter budgets,
tuning protocol, and parity checks for every model, and soften any claim that a
*model class* underperforms when an *implementation* may be responsible.

**M5. Over-broad generalisation from the DDR downstream test.**
The DDR↔accuracy decoupling is evidenced by a **single backbone (DGEKT) on two
datasets**. The abstract/conclusion phrasing ("need not degrade accuracy for every
graph-consuming backbone") is broader than the evidence. Either restrict the claim
to DGEKT or add ≥1–2 more graph backbones (e.g., GKT, GIKT) to the stress test.

**M6. Are the leakage diagnostics actually informative here?**
ECR-flag = 0 by construction, ECR-overlap ≈1 on every corpus (argued to be
expected), EOC is near-constant (~1.42–1.45), and TBVR is *redefined* as a
within-train stress statistic that needs a defensive paragraph to interpret. As
presented, the suite is largely degenerate on these datasets. Please demonstrate
**discriminative power**: e.g., inject a controlled leak and show the metrics move,
or report a setting where a metric flags a real problem. Otherwise the diagnostic
contribution reads as definitional rather than empirical.

**M7. The "multi-relational" framing is only weakly supported.**
Per your own graph statistics, similarity edges are 0 on ASSISTments and Junyi and
only 354 on XES3G5M, so the graph is effectively prerequisite-only on most data.
Either demonstrate a similarity rule that fires (e.g., response-pattern correlation,
which you mention) or relabel the contribution to avoid over-stating the
multi-relational aspect.

---

## 5. Minor points

- **M-min1.** Ground-truth CV uses one dataset, one seed, one threshold (θ=0.5).
  Add a θ-sweep and at least a seed-robustness check; state generality limits.
- **M-min2.** Figure of retained KT graphs (Sec. 4.3) is "not used for inference";
  consider moving to an appendix to tighten the main text.
- **M-min3.** Experiments span nine subsections; consider consolidating
  (e.g., merge the two ablation/observation subsections) to improve readability.
- **M-min4.** H1 is referenced (Sec. on ablation) before it is defined in the C5
  subsection; reorder or add a forward pointer.
- **M-min5.** Define every acronym at first use in the body (DGEKT, GIKT, SKT,
  DyGKT) — currently several appear in tables before introduction.
- **M-min6.** The companion repository URL embeds an author identifier; if APIN
  handles this single-blind it is fine, but anonymise for review if required.
- **M-min7.** Title is long; consider shortening (e.g., "A Leakage-Controlled
  Protocol for Concept-Graph Construction and Auditing in Knowledge Tracing").

---

## 6. Reproducibility / declarations check

- Code + data availability statements present and concrete (good).
- Author contributions, funding, competing-interest, ethics statements present.
- **Action:** complete co-author e-mails; confirm the Vietnamese given/surname
  split used in the metadata; confirm the funding statement is accurate.

---

## 7. Questions to the authors

1. What is the *practical* recommendation a KT practitioner should take from this
   paper, beyond "audit your graph"? Can you quantify the cost/benefit?
2. Does any leakage diagnostic ever flag a problem on a *real* (non-synthetic)
   corpus? If not, what is its empirical value here?
3. Would the C5 ranking change with matched hyperparameter tuning and ≥5 seeds?
4. How sensitive is the ground-truth CV conclusion to θ and to the
   exercise→KC hash mapping?

---

## 8. Overall

A careful, unusually transparent methodological study on a real and under-examined
problem, with strong reproducibility. The core obstacles to acceptance are
**(i)** fit/impact framing for APIN, **(ii)** under-powered statistics behind the
central comparison, and **(iii)** several claims that out-run the evidence
(single-model DDR test, multi-relational framing, informativeness of the leakage
suite). These are addressable without new core machinery. **Major Revision.**
