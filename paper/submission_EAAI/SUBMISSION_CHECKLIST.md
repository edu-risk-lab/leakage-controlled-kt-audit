# EAAI submission checklist

Source: [Guide for authors](https://www.sciencedirect.com/journal/engineering-applications-of-artificial-intelligence/publish/guide-for-authors) (ISSN 0952-1976).

## Four automatic desk-reject rules

- [x] Not a metaphor-based metaheuristic paper
- [x] Abstract states **AI contribution** and **engineering application** as separate labelled paragraphs
- [x] No undefined acronyms in **title** or **abstract** (knowledge tracing, area under the curve, directed-acyclic-graph disruption rate are spelled out)
- [x] Single-column format (`elsarticle` preprint)

## Other editorial requirements

- [x] Abstract ≤ 250 words (current draft ≈ 239; 247 if hyphenated compounds are split)
- [x] Keywords: 1–6
- [x] Double-anonymized manuscript (no author names, no acknowledgements, no GitHub identity)
- [x] Separate title page with authors, corresponding address, acknowledgements, CRediT, funding, competing interests
- [x] Highlights: 3–5 bullets, each ≤ 85 characters (`highlights.txt`)
- [x] Generative-AI declaration on the manuscript (text tools only; no AI figures)
- [x] Data statement + public datasets
- [x] Manuscript ≤ 50 pages / 100 MB (`main_EAAI.pdf` is 47 pages, well under 100 MB)
- [x] Graphical abstract (`graphical_abstract.pdf`, TikZ, no generative AI)
- [x] Supplementary PDF (`supplementary_EAAI.pdf`, 23 pages)
- [ ] Elsevier competing-interest Word form — corresponding author must generate it at https://declarations.elsevier.com/home (answers in `EM_METADATA.md`; cannot be faked in-repo)
- [x] Inspec classification codes prepared (`EM_METADATA.md`): C7810C, C1230L, C1230D, C6170K, C6150G, C6130S — still must be typed into Editorial Manager
- [x] Anonymized code zip for review (`EAAI_code_anonymized.zip`; rebuild with `scripts/package_anonymized_review_zip.py`)
- [ ] Confirm corresponding author and authorship order with all co-authors before submit (order on the title page: Tuan Dao Minh first; Van-Hau Nguyen corresponding, fifth)

## Suggested Editorial Manager article type

Original Research (contributed paper). Regular issue, not a special issue, unless you later choose one that truly fits.

## Remaining scientific risk (not a formatting issue)

EAAI still wants “novel aspects of AI used for a real-world engineering application.”
The rewrite sells the **leakage exposure bound** (reliance times structural delta, computable on a central processing unit before training) plus the train-only audit as the AI method, and **tutoring-system verification** as the application. Observed shifts sit at or below the measured noise floor, so they **bound the channel rather than resolve it**.

It does **not** invent a new tracer that beats state-of-the-art accuracy. An editor who only accepts new backbones can still desk-reject. That risk is lower than at Applied Intelligence if they read the labelled abstract, but it is not zero.

## Do not

- Mention the Applied Intelligence decision in the manuscript or (preferably) the cover letter
- Use undefined acronyms (KT, KC, DDR, AUC, GKT) in the title or abstract
- Upload `main_EAAI.tex` with author names restored
- Generate a graphical abstract with ChatGPT / image models (Elsevier forbids this)
