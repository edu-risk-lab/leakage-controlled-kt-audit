# Revision to Applied Intelligence (APIN) journal standard

**File:** `main_APIN.tex` — journal version of the manuscript, converted from the
LNCS proceedings format to the Springer Nature journal template.

## What changed

**1. Template / format (LNCS -> Springer Nature journal).**
- Document class switched from `\documentclass[runningheads]{llncs}` to
  `\documentclass[pdflatex,sn-basic]{sn-jnl}`. `sn-basic` = "Springer Basic,
  numbered", the reference style Applied Intelligence uses for computer science.
- Author/affiliation block rewritten in sn-jnl form (`\author*[..]{\fnm{..}\sur{..}}`,
  `\affil[..]{\orgname{..}\orgaddress{..}}`). Dao Minh Tuan is set as the
  corresponding author (`\author*`).
- `\titlerunning` / `\authorrunning` replaced by the sn-jnl short-title argument.
- Bibliography switched from `\bibliographystyle{splncs04}` to the class-driven
  Springer Basic style (no manual `\bibliographystyle`; `\bibliography{refs}` kept).
- A robust `\path` definition was added (the journal class does not provide it).

**2. Abstract.** Rewritten and tightened to ~250 words in plain prose, with no
citations and minimal inline math, per Springer journal abstract guidelines
(the LNCS abstract was ~450 words and equation-heavy).

**3. Declarations (mandatory for Springer journals).** New `Declarations`
section added in the back matter: Funding, Competing interests, Ethics approval,
Consent, Data availability, Code availability, and Author contributions. The
former "Ethics and data use" paragraph in the Conclusion was folded into this
section to avoid duplication. An Acknowledgements heading was also added.

**4. Numbers verified against your result files.** Every quantitative claim was
cross-checked against the CSVs in `results/tables/` (DDR sweep, leakage metrics,
DAG audit, autocorrelation, downstream stress test, GT cross-validation,
significance tests). All matched EXCEPT one:
- The XES3G5M downstream DDR-AUC correlation p-value read `p=0.52` in the prose
  but the generated table (`ddr_downstream.tex`) reports `p=5.1e-01`. Corrected
  the prose to **`p=0.51`**.

**5. Body content preserved.** All sections, equations, `\input{results/tables/..}`,
`\includegraphics{results/figures/..}`, labels, `\cref`/`\cite` references are
unchanged, so the file remains a drop-in build against your existing repo.

## Before you compile
1. Move `main_APIN.tex` up one level - to the **project root** (next to your
   current `main.tex` and the `results/` folder) - so the `results/tables/` and
   `results/figures/` paths resolve.
2. Add `sn-jnl.cls` and `sn-basic.bst` from the Springer Nature LaTeX template
   (springernature.com LaTeX author support, or the Overleaf "Springer Nature
   LaTeX Template").
3. Compile: pdflatex -> bibtex -> pdflatex -> pdflatex.

## Please confirm / fill in (placeholders I could not source)
- **Co-author emails** - only your email is in the file; the others are blank.
- **Author-name split** - names were split as `\fnm{Nguyen Tien}\sur{Duong}` etc.
  (last word = surname, matching the old "D. M. Tuan" running head). Adjust if a
  different family-name convention is intended.
- **Author contributions** - drafted a reasonable CRediT statement; verify roles.
- **Funding** - drafted as "no funding received"; change if grants apply.

## Verified locally
Test-compiled against a stand-in class (sn-jnl not in this environment):
38-page PDF, 0 undefined citations (all 49 references resolved), all tables and
figures found, balanced environments.
