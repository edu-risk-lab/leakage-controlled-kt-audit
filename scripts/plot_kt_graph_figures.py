"""Generate schematic KT graph figures for the paper (works without raw data)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

OUT = Path("results/figures")
OUT.mkdir(parents=True, exist_ok=True)

# Toy prerequisite chains per benchmark (illustrative topology, not full graphs).
SPECS: dict[str, list[tuple[str, str]]] = {
    "junyi": [
        ("addition_1", "number_line"),
        ("addition_2", "addition_1"),
        ("fractions_1", "addition_2"),
        ("equiv_frac", "fractions_1"),
        ("linear_eq_3", "equiv_frac"),
        ("linear_eq_4", "linear_eq_3"),
    ],
    "assist2012": [
        ("KC_A", "KC_B"),
        ("KC_B", "KC_C"),
        ("KC_C", "KC_D"),
        ("KC_D", "KC_E"),
        ("KC_E", "KC_F"),
    ],
    "xes3g5m": [
        ("algebra_1", "arithmetic"),
        ("geometry_1", "algebra_1"),
        ("trig_1", "geometry_1"),
        ("calc_1", "trig_1"),
        ("stats_1", "algebra_1"),
    ],
}


def _draw(edges: list[tuple[str, str]], title: str, path: Path) -> None:
    g = nx.DiGraph()
    g.add_edges_from(edges)
    pos = nx.spring_layout(g, seed=42, k=1.4)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    nx.draw_networkx_nodes(g, pos, node_color="#4C72B0", node_size=520, ax=ax)
    nx.draw_networkx_labels(g, pos, font_size=7, ax=ax)
    nx.draw_networkx_edges(
        g,
        pos,
        edge_color="#555555",
        arrows=True,
        arrowsize=14,
        width=1.4,
        connectionstyle="arc3,rad=0.08",
        ax=ax,
    )
    ax.set_title(title, fontsize=9)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for name, edges in SPECS.items():
        _draw(edges, f"Train-only E_pre (schematic): {name}", OUT / f"fig_kt_graph_{name}.pdf")
    print(f"Wrote KT graph figures to {OUT}")


if __name__ == "__main__":
    main()
