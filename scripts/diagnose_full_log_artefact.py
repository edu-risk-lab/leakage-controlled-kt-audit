"""Attribute the full-log replicate gap (revision plan section 2.5).

The isolated m4 rerun and the primary ablation disagree on full-log AUC by
~1.2e-3 while their train-only arms agree to 5e-5. An arm-asymmetric gap is not
training noise, so the two full-log graph artefacts are the prime suspect:

  primary   data/processed/<ds>/full_log/e_pre.csv      (scripts/export_full_log_graph.py)
  isolated  data/processed/<ds>/m4/<cell>/full_log/e_pre.csv  (scripts/run_m4_qk_sweep.py)

Both nominally use the published filter, and ``--graph-root`` redirects the
full-log branch too, so the trained runs really did read different files. The
on-disk primary artefact is never invalidated when ``configs/<ds>.yaml`` changes,
so it can predate the current filter. This script tests that directly: it
rebuilds the full-log graph from the current config, diffs it against both
artefacts, and — when they differ — searches a filter grid for the parameters
that do reproduce the on-disk file.

Requires ``data/processed``, so it runs on the GPU/server checkout, not the
writing machine.

Usage:
    python scripts/diagnose_full_log_artefact.py --config configs/xes3g5m.yaml
    python scripts/diagnose_full_log_artefact.py --config configs/xes3g5m.yaml --no-grid
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.graph_builder import (  # noqa: E402
    UNLIMITED_CAP,
    build_q_matrix_from_interactions,
    count_kc_transitions,
    filter_prerequisite_counts,
    infer_similarity_edges_from_q_matrix,
)
from src.io_utils import load_interactions, load_yaml  # noqa: E402

logger = logging.getLogger("diagnose_full_log")

Q_GRID = (0.5, 0.8, 0.9, 0.95)
K_GRID = (5, 10, 20, UNLIMITED_CAP)
KMAX_GRID = (1000, 5000, UNLIMITED_CAP)
TAU_GRID = (0.05, 0.1, 0.2)


def edge_set(frame: pd.DataFrame) -> set[tuple[int, int]]:
    return set(zip(frame["src_kc"].astype(int), frame["dst_kc"].astype(int), strict=True))


def edge_digest(edges: set[tuple[int, int]]) -> str:
    payload = ";".join(f"{s}>{d}" for s, d in sorted(edges))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def compare(name_a: str, a: set[tuple[int, int]], name_b: str, b: set[tuple[int, int]]) -> dict:
    union = a | b
    return {
        "left": name_a,
        "right": name_b,
        "n_left": len(a),
        "n_right": len(b),
        "n_only_left": len(a - b),
        "n_only_right": len(b - a),
        "jaccard": len(a & b) / len(union) if union else 1.0,
        "identical": a == b,
        "digest_left": edge_digest(a),
        "digest_right": edge_digest(b),
    }


def find_matching_filter(counts: pd.DataFrame, target: set[tuple[int, int]]) -> list[dict]:
    """Filter settings whose output reproduces the on-disk artefact exactly."""
    hits = []
    for q in Q_GRID:
        for k in K_GRID:
            for kmax in KMAX_GRID:
                built, _stages = filter_prerequisite_counts(
                    counts,
                    max_edges=kmax,
                    top_k_per_node=k,
                    support_quantile=q,
                    source_tag="full_log_temporal_precedence",
                )
                if edge_set(built) == target:
                    hits.append({"q": q, "k": k, "K": kmax, "n_edges": len(built)})
    return hits


def find_matching_tau(q_matrix: pd.DataFrame, method: str, target: set[tuple[int, int]]) -> list[dict]:
    hits = []
    for tau in TAU_GRID:
        built = infer_similarity_edges_from_q_matrix(
            q_matrix, method=method, threshold=tau, source_prefix="full_log"
        )
        if edge_set(built) == target:
            hits.append({"tau": tau, "n_edges": len(built)})
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cell", default="q0.95_k5_K5000_tau0.1", help="m4 cell to compare against")
    parser.add_argument("--no-grid", action="store_true", help="skip the filter grid search")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "tables" / "full_log_artefact_diag.csv")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s %(message)s")

    cfg = load_yaml(args.config)
    dataset = cfg["dataset"]
    graph_cfg = cfg.get("graph", {})
    q_cfg = float(graph_cfg.get("e_pre_support_quantile", 0.90))
    k_cfg = int(graph_cfg.get("e_pre_top_k_per_node", 10))
    kmax_cfg = int(graph_cfg.get("e_pre_max_edges", 5000))
    tau_cfg = float(graph_cfg.get("e_sim_threshold", 0.1))
    sim_method = str(graph_cfg.get("e_sim_method", "jaccard"))
    logger.info("config filter q=%s k=%s K=%s tau=%s", q_cfg, k_cfg, kmax_cfg, tau_cfg)

    processed = Path(cfg.get("processed_path", f"data/processed/{dataset}.parquet"))
    df = load_interactions(processed)
    counts = count_kc_transitions(df)
    q_matrix = build_q_matrix_from_interactions(df)

    rebuilt_pre, _ = filter_prerequisite_counts(
        counts,
        max_edges=kmax_cfg,
        top_k_per_node=k_cfg,
        support_quantile=q_cfg,
        source_tag="full_log_temporal_precedence",
    )
    rebuilt_sim = infer_similarity_edges_from_q_matrix(
        q_matrix, method=sim_method, threshold=tau_cfg, source_prefix="full_log"
    )

    primary_dir = Path("data/processed") / dataset / "full_log"
    isolated_dir = Path("data/processed") / dataset / "m4" / args.cell / "full_log"
    artefacts = {
        "primary_on_disk": primary_dir / "e_pre.csv",
        "isolated_m4": isolated_dir / "e_pre.csv",
    }

    rows: list[dict] = []
    rebuilt_set = edge_set(rebuilt_pre)
    logger.info("rebuilt full-log E_pre from current config: %d edges", len(rebuilt_set))

    loaded: dict[str, set[tuple[int, int]]] = {}
    for name, path in artefacts.items():
        if not path.exists():
            logger.warning("missing artefact %s", path)
            continue
        loaded[name] = edge_set(pd.read_csv(path))
        rows.append(compare("rebuilt_from_config", rebuilt_set, name, loaded[name]))

    if len(loaded) == 2:
        rows.append(compare("primary_on_disk", loaded["primary_on_disk"], "isolated_m4", loaded["isolated_m4"]))

    # The train-only arms agreed to 5e-5 across the two runs. If their graphs are
    # also identical, training is effectively deterministic, and an identical
    # full-log graph can no longer explain the full-log gap.
    to_primary = Path("data/processed") / dataset / "fold_0" / "e_pre_train_only.csv"
    to_isolated = Path("data/processed") / dataset / "m4" / args.cell / "fold_0" / "e_pre_train_only.csv"
    if to_primary.exists() and to_isolated.exists():
        rows.append(compare("train_only_primary", edge_set(pd.read_csv(to_primary)),
                            "train_only_isolated", edge_set(pd.read_csv(to_isolated))))

    sim_primary = primary_dir / "e_sim.csv"
    if sim_primary.exists():
        rows.append(compare("rebuilt_sim_from_config", edge_set(rebuilt_sim),
                            "primary_sim_on_disk", edge_set(pd.read_csv(sim_primary))))

    report = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.out, index=False)
    logger.info("wrote %s", args.out)

    print("\nArtefact comparison")
    print(report[["left", "right", "n_left", "n_right", "n_only_left", "n_only_right",
                  "jaccard", "identical"]].to_string(index=False))

    stale = "primary_on_disk" in loaded and loaded["primary_on_disk"] != rebuilt_set
    if stale and not args.no_grid:
        print("\nPrimary artefact does not match the current config. Searching filter grid...")
        hits = find_matching_filter(counts, loaded["primary_on_disk"])
        if hits:
            print("On-disk primary E_pre was built with:")
            for h in hits:
                k_lbl = "inf" if h["k"] >= UNLIMITED_CAP else h["k"]
                kmax_lbl = "inf" if h["K"] >= UNLIMITED_CAP else h["K"]
                print(f"  q={h['q']} k={k_lbl} K={kmax_lbl} -> {h['n_edges']} edges")
            print("VERDICT: stale artefact. Regenerate with scripts/export_full_log_graph.py "
                  "and rerun the full-log ablation arm before quoting any dAUC.")
        else:
            print("No grid cell reproduces the on-disk artefact; the gap is not a filter-parameter "
                  "mismatch. Check the preprocessed parquet and the transition-counting path next.")
        if sim_primary.exists():
            tau_hits = find_matching_tau(q_matrix, sim_method, edge_set(pd.read_csv(sim_primary)))
            if tau_hits:
                print("On-disk primary E_sim matches tau in:", [h["tau"] for h in tau_hits])
    elif not stale:
        print("\nVERDICT: primary artefact matches the current config. "
              "Look elsewhere for the full-log gap (training nondeterminism, cache reuse).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
