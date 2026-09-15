#!/usr/bin/env python3
"""Regenerate results/tables/ddr_downstream_gkt.tex from the merged paper CSV."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DS_LABEL = {"xes3g5m": "XES3G5M", "assist2012": "ASSIST2012"}
OP_ORDER = {"edge_drop": 0, "node_drop": 1, "prereq_preserve": 2}
DS_ORDER = {"xes3g5m": 0, "assist2012": 1}


def _corr_stats(
    gkt: pd.DataFrame, dataset: str, p_max: float | None = None
) -> tuple[float, float, int]:
    part = gkt[gkt["dataset"] == dataset]
    if p_max is not None:
        part = part[part["p"] <= p_max + 1e-9]
    x = part["ddr"].to_numpy(dtype=float)
    y = part["auc_drop"].to_numpy(dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    n = int(ok.sum())
    if n < 3:
        return float("nan"), float("nan"), n
    r = float(stats.pearsonr(x[ok], y[ok])[0])
    rho = float(stats.spearmanr(x[ok], y[ok])[0])
    return r, rho, n


def _row(r: pd.Series) -> str:
    op = str(r.operator).replace("_", r"\_")
    return (
        f"{DS_LABEL.get(str(r.dataset), r.dataset)} & \\texttt{{{op}}} & "
        f"{float(r.p):.2f} & {float(r.ddr_mean):.3f} & "
        f"{float(r.auc_mean):.4f} & {float(r.auc_drop_mean):.4f} \\\\"
    )


def main() -> int:
    df = pd.read_csv(ROOT / "results/tables/ddr_downstream.csv")
    gkt = df[(df["model"] == "gkt") & (df["operator"] != "none")].copy()
    gkt = gkt[pd.notna(gkt["auc_drop"])]
    gkt["p"] = gkt["p"].astype(float).round(4)

    summary = (
        gkt.groupby(["dataset", "operator", "p"])
        .agg(
            ddr_mean=("ddr", "mean"),
            auc_mean=("auc", "mean"),
            auc_drop_mean=("auc_drop", "mean"),
            n=("auc", "size"),
        )
        .reset_index()
    )
    summary["_ds"] = summary["dataset"].map(DS_ORDER)
    summary["_op"] = summary["operator"].map(OP_ORDER)
    summary = summary.sort_values(["_ds", "_op", "p"])

    base = df[(df["model"] == "gkt") & (df["operator"] == "none")]
    xes_base = float(base.loc[base["dataset"] == "xes3g5m", "auc"].mean())
    ast_base = float(base.loc[base["dataset"] == "assist2012", "auc"].mean())
    r_core, _, n_core = _corr_stats(gkt, "xes3g5m", 0.3)
    r_all, rho_all, n_all = _corr_stats(gkt, "xes3g5m", None)

    slope_path = ROOT / "results/tables/ddr_slope_ci.csv"
    slope_core = slope_full = None
    slope_ast = None
    if slope_path.exists():
        sl = pd.read_csv(slope_path)
        def _sl(ds: str, scope: str) -> pd.Series | None:
            hit = sl[(sl["dataset"] == ds) & (sl["model"] == "gkt") & (sl["scope"] == scope)]
            return hit.iloc[0] if not hit.empty else None
        slope_core = _sl("xes3g5m", "core")
        slope_full = _sl("xes3g5m", "core+anchors")
        slope_ast = _sl("assist2012", "core")

    slope_note = ""
    if slope_core is not None:
        slope_note = (
            f" The primary estimand is the OLS slope of AUC-drop on \\DDR{{}} with a "
            f"fold$\\times$seed cluster-bootstrap 95\\% CI (not Pearson $r$, which is "
            f"scale-free). On XES3G5M/GKT the $p{{\\le}}0.3$ core ($n{{=}}{int(slope_core['n'])}$, "
            f"{int(slope_core['n_clusters'])} clusters) has slope "
            f"${float(slope_core['slope']):.3f}$ AUC per unit \\DDR{{}} "
            f"(CI $[{float(slope_core['slope_ci_lo']):+.3f}, "
            f"{float(slope_core['slope_ci_hi']):+.3f}]$); Pearson $r{{=}}{r_core:.2f}$ is secondary. "
            f"Including $p{{=}}0.90$ anchors ($n{{=}}{n_all}$) raises the slope only to "
            f"${float(slope_full['slope']):.3f}$."
            if slope_full is not None
            else ""
        )
        if slope_ast is not None:
            r_ast, _, n_ast = _corr_stats(gkt, "assist2012", 0.3)
            slope_note += (
                f" On ASSISTments/GKT the core slope is only "
                f"${float(slope_ast['slope']):.4f}$ "
                f"(CI $[{float(slope_ast['slope_ci_lo']):+.4f}, "
                f"{float(slope_ast['slope_ci_hi']):+.4f}]$) despite Pearson "
                f"$r{{=}}{r_ast:.2f}$ ($n{{=}}{n_ast}$), so that cell remains a "
                f"low-reliance anchor: high $r$, negligible practical effect."
            )

    core = "\n".join(_row(r) for _, r in summary[summary["p"] <= 0.3 + 1e-9].iterrows())
    anchors = "\n".join(_row(r) for _, r in summary[summary["p"] >= 0.9 - 1e-9].iterrows())
    n_xes = int(summary.loc[(summary["dataset"] == "xes3g5m") & (summary["p"] == 0.1), "n"].max())

    tex = f"""% Auto-derived from results/tables/ddr_downstream.csv (GKT multi-seed merge)
