# Reference audit — Applied Intelligence (APIN) version

Reviewed 2026-06-08 against ACM DL, IEEE Xplore, Springer Link, DBLP, arXiv,
OpenReview, AAAI/ACL/EDM proceedings. The previous `refs.bib` carried a header
warning that its entries were "starter scaffolding"; that warning was justified.

**Deliverables:** `refs_APIN.bib` (corrected, APIN/Springer-Basic consistent) and
an updated `main_APIN.tex` (in-text citations fixed to match). The new file
compiles with **0 undefined citations**.

## Summary

| Status | Count | Meaning |
|---|---|---|
| Verified, correct | 24 | Real; metadata normalised only |
| Corrected (real paper, wrong metadata) | 13 | Entry repointed/fixed to the real source |
| Fabricated / not found (removed) | 4 | No such paper exists; citation dropped from text |
| In-text label fixes | 2 | Wrong model acronym in prose |

---

## 1. Fabricated / not found — REMOVED from bib and from the manuscript text

These four could not be located in any database under the given (or any close)
author/title/venue. Their in-text `\cite{}`s were removed from `main_APIN.tex`.

| Old key | Claimed title / venue | Action |
|---|---|---|
| `wang2022grapkt` | "GrapKT: Graph-Based Knowledge Tracing for Adaptive Learning", ICDM 2022 | Removed. The "(HGKT, GrapKT, IEKT)" list now reads "(HGKT, IEKT)". |
| `wang2023corekt` | "CoreKT: A Compact and Effective Knowledge Tracing Model", CIKM 2023 | Removed from the AKT/simpleKT list. |
| `xiong2023gracekt` | "Graph-Enhanced Context-Aware Knowledge Tracing", WWW 2023 | Removed; the clause now cites only `huang2022hawkt`. |
| `wan2021contrastive` | "Contrastive Learning for Knowledge Tracing", KDD 2021 | Removed. That exact title is CL4KT (Lee et al., WWW 2022), already cited as `lee2022cl4kt`. |

If you would rather keep these slots, replace each with a real model (e.g. SGKT,
JKT, GMKT) and tell me — I'll wire in verified entries.

---

## 2. Corrected — real paper existed, but the entry had wrong metadata

| Key | Was | Now (verified) |
|---|---|---|
| `chang2015junyi` | "A Crowdsourcing Approach to Building a K–12 Prerequisite Graph", Chang/Kao/Wu/Chen, L@S 2015 | **Modeling Exercise Relationships in E-Learning: A Unified Approach**, Chang, Hsu, Chen, EDM 2015, pp. 532–535 (the actual Junyi paper) |
| `chen2023hgkt` | "Hierarchical Graph Knowledge Tracing", Chen et al., WWW 2023 | **HGKT: Introducing Problem Schema with Hierarchical Exercise Graph…**, Tong, Wang, Liu, Zhou, Han, SIGIR 2022, doi 10.1145/3477495.3532004 |
| `liu2021iekt` | "Exploiting Cognitive Structure for Adaptive Learning", KDD 2021 (= CSEAL, 2019) | **Tracing Knowledge State with Individual Cognition and Acquisition Estimation** (IEKT), Long et al., SIGIR 2021, doi 10.1145/3404835.3462827 |
| `huang2022hawkt` | "…", Huang et al., CIKM 2022 | **Learning or Forgetting? A Dynamic Approach…**, Huang et al., ACM TOIS 38(2), 2020, doi 10.1145/3379507 |
| `shen2021saint` | "Convolutional Knowledge Tracing…", year 2021 | Same title but **SIGIR 2020**, doi 10.1145/3397271.3401288; author list fixed |
| `chen2022dimkt` | "Improving KT via Pre-training Question Embeddings", Chen et al., 2022 | Real authors **Liu, Yang, Chen, Shen, Zhang, Yu**, IJCAI **2020**, doi 10.24963/ijcai.2020/219 |
| `khajah2016das3h` | same title, EDM 2016 | **EDM 2014**, pp. 99–106 (and it is not DAS3H) |
| `tong2020skt` | author "Liu, Zhenya … and others" | Full correct author list; +pages 541–550, doi 10.1109/ICDM50108.2020.00063 |
| `feng2022graphmvp` | "GraphMVP…", Feng et al., NeurIPS 2022 | **Pre-training Molecular Graph Representation with 3D Geometry**, Liu et al., ICLR 2022 |
| `deckt2025` | correct title/venue, wrong authors | Authors fixed to **Bai, Wu, Wei, He**, Entropy 27(7):685, doi 10.3390/e27070685 |
| `yudelson2013pfa` | journal entry | Proper AIED 2013 inproceedings, pp. 171–180, doi 10.1007/978-3-642-39112-5_18 |
| `corbett1995bkt` | year 1995 | year **1994**, +doi 10.1007/BF01099821 |
| `yang2021gikt` | no DOI | +doi 10.1007/978-3-030-67658-2_18 (ECML-PKDD 2020 proceedings, LNCS 12457) |

