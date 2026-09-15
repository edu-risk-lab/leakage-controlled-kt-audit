"""Unit tests for DDR→AUC-drop OLS slope and fold-clustered bootstrap CIs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load_slope_mod():
    path = ROOT / "scripts" / "ddr_slope_ci.py"
    spec = importlib.util.spec_from_file_location("ddr_slope_ci", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_slope = _load_slope_mod()
cluster_bootstrap_slope = _slope.cluster_bootstrap_slope
ols_intercept_slope = _slope.ols_intercept_slope
subset = _slope.subset


def test_ols_recovers_known_slope() -> None:
    rng = np.random.default_rng(0)
    x = np.linspace(0.05, 0.6, 40)
    y = 0.08 * x + 0.001 + rng.normal(0.0, 0.0005, size=x.size)
    intercept, slope = ols_intercept_slope(x, y)
    assert abs(slope - 0.08) < 0.01
    assert abs(intercept - 0.001) < 0.005


def test_high_r_tiny_slope_is_scale_free() -> None:
    x = np.linspace(0.1, 1.0, 30)
    y = 0.002 * x  # tiny practical effect, still r = 1
    _a, slope = ols_intercept_slope(x, y)
    r = float(np.corrcoef(x, y)[0, 1])
    assert r > 0.99
    assert abs(slope - 0.002) < 1e-9


def test_cluster_bootstrap_ci_covers_true_slope() -> None:
    rng = np.random.default_rng(1)
    rows = []
    true_slope = 0.09
    for cluster in range(9):
        shift = rng.normal(0.0, 0.004)
        x = rng.uniform(0.05, 0.5, size=6)
        y = true_slope * x + shift + rng.normal(0.0, 0.002, size=x.size)
        for xi, yi in zip(x, y):
            rows.append({"cluster": cluster, "ddr": xi, "auc_drop": yi})
    frame = pd.DataFrame(rows)
    point, lo, hi = cluster_bootstrap_slope(frame, n_boot=400, seed=7)
    assert lo <= true_slope <= hi
    assert lo < point < hi


def test_subset_drops_none_and_anchors_on_core() -> None:
    df = pd.DataFrame(
        {
            "dataset": ["xes3g5m"] * 6,
            "model": ["gkt"] * 6,
            "fold": [0, 0, 0, 0, 0, 0],
            "split_seed": [42] * 6,
            "operator": [
                "none",
                "edge_drop",
                "node_drop",
                "prereq_preserve",
                "attr_mask",
                "edge_drop",
            ],
            "p": [0.0, 0.1, 0.2, 0.3, 0.1, 0.9],
            "ddr": [0.0, 0.1, 0.2, 0.15, 0.0, 0.9],
            "auc_drop": [0.0, 0.01, 0.02, 0.008, 0.0, 0.08],
        }
    )
    core = subset(df, dataset="xes3g5m", model="gkt", p_max=0.3)
    assert set(core["operator"]) == {"edge_drop", "node_drop", "prereq_preserve"}
    assert len(core) == 3
    full = subset(df, dataset="xes3g5m", model="gkt", p_max=None)
    assert len(full) == 4
