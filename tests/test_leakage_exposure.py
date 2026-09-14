"""Unit tests for the leakage exposure bound (census delta x backbone slope)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / "scripts" / "leakage_exposure.py"
    spec = importlib.util.spec_from_file_location("leakage_exposure", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
build_exposure = _mod.build_exposure
effective_delta = _mod.effective_delta
operator_delta = _mod.operator_delta
load_census = _mod.load_census


def _slopes() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "dataset": ["xes3g5m"],
            "model": ["gkt"],
            "slope": [0.084],
            "slope_ci_lo": [0.079],
            "slope_ci_hi": [0.090],
        }
    ).set_index(["dataset", "model"])[["slope", "slope_ci_lo", "slope_ci_hi"]]


def _census() -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "dataset": ["xes3g5m", "xes3g5m"],
            "fold": [0, 0],
            "split_seed": [42, 42],
            "cell_tag": ["q0.95_k5_K5000_tau0.1", "q0.5_kinf_Kinf_tau0.1"],
            "q": [0.95, 0.5],
            "k": [5, 10**9],
            "K": [5000, 10**9],
            "tau": [0.1, 0.1],
            "n_pre_to": [1162, 17211],
            "n_pre_fl": [1260, 19487],
            "n_pre_fl_minus_to": [103, 2276],
            "primary_bind_to": ["k", "q"],
        }
    )
    frame["delta"] = frame["n_pre_fl_minus_to"] / frame["n_pre_to"]
    return frame


def _observed() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "dataset": ["xes3g5m"],
            "fold": [0],
            "split_seed": [42],
            "model": ["gkt"],
            "cell_tag": ["q0.95_k5_K5000_tau0.1"],
            "auc_train_only": [0.8335910934504894],
            "auc_full_log": [0.8342056988717668],
            "observed_delta_auc": [0.0006146054212774],
        }
    )


def test_delta_is_leak_over_retained_train_only_edges() -> None:
    frame = _census()
    assert frame.loc[0, "delta"] == pytest.approx(103 / 1162, rel=1e-9)
    assert frame.loc[1, "delta"] == pytest.approx(2276 / 17211, rel=1e-9)


def test_bound_holds_on_published_default_cell() -> None:
    out = build_exposure(_census(), _slopes(), _observed())
    row = out[out["cell_tag"] == "q0.95_k5_K5000_tau0.1"].iloc[0]
    assert row["bound"] == pytest.approx(0.084 * 103 / 1162, rel=1e-9)
    assert row["abs_observed"] < row["bound"]
    assert bool(row["bound_holds"])
    # The bound is deliberately conservative; slack is the quantity delta_eff explains.
    assert row["slack_ratio"] > 5.0


def test_untrained_cell_yields_prediction_not_verdict() -> None:
    out = build_exposure(_census(), _slopes(), _observed())
    row = out[out["cell_tag"] == "q0.5_kinf_Kinf_tau0.1"].iloc[0]
    assert pd.isna(row["abs_observed"])
    assert pd.isna(row["bound_holds"])
    assert row["bound"] == pytest.approx(0.084 * 2276 / 17211, rel=1e-9)
    # The open-k cell is predicted to exceed the 0.003 cap claimed in the manuscript.
    assert row["bound"] > 0.003


def test_missing_slope_gives_nan_bound_not_crash() -> None:
    census = _census().assign(dataset="junyi")
    out = build_exposure(census, _slopes(), pd.DataFrame())
    assert out["bound"].isna().all()


def test_effective_delta_discounts_transitively_redundant_leaks(tmp_path: Path) -> None:
    pytest.importorskip("networkx")
    # Train-only chain 1 -> 2 -> 3 plus an isolated 4 -> 5.
    train_only = pd.DataFrame({"src_kc": [1, 2, 4], "dst_kc": [2, 3, 5], "weight": [1.0] * 3})
    # Full log adds 1->3 (redundant: 3 already reachable from 1) and 2->5 (novel).
    full_log = pd.concat(
        [train_only, pd.DataFrame({"src_kc": [1, 2], "dst_kc": [3, 5], "weight": [1.0, 1.0]})],
        ignore_index=True,
    )
    to_csv, fl_csv = tmp_path / "e_pre_train_only.csv", tmp_path / "e_pre.csv"
    train_only.to_csv(to_csv, index=False)
    full_log.to_csv(fl_csv, index=False)

    stats = effective_delta(to_csv, fl_csv)
    assert stats["n_leaked"] == 2
    assert stats["n_leaked_novel"] == 1
    assert stats["novel_share"] == pytest.approx(0.5)
    assert stats["delta_eff"] == pytest.approx(1 / 3)


def test_effective_delta_handles_cyclic_train_only_graph(tmp_path: Path) -> None:
    """m4 cells dump pre-prune edges, so the graph need not be acyclic."""
    pytest.importorskip("networkx")
    train_only = pd.DataFrame({"src_kc": [1, 2, 3], "dst_kc": [2, 3, 1], "weight": [1.0] * 3})
    full_log = pd.concat(
        [train_only, pd.DataFrame({"src_kc": [1, 9], "dst_kc": [3, 8], "weight": [1.0, 1.0]})],
        ignore_index=True,
    )
    to_csv, fl_csv = tmp_path / "e_pre_train_only.csv", tmp_path / "e_pre.csv"
    train_only.to_csv(to_csv, index=False)
    full_log.to_csv(fl_csv, index=False)

    stats = effective_delta(to_csv, fl_csv)
    # 1->3 is redundant inside the cycle; 9->8 touches a node absent train-only.
    assert stats["n_leaked"] == 2
    assert stats["n_leaked_novel"] == 1


def _write_pair(tmp_path: Path, to_df: pd.DataFrame, fl_df: pd.DataFrame) -> tuple[Path, Path]:
    to_csv, fl_csv = tmp_path / "e_pre_train_only.csv", tmp_path / "e_pre.csv"
    to_df.to_csv(to_csv, index=False)
    fl_df.to_csv(fl_csv, index=False)
    return to_csv, fl_csv


def test_operator_delta_is_zero_for_identical_graphs(tmp_path: Path) -> None:
    edges = pd.DataFrame({"src_kc": [1, 1, 2], "dst_kc": [2, 3, 3], "weight": [2.0, 1.0, 5.0]})
    to_csv, fl_csv = _write_pair(tmp_path, edges, edges)
    stats = operator_delta(to_csv, fl_csv)
    assert stats["delta_tv"] == pytest.approx(0.0)
    assert stats["delta_w"] == pytest.approx(0.0)


def test_operator_delta_ignores_pure_rescaling_but_weight_delta_does_not(tmp_path: Path) -> None:
    """Row normalisation is what GKT consumes, so doubling every weight is a no-op for TV."""
    edges = pd.DataFrame({"src_kc": [1, 1], "dst_kc": [2, 3], "weight": [2.0, 1.0]})
    doubled = edges.assign(weight=edges["weight"] * 2)
    to_csv, fl_csv = _write_pair(tmp_path, edges, doubled)
    stats = operator_delta(to_csv, fl_csv)
    assert stats["delta_tv"] == pytest.approx(0.0)
    assert stats["delta_w"] == pytest.approx(1.0)


def test_operator_delta_counts_shifted_mass(tmp_path: Path) -> None:
    # Node 1 moves from all-mass-on-2 to an even split between 2 and 3: TV = 0.5.
    to_df = pd.DataFrame({"src_kc": [1], "dst_kc": [2], "weight": [1.0]})
    fl_df = pd.DataFrame({"src_kc": [1, 1], "dst_kc": [2, 3], "weight": [1.0, 1.0]})
    to_csv, fl_csv = _write_pair(tmp_path, to_df, fl_df)
    stats = operator_delta(to_csv, fl_csv)
    assert stats["n_nodes_union"] == 1
    assert stats["delta_tv"] == pytest.approx(0.5)
    assert stats["delta_w"] == pytest.approx(1.0)


def test_operator_delta_charges_full_tv_for_nodes_absent_train_only(tmp_path: Path) -> None:
    to_df = pd.DataFrame({"src_kc": [1], "dst_kc": [2], "weight": [1.0]})
    fl_df = pd.DataFrame({"src_kc": [1, 7], "dst_kc": [2, 8], "weight": [1.0, 3.0]})
    to_csv, fl_csv = _write_pair(tmp_path, to_df, fl_df)
    stats = operator_delta(to_csv, fl_csv)
    # Node 1 unchanged (TV 0), node 7 is wholly new (TV 1), averaged over 2 nodes.
    assert stats["delta_tv"] == pytest.approx(0.5)


def test_real_census_default_cell_matches_manuscript() -> None:
    census_path = ROOT / "results" / "m4" / "builder_census.csv"
    if not census_path.exists():
        pytest.skip("census artefact not present")
    frame = load_census(census_path)
    row = frame[(frame["cell_tag"] == "q0.95_k5_K5000_tau0.1") & (frame["fold"] == 0)].iloc[0]
    assert int(row["n_pre_to"]) == 1162
    assert int(row["n_pre_fl_minus_to"]) == 103
