"""H02: compare bib metadata to Crossref (and open DOI) for each entry with a DOI."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BIB = Path(r"d:\0. NCS\CODE\p0_project\paper\submission_APIN\refs_APIN.bib")
OUT = Path(r"d:\0. NCS\CODE\p0_project\Checklist\_h02_crossref.json")

UA = "p0-project-h02-audit/1.0 (mailto:tuanymc@local)"


def parse_bib(text: str) -> list[dict]:
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)(?=\n@|\Z)", text, re.S):
        typ, key, body = m.group(1), m.group(2), m.group(3)
        if typ.lower() in ("string", "preamble", "comment"):
            continue

        def field(name: str) -> str:
            mm = re.search(
                rf"{name}\s*=\s*(\{{([^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)*)\}}|\"([^\"]*)\")",
                body,
                re.I | re.S,
            )
            if not mm:
                return ""
            s = mm.group(2) if mm.group(2) is not None else mm.group(3)
            s = re.sub(r"%.*", "", s)
            s = re.sub(r"[{}\\]", "", s)
            s = re.sub(r"\s+", " ", s).strip()
            return s

        entries.append(
            {
                "key": key,
                "type": typ,
                "title": field("title"),
                "author": field("author"),
                "year": field("year"),
                "journal": field("journal"),
                "booktitle": field("booktitle"),
                "volume": field("volume"),
                "number": field("number"),
                "pages": field("pages"),
                "articleno": field("articleno"),
                "doi": field("doi"),
                "url": field("url"),
            }
        )
    return entries


def norm_title(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch_crossref(doi: str) -> dict | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("message")
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def crossref_summary(msg: dict) -> dict:
    if not msg or "_error" in msg:
        return msg or {}
    authors = []
    for a in msg.get("author") or []:
        given = a.get("given", "")
        family = a.get("family", "")
        authors.append(f"{family}, {given}".strip(", "))
    title = " ".join(msg.get("title") or [])
    container = " ".join(msg.get("container-title") or [])
    issued = msg.get("issued", {}).get("date-parts", [[None]])[0]
    year = str(issued[0]) if issued and issued[0] else ""
    page = msg.get("page") or ""
    article = msg.get("article-number") or ""
    volume = msg.get("volume") or ""
    issue = msg.get("issue") or ""
    return {
        "title": title,
        "authors": authors,
        "year": year,
        "container": container,
        "volume": volume,
        "issue": issue,
        "page": page,
        "article": article,
        "type": msg.get("type"),
        "doi": msg.get("DOI"),
    }


def author_overlap(bib_author: str, xref_authors: list[str]) -> float:
    if not bib_author or not xref_authors:
        return 0.0
    bib_fam = set()
    for part in re.split(r"\s+and\s+", bib_author, flags=re.I):
        part = part.strip()
        if not part:
            continue
        # "Last, First" or "{Org}" or "First Last"
        if "," in part:
            fam = part.split(",", 1)[0].strip().lower()
        else:
            toks = part.split()
            fam = toks[-1].lower() if toks else part.lower()
        fam = re.sub(r"[^a-z]", "", fam)
        if fam:
            bib_fam.add(fam)
    xref_fam = set()
    for a in xref_authors:
        fam = a.split(",", 1)[0].strip().lower()
        fam = re.sub(r"[^a-z]", "", fam)
        if fam:
            xref_fam.add(fam)
    if not bib_fam or not xref_fam:
        return 0.0
    return len(bib_fam & xref_fam) / max(len(bib_fam), len(xref_fam))


def main():
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    results = []
    for e in entries:
        row = {"key": e["key"], **{k: e[k] for k in e if k != "key"}}
        issues = []
        notes = []
        if not e["doi"]:
            notes.append("NO_DOI")
            if not e["url"]:
                issues.append("NO_DOI_NO_URL")
            row["status"] = "NO_DOI"
            row["issues"] = issues
            row["notes"] = notes
            results.append(row)
            continue

        msg = fetch_crossref(e["doi"])
        time.sleep(0.35)
        summary = crossref_summary(msg) if msg else {}
        row["crossref"] = summary
        if summary.get("_error"):
            issues.append(f"DOI_RESOLVE_FAIL:{summary['_error']}")
            row["status"] = "FAIL"
            row["issues"] = issues
            results.append(row)
            continue

        bt = norm_title(e["title"])
        xt = norm_title(summary.get("title", ""))
        if bt and xt:
            # allow substring either way for truncated titles
            if bt != xt and bt not in xt and xt not in bt:
                # token Jaccard
                bs, xs = set(bt.split()), set(xt.split())
                j = len(bs & xs) / max(1, len(bs | xs))
                if j < 0.7:
                    issues.append(f"TITLE_MISMATCH j={j:.2f}")
                else:
                    notes.append(f"TITLE_SOFT j={j:.2f}")
        else:
            issues.append("TITLE_EMPTY")

        oy = author_overlap(e["author"], summary.get("authors") or [])
        if oy < 0.5:
            issues.append(f"AUTHOR_LOW_OVERLAP={oy:.2f}")
        else:
            notes.append(f"AUTHOR_OK={oy:.2f}")

        by, xy = e["year"], summary.get("year", "")
        if by and xy and by != xy:
            issues.append(f"YEAR_MISMATCH bib={by} xref={xy}")

        # venue soft check
        venue = e["journal"] or e["booktitle"]
        cont = summary.get("container", "")
        if venue and cont:
            vn, cn = norm_title(venue), norm_title(cont)
            if vn not in cn and cn not in vn:
                # common abbrev / NeurIPS vs Advances in...
                notes.append("VENUE_SOFT_DIFF")

        # pages / articleno
        if e["pages"] and summary.get("page"):
            bp = e["pages"].replace("--", "-").replace("–", "-")
            xp = summary["page"].replace("--", "-").replace("–", "-")
            if bp != xp and bp.replace("-", "") not in xp.replace("-", ""):
                notes.append(f"PAGES_DIFF bib={bp} xref={xp}")
        if e["articleno"] and summary.get("article"):
            if e["articleno"] != summary["article"]:
                notes.append(f"ARTICLENO_DIFF bib={e['articleno']} xref={summary['article']}")

        # key-year consistency
        ym = re.search(r"(19|20)\d{2}", e["key"])
        if ym and e["year"] and ym.group(0) != e["year"]:
            notes.append(f"KEY_YEAR_DIFF key={ym.group(0)} year={e['year']}")

        row["status"] = "FAIL" if issues else "PASS"
        row["issues"] = issues
        row["notes"] = notes
        results.append(row)
        print(e["key"], row["status"], issues or notes)

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    fails = [r for r in results if r["status"] == "FAIL"]
    nodoi = [r for r in results if r["status"] == "NO_DOI"]
    print("\nSUMMARY", "total", len(results), "PASS", sum(1 for r in results if r["status"] == "PASS"), "FAIL", len(fails), "NO_DOI", len(nodoi))
    for r in fails:
        print("FAIL", r["key"], r["issues"])
    for r in nodoi:
        print("NO_DOI", r["key"], r.get("url", "")[:60])


if __name__ == "__main__":
    main()
