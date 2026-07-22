#!/usr/bin/env python3
"""Deterministic F-R02 recomputation from ddr_downstream.csv (audit-only I/O)."""

from __future__ import annotations

import hashlib
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(r"D:\0. NCS\CODE\p0_project")
AUDIT = ROOT / "audit" / "2026-07-17-1541"
CSV_PATH = ROOT / "results" / "tables" / "ddr_downstream.csv"
BOOT_SEED = 20260717
BOOT_N = 10000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bootstrap_corr_ci(
    x: np.ndarray,
    y: np.ndarray,
    kind: str,
    n_boot: int = BOOT_N,
    seed: int = BOOT_SEED,
) -> tuple[float, float] | tuple[float, float]:
    """Percentile bootstrap 95% CI for Pearson r or Spearman rho."""
    rng = np.random.default_rng(seed)
    n = len(x)
    if n < 3:
        return (float("nan"), float("nan"))
    stats_boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xb, yb = x[idx], y[idx]
        if np.ptp(xb) == 0 or np.ptp(yb) == 0:
            stats_boot[i] = np.nan
            continue
        if kind == "pearson":
            stats_boot[i] = stats.pearsonr(xb, yb).statistic
        else:
            stats_boot[i] = stats.spearmanr(xb, yb).statistic
    ok = stats_boot[np.isfinite(stats_boot)]
    if len(ok) < max(100, n_boot // 10):
        return (float("nan"), float("nan"))
    lo, hi = np.percentile(ok, [2.5, 97.5])
    return float(lo), float(hi)


def baseline_auc(df: pd.DataFrame) -> dict[tuple, float]:
    """Mirror scripts/plot_ddr_downstream.py::_baseline_auc."""
    base = df[df["operator"] == "none"]
    use_seed = "split_seed" in df.columns
    out: dict[tuple, float] = {}
    for r in base.itertuples():
        if pd.isna(r.auc):
            continue
        if use_seed and pd.notna(getattr(r, "split_seed", np.nan)):
            key = (str(r.dataset), str(r.model), int(r.fold), int(r.split_seed))
        else:
            key = (str(r.dataset), str(r.model), int(r.fold))
        out[key] = float(r.auc)
    return out


def apply_plot_ddr_auc_drop(df: pd.DataFrame) -> pd.DataFrame:
    """Mirror plot_ddr_downstream.py recomputation of auc_drop."""
    out = df[pd.notna(df["auc"])].copy()
    base = baseline_auc(out)
    use_seed = "split_seed" in out.columns

    def _lookup(d, m, f, s) -> float:
        if use_seed and pd.notna(s):
            return base.get((str(d), str(m), int(f), int(s)), np.nan)
        return base.get((str(d), str(m), int(f)), np.nan)

    seeds = out["split_seed"] if use_seed else [np.nan] * len(out)
    out["baseline_auc_recomputed"] = [
        _lookup(d, m, f, s) for d, m, f, s in zip(out["dataset"], out["model"], out["fold"], seeds)
    ]
    out["auc_drop_recomputed"] = out["baseline_auc_recomputed"] - out["auc"]
    return out


def gkt_tex_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Mirror generate_ddr_downstream_gkt_tex.py pre-filter before _corr."""
    gkt = df[(df["model"] == "gkt") & (df["operator"] != "none")].copy()
    gkt = gkt[pd.notna(gkt["auc_drop"])]
    gkt["p"] = gkt["p"].astype(float).round(4)
    return gkt


def corr_pair(x: np.ndarray, y: np.ndarray, kind: str) -> tuple[float, float, int]:
    ok = np.isfinite(x) & np.isfinite(y)
    n = int(ok.sum())
    if n < 3:
        return float("nan"), float("nan"), n
    xv, yv = x[ok], y[ok]
    if np.ptp(xv) == 0:
        return float("nan"), float("nan"), n
    if kind == "pearson":
        r = stats.pearsonr(xv, yv)
        return float(r.statistic), float(r.pvalue), n
    rho = stats.spearmanr(xv, yv)
    return float(rho.statistic), float(rho.pvalue), n


def compare(reported: float, recomputed: float, decimals: int = 2) -> str:
    if not np.isfinite(recomputed):
        return "FAIL_NAN"
    if round(recomputed, decimals) == round(reported, decimals):
        return "PASS_ROUNDING" if abs(recomputed - reported) > 5e-4 else "PASS_EXACT_OR_TIGHT"
    # treat within half-ulp of display rounding as PASS
    if abs(recomputed - reported) <= 0.005 + 1e-12:
        return "PASS_ROUNDING"
    return "FAIL_SUBSTANTIVE"


def main() -> int:
    csv_sha = sha256(CSV_PATH)
    raw = pd.read_csv(CSV_PATH)
    gkt = gkt_tex_frame(raw)

    # (a)(b) — generate_ddr_downstream_gkt_tex.py::_corr
    part_a = gkt[(gkt["dataset"] == "xes3g5m") & (gkt["p"] <= 0.3 + 1e-9)]
    xa = part_a["ddr"].to_numpy(float)
    ya = part_a["auc_drop"].to_numpy(float)
    r_a, p_a, n_a = corr_pair(xa, ya, "pearson")
    ci_a = bootstrap_corr_ci(xa[np.isfinite(xa) & np.isfinite(ya)], ya[np.isfinite(xa) & np.isfinite(ya)], "pearson")

    part_b = gkt[gkt["dataset"] == "xes3g5m"]
    xb = part_b["ddr"].to_numpy(float)
    yb = part_b["auc_drop"].to_numpy(float)
    r_b, p_b, n_b = corr_pair(xb, yb, "pearson")
    ci_b = bootstrap_corr_ci(xb[np.isfinite(xb) & np.isfinite(yb)], yb[np.isfinite(xb) & np.isfinite(yb)], "pearson")

    # (c)(d) — plot_ddr_downstream.py (recomputed auc_drop)
    plot_df = apply_plot_ddr_auc_drop(raw)
    pert = plot_df[plot_df["operator"] != "none"].copy()
    part_c = pert[(pert["dataset"] == "xes3g5m") & (pert["model"] == "gkt")]
    xc = part_c["ddr"].to_numpy(float)
    yc = part_c["auc_drop_recomputed"].to_numpy(float)
    ok_c = np.isfinite(xc) & np.isfinite(yc)
    # plot_ddr also requires ptp(x)>0 for per-cell corr
    rho_c, prho_c, n_c = corr_pair(xc, yc, "spearman")
    r_c_pearson, _, _ = corr_pair(xc, yc, "pearson")  # diagnostic
    ci_c = bootstrap_corr_ci(xc[ok_c], yc[ok_c], "spearman")

    xd = pert["ddr"].to_numpy(float)
    yd = pert["auc_drop_recomputed"].to_numpy(float)
    r_d, p_d, n_d = corr_pair(xd, yd, "pearson")
    ok_d = np.isfinite(xd) & np.isfinite(yd)
    ci_d = bootstrap_corr_ci(xd[ok_d], yd[ok_d], "pearson")

    # Also reproduce plot_ddr caption cell Pearson for xes/gkt (same pool as Spearman)
    r_c_caption, p_c_caption, _ = corr_pair(xc, yc, "pearson")

    # Compare CSV auc_drop vs recomputed for xes/gkt
    gkt_plot = part_c.copy()
    if "auc_drop" in gkt_plot.columns:
        drop_diff = (gkt_plot["auc_drop"].to_numpy(float) - gkt_plot["auc_drop_recomputed"].to_numpy(float))
        max_abs_drop_diff = float(np.nanmax(np.abs(drop_diff))) if len(drop_diff) else float("nan")
    else:
        max_abs_drop_diff = float("nan")

    rows = [
        {
            "stat_id": "a_xes_gkt_pearson_core",
            "dataset": "xes3g5m",
            "model": "gkt",
            "filter": "operator!=none; auc_drop notna; p.round(4)<=0.3; CSV auc_drop (gkt_tex)",
            "script_mirror": "generate_ddr_downstream_gkt_tex.py::_corr(p_max=0.3)",
            "n": n_a,
            "statistic": "pearson_r",
            "value": r_a,
            "pvalue": p_a,
            "boot_ci_low": ci_a[0],
            "boot_ci_high": ci_a[1],
            "boot_n": BOOT_N,
            "boot_seed": BOOT_SEED,
            "reported_target": 0.93,
            "reported_label": "abstract/GKT-caption Pearson r≈0.93 core",
            "match_status": compare(0.93, r_a, 2),
            "display_2dp": round(r_a, 2) if np.isfinite(r_a) else None,
        },
        {
            "stat_id": "b_xes_gkt_pearson_all_p",
            "dataset": "xes3g5m",
            "model": "gkt",
            "filter": "operator!=none; auc_drop notna; all p incl anchors; CSV auc_drop (gkt_tex)",
            "script_mirror": "generate_ddr_downstream_gkt_tex.py::_corr(p_max=None)",
            "n": n_b,
            "statistic": "pearson_r",
            "value": r_b,
            "pvalue": p_b,
            "boot_ci_low": ci_b[0],
            "boot_ci_high": ci_b[1],
            "boot_n": BOOT_N,
            "boot_seed": BOOT_SEED,
            "reported_target": 0.99,
            "reported_label": "abstract/GKT-caption Pearson r≈0.99 with anchors; ddr_downstream.tex r=0.99",
            "match_status": compare(0.99, r_b, 2),
            "display_2dp": round(r_b, 2) if np.isfinite(r_b) else None,
        },
        {
            "stat_id": "c_xes_gkt_spearman_full",
            "dataset": "xes3g5m",
            "model": "gkt",
            "filter": "operator!=none; finite ddr & recomputed auc_drop; all p (plot_ddr per ds/model)",
            "script_mirror": "plot_ddr_downstream.py L108-115 spearmanr",
            "n": n_c,
            "statistic": "spearman_rho",
            "value": rho_c,
            "pvalue": prho_c,
            "boot_ci_low": ci_c[0],
            "boot_ci_high": ci_c[1],
            "boot_n": BOOT_N,
            "boot_seed": BOOT_SEED,
            "reported_target": 0.93,
            "reported_label": "ddr_downstream.tex caption rho=0.93 for xes3g5m/gkt",
            "match_status": compare(0.93, rho_c, 2),
            "display_2dp": round(rho_c, 2) if np.isfinite(rho_c) else None,
            "companion_pearson_same_pool": r_c_caption,
            "companion_pearson_pvalue": p_c_caption,
        },
        {
            "stat_id": "d_global_pearson_all_pert",
            "dataset": "ALL",
            "model": "ALL",
            "filter": "operator!=none; finite ddr & recomputed auc_drop; all datasets/models (figure pool)",
            "script_mirror": "plot_ddr_downstream.py L121-129 pearsonr",
            "n": n_d,
            "statistic": "pearson_r",
            "value": r_d,
            "pvalue": p_d,
            "boot_ci_low": ci_d[0],
            "boot_ci_high": ci_d[1],
            "boot_n": BOOT_N,
            "boot_seed": BOOT_SEED,
            "reported_target": 0.75,
            "reported_label": "fig_ddr_downstream.pdf pooled Pearson r=0.75",
            "match_status": compare(0.75, r_d, 2),
            "display_2dp": round(r_d, 2) if np.isfinite(r_d) else None,
        },
    ]

    out_csv = AUDIT / "ddr_recomputed.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)

    # Report
    lines = [
        "# DDR correlation recomputation report (F-R02)",
        "",
        f"- Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Input: `{CSV_PATH.as_posix()}`",
        f"- SHA-256: `{csv_sha}`",
        f"- Bootstrap: n={BOOT_N}, seed={BOOT_SEED}, percentile 2.5/97.5",
        "- Manuscript / figures: **not modified**",
        "",
        "## Filters mirrored",
        "",
        "### `generate_ddr_downstream_gkt_tex.py` (stats a, b)",
        "",
        "1. `model == 'gkt'` and `operator != 'none'`",
        "2. drop rows with NA `auc_drop` (CSV column)",
        "3. `p = float(p).round(4)`",
        "4. (a) `dataset == 'xes3g5m'` and `p <= 0.3 + 1e-9`",
        "5. (b) `dataset == 'xes3g5m'` (all remaining p, including anchors)",
        "6. Pearson on finite `(ddr, auc_drop)` via `scipy.stats.pearsonr`",
        "",
        "### `plot_ddr_downstream.py` (stats c, d)",
        "",
        "1. Keep rows with non-null `auc`",
        "2. Recompute `baseline_auc` from `operator == 'none'` keyed by `(dataset, model, fold, split_seed)`",
        "3. `auc_drop = baseline_auc - auc` (script path; not the stored column)",
        "4. `pert = operator != 'none'`",
        "5. (c) group cell `xes3g5m`/`gkt`: Spearman on finite `(ddr, auc_drop)`",
        "6. (d) global: Pearson on all finite pert `(ddr, auc_drop)`",
        "",
        f"- Max |CSV `auc_drop` − recomputed| on XES/GKT pert rows: `{max_abs_drop_diff:.6e}`",
        "",
        "## Results",
        "",
        "| ID | Filter | n | Stat | Value | p-value | Boot 95% CI | Reported | Match |",
        "|---|---|---:|---|---:|---:|---|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['stat_id']} | {r['filter'][:48]}… | {r['n']} | {r['statistic']} | "
            f"{r['value']:.6f} | {r['pvalue']:.3e} | "
            f"[{r['boot_ci_low']:.4f}, {r['boot_ci_high']:.4f}] | "
            f"{r['reported_target']} | **{r['match_status']}** |"
        )

    lines += [
        "",
        "## Comparison detail",
        "",
    ]
    for r in rows:
        lines += [
            f"### {r['stat_id']}",
            f"- Recomputed: `{r['value']:.10f}` → display 2 d.p. = `{r['display_2dp']}`",
            f"- Reported target: `{r['reported_target']}` ({r['reported_label']})",
            f"- Match: **{r['match_status']}**",
            f"- n={r['n']}; p={r['pvalue']:.6e}; CI=[{r['boot_ci_low']:.6f}, {r['boot_ci_high']:.6f}]",
            "",
        ]

    fail = [r for r in rows if str(r["match_status"]).startswith("FAIL")]
    lines += [
        "## Findings from recomputation",
        "",
    ]
    if not fail:
        lines.append(
            "No substantive mismatches. All four targets match at 2-decimal display rounding "
            "(`PASS_ROUNDING` or `PASS_EXACT_OR_TIGHT`). **No new CON finding opened.**"
        )
    else:
        lines.append("Substantive mismatches detected (new finding IDs for audit triage):")
        for r in fail:
            lines.append(
                f"- **F-R02-RECOMP-{r['stat_id']}**: recomputed {r['value']:.6f} vs reported "
                f"{r['reported_target']} ({r['match_status']}). Numbers not auto-corrected."
            )

    lines += [
        "",
        "## Companion (not a headline target)",
        "",
        f"- XES/GKT Pearson on the same full pool as Spearman (plot_ddr caption `r`): "
        f"`{r_c_pearson:.10f}` (2 d.p. = `{round(r_c_pearson, 2) if np.isfinite(r_c_pearson) else None}`), "
        f"p=`{p_c_caption:.3e}`, n=`{n_c}` — expected to align with reported `r=0.99` in "
        "`ddr_downstream.tex` caption.",
        f"- Match vs 0.99: **{compare(0.99, r_c_pearson, 2)}**",
        "",
    ]

    (AUDIT / "ddr_recomputation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    log = [
        "# DDR recomputation reproduction log",
        "",
        f"- UTC: {datetime.now(timezone.utc).isoformat()}",
        f"- Python: {sys.version.split()[0]} ({platform.python_implementation()})",
        f"- Platform: {platform.platform()}",
        f"- numpy: {np.__version__}; pandas: {pd.__version__}; scipy: {getattr(stats, '__module__', 'scipy.stats')}",
        f"- scipy version: {__import__('scipy').__version__}",
        f"- Input CSV: `{CSV_PATH}`",
        f"- Input SHA-256: `{csv_sha}`",
        f"- Input size bytes: {CSV_PATH.stat().st_size}",
        f"- Bootstrap seed: {BOOT_SEED}; n_resamples: {BOOT_N}",
        f"- Working directory intent: read `{CSV_PATH}`, write only under `{AUDIT}`",
        "",
        "## Commands",
        "",
        "```",
        f'python "{AUDIT / "recompute_ddr_correlations.py"}"',
        "```",
        "",
        "## Outputs",
        "",
        f"- `{out_csv}`",
        f"- `{AUDIT / 'ddr_recomputation_report.md'}`",
        f"- `{AUDIT / 'ddr_reproduction_log.md'}`",
        "",
        "## Observed summary",
        "",
    ]
    for r in rows:
        log.append(
            f"- {r['stat_id']}: n={r['n']} {r['statistic']}={r['value']:.6f} "
            f"p={r['pvalue']:.3e} CI=[{r['boot_ci_low']:.4f},{r['boot_ci_high']:.4f}] "
            f"vs {r['reported_target']} → {r['match_status']}"
        )
    log += [
        "",
        f"- max_abs auc_drop CSV vs recomputed (XES/GKT): {max_abs_drop_diff:.6e}",
        f"- companion XES/GKT Pearson full pool: {r_c_pearson:.6f} → {compare(0.99, r_c_pearson, 2)}",
        "",
        "## Non-actions",
        "",
        "- Did not modify manuscript, `results/`, or figures.",
        "- Did not rewrite reported manuscript numbers.",
        "",
    ]
    (AUDIT / "ddr_reproduction_log.md").write_text("\n".join(log), encoding="utf-8")

    print(out_csv)
    for r in rows:
        print(
            r["stat_id"],
            f"n={r['n']}",
            f"{r['statistic']}={r['value']:.6f}",
            f"p={r['pvalue']:.3e}",
            f"CI=[{r['boot_ci_low']:.4f},{r['boot_ci_high']:.4f}]",
            r["match_status"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
