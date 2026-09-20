# Cover letter — Engineering Applications of Artificial Intelligence

**Article type:** Original Research  
**Manuscript title:** Bounding graph-mediated leakage in knowledge tracing: a train-only audit protocol with a predictive exposure measure  
**Corresponding author:** Van-Hau Nguyen (nvhau66@gmail.com)

Dear Editor,

Please consider the enclosed original research article for publication in *Engineering Applications of Artificial Intelligence*. The manuscript is not under consideration elsewhere.

**Engineering application.** Graph-enhanced knowledge tracing is used inside intelligent tutoring systems and large-scale online practice platforms to estimate mastery and to schedule practice. Concept graphs are often inferred from the same interaction logs later used for training and evaluation, so held-out learner transitions can enter the model through the graph channel. This paper treats that failure mode as a verification and operational risk-scoring problem for tutoring software, in line with the journal’s foci on decision-support systems, knowledge processing, and verification and validation of AI-based software.

**Artificial-intelligence contribution.** We introduce a *leakage exposure bound*: before any tracer is retrained, the movement in headline accuracy is limited to the product of how much a backbone relies on graph structure and how far pooling moves the graph the builder produces. Both terms are computable without a second training arm; the structural term is read as redistributed weight mass rather than as a count of leaked edges, which tightens the bound and explains why opening the builder filter admits many leaked edges yet little weight. The bound is embedded in a leakage-controlled audit protocol: learner-based temporal splits, train-only prerequisite inference, directed-acyclic-graph validation, knowledge-component cold-start stratification, and a disruption-rate diagnostic that ranks graph-augmentation operators independently of predictive accuracy.

**Public validation.** The protocol is instantiated on public educational logs (XES3G5M, ASSISTments 2012, Junyi Academy) and two synthetic logs. Retraining yields a slope of 0.084 area under the receiver operating characteristic curve per unit disruption rate on a graph-reliant backbone, versus 0.003 where the backbone is graph-inert. Replacing a pooled full-log graph with a train-only graph moves that area by at most 0.003, and deliberate 20% test-fold injection by at most 0.010; on the primary corpus the individual shifts sit at or below a measured training noise floor near 0.002, so these figures bound the channel rather than resolve it. Accuracy is therefore a poor detector of graph-mediated contamination. The audit runs as a central-processing-unit pre-training gate. The intended use is to inform graph-provenance decisions at deployment, not to introduce a new tracing architecture aimed at higher headline scores.

**Compliance with the journal’s four desk-screening conditions.**

1. This is not a metaphor-based metaheuristic paper.
2. The abstract states the artificial-intelligence contribution and the engineering application in separate labelled paragraphs.
3. The title and abstract contain no undefined acronyms.
4. The manuscript is formatted in single-column Elsevier `elsarticle` preprint layout.

The submission is double-anonymized: author identities, acknowledgements, and CRediT roles are on the separate title page. Highlights are provided as a separate file. An anonymized code archive is supplied for review; public dataset URLs are cited in the manuscript. This research received no specific grant. The authors have no competing interests. The work has not been published previously and is not under consideration elsewhere.

We believe the paper fits *Engineering Applications of Artificial Intelligence* as an engineering verification and decision-support study of graph-enhanced knowledge tracing, a setting in which the journal already publishes applied knowledge-tracing research.

Thank you for your consideration.

Sincerely,  
Van-Hau Nguyen (corresponding author)  
on behalf of Tuan Dao Minh, Khanh-Trinh Nguyen, Duong Nguyen Tien, Quoc Khanh Ngo, and Le Hoang Son
