#!/usr/bin/env python3
"""Sync multi-seed DDR prose updates into highlight + submission APIN tex."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []

    def sub(pattern: str, repl: str, label: str, count: int = 0) -> None:
        nonlocal text
        # Use a callable replacer so LaTeX backslashes are not treated as re escapes.
        new, n = re.subn(pattern, lambda _m: repl, text, count=count, flags=re.MULTILINE)
        if n == 0:
            notes.append(f"MISS {label}")
        else:
            notes.append(f"OK {label} x{n}")
            text = new

    # Abstract / intro style (plain and highlight \mbox variants)
    sub(
        r"manipulation check \(GKT on XES3G5M\), \\DDR\{\} predicts AUC loss\n"
        r"\(Pearson (?:\\mbox\{\$r\{=\}0\.97\$\}|\$r\{=\}0\.97\$)\) and the prerequisite-preserving operator costs the least\n"
        r"accuracy at matched budget, whereas on graph-inert cells \(DGEKT; GKT on\n"
        r"ASSISTments\) even total graph destruction moves AUC by \$\{\\le\}0\.002\$\.",
        "manipulation check (GKT on XES3G5M; three seeds, nine folds), \\DDR{} predicts AUC loss\n"
        "(Pearson $r{\\approx}0.93$ on the $p{\\le}0.3$ core, $r{\\approx}0.99$ with\n"
        "manipulation-check anchors) and the prerequisite-preserving operator costs the least\n"
        "accuracy at matched budget, whereas on graph-inert cells (DGEKT; GKT on\n"
        "ASSISTments) even total graph destruction moves AUC by ${\\le}0.003$.",
        "abstract-ddr",
    )

    sub(
        r"under an anchored retraining sweep, \\DDR\{\}\n"
        r"  predicts accuracy loss on a graph-reliant backbone that passes a\n"
        r"  manipulation check \(GKT on XES3G5M, Pearson (?:\\mbox\{\$r\{=\}0\.97\$\}|\$r\{=\}0\.97\$); "
        r"(?:\\mbox\{\\texttt\{prereq\\_preserve\}\}|\\texttt\{prereq\\_preserve\})\n"
        r"  costs the least AUC at matched budget\), while remaining a purely structural\n"
        r"  audit on graph-inert backbones \(DGEKT, and GKT on ASSISTments\), where total\n"
        r"  graph destruction moves AUC by \$\{\\le\}0\.002\$",
        "under an anchored multi-seed retraining sweep, \\DDR{}\n"
        "  predicts accuracy loss on a graph-reliant backbone that passes a\n"
        "  manipulation check (GKT on XES3G5M, Pearson $r{\\approx}0.93$--$0.99$; \\texttt{prereq\\_preserve}\n"
        "  costs the least AUC at matched budget), while remaining a purely structural\n"
        "  audit on graph-inert backbones (DGEKT, and GKT on ASSISTments), where total\n"
        "  graph destruction moves AUC by ${\\le}0.003$",
        "c2-ddr",
    )

    sub(
        r"moves GKT by\n\$0\.07\$--\$0\.09\$ AUC on XES3G5M \(high reliance\) but by \$\{\\le\}0\.002\$ on\n"
        r"ASSISTments and for DGEKT \(low reliance\)",
        "moves GKT by\n$0.07$--$0.09$ AUC on XES3G5M (high reliance; three seeds) but by ${\\le}0.003$ on\n"
        "ASSISTments and for DGEKT (low reliance)",
        "two-factor",
    )

    # Main §4.7 GKT paragraph (seed 42 -> multi-seed)
    sub(
        r"\\DDR\{\}\{\}=\}0\.998\$\) moves AUC by only \$0\.0021\$ \(\$0\.9629\{\\to\}0\.9609\$\)",
        "\\DDR{}${=}0.986$) moves AUC by only $0.0021$ ($0.9630{\\to}0.9607$)",
        "assist-anchor",
    )
    sub(
        r"block; seed~\$42\$, three folds\) tells the opposite story\.",
        "block; seeds $\\{42,17,1234\\}$, nine folds) tells the opposite story.",
        "seed-phrase",
    )
    sub(
        r"baseline \$0\.8344\$ to \$0\.7629\$ \(\\texttt\{edge\\_drop\} \$p\{=\}0\.90\$, \$\{\-\}0\.072\$\) and\n"
        r"\$0\.7469\$ \(\\texttt\{node\\_drop\} \$p\{=\}0\.90\$, \$\{\-\}0\.088\$\)",
        "pooled baseline $0.8354$ to $0.7637$ (\\texttt{edge\\_drop} $p{=}0.90$, ${-}0.072$) and\n"
        "$0.7469$ (\\texttt{node\\_drop} $p{=}0.90$, ${-}0.089$)",
        "baseline-numbers",
    )
    sub(
        r"\(Pearson \$r\{=\}0\.97\$ over the \$p\{\\le\}0\.3\$ core, \$r\{=\}0\.99\$ including anchors;\n"
        r"\$n\{=\}27\$ and \$33\$\)",
        "(Pearson $r{=}0.93$ over the $p{\\le}0.3$ core, $r{=}0.99$ including anchors;\n"
        "$n{=}81$ and $99$)",
        "pearson-n",
    )
    sub(
        r"\\texttt\{prereq\\_preserve\} costs \$0\.0103\$ AUC, \\texttt\{edge\\_drop\} \$0\.0138\$, and\n"
        r"\\texttt\{node\\_drop\} \$0\.0414\$",
        "\\texttt{prereq\\_preserve} costs $0.0104$ AUC, \\texttt{edge\\_drop} $0.0133$, and\n"
        "\\texttt{node\\_drop} $0.0426$",
        "p30-drops",
    )

    sub(
        r"\(GKT on XES3G5M: destroying the graph costs \$0\.07\$--\$0\.09\$ AUC\), \\DDR\{\}\n"
        r"predicts the accuracy loss \((?:\\mbox\{\$r\{=\}0\.97\$\}|\$r\{=\}0\.97\$)\) and "
        r"(?:\\mbox\{\\texttt\{prereq\\_preserve\}\}|\\texttt\{prereq\\_preserve\}) costs the\n"
        r"least AUC at matched budget---structural damage translates into predictive\n"
        r"damage\. Where the manipulation check fails \(DGEKT, and GKT on ASSISTments:\n"
        r"total destruction moves AUC by \$\{\\le\}0\.002\$\)",
        "(GKT on XES3G5M: destroying the graph costs $0.07$--$0.09$ AUC across three seeds), \\DDR{}\n"
        "predicts the accuracy loss ($r{\\approx}0.93$--$0.99$) and \\texttt{prereq\\_preserve} costs the\n"
        "least AUC at matched budget---structural damage translates into predictive\n"
        "damage. Where the manipulation check fails (DGEKT, and GKT on ASSISTments:\n"
        "total destruction moves AUC by ${\\le}0.003$)",
        "discussion",
    )

    sub(
        r"Monotone, \$r\{\\approx\}0\.97\$ on GKT/XES3G5M",
        "Monotone, $r{\\approx}0.93$--$0.99$ on GKT/XES3G5M",
        "checklist",
    )

    sub(
        r"with GKT/XES3G5M reported for seed~\$42\$\n"
        r"\(multi-seed replication in progress\)\.?}",
        "with GKT/XES3G5M reported across three seeds\n"
        "($\\{42,17,1234\\}$, nine folds).",
        "limitations",
    )

    sub(
        r"\\textbf\{\\DDR\{\} downstream coverage\.\} The anchored retraining sweep now covers\n"
        r"two graph consumers \(DGEKT and GKT\) and establishes the manipulation-check\n"
        r"protocol that separates graph-reliant from graph-inert backbones\. Remaining\n"
        r"steps are to complete multi-seed GKT replication on XES3G5M, to add a second\n"
        r"graph-reliant backbone at both throughput levels \(e\.g\.\\ GIKT\), and to pair the\n"
        r"edge-level \\DDR\{\} correlation with the reachability-disruption variant so that",
        "\\textbf{\\DDR{} downstream coverage.} The anchored retraining sweep now covers\n"
        "two graph consumers (DGEKT and GKT), including a completed three-seed GKT\n"
        "replication on XES3G5M, and establishes the manipulation-check protocol that\n"
        "separates graph-reliant from graph-inert backbones. Remaining steps are to add a\n"
        "second graph-reliant backbone at both throughput levels (e.g.\\ GIKT), and to pair\n"
        "the edge-level \\DDR{} correlation with the reachability-disruption variant so that",
        "future-work",
    )

    sub(
        r"manipulation check \(GKT on XES3G5M\) \\DDR\{\} predicts AUC\n"
        r"loss \((?:\\mbox\{\$r\{=\}0\.97\$\}|\$r\{=\}0\.97\$)\) and "
        r"(?:\\mbox\{\\texttt\{prereq\\_preserve\}\}|\\texttt\{prereq\\_preserve\}) costs the least accuracy at\n"
        r"matched budget, whereas on graph-inert cells \(DGEKT; GKT on ASSISTments\) total\n"
        r"graph destruction moves AUC by \$\{\\le\}0\.002\$",
        "manipulation check (GKT on XES3G5M; three seeds) \\DDR{} predicts AUC\n"
        "loss ($r{\\approx}0.93$--$0.99$) and \\texttt{prereq\\_preserve} costs the least accuracy at\n"
        "matched budget, whereas on graph-inert cells (DGEKT; GKT on ASSISTments) total\n"
        "graph destruction moves AUC by ${\\le}0.003$",
        "conclusion",
    )

    sub(
        r"Tables~S19--S20 report exploratory ANOVA summaries\n"
        r"\(Section~\\ref\{sec:supp-anova\} in the Appendix\)\.",
        "Tables~S19--S20 report ANOVA summaries\n"
        "for baselines and the GKT multi-seed \\DDR{}$\\to$downstream sweep\n"
        "(Section~\\ref{sec:supp-anova} in the Appendix).",
        "appendix-index",
    )

    return text, notes


def main() -> int:
    targets = [
        ROOT / "paper/submission_APIN/main_APIN.tex",
        ROOT / "paper/main_APIN_highlight.tex",
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        new, notes = patch(text)
        path.write_text(new, encoding="utf-8")
        print(f"=== {path.relative_to(ROOT)} ===")
        for n in notes:
            print(" ", n)
        print("  leftover 'in progress':", "in progress" in new)
        print("  leftover r{=}0.97:", new.count("r{=}0.97"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
