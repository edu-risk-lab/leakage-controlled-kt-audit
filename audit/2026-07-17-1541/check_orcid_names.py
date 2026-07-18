"""Compare manuscript author (fnm/sur) against ORCID public person records."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

AUTHORS = [
    ("Dao Minh", "Tuan", "0009-0009-1641-6813", "tuanymc@utehy.edu.vn"),
    ("Nguyen Khanh", "Trinh", "0009-0004-3739-0484", "trinhnk@utehy.edu.vn"),
    ("Nguyen Tien", "Duong", "0009-0007-1104-7129", "duongnt@utehy.edu.vn"),
    ("Ngo Quoc", "Khanh", "0009-0001-9250-6433", "quockhanhngo.official@gmail.com"),
    ("Nguyen Van", "Hau", "0000-0002-3256-5626", "nvhau666@gmail.com"),
    ("Le Hoang", "Son", "0000-0001-6356-0046", "sonlh@vnu.edu.vn"),
]


def fetch_person(orcid: str) -> dict:
    req = urllib.request.Request(
        f"https://pub.orcid.org/v3.0/{orcid}/person",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def norm(s: str | None) -> str:
    if not s:
        return ""
    return " ".join(s.replace("-", " ").split()).casefold()


def main() -> None:
    rows = []
    for fnm, sur, orcid, email in AUTHORS:
        person = fetch_person(orcid)
        name = person.get("name") or {}
        given = (name.get("given-names") or {}).get("value")
        family = (name.get("family-name") or {}).get("value")
        credit = (name.get("credit-name") or {}).get("value")
        ms_full = f"{fnm} {sur}"
        orcid_gf = " ".join(x for x in (given, family) if x)
        # Common Vietnamese Westernized order in Springer: Given Sur / Family last syllable
        checks = {
            "fnm==given & sur==family": norm(fnm) == norm(given) and norm(sur) == norm(family),
            "fnm==family & sur==given": norm(fnm) == norm(family) and norm(sur) == norm(given),
            "full==credit": norm(ms_full) == norm(credit),
            "full==given+family": norm(ms_full) == norm(orcid_gf),
            "full==family+given": norm(ms_full) == norm(f"{family} {given}"),
        }
        ok = any(checks.values())
        # Recommend Springer-style from ORCID: prefer credit-name; else given/family as-is
        if credit:
            rec = f"use credit-name: {credit}"
        else:
            rec = f"ORCID fields: given={given!r}, family={family!r}"
        rows.append(
            {
                "orcid": orcid,
                "email": email,
                "ms_fnm": fnm,
                "ms_sur": sur,
                "orcid_given": given,
                "orcid_family": family,
                "orcid_credit": credit,
                "aligned": ok,
                "checks": checks,
                "note": rec,
            }
        )

    out = Path(__file__).with_name("orcid_name_audit.json")
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Manuscript vs ORCID public name\n")
    for r in rows:
        status = "OK" if r["aligned"] else "MISMATCH"
        print(f"[{status}] {r['orcid']}")
        print(f"  MS:     \\fnm{{{r['ms_fnm']}}} \\sur{{{r['ms_sur']}}}")
        print(
            f"  ORCID:  given={r['orcid_given']!r}  family={r['orcid_family']!r}"
            f"  credit={r['orcid_credit']!r}"
        )
        if not r["aligned"]:
            print(f"  -> {r['note']}")
            # Suggest Springer mapping: family-name -> sur, given-names -> fnm
            g, f = r["orcid_given"], r["orcid_family"]
            if g and f:
                print(f"  Suggest (ORCID field order): \\fnm{{{g}}} \\sur{{{f}}}")
        print()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
