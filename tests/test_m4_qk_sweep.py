from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

from src.graph_builder import (
    UNLIMITED_CAP,
    count_kc_transitions,
    filter_prerequisite_counts,
    infer_prerequisites_from_interactions,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_m4():
    path = ROOT / "scripts" / "run_m4_qk_sweep.py"
    spec = importlib.util.spec_from_file_location("run_m4_qk_sweep", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


m4 = _load_m4()


def _toy_interactions() -> pd.DataFrame:
    rows = []
    # User 0: A->B many times (high support), B->C once.
    t = 0
    for _ in range(20):
        rows.append({"user_id": 0, "item_id": 1, "kc_id": 1, "timestamp": t, "correct": 1})
        t += 1
        rows.append({"user_id": 0, "item_id": 2, "kc_id": 2, "timestamp": t, "correct": 1})
        t += 1
    rows.append({"user_id": 0, "item_id": 3, "kc_id": 2, "timestamp": t, "correct": 1})
    rows.append({"user_id": 0, "item_id": 4, "kc_id": 3, "timestamp": t + 1, "correct": 0})
    # User 1: C->A repeated (medium support).
    t = 0
    for _ in range(8):
        rows.append({"user_id": 1, "item_id": 5, "kc_id": 3, "timestamp": t, "correct": 1})
        t += 1
        rows.append({"user_id": 1, "item_id": 1, "kc_id": 1, "timestamp": t, "correct": 0})
        t += 1
    return pd.DataFrame(rows)


def test_phase_a_grid_has_sixteen_unique_cells():
    cells = m4.phase_a_cells()
    keys = {(c.q, c.k, c.K, c.tau) for c in cells}
    assert len(cells) == 16
    assert len(keys) == 16
    assert (0.95, 5, 5000, 0.10) in keys
    assert (0.50, 5, UNLIMITED_CAP, 0.10) in keys
    assert (0.50, UNLIMITED_CAP, UNLIMITED_CAP, 0.10) in keys
    assert (0.95, 5, 5000, 0.05) in keys
    tags = [c.tag for c in cells]
    assert len(tags) == len(set(tags))
    assert "inf" in next(c.tag for c in cells if c.K >= UNLIMITED_CAP)


def test_unlimited_cap_is_not_zero():
    assert UNLIMITED_CAP >= 10**9
    counts = pd.DataFrame({"src_kc": [1], "dst_kc": [2], "support": [4]})
    with pytest.raises(ValueError, match="positive"):
        filter_prerequisite_counts(counts, max_edges=0, top_k_per_node=5, support_quantile=0.5)


def test_filter_matches_infer_prerequisites():
    interactions = _toy_interactions()
    q = interactions[["item_id", "kc_id"]].drop_duplicates()
    direct = infer_prerequisites_from_interactions(
        interactions, q, max_edges=10, top_k_per_node=2, support_quantile=0.5
    )
    counts = count_kc_transitions(interactions)
    filtered, stages = filter_prerequisite_counts(
        counts, max_edges=10, top_k_per_node=2, support_quantile=0.5
    )
    pd.testing.assert_frame_equal(direct.reset_index(drop=True), filtered.reset_index(drop=True))
    assert stages.n_after_K == len(filtered)
    assert stages.primary_bind in {"q", "k", "K", "none"}


def test_k_and_K_binding_flags():
    counts = pd.DataFrame(
        {
            "src_kc": [1, 1, 1, 2],
            "dst_kc": [2, 3, 4, 1],
            "support": [20, 19, 18, 17],
        }
    )
    _edges, stages_k = filter_prerequisite_counts(
        counts, max_edges=UNLIMITED_CAP, top_k_per_node=1, support_quantile=0.0
    )
    assert stages_k.k_binds
    assert stages_k.primary_bind == "k"
    _edges, stages_K = filter_prerequisite_counts(
        counts, max_edges=1, top_k_per_node=10, support_quantile=0.0
    )
    assert stages_K.K_binds
    assert stages_K.primary_bind == "K"


def test_isolated_root_requires_m4_segment(tmp_path: Path):
    with pytest.raises(ValueError, match="m4"):
        m4.assert_isolated_data_root(tmp_path / "xes3g5m", "xes3g5m")
    ok = tmp_path / "processed" / "xes3g5m" / "m4"
    ok.mkdir(parents=True)
    m4.assert_isolated_data_root(ok, "xes3g5m")


def test_edge_signature_stable_under_row_shuffle():
    a = pd.DataFrame({"src_kc": [2, 1], "dst_kc": [3, 4], "weight": [0.2, 1.0]})
    b = a.iloc[::-1].reset_index(drop=True)
    assert m4.edge_signature(a) == m4.edge_signature(b)
    empty = pd.DataFrame(columns=["src_kc", "dst_kc"])
    assert m4.edge_signature(empty) == m4.edge_signature(pd.DataFrame(columns=["src_kc", "dst_kc"]))


def test_jaccard_identical_and_disjoint():
    assert m4.jaccard({(1, 2)}, {(1, 2)}) == 1.0
    assert m4.jaccard({(1, 2)}, {(3, 4)}) == 0.0
    assert m4.jaccard(set(), set()) == 1.0


def test_graph_root_override_does_not_use_primary_paths(tmp_path: Path):
    from src.baseline_runner import _GRAPH_ROOT, _full_log_graph_paths, _graph_data_root, _protocol_edge_csvs

    token = _GRAPH_ROOT.set(tmp_path / "m4cell")
    try:
        assert _graph_data_root("xes3g5m") == tmp_path / "m4cell"
        pre, sim = _protocol_edge_csvs("xes3g5m", 0, "train_only")
        assert pre == tmp_path / "m4cell" / "fold_0" / "e_pre_train_only.csv"
        fl_pre, _fl_sim = _full_log_graph_paths("xes3g5m")
        assert fl_pre == tmp_path / "m4cell" / "full_log" / "e_pre.csv"
        assert "xes3g5m" not in fl_pre.parts or "m4cell" in fl_pre.parts
    finally:
        _GRAPH_ROOT.reset(token)
    assert _graph_data_root("xes3g5m") == Path("data/processed") / "xes3g5m"
