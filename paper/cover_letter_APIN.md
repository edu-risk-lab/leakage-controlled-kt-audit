# Cover Letter — Applied Intelligence (APIN)

**Manuscript title:** Leakage-Controlled Concept Graph Construction and Cold-Start Diagnostic Protocol for Knowledge Tracing

**Corresponding author:** Van-Hau Nguyen (`nvhau666@gmail.com`)

**Co-authors:** Tuan Dao Minh; Khanh-Trinh Nguyen; Duong Nguyen Tien; Quoc Khanh Ngo; Le Hoang Son

---

Dear Editor,

We respectfully submit the enclosed manuscript for consideration in *Applied Intelligence* (APIN).

## Originality and exclusivity

This manuscript is original, has not been published previously (including in conference proceedings or as a journal article), and is not under consideration for publication elsewhere. All co-authors have approved the submission. We confirm that we will not submit this work to another venue while it is under review at APIN.

## Contribution and fit to APIN

The paper presents a **leakage-controlled audit protocol** for knowledge-component (KC) graph construction in graph-enhanced knowledge tracing (KT). It is intentionally **not** a new KT backbone and does not claim state-of-the-art accuracy gains. The deliverable is a reproducible decision-support and leakage risk-scoring layer for practitioners who consume inferred concept graphs—aligned with APIN’s emphasis on trustworthy applied intelligent systems rather than offline score chasing alone.

Core elements include:

- learner-based temporal splits and train-only prerequisite graph construction (with DAG validation / cycle pruning);
- tiered leakage diagnostics and a DAG Disruption Rate (**DDR**) for structure-aware augmentation;
- KC-level cold-start stratification and a practitioner checklist;
- open code and provenance artefacts (`https://github.com/tuanymc/p0_project`).

We instantiate the protocol on XES3G5M (primary model-comparison benchmark), ASSISTments 2012, Junyi Academy, and two synthetic logs. Key empirical messages matched to the submitted PDF include: acyclic train-only graphs; DDR–AUC coupling that is **conditional** on backbone reliance; and, on XES3G5M under primary training budgets (Table S15), stock pyKT GKT trailing *simpleKT* by about 0.041 AUC (Table S16). A targeted seed-42 three-fold extended-training check (Table S21) is reported as exploratory configuration sensitivity (observed mean difference ≈ +0.003; uncertainty interval includes zero)—not as a compute-matched recovery claim. Graph-mediated leakage shifts headline AUC only when contamination **throughput** and graph **reliance** are both high; otherwise AUC is an unreliable leakage alarm.

## Declarations (summary)

- Funding: none.
- Competing interests: none.
- Data: public de-identified KT benchmarks (licences/terms stated in the manuscript).
- Ethics: no human-subjects experiments; ethics approval not required.
- Generative AI: ChatGPT and Cursor used for language refinement / consistency auditing; authors take full responsibility (declared in the manuscript).

Thank you for considering our submission.

Sincerely,

Van-Hau Nguyen  
Corresponding author, on behalf of all authors  
Hung Yen University of Technology and Education  
Email: nvhau666@gmail.com
