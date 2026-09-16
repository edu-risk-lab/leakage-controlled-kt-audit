"""Write compact LaTeX tables from M4 census (Phase A) and GKT fold-0 CSVs (Phase B)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LANDMARKS = [
    ("q0.95_k5_K5000_tau0.1", "Published default"),
    ("q0.95_k5_K1000_tau0.1", "$K$ binds"),
    ("q0.8_k5_K5000_tau0.1", "Mid $q$"),
    ("q0.5_k5_Kinf_tau0.1", "Review open $q$"),
    ("q0.5_k20_Kinf_tau0.1", "$k{=}20$ lift"),
    ("q0.5_kinf_Kinf_tau0.1", "$k{=}\\infty$ lift"),
]


def _fmt_cap(value: float | int) -> str:
    v = int(value)
    return r"$\infty$" if v >= 10**9 else f"{v:,}"


def _fold0(census: pd.DataFrame, tag: str) -> pd.Series:
    hit = census[(census["fold"] == 0) & (census["cell_tag"] == tag)]
    if hit.empty:
        raise SystemExit(f"Missing fold-0 row for {tag}")
    return hit.iloc[0]


def _leak_range(census: pd.DataFrame, tag: str) -> str:
    part = census[census["cell_tag"] == tag]["n_pre_fl_minus_to"]
    lo, hi = int(part.min()), int(part.max())
    return f"{lo}--{hi}" if lo != hi else str(lo)


def write_main_table(census: pd.DataFrame, path: Path) -> None:
    rows = []
    for tag, label in LANDMARKS:
        r = _fold0(census, tag)
        rows.append(
            f"{label} & {r['q']:g} & {_fmt_cap(r['k'])} & {_fmt_cap(r['K'])} & "
            f"{int(r['n_pre_to']):,} & {int(r['n_pre_fl_minus_to'])} & "
            f"{_leak_range(census, tag)} & {r['primary_bind_to']} \\\\"
        )
    tex = r"""\begin{table}[t]
\centering
\caption{Filter-stage census on XES3G5M (builder only; no retraining).
$|E_{\mathrm{pre}}^{\mathrm{to}}|$ and leak $=|E_{\mathrm{pre}}^{\mathrm{fl}}\setminus E_{\mathrm{pre}}^{\mathrm{to}}|$
are fold~0; leak range is the three-fold min--max.
Bind is the last reducing stage ($q$, per-source $k$, or global $K$).
At the published $(q,k,K)=(0.95,5,5000)$, $k$ binds and $K{=}5000$ is slack
($K{=}\infty$ is identical). Opening $q$ with $k{=}5$ kept does not open the
channel; lifting $k$ does. Jaccard $\tau$ changes $|E_{\mathrm{sim}}|$
($618/354/198$ at $\tau{=}0.05/0.10/0.20$ on fold~0) but not $E_{\mathrm{pre}}$ leak.
Downstream $\Delta$AUC for the three GKT fold-0 cells is in
Table~\ref{tab:m4-phase-b-auc}.}
\label{tab:m4-qk-census}
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabularx}{\linewidth}{@{} >{\RaggedRight\arraybackslash}p{0.22\linewidth}
  *{7}{>{\centering\arraybackslash}X} @{}}
\toprule
Cell & $q$ & $k$ & $K$ & $|E_{\mathrm{pre}}^{\mathrm{to}}|$ & Leak (f0) & Leak (3f) & Bind \\
\midrule
"""
    tex += "\n".join(rows) + "\n"
    tex += r"""\bottomrule
\end{tabularx}
\end{table}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tex, encoding="utf-8")


def write_phase_b_table(census: pd.DataFrame, path: Path) -> None:
    cells = [
        ("q0.95_k5_K5000_tau0.1", "Published default"),
        ("q0.5_k5_Kinf_tau0.1", "Open $q$, $k{=}5$"),
        ("q0.5_k20_Kinf_tau0.1", "$k{=}20$ lift"),
    ]
    rows = []
    deltas: list[float] = []
    for tag, label in cells:
        csv_path = ROOT / "results" / "q1" / f"m4_{tag}" / "baseline_results.csv"
        if not csv_path.exists():
            raise SystemExit(f"Missing Phase B CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        to = float(df.loc[df["graph_construction"] == "train_only", "auc"].iloc[0])
        fl = float(df.loc[df["graph_construction"] == "full_log", "auc"].iloc[0])
        delta = fl - to
        deltas.append(delta)
        leak = int(_fold0(census, tag)["n_pre_fl_minus_to"])
        sign = "+" if delta >= 0 else ""
        rows.append(
            f"{label} & {leak} & {to:.4f} & {fl:.4f} & ${sign}{delta:.4f}$ \\\\"
        )
    max_abs = max(abs(x) for x in deltas)
    tex = (
        "\\begin{table}[t]\n"
        "\\centering\n"
        "\\caption{Train-only versus full-log GKT AUC on XES3G5M fold~0 (primary "
        "budget: 10 epochs, batch 4, seed 42). $\\Delta$AUC $=$ full-log $-$ train-only. "
        "The open-$q$ cell keeps $k{=}5$; the $k{=}20$ cell is the opened-channel "
        "landmark. Absolute AUC rises with denser graphs, but "
        f"$|\\Delta\\text{{AUC}}|{{\\le}}{max_abs:.4f}$ on all three cells. Not a three-fold "
        "result; the per-source $k{=}\\infty$ lift was not trained (stop rule). "
        "A slack-$K$ cell at the published $k$ reproduced the default AUCs and is omitted.}\n"
        "\\label{tab:m4-phase-b-auc}\n"
        "\\footnotesize\n"
        "\\setlength{\\tabcolsep}{4pt}\n"
        "\\begin{tabularx}{\\linewidth}{@{} >{\\RaggedRight\\arraybackslash}X c c c c @{}}\n"
        "\\toprule\n"
        "Cell & Leak (f0) & Train-only AUC & Full-log AUC & $\\Delta$AUC \\\\\n"
        "\\midrule\n"
    )
    tex += "\n".join(rows) + "\n"
    tex += r"""\bottomrule
\end{tabularx}
\end{table}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tex, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, default=ROOT / "results" / "m4" / "builder_census.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "tables" / "m4_qk_census.tex")
    parser.add_argument(
        "--out-phase-b",
        type=Path,
        default=ROOT / "results" / "tables" / "m4_phase_b_auc.tex",
    )
    parser.add_argument(
        "--copy-to",
        action="append",
        default=[],
        help="Extra destinations for the census table",
    )
    parser.add_argument(
        "--copy-phase-b-to",
        action="append",
        default=[],
        help="Extra destinations for the Phase B AUC table",
    )
    args = parser.parse_args()
    census = pd.read_csv(args.census)
    write_main_table(census, args.out)
    write_phase_b_table(census, args.out_phase_b)
    text = args.out.read_text(encoding="utf-8")
    for dest in args.copy_to:
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    pb = args.out_phase_b.read_text(encoding="utf-8")
    for dest in args.copy_phase_b_to:
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(pb, encoding="utf-8")
    print(f"Wrote {args.out}")
    print(f"Wrote {args.out_phase_b}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
