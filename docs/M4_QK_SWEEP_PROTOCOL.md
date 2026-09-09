# M4 — Support-quantile × global-cap sweep

Protocol for the remaining required experiment: the train-only vs full-log **null** (`|ΔAUC| ≤ 0.003` on XES3G5M) may be an artefact of the default filter `(q, k, K, τ) = (0.95, 5, 5000, 0.10)`, not a property of leakage. C5 / compute-matched GKT is **out of scope**.

Primary corpus: **XES3G5M** only. Hold learner splits, evaluation code, and GKT training budget fixed at the **attested primary** setting (max 10 epochs, batch 4, seed 42, early stopping patience 5). Do not mix in GKT30 / batch 32.

---

## 1. Estimand

For each filter cell `θ = (q, k, K, τ)` and each fold `f`:

```
ΔAUC(θ, f, m) = AUC_full-log(θ, f, m) − AUC_train-only(θ, f, m)
```

- Same learner split, same optimiser, same graph-consumer backbone `m`.
- Only the static graph artefact changes; sequences stay train-fold only.
- Primary backbone: **GKT** (graph-reliant; the cell that can move).
- Secondary (landmark cells only): **GIKT**.
- Do **not** score SKT / DyGKT (wiring diagnostics; they do not inform M4).

Companion **builder** estimands (Phase A; no GPU):

| Symbol | Definition |
|---|---|
| `|E_pre^to|`, `|E_pre^fl|` | Retained prerequisite edges after `(q, k, K)` and DAG prune |
| `J_pre` | Jaccard of undirected edge sets, train-only vs full-log |
| `|E_pre^fl \ E_pre^to|` | Edges that exist only after pooling (throughput of the leak) |
| `p90(π_e)` | 90th percentile of per-edge held-out transition share (existing `edge_share` code) |
| `bind` | Which stage is active: quantile / per-source `k` / global `K` |

A GPU cell is **redundant** if Phase A shows identical `(E_pre^to, E_pre^fl, E_sim^to, E_sim^fl)` (same edge sets) as another cell already trained.

---

## 2. Why a naive 4 × 3 GPU grid is the wrong first step

Default XES3G5M already has `|E_pre| ≈ 1163` at `(q, k, K) = (0.95, 5, 5000)`. Therefore:

- At `q = 0.95`, **`K = 5000` and `K = ∞` are the same graph**.
- `K = 1000` is the only new global-cap cell at the published `q`.
- Lowering `q` without raising `k` may still leave **`k = 5` as the binding throttle**. Review asked for `q × K`; if we never inspect `k`, we can “sweep” 12 cells and still never open the channel.

`τ` builds `E_sim` from the Q-matrix and is **orthogonal** to `(q, K)`. Do not run the full 4 × 3 × |τ| factorial.

`K = ∞` in code must be a large sentinel (e.g. `10**9`). `max_edges = 0` would yield an empty graph (`nlargest(min(0, n))`).

---

## 3. Grid

### Held fixed (unless a named phase says otherwise)

- Dataset: XES3G5M
- Split: `configs/xes3g5m.yaml` (`seed = 42`, 3 learner folds)
- `e_pre_source` / inference rule: unchanged (train-only temporal transitions)
- Per-source cap: **`k = 5`** on the review grid
- Jaccard method; `τ = 0.10` on the `q × K` grid
- GKT: 10 epoch / batch 4 (primary attested)

### Phase A — builder census (CPU, all cells, 3 folds)

`q ∈ {0.50, 0.80, 0.90, 0.95}` × `K ∈ {1000, 5000, ∞}`, `k = 5`, `τ = 0.10`.

Plus a **one-factor `τ` arm** at the published `(q, k, K) = (0.95, 5, 5000)`:

`τ ∈ {0.05, 0.10, 0.20}`.

Plus a **binding check for `k`** at the most open review corner `(q, K) = (0.50, ∞)`:

`k ∈ {5, 20, ∞}`.

Outputs: one CSV row per `(θ, fold, construction)` with the builder estimands and `bind`. Collapse to **unique graph signatures** before any GKT job.

Expected wall-clock: **hours, not days** (graph build + full-log export + edge-share; no KT training).

### Phase B — downstream (GPU), unique signatures only

Train GKT **train-only and full-log** on each unique Phase A signature.

**Minimum set (always train, even if Phase A collapses some `K`):**

1. Published default: `(0.95, 5, 5000, 0.10)` — reproduce Table S6-class cell (`ΔAUC ≈ +0.002` on fold 0).
2. `K` binds at default `q`: `(0.95, 5, 1000, 0.10)`.
3. Review “open” corner: `(0.50, 5, ∞, 0.10)`.
4. Mid: `(0.80, 5, 5000, 0.10)`.
5. If Phase A shows `k = 5` still binds at (3): add `(0.50, 20, ∞, 0.10)` and `(0.50, ∞, ∞, 0.10)`.
6. If `|E_sim|` changes by ≥ 20% under the `τ` arm: add those `τ` cells at default `(q, k, K)`.

**Folds**

- All Phase B cells: **fold 0** (matches the published ablation table).
- **Three-fold** only for three landmarks: default, mid `(0.80, 5000)`, and the most open cell that Phase A actually opened.

**GIKT:** fold 0 only, same three landmarks.

Stop rule: if the most open cell still has `|ΔAUC| ≤ 0.003` on fold 0, **do not** expand to extra seeds. That *strengthens* the bounded-negative claim. If `|ΔAUC| > 0.010` (abstract bound) or `> 0.003` (published ablation bound), run the 3-fold landmarks and write a **safe-region** entry on the decision map.

