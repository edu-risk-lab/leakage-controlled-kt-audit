#!/usr/bin/env python3
"""Create a read-only manuscript inventory and deterministic warning list."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

TEXT_EXTENSIONS = {".tex", ".bib", ".md", ".txt", ".rst", ".csv", ".tsv", ".yaml", ".yml", ".json"}
SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "__pycache__", "audit"}
PATTERNS = {
    "placeholder": re.compile(r"\b(?:TODO|FIXME|TBD|XXX)\b", re.I),
    "unresolved_marker": re.compile(r"(?:Table|Figure|Fig\.|Equation|Eq\.|Appendix|Section)\s*\?\?|\?\?"),
    "latex_ref": re.compile(r"\\(?:ref|eqref|autoref|cref)\{([^}]+)\}"),
    "latex_label": re.compile(r"\\label\{([^}]+)\}"),
    "latex_cite": re.compile(r"\\(?:cite|citep|citet|parencite|textcite)\w*\{([^}]+)\}"),
    "bib_key": re.compile(r"^\s*@\w+\s*\{\s*([^,]+),", re.M),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def readable_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS or path.stat().st_size > 20 * 1024 * 1024:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    files: list[dict] = []
    labels: set[str] = set()
    refs: list[tuple[str, str]] = []
    bib_keys: set[str] = set()
    cites: list[tuple[str, str]] = []
    warnings: list[dict] = []

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root)
        if any(part in SKIP_PARTS for part in relative.parts) or path.resolve() == output:
            continue
        stat = path.stat()
        files.append({
            "path": relative.as_posix(),
            "size": stat.st_size,
            "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "sha256": sha256(path),
        })
        text = readable_text(path)
        if text is None:
            continue
        for kind in ("placeholder", "unresolved_marker"):
            for match in PATTERNS[kind].finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                warnings.append({"type": kind, "path": relative.as_posix(), "line": line, "value": match.group(0)})
        labels.update(PATTERNS["latex_label"].findall(text))
        refs.extend((relative.as_posix(), x) for x in PATTERNS["latex_ref"].findall(text))
        bib_keys.update(x.strip() for x in PATTERNS["bib_key"].findall(text))
        for group in PATTERNS["latex_cite"].findall(text):
            cites.extend((relative.as_posix(), key.strip()) for key in group.split(",") if key.strip())

    for path, key in refs:
        if key not in labels:
            warnings.append({"type": "missing_latex_label", "path": path, "value": key})
    for path, key in cites:
        if bib_keys and key not in bib_keys:
            warnings.append({"type": "missing_bib_key", "path": path, "value": key})

    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "file_count": len(files),
        "files": files,
        "counts": {"labels": len(labels), "references": len(refs), "bib_keys": len(bib_keys), "citations": len(cites), "warnings": len(warnings)},
        "warnings": warnings,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
