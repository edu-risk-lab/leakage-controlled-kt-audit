"""Phase A driver for the M4 q × K builder census (no KT training).

Writes isolated graphs under data/processed/<dataset>/m4/ and never touches
primary fold_* / full_log artefacts or results/tables/graph_ablation*.csv.

Usage (repo root):
    python scripts/run_m4_qk_sweep.py
    python scripts/run_m4_qk_sweep.py --dry-run
    python scripts/run_m4_qk_sweep.py --fold-idx 0
    python scripts/run_m4_qk_sweep.py --phase b --cells default --dry-run
    python scripts/run_m4_qk_sweep.py --phase b --cells default --fold-idx 0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.graph_builder import (  # noqa: E402
    UNLIMITED_CAP,
    build_q_matrix_from_interactions,
    build_q_matrix_from_train,
    count_kc_transitions,
    filter_prerequisite_counts,
    infer_similarity_edges_from_q_matrix,
)
from src.io_utils import dump_csv, load_interactions, load_yaml  # noqa: E402
from src.leakage_metrics import (  # noqa: E402
    _pair_count_map,
    compute_edge_heldout_shares,
    summarize_edge_heldout_shares,
)
from src.split_checker import learner_based_folds  # noqa: E402

logger = logging.getLogger("m4")

Q_GRID = (0.50, 0.80, 0.90, 0.95)
K_GRID = (1000, 5000, UNLIMITED_CAP)
TAU_ARM = (0.05, 0.10, 0.20)
K_ARM = (5, 20, UNLIMITED_CAP)
DEFAULT_Q = 0.95
DEFAULT_K = 5
DEFAULT_K_GLOBAL = 5000
DEFAULT_TAU = 0.10
OPEN_Q = 0.50


@dataclass(frozen=True)
class FilterCell:
    q: float
    k: int
    K: int
    tau: float
    arm: str

    @property
    def tag(self) -> str:
        return f"q{self.q:g}_k{_fmt_cap(self.k)}_K{_fmt_cap(self.K)}_tau{self.tau:g}"

    def as_overlay(self, base_graph: dict) -> dict:
        graph = dict(base_graph)
        graph["e_pre_support_quantile"] = float(self.q)
        graph["e_pre_top_k_per_node"] = int(self.k)
        graph["e_pre_max_edges"] = int(self.K)
        graph["e_sim_threshold"] = float(self.tau)
        return graph


def _fmt_cap(value: int) -> str:
    return "inf" if int(value) >= UNLIMITED_CAP else str(int(value))


def phase_a_cells() -> list[FilterCell]:
    """Review q×K grid plus one-factor τ and k arms; unique (q, k, K, τ)."""
    cells: list[FilterCell] = []
    for q in Q_GRID:
        for K in K_GRID:
            cells.append(FilterCell(q=q, k=DEFAULT_K, K=K, tau=DEFAULT_TAU, arm="qk"))
    for tau in TAU_ARM:
        cells.append(
            FilterCell(q=DEFAULT_Q, k=DEFAULT_K, K=DEFAULT_K_GLOBAL, tau=tau, arm="tau")
        )
    for k in K_ARM:
        cells.append(FilterCell(q=OPEN_Q, k=k, K=UNLIMITED_CAP, tau=DEFAULT_TAU, arm="k"))
    seen: dict[tuple[float, int, int, float], FilterCell] = {}
    for cell in cells:
        key = (cell.q, cell.k, cell.K, cell.tau)
        if key not in seen:
            seen[key] = cell
        else:
            seen[key] = FilterCell(
                q=cell.q,
                k=cell.k,
                K=cell.K,
                tau=cell.tau,
                arm=f"{seen[key].arm}+{cell.arm}",
            )
    return list(seen.values())


def assert_isolated_data_root(path: Path, dataset: str) -> None:
    resolved = path.resolve()
    parts = set(resolved.parts)
    if "m4" not in parts:
        raise ValueError(f"M4 data root must contain an 'm4' path segment: {resolved}")
    processed = (ROOT / "data" / "processed" / dataset).resolve()
    forbidden = [processed / "full_log"]
    forbidden.extend(processed / f"fold_{i}" for i in range(8))
    for item in forbidden:
        item_res = item.resolve()
        if resolved == item_res or item_res in resolved.parents:
            raise ValueError(f"Refusing to write M4 artefacts under primary path {item_res}")


def _edge_pairs(df: pd.DataFrame, *, directed: bool) -> set[tuple[int, int] | frozenset[int]]:
    if df is None or df.empty:
        return set()
    pairs: set[tuple[int, int] | frozenset[int]] = set()
    for src, dst in zip(df["src_kc"].astype(int), df["dst_kc"].astype(int), strict=True):
        pairs.add((src, dst) if directed else frozenset((src, dst)))
    return pairs


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return float(len(a & b) / len(union)) if union else 1.0


def edge_signature(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        payload = b""
    else:
        ordered = (
            df[["src_kc", "dst_kc"]]
            .astype(int)
            .sort_values(["src_kc", "dst_kc"], kind="mergesort")
            .drop_duplicates()
        )
        payload = ordered.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def _load_or_build_counts(path: Path, interactions: pd.DataFrame, label: str) -> pd.DataFrame:
    if path.exists():
        logger.info("Reusing cached transitions %s", path)
        return pd.read_parquet(path)
    logger.info("Counting transitions (%s) on %s rows", label, len(interactions))
    counts = count_kc_transitions(interactions)
    _write_parquet(counts, path)
    return counts


def _load_or_build_q(path: Path, interactions: pd.DataFrame, *, train_only: bool) -> pd.DataFrame:
    if path.exists():
        logger.info("Reusing cached Q-matrix %s", path)
        return pd.read_parquet(path)
    q = build_q_matrix_from_train(interactions) if train_only else build_q_matrix_from_interactions(interactions)
    _write_parquet(q, path)
    return q


def _iter_folds(
    df: pd.DataFrame,
    cfg: dict,
    fold_idx: int | None,
) -> Iterator[tuple[int, int, dict[str, pd.DataFrame]]]:
    ratios = tuple(cfg.get("split", {}).get("ratios", [0.7, 0.1, 0.2]))
    split_cfg = cfg.get("split", {})
    seed = int(split_cfg.get("seed", 42))
    for fold, split_seed, splits in learner_based_folds(df, ratios, split_cfg, default_seed=seed):
        if fold_idx is not None and fold != fold_idx:
            continue
        yield fold, split_seed, splits


def _cell_dir(data_root: Path, cell: FilterCell) -> Path:
    return data_root / cell.tag


def write_overlays(cells: list[FilterCell], dest: Path, base_cfg: dict) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for cell in cells:
        overlay = dict(base_cfg)
        overlay["graph"] = cell.as_overlay(base_cfg.get("graph", {}))
        overlay["graph_ablation"] = dict(base_cfg.get("graph_ablation", {}))
        overlay["graph_ablation"]["enabled"] = True
        overlay["graph_ablation"]["models"] = ["gkt"]
        overlay["m4_cell"] = {
            "tag": cell.tag,
            "arm": cell.arm,
            "q": cell.q,
            "k": cell.k,
            "K": cell.K,
            "tau": cell.tau,
        }
        path = dest / f"{cell.tag}.yaml"
        path.write_text(yaml.safe_dump(overlay, sort_keys=False), encoding="utf-8")
        logger.info("Wrote overlay %s", path)


def _phase_b_jobs(census: pd.DataFrame) -> dict:
    """Recommend GPU jobs from fold-0 signatures (no training here)."""
    if census.empty:
        return {"jobs": [], "unique_fold0": []}
    fold0 = census[census["fold"] == 0].copy()
    unique_ids = (
        fold0.groupby("graph_signature", dropna=False)
        .agg(
            tags=("cell_tag", lambda s: sorted(set(s))),
            n_pre_to=("n_pre_to", "first"),
            n_pre_fl_minus_to=("n_pre_fl_minus_to", "first"),
            primary_bind_to=("primary_bind_to", "first"),
            n_sim_to=("n_sim_to", "first"),
        )
        .reset_index()
    )

    def _row(tag: str) -> pd.Series | None:
        hit = fold0[fold0["cell_tag"] == tag]
        return None if hit.empty else hit.iloc[0]

    def _sig(tag: str) -> str | None:
        row = _row(tag)
        return None if row is None else str(row["graph_signature"])

    default_tag = FilterCell(DEFAULT_Q, DEFAULT_K, DEFAULT_K_GLOBAL, DEFAULT_TAU, "qk").tag
    k1000_tag = FilterCell(DEFAULT_Q, DEFAULT_K, 1000, DEFAULT_TAU, "qk").tag
    mid_tag = FilterCell(0.80, DEFAULT_K, DEFAULT_K_GLOBAL, DEFAULT_TAU, "qk").tag
    open_tag = FilterCell(OPEN_Q, DEFAULT_K, UNLIMITED_CAP, DEFAULT_TAU, "qk").tag

    always = [default_tag, k1000_tag, mid_tag, open_tag]
    jobs: list[dict] = []
    seen_sig: set[str] = set()
    for tag, reason in (
        (default_tag, "published_default"),
        (k1000_tag, "K_binds_at_default_q"),
        (mid_tag, "mid_q"),
        (open_tag, "review_open_corner"),
    ):
        sig = _sig(tag)
        if sig is None:
            continue
        if sig in seen_sig:
            jobs.append({"tag": tag, "fold": 0, "model": "gkt", "reason": f"{reason}_duplicate_signature", "train": False})
            continue
        seen_sig.add(sig)
        jobs.append({"tag": tag, "fold": 0, "model": "gkt", "reason": reason, "train": True})

    open_row = _row(open_tag)
    k_lift_needed = bool(open_row is not None and open_row["k_binds_to"])
    if k_lift_needed:
        for k in (20, UNLIMITED_CAP):
            tag = FilterCell(OPEN_Q, k, UNLIMITED_CAP, DEFAULT_TAU, "k").tag
            sig = _sig(tag)
            if sig is None or sig in seen_sig:
                continue
            seen_sig.add(sig)
            jobs.append({"tag": tag, "fold": 0, "model": "gkt", "reason": "k_lift_opens_channel", "train": True})

    default_row = _row(default_tag)
    tau_needed = False
    if default_row is not None:
        base_sim = float(default_row["n_sim_to"])
        for tau in (0.05, 0.20):
            tag = FilterCell(DEFAULT_Q, DEFAULT_K, DEFAULT_K_GLOBAL, tau, "tau").tag
            row = _row(tag)
            if row is None:
                continue
            if base_sim <= 0:
                changed = int(row["n_sim_to"]) != int(base_sim)
            else:
                changed = abs(int(row["n_sim_to"]) - base_sim) / base_sim >= 0.20
            if changed:
                tau_needed = True
                sig = str(row["graph_signature"])
                if sig not in seen_sig:
                    seen_sig.add(sig)
                    jobs.append({"tag": tag, "fold": 0, "model": "gkt", "reason": "tau_changes_E_sim", "train": True})

    landmarks = [default_tag, mid_tag, open_tag]
    landmark_jobs = []
    for tag in landmarks:
        if _sig(tag) is None:
            continue
        landmark_jobs.append({"tag": tag, "folds": [0, 1, 2], "model": "gkt", "reason": "three_fold_landmark"})
        landmark_jobs.append({"tag": tag, "folds": [0], "model": "gikt", "reason": "gikt_landmark_fold0"})

    return {
        "unique_fold0": unique_ids.to_dict(orient="records"),
        "always_tags": always,
        "k_lift_recommended": k_lift_needed,
        "tau_recommended": tau_needed,
        "fold0_gkt_jobs": jobs,
        "conditional_landmarks": landmark_jobs,
        "note": "Phase B only. Do not train until fold-0 unique list is reviewed.",
    }


def run_phase_a(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    cfg = load_yaml(cfg_path)
    dataset = str(cfg["dataset"])
    processed = Path(cfg.get("processed_path", f"data/processed/{dataset}.parquet"))
    if not processed.exists():
        raise SystemExit(f"Missing processed log: {processed}")

    data_root = Path(args.data_root) if args.data_root else ROOT / "data" / "processed" / dataset / "m4"
    out_root = Path(args.out_root) if args.out_root else ROOT / "results" / "m4"
    cache_dir = out_root / "cache"
    assert_isolated_data_root(data_root, dataset)
    out_root.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    cells = phase_a_cells()
    logger.info("Phase A cells: %s", ", ".join(c.tag for c in cells))
    if args.dry_run:
        print(json.dumps([asdict(c) | {"tag": c.tag} for c in cells], indent=2))
        return 0
    if args.write_overlays:
        write_overlays(cells, Path(args.overlay_dir), cfg)
    write_overlays(cells, out_root / "overlays", cfg)

    df = load_interactions(processed)
    graph_cfg = cfg.get("graph", {})
    sim_method = str(graph_cfg.get("e_sim_method", "jaccard"))

    full_counts = _load_or_build_counts(cache_dir / "transitions_full_log.parquet", df, "full_log")
    full_q = _load_or_build_q(cache_dir / "q_full_log.parquet", df, train_only=False)

    rows: list[dict] = []
    for fold, split_seed, splits in _iter_folds(df, cfg, args.fold_idx):
        train = splits["train"].copy()
        train["split"] = "train"
        train["fold"] = fold
        held = pd.concat([splits["valid"], splits["test"]], ignore_index=True)
        fold_counts = _load_or_build_counts(
            cache_dir / f"transitions_train_fold{fold}.parquet", train, f"train fold {fold}"
        )
        q_train = _load_or_build_q(cache_dir / f"q_train_fold{fold}.parquet", train, train_only=True)
        train_pair_counts = _pair_count_map(train)
        held_pair_counts = _pair_count_map(held)

        sim_cache: dict[float, tuple[pd.DataFrame, pd.DataFrame]] = {}
        for cell in cells:
            pre_to, stages_to = filter_prerequisite_counts(
                fold_counts,
                max_edges=cell.K,
                top_k_per_node=cell.k,
                support_quantile=cell.q,
                source_tag="train_temporal_precedence",
            )
            pre_fl, stages_fl = filter_prerequisite_counts(
                full_counts,
                max_edges=cell.K,
                top_k_per_node=cell.k,
                support_quantile=cell.q,
                source_tag="full_log_temporal_precedence",
            )
            if cell.tau not in sim_cache:
                sim_to = infer_similarity_edges_from_q_matrix(
                    q_train, method=sim_method, threshold=cell.tau, source_prefix="train"
                )
                sim_fl = infer_similarity_edges_from_q_matrix(
                    full_q, method=sim_method, threshold=cell.tau, source_prefix="full_log"
                )
                sim_cache[cell.tau] = (sim_to, sim_fl)
            sim_to, sim_fl = sim_cache[cell.tau]

            cell_path = _cell_dir(data_root, cell)
            dump_csv(pre_to, cell_path / f"fold_{fold}" / "e_pre_train_only.csv")
            dump_csv(sim_to, cell_path / f"fold_{fold}" / "e_sim_train_only.csv")
            if fold == (args.fold_idx if args.fold_idx is not None else 0):
                dump_csv(pre_fl, cell_path / "full_log" / "e_pre.csv")
                dump_csv(sim_fl, cell_path / "full_log" / "e_sim.csv")

            shares = compute_edge_heldout_shares(
                pre_to,
                sim_to,
                train,
                held,
                q_train,
                train_counts=train_pair_counts,
                held_counts=held_pair_counts,
            )
            share_summary = summarize_edge_heldout_shares(shares)
            to_dir = _edge_pairs(pre_to, directed=True)
            fl_dir = _edge_pairs(pre_fl, directed=True)
            row = {
                "dataset": dataset,
                "fold": int(fold),
                "split_seed": int(split_seed),
                "cell_tag": cell.tag,
                "arm": cell.arm,
                "q": cell.q,
                "k": cell.k,
                "K": cell.K,
                "tau": cell.tau,
                "n_pre_to": int(len(pre_to)),
                "n_pre_fl": int(len(pre_fl)),
                "n_sim_to": int(len(sim_to)),
                "n_sim_fl": int(len(sim_fl)),
                "n_pre_fl_minus_to": int(len(fl_dir - to_dir)),
                "jaccard_pre_directed": jaccard(to_dir, fl_dir),
                "jaccard_pre_undirected": jaccard(
                    _edge_pairs(pre_to, directed=False), _edge_pairs(pre_fl, directed=False)
                ),
                "jaccard_sim_undirected": jaccard(
                    _edge_pairs(sim_to, directed=False), _edge_pairs(sim_fl, directed=False)
                ),
                "share_p90": share_summary["share_p90"],
                "frac_share_gt_50": share_summary["frac_share_gt_50"],
                "n_share_edges": share_summary["n_edges"],
                **stages_to.as_dict("_to"),
                **stages_fl.as_dict("_fl"),
                "sig_pre_to": edge_signature(pre_to),
                "sig_pre_fl": edge_signature(pre_fl),
                "sig_sim_to": edge_signature(sim_to),
                "sig_sim_fl": edge_signature(sim_fl),
            }
            row["graph_signature"] = "|".join(
                [row["sig_pre_to"], row["sig_pre_fl"], row["sig_sim_to"], row["sig_sim_fl"]]
            )
            rows.append(row)
            logger.info(
                "cell=%s fold=%s |E_pre to/fl=%s/%s leak=%s bind_to=%s p90=%.3f",
                cell.tag,
                fold,
                row["n_pre_to"],
                row["n_pre_fl"],
                row["n_pre_fl_minus_to"],
                row["primary_bind_to"],
                row["share_p90"],
            )
        del splits, train, held
    census = pd.DataFrame(rows)
    census_path = out_root / "builder_census.csv"
    if census_path.exists():
        previous = pd.read_csv(census_path)
        census = pd.concat([previous, census], ignore_index=True)
        census = census.drop_duplicates(subset=["dataset", "fold", "cell_tag"], keep="last")
        census = census.sort_values(["fold", "q", "k", "K", "tau"]).reset_index(drop=True)
    dump_csv(census, census_path)
    jobs = _phase_b_jobs(census)
    jobs_path = out_root / "phase_b_jobs.json"
    jobs_path.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    unique_path = out_root / "unique_signatures.json"
    unique_path.write_text(json.dumps(jobs["unique_fold0"], indent=2), encoding="utf-8")
    logger.info("Wrote %s (%s rows)", census_path, len(census))
    logger.info("Wrote %s and %s", jobs_path, unique_path)
    train_jobs = [j for j in jobs["fold0_gkt_jobs"] if j.get("train")]
    print(f"Phase A done. Unique fold-0 signatures: {len(jobs['unique_fold0'])}")
    print(f"Recommended fold-0 GKT train jobs: {len(train_jobs)}")
    for job in train_jobs:
        print(f"  - {job['tag']}  ({job['reason']})")
    print(f"k_lift_recommended={jobs['k_lift_recommended']}  tau_recommended={jobs['tau_recommended']}")
    _write_census_preview(census, out_root / "census_fold0_preview.md")
    return 0


def _write_census_preview(census: pd.DataFrame, path: Path) -> None:
    fold0 = census[census["fold"] == 0].copy()
    if fold0.empty:
        return
    cols = [
        "cell_tag",
        "n_pre_to",
        "n_pre_fl_minus_to",
        "primary_bind_to",
        "n_sim_to",
        "share_p90",
        "graph_signature",
    ]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = []
    for rec in fold0[cols].to_dict(orient="records"):
        body.append("| " + " | ".join(str(rec[c]) for c in cols) + " |")
    lines = ["# M4 Phase A fold-0 preview", "", header, sep, *body, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", path)


def _resolve_phase_b_tags(args: argparse.Namespace, jobs: dict) -> list[str]:
    if args.cells == "recommended":
        return [j["tag"] for j in jobs.get("fold0_gkt_jobs", []) if j.get("train")]
    if args.cells == "default":
        return [FilterCell(DEFAULT_Q, DEFAULT_K, DEFAULT_K_GLOBAL, DEFAULT_TAU, "qk").tag]
    return [t.strip() for t in args.cells.split(",") if t.strip()]


def run_phase_b(args: argparse.Namespace) -> int:
    out_root = Path(args.out_root) if args.out_root else ROOT / "results" / "m4"
    jobs_path = out_root / "phase_b_jobs.json"
    if not jobs_path.exists():
        raise SystemExit(f"Missing {jobs_path}; run --phase a first.")
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    cfg = load_yaml(Path(args.config))
    dataset = str(cfg["dataset"])
    data_root = Path(args.data_root) if args.data_root else ROOT / "data" / "processed" / dataset / "m4"
    assert_isolated_data_root(data_root, dataset)
    tags = _resolve_phase_b_tags(args, jobs)
    if not tags:
        raise SystemExit("No Phase B cells selected.")
    python = args.python or sys.executable
    commands: list[list[str]] = []
    for tag in tags:
        graph_root = data_root / tag
        overlay = out_root / "overlays" / f"{tag}.yaml"
        if not (graph_root / "fold_0" / "e_pre_train_only.csv").exists():
            raise SystemExit(f"Missing isolated train-only graph: {graph_root / 'fold_0' / 'e_pre_train_only.csv'}")
        if not overlay.exists():
            raise SystemExit(f"Missing overlay {overlay}")
        isolate = f"m4_{tag}"
        seed = int(getattr(args, "seed", 42))
        split_base = args.split_base_seed
        if seed != 42 and split_base is None:
            split_base = 42
        if seed != 42:
            isolate = f"m4_{tag}_seed{seed}"
        cmd = [
            python,
            "-m",
            "src.baseline_runner",
            "--config",
            str(overlay),
            "--models",
            args.model,
            "--skip-cold-start",
            "--no-ablation-trained-head",
            "--graph-root",
            str(graph_root),
            "--isolated-results",
            isolate,
            "--seed",
            str(seed),
            "--log-level",
            str(args.log_level),
        ]
        if split_base is not None:
            cmd.extend(["--split-base-seed", str(split_base)])
        fold_idx = 0 if args.fold_idx is None else args.fold_idx
        if fold_idx >= 0:
            cmd.extend(["--fold-idx", str(fold_idx)])
        commands.append(cmd)
    if args.dry_run:
        for cmd in commands:
            print(" ".join(cmd))
        return 0
    for cmd in commands:
        logger.info("Phase B: %s", " ".join(cmd))
        subprocess.run(cmd, cwd=str(ROOT), check=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "xes3g5m.yaml")
    parser.add_argument("--phase", choices=["a", "b"], default="a")
    parser.add_argument("--fold-idx", type=int, default=None, help="Restrict to one fold (default: all in A; all in B if omitted).")
    parser.add_argument("--data-root", type=Path, default=None, help="Isolated graph root (must contain /m4/).")
    parser.add_argument("--out-root", type=Path, default=None, help="Census/JSON output root.")
    parser.add_argument("--dry-run", action="store_true", help="Print the unique cell grid / Phase B commands and exit.")
    parser.add_argument("--write-overlays", action="store_true", help="Also write YAML under --overlay-dir.")
    parser.add_argument(
        "--overlay-dir",
        type=Path,
        default=ROOT / "configs" / "experiments" / "m4",
    )
    parser.add_argument(
        "--cells",
        default="default",
        help="Phase B: 'default', 'recommended', or comma-separated cell tags.",
    )
    parser.add_argument("--model", default="gkt", help="Phase B backbone (default gkt).")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Experiment seed forwarded to baseline_runner. For a noise-floor replicate "
        "use a different value and keep --split-base-seed at 42.",
    )
    parser.add_argument(
        "--split-base-seed",
        type=int,
        default=None,
        help="Learner-split seed forwarded to baseline_runner. Defaults to 42 when "
        "--seed is not 42, so a replicate does not silently change the split.",
    )
    parser.add_argument("--python", default=None, help="Interpreter for Phase B subprocesses.")
    parser.add_argument("--log-level", default="INFO")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper()), format="%(levelname)s %(message)s")
    if args.phase == "a":
        return run_phase_a(args)
    if args.phase == "b":
        return run_phase_b(args)
    raise SystemExit(f"Unknown phase {args.phase}")


if __name__ == "__main__":
    raise SystemExit(main())
