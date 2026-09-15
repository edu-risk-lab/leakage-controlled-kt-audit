# Elsevier LaTeX instructions — EAAI compliance

Source: [LaTeX instructions](https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions)
(checked 2026-09-08). Journal-specific rules still come from the
[EAAI Guide for Authors](https://www.sciencedirect.com/journal/engineering-applications-of-artificial-intelligence/publish/guide-for-authors).

## Verdict

The manuscript uses the **correct Elsevier article class** (`elsarticle`,
not `ecrc` / Procedia CRC, not a Word two-column file). The working
directory is **flat** (no subfolders in `\input` / `\includegraphics`
paths). A local PDF builds without fatal errors.

The gaps were **upload packaging**, not the class file: Editorial Manager
must receive a compiled PDF + one flat source archive, and `.tex` files
must **not** be labelled Supplementary material.

`elsarticle.cls` in this folder was generated from your downloaded
`docs/elsarticle/elsarticle.ins` + `elsarticle.dtx`.

## Checklist against the Elsevier page

| Instruction | Status |
|---|---|
| Use the Elsevier article class `elsarticle` | Pass |
| Do **not** use `ecrc.sty` unless the journal is camera-ready (Procedia, etc.) | Pass — EAAI is not CRC |
| CAS `cas-sc` / `cas-dc` only if the journal asks for that workflow | Pass — EAAI Guide does not require CAS; single-column `preprint` matches the desk-reject rule |
| Reference style: follow the journal Guide for Authors | Numbered `elsarticle-num` is valid at submission (GfA: any consistent style). GfA prose describes author–year; switch to `elsarticle-harv` only if you want exact GfA style |
| Compile a PDF locally and upload it as **Manuscript** | `main_EAAI.pdf` (45 pages, under the 50-page EAAI cap) |
| Bundle **all** source in **one archive**, item type **LaTeX source files** | Use `EAAI_latex_source.zip` (created beside this file) |
| No subfolders in the archive | Pass — every path is a basename |
| Do **not** upload `.tex` as Supplementary material | Upload `supplementary_EAAI.pdf` as Supplementary; keep `.tex` only inside the source zip |
| Figures in the same folder as the `.tex` | Pass |
| Include `.bbl` so citations do not become `?` if EM skips BibTeX | `main_EAAI.bbl` is in the zip |
| Include `.cls` / `.bst` used by the paper | `elsarticle.cls`, `elsarticle-num.bst` |
| Packages not in TeX Live | None required (`hyperref`, `cleveref`, `tikz`, … are in TeX Live) |
| Overleaf / EM compile: no ignored errors | Local `pdflatex` exit code 0 |

## What to click in Editorial Manager

1. **Manuscript** — `main_EAAI.pdf` only (anonymized).
2. **LaTeX source files** — `EAAI_latex_source.zip` (flat). Do **not**
   put this zip under Supplementary material.
3. **Title page** — `title_page.pdf` (authors, CRediT, acknowledgements).
   Do **not** put `title_page.tex` in the source zip.
4. **Highlights** — `highlights.txt` (also already inside the manuscript
   frontmatter).
5. **Graphical abstract** — `graphical_abstract.pdf`.
6. **Supplementary material** — `supplementary_EAAI.pdf` only.
7. **Cover letter** — `CoverLetter_EAAI.md` (paste into Word if EM wants
   `.doc`).
8. Competing-interest form from Elsevier’s declarations tool
   (https://declarations.elsevier.com/home). Item type **Conflict of
   Interest**.
9. **Computer code** (or a second Supplementary file) —
   `EAAI_code_anonymized.zip`. Rebuild with
   `py -3 scripts/package_anonymized_review_zip.py` from the repo root.
   Do **not** put this zip inside `EAAI_latex_source.zip`.

Inspec codes and authorship order: `EM_METADATA.md` (editor metadata;
do not upload that file).

If EM later asks for individual source files instead of a zip:

- Item type **Manuscript**: `.tex`, `.bbl`, `.bst`, `.bib`, `.cls`
- Item type **Figure**: `fig_*.pdf`, `graphical_abstract.pdf`

## Do not upload into the source zip

Build junk (`.aux`, `.log`, `.out`, `.blg`), `refs_APIN.bib`, CSV
exports, `title_page.tex`, markdown notes. They either leak identity,
confuse EM, or are not needed to compile.
