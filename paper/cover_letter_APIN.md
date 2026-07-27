# Cover Letter — Applied Intelligence (APIN)

**Date:** 27 July 2026  
**To:** Professor Hamido Fujita, Editor-in-Chief, *Applied Intelligence*  
**Re:** Submission of the manuscript “Leakage-Controlled Concept Graph Construction and Cold-Start Diagnostic Protocol for Knowledge Tracing”

---

Dear Professor Fujita,

On behalf of my co-authors, I am pleased to submit the above manuscript for consideration as an original research article in *Applied Intelligence*. The manuscript has not been published previously and is not under consideration by any other journal.

Knowledge tracing models are increasingly deployed in intelligent tutoring systems to drive scheduling and gating decisions, and graph-enhanced variants depend on an auxiliary concept graph that is, in common practice, inferred from the very interaction logs used for training and evaluation. When edges are pooled before the train/test split, held-out information can reach the model through the graph even though the sequence-level split appears clean. Our manuscript addresses this problem at the level of protocol rather than model design: we propose a leakage-controlled audit procedure for knowledge-component graph construction, comprising learner-based temporal splits, fold-specific train-only edge inference with exported per-edge provenance, DAG validation with logged cycle pruning, a structural diagnostic (the DAG Disruption Rate) for graph augmentations, cold-start stratification at the knowledge-component level, and a ground-truth cross-validation procedure against expert prerequisite annotations where such annotations exist.

We evaluate the protocol on three public benchmarks (XES3G5M, ASSISTments 2012, and Junyi Academy) and two synthetic sanity logs, with nine knowledge-tracing baselines. Two findings shape the contribution. First, graph-mediated leakage shifts headline accuracy only when contamination throughput and the backbone’s reliance on the graph are simultaneously high; under realistic settings on these corpora the train-only versus full-log ablation moves AUC by at most 0.003, which means aggregate accuracy alone is an unreliable leakage alarm and independent throughput indicators are needed. Second, a controlled injection experiment shows that a contaminated graph can inflate the accuracy of graph-reliant backbones while structural flags remain silent. We therefore present the protocol as a decision-support and risk-scoring layer for trustworthy deployment — with a practitioner checklist and a decision map — rather than as a route to higher headline numbers, and we are deliberate throughout the manuscript in separating measured results from bounded observations.

We believe the work fits the journal’s focus on intelligent systems for real-life problems: the protocol is aimed directly at practitioners who must decide whether and how to deploy graph-augmented knowledge tracing in tutoring platforms, MOOC pipelines, and corporate training, and every audit signal is mapped to a concrete deployment action. All datasets used are publicly available, and the complete pipeline, configurations, and result artefacts are released in a public repository (`https://github.com/edu-risk-lab/leakage-controlled-kt-audit`) to support reproduction.

All authors have read and approved the manuscript and agree to its submission. We have no conflicts of interest to declare, and the work received no external funding. The study uses only publicly available, de-identified benchmark datasets, so no ethics approval was required. In line with the journal’s editorial policies, the manuscript includes a declaration describing the use of generative AI tools for language refinement and consistency checking; all scientific content and final decisions are the authors’ own.

Thank you for considering our manuscript. I am happy to provide any further information the editorial office may require.

Yours sincerely,

**Tuan Dao Minh**  
Hung Yen University of Technology and Education

**Co-authors:** Tuan Dao Minh, Khanh-Trinh Nguyen, Duong Nguyen Tien, Quoc Khanh Ngo, Van-Hau Nguyen, and Le Hoang Son

**Corresponding author (manuscript):** Van-Hau Nguyen — `nvhau66@gmail.com`
