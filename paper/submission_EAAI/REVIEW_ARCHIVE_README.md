# Leakage-controlled concept-graph audit (review archive)

Companion research software for the anonymized manuscript *Leakage-controlled
concept-graph construction and cold-start diagnostics for graph-enhanced
knowledge tracing*, submitted to *Engineering Applications of Artificial
Intelligence*. Author identities, acknowledgements, and the public repository
URL are withheld for double-anonymized review.

This archive is **not** a new knowledge-tracing backbone. It implements the
train-only graph audit, directed-acyclic-graph validation, leakage scalars,
cold-start stratification, directed-acyclic-graph disruption-rate probes, and
the table/figure generators used in the manuscript.

## Contents

```
README.md                 this file
LICENSE                   MIT (author names withheld)
requirements.txt
pyproject.toml            no author or repository URLs
configs/                  dataset and experiment YAML
src/                      audit pipeline
scripts/                  reproduction and table generators
tests/                    unit tests (no raw logs required for most)
docs/M4_QK_SWEEP_PROTOCOL.md
results/tables/           paper-facing CSV/TeX artefacts
results/figures/          paper-facing PDF figures
results/m4/               builder census for the q×k sweep
results/q1/               fold-level GKT CSVs (no large caches)
results/audit_cost/       wall-clock / RAM measurements
data/raw/.gitkeep         place public benchmarks here (not redistributed)
data/processed/.gitkeep
third_party/README.md     how to obtain pyKT (public MIT toolkit)
```

Raw interaction logs are **not** included. Download them under each provider's
terms of use (URLs are in the manuscript Data availability statement).

## Environment

Python 3.10 or 3.11 recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Graph-enhanced tracers (GKT / GIKT) additionally need the public pyKT toolkit:

```bash
git clone https://github.com/pykt-team/pykt-toolkit.git third_party/pykt-toolkit
pip install -e ".[pykt]"
pip install -e third_party/pykt-toolkit
```

## Tests that do not need raw logs

```bash
python -m pytest tests/test_leakage_metrics.py tests/test_dag_audit.py \
  tests/test_graph_builder_train_only.py tests/test_ddr_slope_ci.py \
  tests/test_m4_qk_sweep.py -q
```

On some Windows Python builds, disable third-party pytest plugins:

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -p no:typeguard tests/test_ddr_slope_ci.py -q
```

## Regenerating paper tables (after data + graphs exist)

```bash
python scripts/generate_phase_c_tables.py
python scripts/ddr_slope_ci.py
python scripts/generate_m4_qk_tables.py
python scripts/measure_audit_cost.py   # optional; writes results/audit_cost/
```

Train-only vs full-log GKT jobs used the attested primary budget: 10 epochs,
batch size 4, seed 42, early-stopping patience 5. Do **not** substitute the
parked 30-epoch / batch-32 configuration when reproducing the main null.

## Licence

Code is MIT. Junyi Academy / PSLC DataShop, ASSISTments 2012–2013, and
XES3G5M remain under their providers' terms and are not redistributed here.
pyKT is MIT (`https://github.com/pykt-team/pykt-toolkit`).
