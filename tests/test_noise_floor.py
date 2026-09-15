"""Unit tests for the replicate-based training noise floor."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load_noise_mod():
    path = ROOT / "scripts" / "noise_floor.py"
    spec = importlib.util.spec_from_file_location("noise_floor", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_noise = _load_noise_mod()
replicate_groups = _noise.replicate_groups
summarise = _noise.summarise
vintage_comparison = _noise.vintage_comparison
load_sweep = _noise.load_sweep
pairwise_null = _noise.pairwise_null
tail_fraction = _noise.tail_fraction


def _row(*, dataset="assist2012", split_seed=42, n_edges=413, auc=0.96, source="a.csv") -> dict:
    return {
        "dataset": dataset,
        "model": "gkt",
        "fold": 0,
        "split_seed": split_seed,
        "operator": "none",
        "p": 0.0,
        "n_edges_orig": n_edges,
        "num_c": 265,
        "auc": auc,
        "source": source,
    }


def test_same_split_and_graph_forms_a_replicate_group() -> None:
    df = pd.DataFrame(
        [
            _row(auc=0.9622128176198464, source="seed17.csv"),
            _row(auc=0.9623257796250674, source="seed42.csv"),
            _row(auc=0.9623886977887952, source="seed1234.csv"),
        ]
    )
    groups = replicate_groups(df)
    assert len(groups) == 1
    assert int(groups.loc[0, "n_replicates"]) == 3
    assert abs(float(groups.loc[0, "auc_range"]) - 1.7588e-4) < 1e-8


def test_differing_split_or_graph_is_not_a_replicate() -> None:
    df = pd.DataFrame(
        [
            _row(dataset="xes3g5m", split_seed=42, n_edges=1162, auc=0.8348),
            _row(dataset="xes3g5m", split_seed=17, n_edges=1163, auc=0.8345),
            _row(dataset="xes3g5m", split_seed=1234, n_edges=1408, auc=0.8361),
        ]
    )
    assert replicate_groups(df).empty


def test_singleton_groups_are_dropped() -> None:
    df = pd.DataFrame([_row(auc=0.96)])
    assert replicate_groups(df).empty


def test_summary_reports_worst_group_as_sigma() -> None:
    df = pd.DataFrame(
        [
            _row(auc=0.9600, source="a.csv"),
            _row(auc=0.9601, source="b.csv"),
            {**_row(split_seed=43, n_edges=416, auc=0.9700), "source": "a.csv"},
            {**_row(split_seed=43, n_edges=416, auc=0.9705), "source": "b.csv"},
        ]
    )
    summary = summarise(replicate_groups(df))
    assert len(summary) == 1
    assert abs(float(summary.loc[0, "sigma_range_max"]) - 5e-4) < 1e-9
    assert int(summary.loc[0, "n_groups"]) == 2


def test_load_sweep_deduplicates_repeated_exports(tmp_path: Path) -> None:
    frame = pd.DataFrame([_row(auc=0.96)]).drop(columns=["source"])
    frame.to_csv(tmp_path / "ddr_downstream_gkt_seed42.csv", index=False)
    frame.to_csv(tmp_path / "ddr_downstream_gkt_seed42_part1.csv", index=False)
    assert len(load_sweep(tmp_path)) == 1


def test_vintage_asymmetry_flags_localised_discrepancy(tmp_path: Path) -> None:
    path = tmp_path / "replicate.csv"
    pd.DataFrame(
        [
            {
                "dataset": "xes3g5m",
                "model": "gkt",
                "fold": 0,
                "train_only_gap": 5.325350022156172e-05,
                "full_log_gap": 0.0011767257922261631,
            }
        ]
    ).to_csv(path, index=False)
    out = vintage_comparison(path)
    assert out is not None
    assert float(out.loc[0, "asymmetry"]) > 20.0


def test_vintage_comparison_absent_file_is_tolerated(tmp_path: Path) -> None:
    assert vintage_comparison(tmp_path / "missing.csv") is None


def test_pairwise_null_enumerates_all_pairs_within_group() -> None:
    df = pd.DataFrame(
        [
            _row(auc=0.9600, source="a.csv"),
            _row(auc=0.9602, source="b.csv"),
            _row(auc=0.9605, source="c.csv"),
        ]
    )
    null = pairwise_null(df)
    assert len(null) == 3
    assert sorted(round(v, 6) for v in null) == [0.0002, 0.0003, 0.0005]


def test_pairwise_null_does_not_cross_groups() -> None:
    df = pd.DataFrame(
        [
            _row(auc=0.9600, source="a.csv"),
            _row(auc=0.9602, source="b.csv"),
            {**_row(split_seed=43, n_edges=416, auc=0.5000), "source": "a.csv"},
            {**_row(split_seed=43, n_edges=416, auc=0.5001), "source": "b.csv"},
        ]
    )
    null = pairwise_null(df)
    assert len(null) == 2
    assert max(null) < 1e-3  # no 0.46 cross-group difference leaked in


def test_tail_fraction_brackets_the_null() -> None:
    null = pd.Series([1e-4, 2e-4, 3e-4, 4e-4])
    assert tail_fraction(null, 5e-4) == 0.0
    assert tail_fraction(null, 0.0) == 1.0
    assert tail_fraction(null, 3e-4) == 0.5


def test_tail_fraction_on_empty_null_is_nan() -> None:
    assert pd.isna(tail_fraction(pd.Series([], dtype=float), 1e-3))