### Phase C — do not run

- Compute-matched GKT vs simpleKT (parked C5).
- Injection sweep at every `q` (optional later; not M4).
- ASSISTments / Junyi `q × K` (Junyi GKT already omitted for cost; ASSIST is graph-inert).
- Extra GKT seeds (17 / 1234) unless fold-0 open cell exceeds 0.010.

---

## 4. Isolation (non-negotiable)

Primary artefacts live in `data/processed/xes3g5m/fold_*/` and `full_log/`. Cache keys today are

`results/cache/xes3g5m_fold_{f}_gkt_s42_{train_only|full_log}_result.json`

and **do not include `(q, k, K, τ)`**. Writing M4 graphs into those paths, or training without `--isolated-results`, will **corrupt the submission tables**.

Required layout:

```
data/processed/xes3g5m/m4/q{q}_k{k}_K{K}_tau{tau}/
    fold_{f}/e_pre_train_only.csv
    fold_{f}/e_sim_train_only.csv
    full_log/e_pre.csv
    full_log/e_sim.csv
results/m4/{tag}/
    builder_census.csv
    baseline_fold_results.csv
    unique_signatures.json
```

`--isolated-results m4_<tag>` on every `baseline_runner` call. After M4, primary `fold_*` / `full_log/` / `results/tables/graph_ablation*.csv` must still hash-match the submission snapshot.

---

## 5. How to run Phase A

```bash
# From repo root. Phase A does not train GKT and does not write primary fold_* / full_log.
python scripts/run_m4_qk_sweep.py --dry-run
python scripts/run_m4_qk_sweep.py                  # 3 folds
python scripts/run_m4_qk_sweep.py --fold-idx 0     # fold 0 first
python scripts/run_m4_qk_sweep.py --phase b --cells default --dry-run
python scripts/run_m4_qk_sweep.py --phase b --cells default --fold-idx 0
```

Phase B uses `--graph-root` + `--isolated-results` so GKT cache/work dirs never reuse primary artefacts.

Outputs (isolated):

- `data/processed/xes3g5m/m4/<cell_tag>/fold_*/e_{pre,sim}_train_only.csv`
- `data/processed/xes3g5m/m4/<cell_tag>/full_log/e_{pre,sim}.csv`
- `results/m4/builder_census.csv`
- `results/m4/unique_signatures.json`
- `results/m4/phase_b_jobs.json` (recommended GPU list; no training)
- `results/m4/overlays/*.yaml`
- `results/m4/cache/transitions_*.parquet` (reuse across reruns)

Sentinel: `UNLIMITED_CAP = 10**9` in `src/graph_builder.py`. Transition counts are computed once per fold / full-log, then every `(q, k, K)` is a filter. `τ` only rebuilds `E_sim`.

---

## 6. Time (RTX 3090, GKT 10 ep / bs 4)

| Work | Estimate |
|---|---|
| Phase A (≤ 12 + 3 + 2 builder cells × 3 folds) | **2–6 h** CPU |
| Phase B fold-0 GKT, ~6–8 unique cells × 2 graphs | **1–2 days** |
| + 3-fold on 3 landmarks × 2 graphs | **+1 day** |
| + GIKT landmarks fold 0 | **+4–8 h** |
| Worst case (no collapse, all 12 × fold 0 × GKT) | **~2–4 days** |

Phase A first is what keeps this off the 1–2 week naive grid.

---

## 7. How the manuscript changes (pre-commit the wording)

Main-text Table (new, compact): `q × K` on XES3G5M fold 0, GKT, columns `|E_pre^to|`, `|E_pre^fl \ E_pre^to|`, `p90(π_e)`, `ΔAUC`. Default cell in bold as the published operating point.

Rewrite §4.5 / ablation paragraph — pick **one** of:

| Outcome | Claim |
|---|---|
| A. Open cell still `|ΔAUC| ≤ 0.003` | Null is **not** an artefact of `q = 0.95`. Strengthen the bounded-negative result; keep “aggressive filter” as a *throughput* remark, not as the explanation of the AUC null. |
| B. `ΔAUC` grows only when `k` is also lifted | Safe region is **`(q, k)` jointly**, not `q` alone. Decision-map: do not publish graphs with `(q ≤ 0.80` and `k ≥ 20)` without a train-only vs full-log row. |
| C. `ΔAUC > 0.010` at some review cell | Abstract bound “at most 0.010” must be scoped: *under the published filter*; report the open-filter shift and the safe region. |

Highlight 2 (“Full-log versus train-only … at most 0.003”) is **conditional on the published filter** until Phase B says otherwise. Do not touch Highlights until Phase B fold-0 of the most open cell is in.

---

## 8. Acceptance tests

- [ ] Primary `graph_ablation` CSV / fold graphs unchanged after the campaign.
- [ ] Default cell fold-0 GKT `|ΔAUC|` within 0.003 of the published `+0.002` (sanity).
- [ ] Every GPU row has a Phase A signature; no two GPU jobs share a signature.
- [ ] `K = ∞` encoded as a large sentinel; empty-graph rows rejected.
- [ ] Table reports which of `q`, `k`, `K` binds in each cell.
- [ ] C5 numbers not reopened.

---

## 9. First executable step

```bash
python scripts/run_m4_qk_sweep.py --fold-idx 0
```

Then inspect `results/m4/phase_b_jobs.json` before any GKT job. Re-run without `--fold-idx` to fill folds 1–2 (cache makes the second pass filter-only on saved counts).
