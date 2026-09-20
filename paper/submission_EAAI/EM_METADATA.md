# Editorial Manager metadata (not for reviewers)

Fill these fields in Editorial Manager. Do **not** put this file in the
LaTeX source zip or the anonymized code zip.

## Article type

Original Research (contributed paper). Regular issue.

## Corresponding author

Van-Hau Nguyen  
Department of Quality Assurance and Testing  
Hung Yen University of Technology and Education, Hung Yen, Vietnam  
E-mail: nvhau66@gmail.com  
ORCID: 0000-0002-3256-5626

## Authorship order (must be confirmed with all co-authors before submit)

This is the order on `title_page.tex`. Do not reorder in EM without updating
the title page, cover letter, `CITATION.cff`, and `pyproject.toml`.

| # | Name | Affiliation | ORCID | CRediT (short) |
|---|---|---|---|---|
| 1 | Tuan Dao Minh | UTEHY | 0009-0009-1641-6813 | Conceptualization, methodology, software, investigation, data curation, formal analysis, visualization, writing — original draft |
| 2 | Khanh-Trinh Nguyen | UTEHY | 0009-0004-3739-0484 | Software, investigation, data curation, formal analysis |
| 3 | Duong Nguyen Tien | UTEHY | 0009-0007-1104-7129 | Software, investigation, data curation, formal analysis |
| 4 | Quoc Khanh Ngo | AIRCA / ITI, VNU | 0009-0001-9250-6433 | Writing — review and editing, validation |
| 5 | Van-Hau Nguyen (corresponding) | UTEHY | 0000-0002-3256-5626 | Supervision, methodology, writing — review and editing |
| 6 | Le Hoang Son | ITI, VNU | 0000-0001-6356-0046 | Supervision, methodology, writing — review and editing |

First author is Tuan Dao Minh. Corresponding author is fifth.

## Inspec classification codes (up to 6)

Guide for Authors: “Please provide up to 6 standard Inspec classification
codes.” Enter these in the EM classification field (not in the anonymized PDF).

| Code | Heading | Why it fits |
|---|---|---|
| C7810C | Computer-aided instruction | Tutoring-system / online-practice application |
| C1230L | Learning in AI | Knowledge tracing as learner modelling |
| C1230D | Neural nets | Graph-enhanced tracers (GKT) used as consumers |
| C6170K | Knowledge engineering techniques | Knowledge-component / concept-graph construction |
| C6150G | Diagnostic, testing, debugging and evaluating systems | Train-only audit and disruption-rate instrument |
| C6130S | Data security | Graph-channel leakage / provenance contamination |

Copy-paste line for EM:

```
C7810C, C1230L, C1230D, C6170K, C6150G, C6130S
```

If a dropdown lacks `C6170K`, use `C1230R` (reasoning and inference in AI).
If it lacks `C6130S`, use `C7110` (educational administration). Do not use
Section D codes (retired after 2019).

Keywords already in the manuscript (do not add Inspec codes there):

```
knowledge tracing; concept graphs; data leakage; decision support;
intelligent tutoring; diagnostics
```

## Competing-interest Word form

EM requires the **tool-generated** Word file, not a homemade statement.
The manuscript and title page already contain the standard “no competing
interests” sentence; that does **not** replace the upload.

1. Open https://declarations.elsevier.com/home
   (or the “Declaration of Interest” link on EM Attach files).
2. Corresponding author: Van-Hau Nguyen, nvhau66@gmail.com.
3. List all six authors as on the title page.
4. Answer **No** to financial support from a third party for this work,
   financial relationships that could be affected, patents, and other
   competing interests.
5. Funding: none (no specific grant).
6. Download the `.doc` / `.docx`.
7. In EM, item type **Conflict of Interest** / **Declaration of Interest**.

Downloaded file (do not commit; do not put in either zip):
`declarationStatement (haunv).docx`.
The checked box is the standard “no known competing financial interests
or personal relationships” statement, matching the title page.

The tool e-mails a one-time password to the corresponding author. That step
cannot be completed from this repository.

## Anonymized code archive

Build (repo root):

```powershell
py -3 scripts/package_anonymized_review_zip.py
```

Output: `paper/submission_EAAI/EAAI_code_anonymized.zip`.

Upload as **Computer code** if EM offers that item type; otherwise as a
second **Supplementary material** file. Do **not** label it LaTeX source
and do **not** put it inside `EAAI_latex_source.zip`.

The zip is scanned for author names, e-mails, ORCIDs, and the public GitHub
organisation. If the scan fails, the script refuses to write the archive.

## EM attach-files map

| Item type | File |
|---|---|
| Manuscript | `main_EAAI.pdf` |
| LaTeX source files | `EAAI_latex_source.zip` (run `_make_em_zip.ps1`) |
| Title page | `title_page.pdf` (rebuilt 2026-09-20; `title_page_em.pdf` is equivalent) |
| Highlights | `highlights.txt` |
| Graphical abstract | `graphical_abstract.pdf` |
| Supplementary material | `supplementary_EAAI.pdf` |
| Cover letter | paste `CoverLetter_EAAI.md` into Word if EM wants `.doc` |
| Conflict of Interest | `declarationStatement (haunv).docx` |
| Computer code / extra supplementary | `EAAI_code_anonymized.zip` |

Do not upload `title_page.tex`, `refs_APIN.bib`, this metadata file, or a
manuscript PDF that lists authors.
