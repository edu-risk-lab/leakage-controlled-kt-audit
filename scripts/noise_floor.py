"""Training noise floor (sigma) from replicate runs already on disk.

A replicate group is a set of runs that share dataset, model, fold, split_seed,
operator, strength, and graph size, but were produced under different
experiment seeds. Such runs consume an identical graph and an identical split,
so their AUC spread isolates training nondeterminism.

Only the ASSISTments cells of the multi-seed GKT sweep satisfy this: the
XES3G5M cells vary split_seed and edge count across seed files, so they are not
replicates and are reported separately as a diagnostic.

Usage:
    python scripts/noise_floor.py
    python scripts/noise_floor.py --sync-tex
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SWEEP_DIR = ROOT / "results" / "q1" / "ddr_downstream_gkt"

# Columns that must agree for two runs to consume the same graph and split.
GROUP_KEYS = ("dataset", "model", "fold", "split_seed", "operator", "p", "n_edges_orig", "num_c")


def load_sweep(sweep_dir: Path) -> pd.DataFrame:
    """Concatenate per-seed sweep CSVs, tagging each row with its source file."""
    frames = []
    for path in sorted(sweep_dir.glob("ddr_downstream_gkt_seed*.csv")):
        part = pd.read_csv(path)
        part["source"] = path.name
        frames.append(part)
    if not frames:
        raise FileNotFoundError(f"no sweep CSVs under {sweep_dir}")
    df = pd.concat(frames, ignore_index=True)
    return df.drop_duplicates(subset=[*GROUP_KEYS, "auc"]).reset_index(drop=True)


def replicate_groups(df: pd.DataFrame, *, min_size: int = 2) -> pd.DataFrame:
    """One row per replicate group with the AUC spread across experiment seeds."""
    rows = []
    for key, part in df.groupby(list(GROUP_KEYS), sort=False):
        auc = part["auc"].astype(float)
        if auc.size < min_size:
            continue
        rows.append(
            {
                **dict(zip(GROUP_KEYS, key, strict=True)),
                "n_replicates": int(auc.size),
                "auc_mean": float(auc.mean()),
                "auc_range": float(auc.max() - auc.min()),
                "auc_std": float(auc.std(ddof=1)),
            }
        )
    return pd.DataFrame(rows)


def pairwise_null(df: pd.DataFrame, *, min_size: int = 2) -> pd.Series:
    """Absolute AUC differences between run pairs that differ only by seed.

    This is the null distribution the vintage gap must be judged against: a
    two-run difference, not the range of a three-seed group, which is
    systematically wider and would make the comparison anti-conservative.
    """
    diffs: list[float] = []
    for _key, part in df.groupby(list(GROUP_KEYS), sort=False):
        auc = part["auc"].astype(float).to_numpy()
        if auc.size < min_size:
            continue
        for i in range(auc.size):
            for j in range(i + 1, auc.size):
                diffs.append(abs(float(auc[i] - auc[j])))
    return pd.Series(diffs, dtype=float, name="abs_diff")


def tail_fraction(null: pd.Series, observed: float) -> float:
    """Fraction of seed-only pairs at least as extreme as the observed gap."""
    if null.empty:
        return float("nan")
    return float((null >= observed).mean())


def dispersion(df: pd.DataFrame, dataset: str, *, max_edges: int | None = None) -> dict:
    """Seed-only and total AUC dispersion for the unperturbed cells of one corpus.

    ``seed_sd`` pools the within-split variance across replicate groups, so it
    isolates training seed. ``total_sd`` spans splits, graphs, and seeds. Their
    ratio is the share of dispersion that retraining alone contributes, and it
    is dimensionless, which is what makes it transferable between corpora that
    sit at different AUC levels.
    """
    part = df[(df["dataset"] == dataset) & (df["operator"] == "none")]
    part = part.drop_duplicates(subset=["dataset", "fold", "split_seed", "n_edges_orig", "auc"])
    if max_edges is not None:
        part = part[part["n_edges_orig"] <= max_edges]
    auc = part["auc"].astype(float)
    grouped = part.groupby(["fold", "split_seed"])["auc"]
    ss = sum(float(((g - g.mean()) ** 2).sum()) for _name, g in grouped)
    dof = sum(len(g) - 1 for _name, g in grouped)
    seed_sd = float(np.sqrt(ss / dof)) if dof > 0 else float("nan")
    total_sd = float(auc.std(ddof=1)) if auc.size > 1 else float("nan")
    return {
        "dataset": dataset,
        "n_cells": int(auc.size),
        "n_replicated_splits": int(sum(1 for _name, g in grouped if len(g) > 1)),
        "seed_sd": seed_sd,
        "total_sd": total_sd,
        "seed_share": seed_sd / total_sd if total_sd and np.isfinite(seed_sd) else float("nan"),
    }


def transfer_sigma(df: pd.DataFrame, *, source: str, target: str, max_edges: int | None = None) -> dict:
    """Estimate the target corpus noise floor without retraining it.

    The target has no replicate groups, so its seed dispersion cannot be read
    directly. We instead scale its observed total dispersion by the seed share
    measured on the source corpus, then convert that standard deviation into a
    worst-case two-run difference using the tail factor the source exhibits.
    Transferring a ratio rather than an absolute AUC is the weaker assumption,
    but it is still an assumption and the result is an estimate, not a
    measurement.
    """
    src = dispersion(df, source)
    tgt = dispersion(df, target, max_edges=max_edges)
    null = pairwise_null(df[df["dataset"] == source])
    tail_factor = float(null.max() / src["seed_sd"]) if not null.empty and src["seed_sd"] else float("nan")
    seed_sd_est = src["seed_share"] * tgt["total_sd"]
    return {
        "source": source,
        "target": target,
        "seed_share_source": src["seed_share"],
        "total_sd_target": tgt["total_sd"],
        "seed_sd_target_est": seed_sd_est,
        "tail_factor_source": tail_factor,
        "sigma_target_est": seed_sd_est * tail_factor,
    }


def summarise(groups: pd.DataFrame) -> pd.DataFrame:
    """Per-dataset noise floor, taking the worst replicate group as sigma."""
    rows = []
    for (dataset, model), part in groups.groupby(["dataset", "model"], sort=False):
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "n_groups": int(len(part)),
                "n_replicates_min": int(part["n_replicates"].min()),
                "sigma_range_max": float(part["auc_range"].max()),
                "sigma_range_median": float(part["auc_range"].median()),
                "sigma_std_max": float(part["auc_std"].max()),
            }
        )
    return pd.DataFrame(rows)


def vintage_comparison(path: Path) -> pd.DataFrame | None:
    """Per-arm vintage gaps, for comparison against the measured noise floor.

    The asymmetry matters more than either gap alone: generic training
    nondeterminism would move both arms by a similar amount.
    """
    if not path.exists():
        return None
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        train_gap = abs(float(r["train_only_gap"]))
        full_gap = abs(float(r["full_log_gap"]))
        rows.append(
            {
                "dataset": r["dataset"],
                "model": r["model"],
                "fold": int(r["fold"]),
                "train_only_gap": train_gap,
                "full_log_gap": full_gap,
                "asymmetry": full_gap / train_gap if train_gap > 0 else float("inf"),
            }
        )
    return pd.DataFrame(rows)


def _sci(value: float, digits: int = 1) -> str:
    """LaTeX scientific notation, e.g. 1.586e-4 -> 1.6\\times10^{-4}."""
    if value == 0:
        return "0"
    exponent = int(f"{value:e}".split("e")[1])
    mantissa = value / (10.0**exponent)
    if abs(round(mantissa, digits)) >= 10.0:  # e.g. 9.99 rounds up to 10.0
        mantissa /= 10.0
        exponent += 1
    return rf"{mantissa:.{digits}f}\times10^{{{exponent}}}"


def write_macros(summary: pd.DataFrame, null: pd.Series, path: Path, transfer: dict | None = None) -> None:
    lines = [r"% Auto-generated by scripts/noise_floor.py — do not edit."]
    by = {r["dataset"]: r for _, r in summary.iterrows()}
    if "assist2012" in by:
        row = by["assist2012"]
        lines += [
            rf"\newcommand{{\NoiseFloorGroups}}{{{int(row['n_groups'])}}}",
            rf"\newcommand{{\NoiseFloorPairs}}{{{len(null)}}}",
            rf"\newcommand{{\NoiseFloorMedian}}{{\ensuremath{{{_sci(float(null.median()))}}}}}",
            rf"\newcommand{{\NoiseFloorNinety}}{{\ensuremath{{{_sci(float(null.quantile(0.9)))}}}}}",
            rf"\newcommand{{\NoiseFloorMax}}{{\ensuremath{{{_sci(float(null.max()))}}}}}",
        ]
    if transfer is not None:
        lines += [
            rf"\newcommand{{\NoiseFloorSeedShare}}{{{transfer['seed_share_source']:.2f}}}",
            rf"\newcommand{{\NoiseFloorPrimaryEst}}"
            rf"{{\ensuremath{{{_sci(float(transfer['sigma_target_est']))}}}}}",
        ]
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-dir", type=Path, default=SWEEP_DIR)
    parser.add_argument(
        "--replicate-csv", type=Path, default=ROOT / "results" / "tables" / "exposure_replicate_check.csv"
    )
    parser.add_argument("--out-csv", type=Path, default=ROOT / "results" / "tables" / "noise_floor.csv")
    parser.add_argument("--out-groups", type=Path, default=ROOT / "results" / "tables" / "noise_floor_groups.csv")
    parser.add_argument("--out-macros", type=Path, default=ROOT / "results" / "tables" / "noise_floor_macros.tex")
    parser.add_argument("--out-transfer", type=Path, default=ROOT / "results" / "tables" / "noise_floor_transfer.csv")
    parser.add_argument("--sync-tex", action="store_true")
    args = parser.parse_args()

    df = load_sweep(args.sweep_dir)
    groups = replicate_groups(df)
    if groups.empty:
        print("No replicate groups found: every cell was run under a single experiment seed.")
        return 1

    summary = summarise(groups)
    null = pairwise_null(df)
    transfers = [
        ("all cells", transfer_sigma(df, source="assist2012", target="xes3g5m")),
        ("excl. odd-vintage graphs", transfer_sigma(df, source="assist2012", target="xes3g5m", max_edges=1300)),
    ]
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    groups.to_csv(args.out_groups, index=False)
    summary.to_csv(args.out_csv, index=False)
    write_macros(summary, null, args.out_macros, transfer=transfers[0][1])

    print("Replicate groups (identical graph + split, differing experiment seed):")
    print(summary.to_string(index=False))

    singles = sorted(set(df["dataset"]) - set(summary["dataset"]))
    if singles:
        print(f"\nNo replicates available for: {', '.join(singles)}")
        print("  (seed files use different split_seed and edge counts, so runs are not comparable)")

    print(f"\nSeed-only pair differences (n={len(null)}): "
          f"median {null.median():.3e}, p90 {null.quantile(0.9):.3e}, max {null.max():.3e}")

    print("\nDispersion of unperturbed cells by corpus:")
    disp = pd.DataFrame([dispersion(df, ds) for ds in sorted(df["dataset"].unique())])
    print(disp.to_string(index=False, float_format=lambda v: f"{v:.3e}"))

    print("\nNoise floor transferred to the primary corpus (no retraining):")
    for label, row in transfers:
        print(
            f"  {label:24s} seed sd est {row['seed_sd_target_est']:.3e}"
            f"  x tail {row['tail_factor_source']:.1f}"
            f"  -> sigma {row['sigma_target_est']:.3e}"
        )
    pd.DataFrame([r for _label, r in transfers]).to_csv(args.out_transfer, index=False)

    vintage = vintage_comparison(args.replicate_csv)
    if vintage is not None:
        vintage["full_log_tail"] = [tail_fraction(null, v) for v in vintage["full_log_gap"]]
        vintage["train_only_tail"] = [tail_fraction(null, v) for v in vintage["train_only_gap"]]
        print("\nVintage gaps by arm, against the seed-only null:")
        print(vintage.to_string(index=False, float_format=lambda v: f"{v:.3e}"))
        print("\nA small full-log tail with a large train-only tail localises the")
        print("discrepancy to the full-log branch; generic training noise would")
        print("place both arms in comparable parts of the null.")

    print(f"\nWrote {args.out_csv}")
    print(f"Wrote {args.out_groups}")
    print(f"Wrote {args.out_macros}")
    print(f"Wrote {args.out_transfer}")
    if args.sync_tex:
        dest = ROOT / "paper" / "submission_EAAI" / "noise_floor_macros.tex"
        dest.write_text(args.out_macros.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Synced {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