### Prerequisite-learning cluster — original entries not found, repointed to verified papers
These keys were cited only inside a generic cluster (not named in prose), so they
were repointed to real, topically-matching papers with no text change needed:

| Key | Now points to (verified) |
|---|---|
| `lin2016moocprereq` | Pan, Li, Li, Tang, **Prerequisite Relation Learning for Concepts in MOOCs**, ACL 2017, doi 10.18653/v1/P17-1133 |
| `pan2020concept` | Pan et al., **Concept Extraction and Prerequisite Relation Learning from Educational Data**, AAAI 2019, doi 10.1609/aaai.v33i01.33019678 |
| `chen2020dlprereq` | Chen, Lu, Zheng, Pian, **Prerequisite-Driven Deep Knowledge Tracing**, ICDM 2018, doi 10.1109/ICDM.2018.00019 |
| `laguna2018prereq` | Liang, Ye, Wu, Pursel, Giles, **Recovering Concept Prerequisite Relations from University Course Dependencies**, AAAI 2017 |
| `heffernan2006assist` | Heffernan & Heffernan, **The ASSISTments Ecosystem**, IJAIED 2014, doi 10.1007/s40593-014-0024-x (the original "ASSISTment Builder 2006" title could not be matched exactly) |

---

## 3. In-text label fixes applied to `main_APIN.tex`

- "Self-attentive and convolutional designs **(RKT, SAINT)**" → **(SAKT, CKT)**.
  `pandey2019rkt` is actually SAKT (Pandey & Karypis, EDM 2019); `shen2021saint`
  is actually CKT (Shen et al., SIGIR 2020). The new labels match the real papers.

---

## 4. Verified as correct (metadata normalised only)

`liu2022pykt`, `abdelrahman2023kt_survey`, `piech2015dkt`, `zhang2017dkvmn`,
`ghosh2020akt`, `liu2023simplekt`, `pandey2019rkt`, `minn2018deep`,
`nakagawa2019gkt`, `dygkt2024`, `dgekt2024`, `bai2025survey`, `you2020graphcl`,
`zhu2021gca`, `xia2022simgrace`, `thakoor2021bgrl`, `velickovic2018dgi`,
`hassani2020mvgrl`, `zhu2020graphtsa`, `hamilton2017graphsage`, `kipf2017gcn`,
`lee2022cl4kt`, `song2022biclkt`, `guo2017calibration`, `delong1988auc`,
`johnson1975finding`, `chollet2021deeplearning`, `choi2020ednet`, `xes3g5m2023`,
`junyi_dataset`, `schein2002coldstart`.

---

## 5. Please double-check (minor, source-ambiguous)

- `bai2025survey`: DOI is authoritative (10.1145/3733593); the ACM volume/issue
  assignment was still settling — confirm the final volume/issue/article number.
- `dgekt2024`: DOI authoritative; issue/article number set to a best estimate.
- `thakoor2021bgrl`: **decided** — cited as the ICLR 2022 version
  ("Large-Scale Representation Learning on Graphs via Bootstrapping", Thakoor et al.,
  ICLR 2022). Verified against OpenReview; no change needed.
