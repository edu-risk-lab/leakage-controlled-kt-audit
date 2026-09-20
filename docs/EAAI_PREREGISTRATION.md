# Pre-registration: leakage exposure bound, XES3G5M / GKT

**Frozen at commit `149a7595`, 2026-09-14, before any of the cells below were trained.**

Purpose: the exposure bound in `docs/EAAI_REVISION_PLAN.md` §2 is fitted to nothing —
it is a product of two independently measured quantities. That makes it falsifiable
in advance. This file records the predictions so the confirming runs cannot be
reinterpreted after the fact. Do not edit the numbers below once a cell is trained;
append results in §6 instead.

Reproduce every number here with:

```bash
python scripts/leakage_exposure.py --edge-root data/processed/xes3g5m/m4
```

---

## 1. The two competing predictors

Both take the form `|ΔAUC_leak| ≤ s · δ`, with `s = 0.084` the DDR slope for
GKT/XES3G5M (`results/tables/ddr_slope_ci.csv`, core scope, 95% CI
[0.0794, 0.0900]). They differ only in how the structural delta from pooling is
measured:

| Predictor | δ definition | Status on 3 trained cells |
|---|---|---|
| **P1 raw** | leaked edges / retained train-only edges | holds 3/3, worst slack 12.7× |
| **P2 weighted** | weight mass moved / total train-only weight mass | holds 3/3, worst slack 4.8× |

A third candidate, `δ_eff` (leaked edges creating a new reachability pair), was
**refuted** before freezing: it holds on only 1 of 3 cells. It is recorded here so
it cannot be revived post hoc.

Conservative bounds below use the upper end of the slope CI (0.0900) for P1 and the
point estimate (0.084) for P2, as implemented.

---

## 2. Primary test — the `k=∞` cell discriminates P1 from P2

Cell `q0.5_kinf_Kinf_tau0.1`, fold 0, seed 42, GKT at the primary budget
(10 epochs, batch 4).

| | δ | Predicted bound |
|---|---|---|
| P1 raw | 0.13224 | **|ΔAUC| ≤ 0.01190** |
| P2 weighted | 0.02176 | **|ΔAUC| ≤ 0.00183** |

The manuscript currently claims graph-mediated leakage moves AUC by at most 0.003.
P1 permits that claim to break here; P2 does not. Decision rules:

| Observed \|ΔAUC\| | Verdict |
|---|---|
| ≤ 0.00183 | P2 survives and is the operative predictor. C3 reports the weighted bound. The 0.003 claim holds at the most open filter tested. |
| 0.00183 – 0.01190 | **P2 refuted**, P1 survives. C3 falls back to the raw bound and the manuscript must state that the tight predictor failed. If the value also exceeds 0.003, every "at most 0.003" sentence must be rewritten. |
| > 0.01190 | Both refuted. This is a positive finding: a filter regime where graph leakage genuinely moves accuracy. The paper's framing changes from bounded null to located harm. |

No outcome here is uninformative. That is the point of running it.

---

## 3. Replicate test — noise floor at zero extra graph cost

Cell `q0.95_k5_Kinf_tau0.1` has a **byte-identical graph** to the published default
cell `q0.95_k5_K5000_tau0.1` (`k` binds, so `K` never engages). The census confirms
the same four-part signature for both:

```
132d537d45fcb1ab | c0f8d1d7ff10f6a3 | 84c1246a286505fa | 1001763cf0599b22
```

Training it is therefore a pure replicate of a cell already run. Prediction:

> Observed ΔAUC = **+0.00061**, identical to the default cell, if GKT training at
> this budget is deterministic given fixed seed and graph.

Any deviation is the training noise floor `σ`. This matters more than it looks:
the manuscript's headline claims sit at 0.0006–0.0017, so if `σ ≳ 0.001` then the
default-cell ΔAUC is **not measurable with one run** and every point estimate in
the M4 table needs either replicates or an explicit "below noise floor" statement.

This is the cheapest available answer to the reviewer complaint that the bounded
null has no confidence interval: one cell, 4–8 GPU-hours, no new code.

**Prior from an already-measured corpus.** The multi-seed DDR sweep contains true
replicates on ASSIST2012: all three seed files share `split_seed` 42/43/44 and
edge counts 413/416/416, so the runs differ only in training seed.
`scripts/noise_floor.py` extracts 36 such groups and 96 seed-only pairs, giving a
median absolute difference of 1.59e-4, a p90 of 4.32e-4, and a maximum of 9.99e-4.

