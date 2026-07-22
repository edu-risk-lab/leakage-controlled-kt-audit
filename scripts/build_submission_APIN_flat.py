"""Create a flat, self-contained APIN LaTeX submission package.

Copies dependencies referenced by paper/main_APIN.tex into
paper/submission_APIN_flat/ with flattened basenames and rewritten paths.
Does not modify historical result CSVs or the canonical manuscript source
beyond writing the package copy.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
SRC = PAPER / "main_APIN.tex"
OUT = PAPER / "submission_APIN_flat"

INPUT_RE = re.compile(
    r"\\(?:input|includegraphics|IfFileExists)(?:\[[^\]]*\])?\{([^}]+)\}"
)
BIB_RE = re.compile(r"\\bibliography\{([^}]+)\}")
DOCUMENTCLASS_RE = re.compile(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_dep(raw: str) -> Path | None:
    raw = raw.strip()
    bases = []
    if raw.startswith("results/") or raw.startswith("paper/"):
        bases.append(ROOT / raw)
    bases.append(PAPER / raw)
    bases.append(ROOT / raw)
    # class/bst/tex without extension
    if not Path(raw).suffix:
        for ext in (".tex", ".cls", ".sty", ".bst", ".pdf", ".png", ".jpg"):
            bases.append(PAPER / f"{raw}{ext}")
            bases.append(ROOT / f"{raw}{ext}")
    for c in bases:
        if c.exists() and c.is_file():
            return c.resolve()
    return None


def unique_flat_name(src: Path, used: dict[str, Path]) -> str:
    name = src.name
    if name not in used or used[name] == src:
        used[name] = src
        return name
    stem, suf = src.stem, src.suffix
    # disambiguate by parent folder hint
    parent = src.parent.name
    alt = f"{parent}_{stem}{suf}"
    i = 2
    while alt in used and used[alt] != src:
        alt = f"{parent}_{stem}_{i}{suf}"
        i += 1
    used[alt] = src
    return alt


def strip_comments(src: str) -> str:
    """Remove TeX % comments so example paths in build notes are ignored."""
    out = []
    for line in src.splitlines(keepends=True):
        if line.lstrip().startswith("%"):
            out.append("\n" if line.endswith("\n") else "")
            continue
        # keep escaped \% ; strip unescaped %
        buf = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "%" and (i == 0 or line[i - 1] != "\\"):
                buf.append("\n" if line.endswith("\n") else "")
                break
            buf.append(ch)
            i += 1
        else:
            out.append("".join(buf))
            continue
        out.append("".join(buf))
    return "".join(out)


def main() -> None:
    raw_text = SRC.read_text(encoding="utf-8")
    text = strip_comments(raw_text)
    deps: list[tuple[str, Path]] = []

    for m in INPUT_RE.finditer(text):
        raw = m.group(1)
        if "..." in raw or raw.endswith("/"):
            continue
        p = resolve_dep(raw)
        if p is None:
            # allow graphics without extension in tex
            p = resolve_dep(raw + ".pdf") or resolve_dep(raw + ".png")
        if p is None:
            raise FileNotFoundError(f"Unresolved dependency: {raw}")
        deps.append((raw, p))

    for m in BIB_RE.finditer(text):
        for part in m.group(1).split(","):
            part = part.strip()
            p = resolve_dep(part if part.endswith(".bib") else part + ".bib")
            if p is None:
                raise FileNotFoundError(f"Unresolved bibliography: {part}")
            deps.append((part, p))

    # class + local style files referenced by documentclass / known project files
    for m in DOCUMENTCLASS_RE.finditer(text):
        cls = m.group(1)
        p = resolve_dep(cls)
        if p is None:
            raise FileNotFoundError(f"Unresolved class: {cls}")
        deps.append((cls, p))

    # Always include Springer bst used by APIN build
    for bst in ("sn-mathphys-num.bst", "sn-basic.bst", "cuted.sty"):
        p = PAPER / bst
        if p.exists():
            deps.append((bst, p.resolve()))

    # Deduplicate by resolved path
    by_path: dict[Path, str] = {}
    for raw, p in deps:
        by_path.setdefault(p, raw)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    used_names: dict[str, Path] = {}
    mapping: dict[Path, str] = {}  # abs path -> flat name
    manifest_rows = []

    for p, raw in sorted(by_path.items(), key=lambda kv: str(kv[0])):
        flat = unique_flat_name(p, used_names)
        mapping[p] = flat
        shutil.copy2(p, OUT / flat)
        manifest_rows.append(
            {
                "original_path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "flat_filename": flat,
                "sha256": sha256(p),
                "used_by": "main_APIN.tex",
            }
        )

    # Rewrite manuscript copy (use full source including comments)
    new_text = raw_text
    # Replace longer paths first
    replacements = []
    for p, flat in mapping.items():
        rel_results = str(p.relative_to(ROOT)).replace("\\", "/") if p.is_relative_to(ROOT) else p.name
        replacements.append((rel_results, flat))
        # also paper-relative
        if p.is_relative_to(PAPER):
            replacements.append((str(p.relative_to(PAPER)).replace("\\", "/"), flat))
        replacements.append((p.name, flat))
    # unique ordered by length desc
    seen = set()
    ordered = []
    for a, b in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
        if a == b or a in seen:
            continue
        seen.add(a)
        ordered.append((a, b))

    for old, new in ordered:
        # Only rewrite inside latex path arguments roughly
        new_text = new_text.replace("{" + old + "}", "{" + new + "}")
        new_text = new_text.replace("{" + old + ".pdf}", "{" + new + "}")
        if old.endswith(".tex"):
            # \input{.../file} without extension
            new_text = new_text.replace("{" + old[:-4] + "}", "{" + new[:-4] + "}")
        if old.endswith(".bib"):
            new_text = new_text.replace("{" + old[:-4] + "}", "{" + new[:-4] + "}")

    # Prose \path{results/...} mentions are repository documentation, not package inputs.
    # Neutralise remaining results/ path tokens so the flat PDF has no parent-repo paths.
    new_text = new_text.replace(
        r"\path{results/reports/<dataset>_dag_pruning_log.csv}",
        r"\path{<dataset>\_dag\_pruning\_log.csv} (repository reports/)",
    )
    new_text = new_text.replace(
        r"\path{results/tables/disagreement_examples.csv}",
        r"\path{disagreement\_examples.csv} (repository tables/)",
    )

    # bibliography{refs_APIN} without .bib
    if (PAPER / "refs_APIN.bib").resolve() in mapping:
        flat_bib = mapping[(PAPER / "refs_APIN.bib").resolve()]
        new_text = re.sub(
            r"\\bibliography\{[^}]+\}",
            r"\\bibliography{" + flat_bib.replace(".bib", "") + "}",
            new_text,
            count=1,
        )

    # Update build notes in the flat copy
    new_text = new_text.replace(
        "Place this file at the PROJECT ROOT (next to the results/ folder), the\n"
        "%     same location the original main.tex used, so that the\n"
        "%     \\input{results/tables/...} and \\includegraphics{results/figures/...}\n"
        "%     paths resolve correctly.",
        "This file is the FLAT submission package: all \\input / \\includegraphics\n"
        "%     paths are local basenames in this directory (no results/ prefixes).",
    )

    (OUT / "main_APIN.tex").write_text(new_text, encoding="utf-8")
    manifest_rows.insert(
        0,
        {
            "original_path": "paper/main_APIN.tex",
            "flat_filename": "main_APIN.tex",
            "sha256": sha256(SRC),
            "used_by": "canonical source (paths rewritten in flat copy)",
        },
    )

    # MANIFEST.csv
    lines = ["original_path,flat_filename,sha256,used_by"]
    for r in manifest_rows:
        lines.append(
            f"{r['original_path']},{r['flat_filename']},{r['sha256']},{r['used_by']}"
        )
    (OUT / "MANIFEST.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (OUT / "BUILD_INSTRUCTIONS.txt").write_text(
        "\n".join(
            [
                "APIN flat submission package — clean-room build",
                "",
                "Requirements: pdflatex, bibtex (TeX Live / MiKTeX).",
                "Compile inside this directory only; do not rely on parent-repo paths.",
                "",
                "Commands (Windows / POSIX):",
                "  pdflatex -interaction=nonstopmode main_APIN.tex",
                "  bibtex main_APIN",
                "  pdflatex -interaction=nonstopmode main_APIN.tex",
                "  pdflatex -interaction=nonstopmode main_APIN.tex",
                "",
                "Expected output: main_APIN.pdf",
                "Do not include .aux/.log/.out in the journal upload unless requested.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # Sanity: no compile-time inputs still pointing outside the package
    bad = re.findall(r"\\(?:input|includegraphics|IfFileExists)(?:\[[^\]]*\])?\{(?:results/|\.\./)[^}]+\}", new_text)
    if bad:
        raise RuntimeError(f"Flat tex still contains external inputs: {bad[:10]}")

    print(f"Wrote flat package to {OUT} with {len(manifest_rows)} manifest rows")


if __name__ == "__main__":
    raise SystemExit(main())
