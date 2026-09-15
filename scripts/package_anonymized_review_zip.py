"""Build the double-anonymized code archive for EAAI Editorial Manager.

Writes paper/submission_EAAI/EAAI_code_anonymized.zip from the repo root.
Refuses to write if author-identity strings are found in the staged tree.

Usage (repo root):
    py -3 scripts/package_anonymized_review_zip.py
"""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "paper" / "submission_EAAI"
ZIP_PATH = OUT_DIR / "EAAI_code_anonymized.zip"
STAGE = OUT_DIR / "_code_stage"

COPY_TREES = (
    "src",
    "scripts",
    "configs",
    "tests",
    "results/tables",
    "results/figures",
    "results/m4",
    "results/q1",
    "results/audit_cost",
)

COPY_FILES = (
    "requirements.txt",
    "docs/M4_QK_SWEEP_PROTOCOL.md",
    "third_party/README.md",
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
)

SKIP_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "cache",
    "scratch",
    ".git",
}

SKIP_FILE_SUFFIXES = {".pyc", ".pyo", ".zip"}

# Paper-only helpers: filenames or comments name a previous venue.
DROP_SCRIPTS = {
    "package_anonymized_review_zip.py",
    "apply_revision_highlight.py",
    "merge_apin_appendix.py",
    "extract_highlights.py",
    "strip_highlights.py",
}

SANITIZE_SUBS = (
    (re.compile(r"paper/submission_APIN", re.IGNORECASE), "paper/submission"),
    (re.compile(r"main_APIN_highlight\.tex", re.IGNORECASE), "main_highlight.tex"),
    (re.compile(r"main_APIN\.tex", re.IGNORECASE), "main.tex"),
    (re.compile(r"main_APIN", re.IGNORECASE), "main"),
    (re.compile(r"Applied Intelligence", re.IGNORECASE), "the target journal"),
    (re.compile(r"\bAPIN\b"), "the manuscript"),
)

# Author, affiliation, venue-leak, and public-repo identity.
FORBIDDEN = re.compile(
    r"""
    tuanymc
    |nvhau
    |edu-risk-lab
    |utehy
    |dao\s*minh
    |van-?hau
    |khanh-trinh
    |duong\s+nguyen\s+tien
    |quoc\s+khanh
    |le\s+hoang\s+son
    |sonlh@
    |trinhnk@
    |duongnt@
    |hung\s+yen\s+university
    |0009-0009-1641
    |0009-0004-3739
    |0009-0007-1104
    |0009-0001-9250
    |0000-0002-3256
    |0000-0001-6356
    |submission_apin
    |applied\s+intelligence
    |title_page
    |coverletter
    """,
    re.IGNORECASE | re.VERBOSE,
)

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".ps1",
    ".sh",
    ".yml",
    ".yaml",
    ".toml",
    ".cfg",
    ".ini",
    ".csv",
    ".tex",
    ".json",
    ".gitignore",
    ".cff",
    ".rst",
}


def _ignore(_dir: str, names: list[str]) -> set[str]:
    skip = set()
    for name in names:
        path = Path(_dir) / name
        if name in SKIP_DIR_NAMES or name.endswith(".egg-info"):
            skip.add(name)
        elif path.is_file() and path.suffix.lower() in SKIP_FILE_SUFFIXES:
            skip.add(name)
    return skip


def _copy_tree(rel: str) -> None:
    src = REPO / rel
    dst = STAGE / rel
    if not src.exists():
        print(f"skip missing tree: {rel}", file=sys.stderr)
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=_ignore, dirs_exist_ok=True)


def _copy_file(rel: str, *, required: bool = True) -> None:
    src = REPO / rel
    dst = STAGE / rel
    if not src.exists():
        if required:
            raise FileNotFoundError(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text("", encoding="utf-8")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _sanitize_text_files() -> None:
    for path in STAGE.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "LICENSE",
            "README.md",
            ".gitignore",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new = text
        for pattern, repl in SANITIZE_SUBS:
            new = pattern.sub(repl, new)
        if new != text:
            path.write_text(new, encoding="utf-8")


def _write_reviewer_overlays() -> None:
    shutil.copy2(OUT_DIR / "REVIEW_ARCHIVE_README.md", STAGE / "README.md")
    shutil.copy2(OUT_DIR / "REVIEW_ARCHIVE_LICENSE.txt", STAGE / "LICENSE")
    shutil.copy2(OUT_DIR / "REVIEW_ARCHIVE_pyproject.toml", STAGE / "pyproject.toml")
    (STAGE / ".gitignore").write_text(
        "\n".join(
            [
                "data/raw/**",
                "!data/raw/.gitkeep",
                "data/processed/**",
                "!data/processed/.gitkeep",
                "__pycache__/",
                ".venv/",
                "venv/",
                "*.egg-info/",
                ".pytest_cache/",
                "results/cache/",
                "results/predictions/",
                "results/pykt_work/",
                "logs/",
                ".env",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _scan() -> list[str]:
    hits: list[str] = []
    for path in STAGE.rglob("*"):
        rel = path.relative_to(STAGE).as_posix()
        found_name = {m.group(0) for m in FORBIDDEN.finditer(rel)}
        if found_name:
            hits.append(f"{rel} [path]: {sorted(found_name)}")
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "LICENSE",
            "README.md",
            ".gitignore",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = {m.group(0) for m in FORBIDDEN.finditer(text)}
        if found:
            hits.append(f"{rel}: {sorted(found)}")
    return hits


def _zip_stage() -> int:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    n_files = 0
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(STAGE).as_posix())
                n_files += 1
    return n_files


def main() -> int:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    for rel in COPY_TREES:
        _copy_tree(rel)
    for rel in COPY_FILES:
        _copy_file(rel, required=not rel.endswith(".gitkeep"))
    _write_reviewer_overlays()

    for leak_name in DROP_SCRIPTS:
        extra = STAGE / "scripts" / leak_name
        if extra.exists():
            extra.unlink()

    _sanitize_text_files()

    hits = _scan()
    if hits:
        print("Identity leak in staged archive:", file=sys.stderr)
        for row in hits:
            print(f"  {row}", file=sys.stderr)
        shutil.rmtree(STAGE)
        return 1

    n_files = _zip_stage()
    size = ZIP_PATH.stat().st_size
    shutil.rmtree(STAGE)
    print(f"Wrote {ZIP_PATH}")
    print(f"files={n_files} bytes={size} miB={size / (1024 * 1024):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
