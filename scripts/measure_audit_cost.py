"""Measure wall-clock and peak RAM of one-fold graph audit (M6).

Does not write to data/processed/<dataset>/fold_*. Graphs go to
results/audit_cost/scratch/<dataset>/ so primary artefacts stay intact.

Usage:
    python scripts/measure_audit_cost.py --dataset assist2012
    python scripts/measure_audit_cost.py                 # all public corpora, subprocess-isolated
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = (
    ("assist2012", "configs/assist2012.yaml"),
    ("xes3g5m", "configs/xes3g5m.yaml"),
    ("junyi", "configs/junyi.yaml"),
)


def _rss_mb() -> float:
    try:
        import psutil

        info = psutil.Process().memory_info()
        current = float(info.rss)
        peak = float(getattr(info, "peak_wset", 0) or 0)
        return max(current, peak) / (1024 * 1024)
    except Exception:
        pass
    if sys.platform != "win32":
        return float("nan")
    import ctypes
    from ctypes import wintypes

    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    counters = PROCESS_MEMORY_COUNTERS_EX()
    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    if not ok:
        return float("nan")
    return float(counters.PeakWorkingSetSize) / (1024 * 1024)


def _time_stage(fn, tracker: dict) -> object:
    gc.collect()
    t0 = time.perf_counter()
    rss0 = _rss_mb()
    out = fn()
    elapsed = time.perf_counter() - t0
    rss1 = _rss_mb()
    tracker["elapsed_s"] = elapsed
    tracker["rss_before_mb"] = rss0
    tracker["rss_after_mb"] = rss1
    tracker["rss_peak_mb"] = max(rss0, rss1) if pd.notna(rss0) and pd.notna(rss1) else rss1
    return out


def run_one(dataset: str, config_path: Path, out_dir: Path) -> dict:
    sys.path.insert(0, str(ROOT))
    from src.dag_audit import prune_cycles
    from src.graph_builder import (
        build_q_matrix_from_train,
        infer_prerequisites_from_train,
        infer_similarity_edges_from_train,
    )
    from src.io_utils import dump_csv, load_interactions, load_yaml
    from src.leakage_metrics import compute_edge_heldout_shares, compute_leakage_row
    from src.split_checker import learner_based_folds

    cfg = load_yaml(config_path)
    processed = Path(cfg.get("processed_path", f"data/processed/{dataset}.parquet"))
    if not processed.exists():
        raise FileNotFoundError(processed)
    graph_cfg = cfg.get("graph", {})
    ratios = tuple(cfg.get("split", {}).get("ratios", [0.7, 0.1, 0.2]))
    stages: dict[str, dict] = {}
    peak = _rss_mb()

    def bump() -> None:
        nonlocal peak
        now = _rss_mb()
        if pd.notna(now) and (pd.isna(peak) or now > peak):
            peak = now

    t_all = time.perf_counter()
    df = _time_stage(lambda: load_interactions(processed), stages.setdefault("load", {}))
    bump()
    n_rows = int(len(df))

    def _split():
        for fold, split_seed, splits in learner_based_folds(
            df, ratios, cfg.get("split", {}), default_seed=int(cfg.get("split", {}).get("seed", 42))
        ):
            if int(fold) == 0:
                return fold, split_seed, splits
        raise RuntimeError("fold 0 not produced")

    fold, split_seed, splits = _time_stage(_split, stages.setdefault("split", {}))
    bump()
    train = splits["train"]
    q_train = _time_stage(lambda: build_q_matrix_from_train(train), stages.setdefault("q_matrix", {}))
    bump()
    pre = _time_stage(
        lambda: infer_prerequisites_from_train(
            train,
            q_train,
            max_edges=int(graph_cfg.get("e_pre_max_edges", 5000)),
            top_k_per_node=int(graph_cfg.get("e_pre_top_k_per_node", 10)),
            support_quantile=float(graph_cfg.get("e_pre_support_quantile", 0.90)),
        ),
        stages.setdefault("infer_pre", {}),
    )
    bump()
    sim = _time_stage(
        lambda: infer_similarity_edges_from_train(
            train,
            q_train,
            method=graph_cfg.get("e_sim_method", "jaccard"),
            threshold=float(graph_cfg.get("e_sim_threshold", 0.1)),
        ),
        stages.setdefault("infer_sim", {}),
    )
    bump()
    pruned, _log = _time_stage(lambda: prune_cycles(pre), stages.setdefault("dag_prune", {}))
    bump()
    _time_stage(
        lambda: compute_leakage_row(
            dataset=dataset,
            fold=int(fold),
            splits=splits,
            pre_df=pruned,
            sim_df=sim,
            q_train=q_train,
            train_ratio=float(ratios[0]) if ratios else 0.7,
        ),
        stages.setdefault("leakage_scalars", {}),
    )
    bump()
    held = pd.concat([splits["valid"], splits["test"]], ignore_index=True)
    _time_stage(
        lambda: compute_edge_heldout_shares(pruned, sim, train, held, q_train),
        stages.setdefault("edge_shares", {}),
    )
    bump()

    scratch = out_dir / "scratch" / dataset
    scratch.mkdir(parents=True, exist_ok=True)
    dump_csv(pruned, scratch / "e_pre_fold0.csv")
    dump_csv(sim, scratch / "e_sim_fold0.csv")

    wall = time.perf_counter() - t_all
    row = {
        "dataset": dataset,
        "fold": int(fold),
        "split_seed": int(split_seed),
        "n_interactions": n_rows,
        "n_train": int(len(train)),
        "n_pre_raw": int(len(pre)),
        "n_pre_pruned": int(len(pruned)),
        "n_sim": int(len(sim)),
        "wall_clock_s": round(wall, 1),
        "wall_clock_min": round(wall / 60.0, 2),
        "est_three_fold_min": round(3.0 * wall / 60.0, 2),
        "peak_rss_mb": round(float(peak), 1) if pd.notna(peak) else None,
        "host": sys.platform,
        "python": sys.version.split()[0],
    }
    for name, st in stages.items():
        row[f"{name}_s"] = round(float(st.get("elapsed_s", float("nan"))), 2)
    (out_dir / f"{dataset}_fold0.json").write_text(json.dumps({"row": row, "stages": stages}, indent=2), encoding="utf-8")
    return row


def write_tex(df: pd.DataFrame, path: Path) -> None:
    def fmt_min(v: float) -> str:
        if pd.isna(v):
            return "---"
        if v < 1:
            return rf"${v * 60:.0f}$\,s"
        return rf"${v:.1f}$\,min"

    def fmt_ram(v: float) -> str:
        if pd.isna(v):
            return "---"
        if v >= 1024:
            return rf"${v / 1024:.1f}$\,GiB"
        return rf"${v:.0f}$\,MiB"

    labels = {"assist2012": "ASSISTments 2012", "xes3g5m": "XES3G5M", "junyi": "Junyi Academy"}
    lines = [
        r"% Auto-generated by scripts/measure_audit_cost.py",
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Measured CPU cost of one fold-0 audit gate (load $\to$ train-only "
        r"$G_f$ inference $\to$ DAG prune $\to$ leakage scalars and per-edge shares). "
        r"Peak RSS is the process working set on the measurement host. "
        r"The three-fold column is $3\times$ fold-0 wall-clock (protocol default). "
        r"No GPU is required. Scratch graphs are written under "
        r"\texttt{results/audit\_cost/} and do not overwrite primary fold exports.}",
        r"\label{tab:audit-cost}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabularx}{\linewidth}{@{} >{\RaggedRight\arraybackslash}X r r r r r @{}}",
        r"\toprule",
        r"Dataset & Interactions & Fold-0 wall & Est.\ 3-fold & Peak RSS & $|\Epre|$ \\",
        r"\midrule",
    ]
    order = ["assist2012", "xes3g5m", "junyi"]
    for ds in order:
        part = df[df["dataset"] == ds]
        if part.empty:
            continue
        r0 = part.iloc[0]
        n_int = f"{int(r0['n_interactions']):,}".replace(",", "{,}")
        n_pre = f"{int(r0['n_pre_pruned']):,}".replace(",", "{,}")
        ram = fmt_ram(float(r0["peak_rss_mb"])) if pd.notna(r0["peak_rss_mb"]) else "---"
        lines.append(
            f"{labels.get(ds, ds)} & {n_int} & {fmt_min(float(r0['wall_clock_min']))} & "
            f"{fmt_min(float(r0['est_three_fold_min']))} & {ram} & {n_pre} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "audit_cost")
    parser.add_argument("--sync-tex", action="store_true")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.dataset:
        cfg = args.config or ROOT / dict(DEFAULTS)[args.dataset]
        row = run_one(args.dataset, cfg, args.out_dir)
        csv_path = args.out_dir / "audit_cost.csv"
        new = pd.DataFrame([row])
        if csv_path.exists():
            old = pd.read_csv(csv_path)
            old = old[old["dataset"] != args.dataset]
            new = pd.concat([old, new], ignore_index=True)
        new.to_csv(csv_path, index=False)
        print(json.dumps(row, indent=2))
        if args.sync_tex:
            write_tex(new, ROOT / "results" / "tables" / "audit_cost.tex")
            dest = ROOT / "paper" / "submission_EAAI" / "audit_cost.tex"
            dest.write_text((ROOT / "results" / "tables" / "audit_cost.tex").read_text(encoding="utf-8"), encoding="utf-8")
        return 0

    csv_path = args.out_dir / "audit_cost.csv"
    if csv_path.exists():
        csv_path.unlink()
    for ds, cfg in DEFAULTS:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--dataset",
            ds,
            "--config",
            str(ROOT / cfg),
            "--out-dir",
            str(args.out_dir),
        ]
        print("RUN", " ".join(cmd), flush=True)
        proc = subprocess.run(cmd, cwd=str(ROOT))
        if proc.returncode != 0:
            return proc.returncode
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        write_tex(df, ROOT / "results" / "tables" / "audit_cost.tex")
        if args.sync_tex:
            dest = ROOT / "paper" / "submission_EAAI" / "audit_cost.tex"
            dest.write_text((ROOT / "results" / "tables" / "audit_cost.tex").read_text(encoding="utf-8"), encoding="utf-8")
        print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