That is a prior, not a substitute. It is measured at AUC 0.96 on ASSIST2012 while
the cell above sits at AUC 0.83 on XES3G5M, where dispersion is typically larger,
so we register the directional expectation:

> `σ` on XES3G5M/GKT will be **at least** the ASSISTments median of 1.59e-4, and
> we will not treat any XES3G5M ΔAUC below that as resolved by a single run.

Registering this now prevents the failure mode where a large measured `σ` is later
explained away as corpus-specific after the fact.

---

## 4. Full prediction table (all untrained fold-0 cells)

| Cell | δ raw | δ weighted | P1 bound | P2 bound |
|---|---|---|---|---|
| `q0.5_k5_K1000_tau0.1` | 0.01000 | 0.02045 | 0.00090 | 0.00172 |
| `q0.8_k5_K1000_tau0.1` | 0.01000 | 0.02045 | 0.00090 | 0.00172 |
| `q0.9_k5_K1000_tau0.1` | 0.01000 | 0.02045 | 0.00090 | 0.00172 |
| `q0.95_k5_K1000_tau0.1` | 0.01000 | 0.02045 | 0.00090 | 0.00172 |
| `q0.5_k5_K5000_tau0.1` | 0.04233 | 0.02155 | 0.00381 | 0.00182 |
| `q0.8_k5_K5000_tau0.1` | 0.05094 | 0.02200 | 0.00458 | 0.00185 |
| `q0.8_k5_Kinf_tau0.1` | 0.05094 | 0.02200 | 0.00458 | 0.00185 |
| `q0.9_k5_K5000_tau0.1` | 0.06401 | 0.02499 | 0.00576 | 0.00211 |
| `q0.9_k5_Kinf_tau0.1` | 0.06401 | 0.02499 | 0.00576 | 0.00211 |
| `q0.95_k5_K5000_tau0.05` | 0.08864 | 0.03526 | 0.00798 | 0.00297 |
| `q0.95_k5_K5000_tau0.2` | 0.08864 | 0.03526 | 0.00798 | 0.00297 |
| `q0.95_k5_Kinf_tau0.1` | 0.08864 | 0.03526 | 0.00798 | 0.00297 |
| `q0.5_kinf_Kinf_tau0.1` | 0.13224 | 0.02176 | 0.01190 | 0.00183 |

The four `K=1000` cells share one graph, as do several other groups; the census
signature column identifies which. P1 and P2 disagree in direction on the
`K=1000` group (P1 tighter) and on the `k=∞` cell (P2 tighter by 6.5×), so those
two ends of the sweep carry the discriminating information.

---

## 5. Rules of engagement

1. Run the replicate cell (§3) early, though it no longer gates the rest. The
   ASSISTments replicates in §3 already settled the vintage gap of revision plan
   §2.5: the train-only arm sits at the 85th percentile of the seed-only null
   while the full-log arm exceeds all 96 pairs, so training noise is excluded.
   What remains is `σ` on the **primary** corpus, which the C3 bound and the
   confidence-interval complaint both need, and which no existing run supplies.
2. Do not adjust `s`, the δ definitions, or the CI convention after seeing any
   outcome. If a definition must change, that is a new pre-registration with a new
   freeze commit, and the old one stays in the repo.
3. Report every trained cell, including ones that make the bound look bad.
4. `s` is estimated from edge **removal** (DDR). Leakage **adds** edges. Until the
   `s⁺` experiment in §Pha 2 task 2.2 is run, both predictors rest on an untested
   transfer assumption, and the manuscript must say so.

---

## 6. Results log (append only, after each run)

| Date | Cell | Fold | Observed ΔAUC | P1 held? | P2 held? | Commit |
|---|---|---|---|---|---|---|
| 2026-09-17 | `q0.95_k5_Kinf_tau0.1` | 0 | **+0.000615** (bit-identical to default `K=5000`) | yes (same graph as published default) | yes | *this commit* |
| 2026-09-20 | `q0.5_kinf_Kinf_tau0.1` | 0 | **−0.000435** | yes (≤ 0.01190) | yes (≤ 0.00183) | *below measured σ = 1.8e-3; does not discriminate P1 from P2* |
