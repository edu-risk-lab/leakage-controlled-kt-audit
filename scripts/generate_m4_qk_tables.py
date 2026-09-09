"""Write compact LaTeX tables from results/m4/builder_census.csv (Phase A only)."""

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
Downstream $\Delta$AUC for opened cells is not reported here.}
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, default=ROOT / "results" / "m4" / "builder_census.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "tables" / "m4_qk_census.tex")
    parser.add_argument(
        "--copy-to",
        action="append",
        default=[],
        help="Extra destinations (e.g. paper/submission_EAAI/m4_qk_census.tex)",
    )
    args = parser.parse_args()
    census = pd.read_csv(args.census)
    write_main_table(census, args.out)
    text = args.out.read_text(encoding="utf-8")
    for dest in args.copy_to:
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
