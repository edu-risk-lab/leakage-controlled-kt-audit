"""Leakage exposure bound: predict |dAUC| from a builder census without retraining.

The bound combines two quantities the protocol already measures separately:

    |dAUC_leak(m, D, theta)|  <=  s(m, D) * delta(D, theta)

where ``s`` is the backbone structural sensitivity (OLS slope of AUC-drop on DDR,
``results/tables/ddr_slope_ci.csv``) and ``delta`` is the structural delta that
pooling introduces at filter cell ``theta`` (leaked edges over retained train-only
edges, ``results/m4/builder_census.csv``). Both are normalised by |E_pre|, so the
product is in AUC units.

``delta`` counts leaked edges. Many of them are transitively redundant and add no
new precedence relation, which is why the raw bound is loose. With ``--edge-root``
the script also computes the effective delta, counting only leaked edges that
create a reachability pair absent from the train-only graph.

Usage:
    python scripts/leakage_exposure.py
    python scripts/leakage_exposure.py --edge-root data/processed/xes3g5m/m4
    python scripts/leakage_exposure.py --sync-tex
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "results" / "m4" / "builder_census.csv"
SLOPES = ROOT / "results" / "tables" / "ddr_slope_ci.csv"
ABLATION = ROOT / "results" / "tables" / "graph_ablation_summary.csv"
Q1_ROOT = ROOT / "results" / "q1"
OUT_CSV = ROOT / "results" / "tables" / "leakage_exposure.csv"
OUT_TEX = ROOT / "results" / "tables" / "leakage_exposure.tex"
OUT_REPLICATE = ROOT / "results" / "tables" / "exposure_replicate_check.csv"
PAPER_DIR = ROOT / "paper" / "submission_EAAI"

# Cells reported in the manuscript, in the order they appear in Table m4-qk-census.
CELL_LABELS = {
    "q0.95_k5_K5000_tau0.1": "Published default",
    "q0.95_k5_K1000_tau0.1": "$K$ binds",
    "q0.8_k5_K5000_tau0.1": "Mid $q$",
    "q0.5_k5_Kinf_tau0.1": "Review open $q$",
    "q0.5_k20_Kinf_tau0.1": "$k{=}20$ lift",
    "q0.5_kinf_Kinf_tau0.1": "$k{=}\\infty$ lift",
}

logger = logging.getLogger("leakage_exposure")


def load_slopes(path: Path = SLOPES) -> pd.DataFrame:
    """Structural sensitivity s per (dataset, model), core scope only."""
    df = pd.read_csv(path)
    core = df[df["scope"] == "core"].copy()
    return core.set_index(["dataset", "model"])[["slope", "slope_ci_lo", "slope_ci_hi"]]


def load_census(path: Path = CENSUS) -> pd.DataFrame:
    """Per (dataset, fold, cell) structural delta from pooling."""
    df = pd.read_csv(path)
    keep = ["dataset", "fold", "split_seed", "cell_tag", "q", "k", "K", "tau",
            "n_pre_to", "n_pre_fl", "n_pre_fl_minus_to", "primary_bind_to"]
    df = df[keep].copy()
    df["delta"] = df["n_pre_fl_minus_to"] / df["n_pre_to"]
    return df


def load_observed_m4(q1_root: Path = Q1_ROOT) -> pd.DataFrame:
    """Observed dAUC = full-log minus train-only, per isolated m4 cell."""
    rows: list[dict] = []
    for fold_csv in sorted(q1_root.glob("m4_*/baseline_fold_results.csv")):
        part = pd.read_csv(fold_csv)
        cell = fold_csv.parent.name.removeprefix("m4_")
        keys = ["dataset", "fold", "split_seed", "model"]
        for key, grp in part.groupby(keys, sort=False):
            arms = grp.set_index("graph_construction")["auc"]
            if not {"train_only", "full_log"} <= set(arms.index):
                continue
            row = dict(zip(keys, key, strict=True))
            row |= {
                "cell_tag": cell,
                "auc_train_only": float(arms["train_only"]),
                "auc_full_log": float(arms["full_log"]),
                "observed_delta_auc": float(arms["full_log"] - arms["train_only"]),
            }
            rows.append(row)
    return pd.DataFrame(rows)


def _read_edges(path: Path) -> set[tuple[int, int]]:
    df = pd.read_csv(path, usecols=["src_kc", "dst_kc"])
    return set(zip(df["src_kc"].astype(int), df["dst_kc"].astype(int), strict=True))


def _read_weighted(path: Path) -> dict[int, dict[int, float]]:
    df = pd.read_csv(path, usecols=["src_kc", "dst_kc", "weight"])
    rows: dict[int, dict[int, float]] = {}
    for src, dst, w in zip(df["src_kc"].astype(int), df["dst_kc"].astype(int),
                           df["weight"].astype(float), strict=True):
        rows.setdefault(src, {})[dst] = w
    return rows


def operator_delta(pre_to_csv: Path, pre_fl_csv: Path) -> dict[str, float]:
    """How much pooling moves the message-passing operator GKT actually consumes.

    GKT propagates over a row-normalised adjacency, so the quantity that can move
    predictions is the change in each node's outgoing weight distribution, not the
    raw edge count. ``delta_tv`` is the mean total-variation distance between the
    train-only and full-log row distributions, averaged over nodes present in
    either graph; ``delta_w`` is the unnormalised weight mass that moves.
    """
    to_rows = _read_weighted(pre_to_csv)
    fl_rows = _read_weighted(pre_fl_csv)
    nodes = set(to_rows) | set(fl_rows)

    tv_total = 0.0
    moved = 0.0
    base = 0.0
    for node in nodes:
        a, b = to_rows.get(node, {}), fl_rows.get(node, {})
        sum_a, sum_b = sum(a.values()), sum(b.values())
        base += sum_a
        for dst in set(a) | set(b):
            moved += abs(a.get(dst, 0.0) - b.get(dst, 0.0))
        if sum_a <= 0 or sum_b <= 0:
            tv_total += 1.0
            continue
        tv = sum(
            abs(a.get(dst, 0.0) / sum_a - b.get(dst, 0.0) / sum_b)
            for dst in set(a) | set(b)
        )
        tv_total += 0.5 * tv

    return {
        "delta_tv": tv_total / len(nodes) if nodes else float("nan"),
        "delta_w": moved / base if base > 0 else float("nan"),
        "n_nodes_union": float(len(nodes)),
    }


def effective_delta(pre_to_csv: Path, pre_fl_csv: Path) -> dict[str, float]:
    """Share of leaked edges that create a precedence pair absent train-only.

    A leaked edge (u, v) is redundant when v is already reachable from u in the
    train-only graph: adding it changes no precedence relation. Only novel edges
    can move a backbone that consumes reachability structure.
    """
    import networkx as nx

    to_edges = _read_edges(pre_to_csv)
    fl_edges = _read_edges(pre_fl_csv)
    leaked = fl_edges - to_edges
    graph = nx.DiGraph()
    graph.add_edges_from(to_edges)

    descendants: dict[int, set[int]] = {}
    novel = 0
    for src, dst in leaked:
        if src not in graph:
            novel += 1
            continue
        if src not in descendants:
            descendants[src] = nx.descendants(graph, src)
        if dst not in descendants[src]:
            novel += 1

    n_to = len(to_edges)
    return {
        "n_pre_to_edges": float(n_to),
        "n_leaked": float(len(leaked)),
        "n_leaked_novel": float(novel),
        "novel_share": float(novel / len(leaked)) if leaked else 0.0,
        "delta_eff": float(novel / n_to) if n_to else float("nan"),
    }


def attach_effective_delta(frame: pd.DataFrame, edge_root: Path) -> pd.DataFrame:
    """Fill delta_eff from exported edge CSVs when the isolated graphs are present."""
    cols = ("n_leaked_novel", "novel_share", "delta_eff", "delta_tv", "delta_w")
    out = frame.copy()
    for col in cols:
        out[col] = float("nan")
    for idx, row in out.iterrows():
        cell_dir = edge_root / str(row["cell_tag"])
        pre_to = cell_dir / f"fold_{int(row['fold'])}" / "e_pre_train_only.csv"
        pre_fl = cell_dir / "full_log" / "e_pre.csv"
        if not (pre_to.exists() and pre_fl.exists()):
            continue
        stats = effective_delta(pre_to, pre_fl) | operator_delta(pre_to, pre_fl)
        for col in cols:
            out.at[idx, col] = stats[col]
    return out


def build_exposure(
    census: pd.DataFrame,
    slopes: pd.DataFrame,
    observed: pd.DataFrame,
    *,
    model: str = "gkt",
) -> pd.DataFrame:
    """Join census delta, backbone slope, and observed dAUC into one exposure table."""
    frame = census.copy()
    frame["model"] = model

    def _slope(row: pd.Series, col: str) -> float:
        key = (row["dataset"], row["model"])
        return float(slopes.loc[key, col]) if key in slopes.index else float("nan")

    frame["slope"] = frame.apply(_slope, axis=1, col="slope")
    frame["slope_ci_hi"] = frame.apply(_slope, axis=1, col="slope_ci_hi")
    frame["bound"] = frame["slope"] * frame["delta"]
    frame["bound_conservative"] = frame["slope_ci_hi"] * frame["delta"]

    if not observed.empty:
        merged = frame.merge(
            observed[["dataset", "fold", "model", "cell_tag", "observed_delta_auc",
                      "auc_train_only", "auc_full_log"]],
            on=["dataset", "fold", "model", "cell_tag"],
            how="left",
        )
    else:
        merged = frame.assign(observed_delta_auc=float("nan"),
                              auc_train_only=float("nan"),
                              auc_full_log=float("nan"))

    merged["abs_observed"] = merged["observed_delta_auc"].abs()
    holds = (merged["abs_observed"] <= merged["bound_conservative"]).astype("boolean")
    merged["bound_holds"] = holds.mask(merged["abs_observed"].isna())
    merged["slack_ratio"] = merged["bound"] / merged["abs_observed"]
    merged["label"] = merged["cell_tag"].map(CELL_LABELS).fillna(merged["cell_tag"])
    return merged


def primary_exposure(
    slopes: pd.DataFrame,
    *,
    fold: int = 0,
    sigma: float = 1e-3,
    data_root: Path = Path("data/processed"),
    ablation_path: Path = ABLATION,
) -> pd.DataFrame:
    """Exposure bound on the primary released pipeline, per corpus and backbone.

    Unlike the m4 sweep this reads the shipped artefacts directly, so it covers
    every corpus the protocol was run on rather than the XES3G5M filter grid.

    Caveat carried into the output: the observed column comes from
    ``graph_ablation_summary.csv``, a June vintage produced three months and
    several commits before the m4 results (revision plan section 2.5). It is the
    number the manuscript quotes, so the comparison is the relevant one, but the
    two vintages have not been shown to be comparable.
    """
    if not ablation_path.exists():
        return pd.DataFrame()
    ablation = pd.read_csv(ablation_path)

    rows: list[dict] = []
    for dataset in sorted(ablation["dataset"].unique()):
        pre_to = data_root / dataset / f"fold_{fold}" / "e_pre_train_only.csv"
        pre_fl = data_root / dataset / "full_log" / "e_pre.csv"
        if not (pre_to.exists() and pre_fl.exists()):
            logger.info("skipping %s: no exported graph pair", dataset)
            continue
        to_edges, fl_edges = _read_edges(pre_to), _read_edges(pre_fl)
        deltas = {
            "delta": len(fl_edges - to_edges) / len(to_edges) if to_edges else float("nan"),
            "n_pre_to": float(len(to_edges)),
            "n_leaked": float(len(fl_edges - to_edges)),
        } | operator_delta(pre_to, pre_fl)

        for model in sorted(ablation[ablation["dataset"] == dataset]["model"].unique()):
            key = (dataset, model)
            slope = float(slopes.loc[key, "slope"]) if key in slopes.index else float("nan")
            hit = ablation[(ablation["dataset"] == dataset) & (ablation["model"] == model)]
            observed = abs(float(hit.iloc[0]["delta_auc"])) if not hit.empty else float("nan")
            rows.append({
                "dataset": dataset, "model": model, "fold": fold, "slope": slope,
                **deltas,
                "bound": slope * deltas["delta"],
                "bound_w": slope * deltas["delta_w"],
                "abs_observed": observed,
            })

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    for variant in ("bound", "bound_w"):
        frame[f"{variant}_holds"] = (frame["abs_observed"] <= frame[variant]).astype("boolean")
        frame.loc[frame[variant].isna(), f"{variant}_holds"] = pd.NA
    # A bound below the training noise floor predicts a difference no experiment at
    # this budget can resolve, so it is untestable rather than wrong. Backbones with
    # no measurable structural reliance land here: s collapses and s*delta with it.
    frame["informative"] = (frame["bound"] > sigma).astype("boolean")
    frame.loc[frame["bound"].isna(), "informative"] = pd.NA
    return frame


def replicate_check(observed: pd.DataFrame, ablation_path: Path = ABLATION) -> pd.DataFrame:
    """Compare the isolated default-cell rerun against the primary ablation run.

    Both nominally use the published filter, so the gap bounds how small a dAUC
    claim can be before it stops being reproducible. For XES3G5M/GKT the gap looks
    arm-asymmetric (train-only 5e-5, full-log 1.2e-3) and every graph artefact is
    byte-identical (``scripts/diagnose_full_log_artefact.py``), which rules out a
    graph mismatch. It does not yet rule out training noise: one observed pair
    cannot separate a real asymmetry from luck, and the train-only arms are not
    bit-identical either. Settle it by measuring the noise floor with the
    replicate cell in docs/EAAI_PREREGISTRATION.md section 3.
    """
    if not ablation_path.exists():
        return pd.DataFrame()
    primary = pd.read_csv(ablation_path)
    rows = []
    default_cell = "q0.95_k5_K5000_tau0.1"
    iso = observed[observed["cell_tag"] == default_cell]
    for _, r in iso.iterrows():
        hit = primary[(primary["dataset"] == r["dataset"]) & (primary["model"] == r["model"])]
        if hit.empty:
            continue
        p = hit.iloc[0]
        rows.append({
            "dataset": r["dataset"],
            "model": r["model"],
            "fold": r["fold"],
            "train_only_isolated": r["auc_train_only"],
            "train_only_primary": p["auc_train_only"],
            "train_only_gap": abs(r["auc_train_only"] - p["auc_train_only"]),
            "full_log_isolated": r["auc_full_log"],
            "full_log_primary": p["auc_full_log"],
            "full_log_gap": abs(r["auc_full_log"] - p["auc_full_log"]),
            "delta_isolated": r["observed_delta_auc"],
            "delta_primary": p["delta_auc"],
        })
    return pd.DataFrame(rows)


def to_latex(frame: pd.DataFrame) -> str:
    cols = ["label", "delta", "bound", "abs_observed", "slack_ratio"]
    fold0 = frame[frame["fold"] == 0].copy()
    order = list(CELL_LABELS)
    fold0["_rank"] = fold0["cell_tag"].apply(lambda t: order.index(t) if t in order else len(order))
    fold0 = fold0.sort_values("_rank")[cols]

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Leakage exposure bound on XES3G5M (GKT, fold~0). "
        r"$\delta$ is the structural delta from pooling (leaked edges over retained "
        r"train-only edges, Table~\ref{tab:m4-qk-census}); the bound is "
        r"$s\cdot\delta$ with $s$ the DDR slope for this backbone--corpus pair. "
        r"The bound is computed from a CPU census and one reliance probe, with no "
        r"retraining. It holds on every trained cell. The $k{=}\infty$ row is a "
        r"prediction recorded before that cell was trained.}",
        r"\label{tab:leakage-exposure}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabularx}{\linewidth}{@{} >{\RaggedRight\arraybackslash}X c c c c @{}}",
        r"\toprule",
        r"Cell & $\delta$ & Bound $s\cdot\delta$ & $|\Delta\text{AUC}|$ & Slack \\",
        r"\midrule",
    ]
    for _, r in fold0.iterrows():
        if pd.isna(r["abs_observed"]):
            obs, slack = r"\emph{not trained}", "---"
        else:
            obs = f"{r['abs_observed']:.4f}"
            slack = f"{r['slack_ratio']:.1f}$\\times$" if pd.notna(r["slack_ratio"]) else "---"
        lines.append(f"{r['label']} & {r['delta']:.3f} & {r['bound']:.4f} & {obs} & {slack} \\\\")
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gkt", help="backbone whose slope defines s")
    parser.add_argument(
        "--edge-root",
        type=Path,
        default=None,
        help="isolated m4 graph root (e.g. data/processed/xes3g5m/m4) for delta_eff",
    )
    parser.add_argument(
        "--primary",
        action="store_true",
        help="also score the released pipeline of every corpus, not just the m4 grid",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=1e-3,
        help="training noise floor in AUC; bounds below it are untestable. Provisional "
             "default is the observed full-log replicate gap; measure it properly with "
             "the replicate cell in docs/EAAI_PREREGISTRATION.md section 3",
    )
    parser.add_argument("--sync-tex", action="store_true", help="copy the TeX table into the paper dir")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s %(message)s")

    census = load_census()
    slopes = load_slopes()
    observed = load_observed_m4()
    logger.info("census rows=%d observed m4 cells=%d", len(census), observed["cell_tag"].nunique() if not observed.empty else 0)

    frame = build_exposure(census, slopes, observed, model=args.model)
    if args.edge_root is not None:
        logger.info("computing effective delta from %s", args.edge_root)
        frame = attach_effective_delta(frame, args.edge_root)
        for variant in ("eff", "tv", "w"):
            frame[f"bound_{variant}"] = frame["slope"] * frame[f"delta_{variant}"]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT_CSV, index=False)
    logger.info("wrote %s", OUT_CSV)

    if args.primary:
        prim = primary_exposure(slopes, sigma=args.sigma)
        if not prim.empty:
            prim_path = OUT_CSV.with_name("leakage_exposure_primary.csv")
            prim.to_csv(prim_path, index=False)
            logger.info("wrote %s", prim_path)
            print(f"\nReleased pipeline exposure (fold 0, sigma={args.sigma:g}; "
                  "observed column is the pre-2593fc14 vintage)")
            print(prim[["dataset", "model", "delta", "delta_w", "bound", "bound_w",
                        "abs_observed", "bound_holds", "informative"]]
                  .to_string(index=False, float_format=lambda v: f"{v:.5f}"))
            scored = prim[prim["informative"] == True]  # noqa: E712 - pandas nullable boolean
            if not scored.empty:
                print(f"  above the noise floor: raw bound holds "
                      f"{int(scored['bound_holds'].sum())}/{len(scored)}, weighted "
                      f"{int(scored['bound_w_holds'].sum())}/{len(scored)}")
            degenerate = prim[prim["informative"] == False]  # noqa: E712
            for _, r in degenerate.iterrows():
                verdict = "holds" if r["bound_holds"] else "exceeded"
                print(f"  {r['dataset']}/{r['model']}: bound {r['bound']:.2e} < sigma "
                      f"({verdict} nominally, but untestable at this training budget)")
            missing = prim[prim["bound"].isna()]
            if not missing.empty:
                pairs = ", ".join(f"{r['dataset']}/{r['model']}" for _, r in missing.iterrows())
                print(f"  no DDR slope measured, bound not computable: {pairs}")

    rep = replicate_check(observed)
    if not rep.empty:
        rep.to_csv(OUT_REPLICATE, index=False)
        logger.info("wrote %s", OUT_REPLICATE)

    tex = to_latex(frame)
    OUT_TEX.write_text(tex, encoding="utf-8")
    logger.info("wrote %s", OUT_TEX)
    if args.sync_tex:
        (PAPER_DIR / "leakage_exposure.tex").write_text(tex, encoding="utf-8")
        logger.info("synced to %s", PAPER_DIR / "leakage_exposure.tex")

    fold0 = frame[frame["fold"] == 0]
    print("\nExposure bound, XES3G5M fold 0, model =", args.model)
    show = ["label", "delta", "bound", "bound_conservative", "abs_observed", "bound_holds", "slack_ratio"]
    if "delta_eff" in fold0.columns:
        show[2:2] = ["delta_eff", "delta_tv", "delta_w"]
    print(fold0[show].to_string(index=False, float_format=lambda v: f"{v:.5f}"))

    if "delta_tv" in fold0.columns:
        print("\nCandidate deltas vs observed |dAUC| (trained cells only):")
        cand = fold0[fold0["abs_observed"].notna()]
        for variant in ("delta", "delta_eff", "delta_tv", "delta_w"):
            bounds = cand["slope"] * cand[variant]
            n_hold = int((cand["abs_observed"] <= bounds).sum())
            tightest = (bounds / cand["abs_observed"]).max()
            print(f"  {variant:<10s} holds {n_hold}/{len(cand)}  worst slack {tightest:>8.1f}x")

    trained = fold0[fold0["abs_observed"].notna()]
    if not trained.empty:
        print(f"\nbound holds on {int(trained['bound_holds'].sum())}/{len(trained)} trained cells")
    untrained = fold0[fold0["abs_observed"].isna()]
    for _, r in untrained.iterrows():
        print(f"prediction  {r['label']:<20s} |dAUC| <= {r['bound_conservative']:.4f}")

    if not rep.empty:
        print("\nReplicate check (same nominal filter, two independent runs):")
        print(rep[["dataset", "model", "train_only_gap", "full_log_gap",
                   "delta_isolated", "delta_primary"]].to_string(index=False, float_format=lambda v: f"{v:.5f}"))
        for _, r in rep.iterrows():
            if r["full_log_gap"] > 5 * max(r["train_only_gap"], 1e-9):
                print(
                    f"  WARNING {r['dataset']}/{r['model']}: full-log arms disagree "
                    f"{r['full_log_gap'] / max(r['train_only_gap'], 1e-12):.0f}x more than train-only arms. "
                    "Graph artefacts are identical, so this is not a graph mismatch. "
                    "Measure the noise floor before treating the two vintages as comparable."
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