% XES3G5M: seeds 42/17/1234 x 3 folds (n={n_xes}); ASSIST2012: seed-42 grid (+ anchors).
% AUC drop = mean decrease in test AUC vs. the unperturbed (DDR=0) baseline.
% Caption scopes: r_core n={n_core}; r_all/rho_all n={n_all}; slope from ddr_slope_ci.csv.
\\begin{{table}}[h!]
\\centering
\\caption{{\\DDR{{}}$\\to$downstream AUC for the graph-reliant backbone GKT, with a
positive control (Table S24). For each dataset the prerequisite graph $\\Epre$ is perturbed
by each operator at strength $p$; \\emph{{AUC drop}} is the mean decrease in test
AUC relative to the unperturbed (\\DDR{{}}$=0$) baseline across folds (baselines:
XES3G5M $0.8346$, ASSISTments $0.9630$; XES3G5M pooled over
six fold$\\times$seed clusters per cell). The bottom block reports the
manipulation-check anchors ($p{{=}}0.90$, near-total graph destruction).
{slope_note}
At matched budget,
\\texttt{{prereq\\_preserve}} degrades AUC least and \\texttt{{node\\_drop}} most.
Spearman $\\rho{{=}}{rho_all:.2f}$ on the full XES3G5M/GKT pool ($n{{=}}{n_all}$)
is a rank check only; the global pooled Pearson $r{{\\approx}}0.75$ ($n{{=}}186$)
on Fig.~S3 must not be conflated with these estimands.}}
\\label{{tab:ddr-downstream-gkt}}
\\footnotesize
\\setlength{{\\tabcolsep}}{{3pt}}
\\begin{{tabularx}}{{\\linewidth}}{{@{{}} >{{\\RaggedRight\\arraybackslash}}p{{0.13\\linewidth}} >{{\\RaggedRight\\arraybackslash}}p{{0.20\\linewidth}} c *{{3}}{{>{{\\centering\\arraybackslash}}X}} @{{}}}}
\\toprule
Dataset & Operator & $p$ & Mean \\DDR{{}} & Mean AUC & AUC drop \\\\
\\midrule
{core}
\\midrule
\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{Manipulation-check anchors (near-total destruction)}}}}\\\\
{anchors}
\\bottomrule
\\end{{tabularx}}
\\end{{table}}
"""
    out = ROOT / "results/tables/ddr_downstream_gkt.tex"
    out.write_text(tex, encoding="utf-8")
    paper = ROOT / "paper/submission_EAAI/ddr_downstream_gkt.tex"
    paper.write_text(tex, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Wrote {paper}")
    print(f"XES baseline={xes_base:.4f} ASSIST baseline={ast_base:.4f}")
    print(f"Pearson XES core p<=0.3 r={r_core:.3f} n={n_core}; all r={r_all:.3f} rho={rho_all:.3f} n={n_all}")
    print(summary[summary["dataset"] == "xes3g5m"][["operator", "p", "ddr_mean", "auc_mean", "auc_drop_mean", "n"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
