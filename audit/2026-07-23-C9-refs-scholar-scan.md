# C9 — Reference verification and 2025–2026 literature scan

**Date:** 2026-07-23  
**Scope:** Verify in-text refs [6][11][13][18][29]; remove unstable URLs; Scholar-style scan for graph-leakage / provenance prior art.

## Verified bibliography entries (first-appearance numbering)

| Ref | Key | Status | Notes |
|-----|-----|--------|-------|
| [6] | `pandey2019rkt` | **Fixed** | EDM 2019, pp. 384–389; DOI `10.48550/arXiv.1907.06837`. Removed unstable Google Drive `url`. |
| [11] | `dygkt2024` | **OK** | KDD 2024, pp. 409–420; DOI `10.1145/3637528.3671773`. |
| [13] | `chen2023hgkt` | **OK** | HGKT, SIGIR 2022, pp. 405–415; DOI `10.1145/3477495.3532004`. Bib key retains `chen2023` alias; authors are Tong et al. |
| [18] | `badran2024labelleakage` | **OK** | arXiv:2403.15304 / SciTePress 2025 proceedings; DOI `10.48550/arXiv.2403.15304`. Covers **sequence-level label leakage** in KC-expanded inputs, not graph-provenance audit. |
| [29] | `bai2025survey` | **Fixed** | ACM CSur 2025; added vol. 57, no. 9, articleno 229; DOI `10.1145/3733593`. |

## Scholar-style scan (2025–2026)

Queries: *knowledge tracing graph leakage*, *concept graph provenance*, *leakage-free knowledge tracing*.

| Work | Relevance | Action |
|------|-----------|--------|
| Badran & Preisach (2024/2025) [18] | Sequence label leakage in multi-KC items | Already cited; intro now contrasts sequence-level remedies vs. graph-provenance gap. |
| Leakage-free recency-aware embeddings (arXiv:2508.17092, 2025) | MASK-based sequence leakage fix | **No add** — orthogonal to graph-provenance audit; would dilute scope. |
| pyKT / KT surveys (Liu 2022; Abdelrahman 2023) | Split discipline, not graph builder audit | Already cited. |
| Prerequisite-relation surveys (Bai 2025 [29]; Pan 2017) | Edge inference methods, not leakage audit | Already cited in Related Work. |

**Conclusion:** No 2025–2026 paper found that subsumes fold-specific **graph-provenance** auditing (train-only $G_f$, throughput/TBMR, controlled injection). The “under-specified” claim is retained but scoped: relative to sequence-level label-leakage work [18], not as an absolute “no prior art” statement.

## Manuscript edits tied to C9

- `refs_APIN.bib`: removed Google Drive from [6]; completed [29] metadata.
- `main_APIN.tex` intro: graph-provenance gap qualified vs. [18].
