# Targeted GKT30 scope verification

Author attestation (this turn) is treated as `SERVER_ATTESTED`, not as a substitute for logs.

## 1. What the targeted GKT30 check is

| Field | Determined value | Evidence |
|---|---|---|
| Dataset | **XES3G5M** | `results/q1/gkt_epochs30_s42/baseline_fold_results.csv`; primary baseline same dataset |
| Split | **learner-temporal 3-fold**, `train_only` graphs | CSV `graph_construction=train_only`; config `split.type: learner_temporal` |
| Seeds/folds for **+0.003 epoch gain** | **`split_base_seed=42` only**, folds **0,1,2** (`split_seed` 42,43,44) | Only seed with both GKT10 and GKT30 AUCs; S21 generator `_load_gkt30_seed42()` |
| GKT10 hp | **max_epochs=10, batch=4** | Author `SERVER_ATTESTED`; config@`619c02cf` matches |
| GKT30 hp (epochs) | **max_epochs=30** | Author (extension 10→30); config@`b02afca9` `epochs: 30` |
| GKT30 hp (batch) | **16 at intro commit** (`b02afca9`); S21 prints **32** | Config blob `47f0082a…`; **not** author-attested this turn; **not** EXECUTION_VERIFIED |
| Config/commit (GKT30 seed42) | `configs/xes3g5m_gkt_epochs30.yaml` @ **`b02afca9`** | First commit storing paper-level ~0.84 AUCs for s42 |
| Result artifact | `results/q1/gkt_epochs30_s42/baseline_fold_results.csv` | SHA16 `04b99459a008294d` |
| Not this check | Full primary pipeline re-run at 30 ep | Author explicit; primary AUCs remain the 10-ep rows |

## 2. Valid GKT10 ↔ GKT30 pairs

Exactly **three** pairs (same `fold` and `split_seed`):

| Fold | split_seed | auc_gkt10 | auc_gkt30 | Δ |
|---:|---:|---:|---:|---:|
| 0 | 42 | 0.834557 | 0.840181 | +0.005624 |
| 1 | 43 | 0.833752 | 0.838300 | +0.004547 |
| 2 | 44 | 0.832624 | 0.832804 | +0.000181 |

See `paired_gkt10_gkt30_deltas.csv`.

**Excluded from +0.003:** all `gkt_epochs30_s17` / `s1234` rows — no primary GKT10 twins.  
**Excluded:** any log/CSV with AUC ≈ 0.71 (`d9efa271` / `logs/q1/gkt_epochs30_s17.log`).

## 3. Recomputed +0.003 (valid pairs only)

| Statistic | Value |
|---|---|
| n | 3 |
| mean ΔAUC (GKT30 − GKT10) | **+0.003451** |
| sample std (ddof=1) | 0.002883 |
| paired-*t* 95% CI | **[−0.003710, +0.010611]** |
| Display match to S21 “Epoch gain … +0.003” / CI `[−0.004, +0.011]` | **YES** (rounding) |

Classification of these three pairs: **`CONFIG_AND_ARTIFACT_SUPPORTED` + `SERVER_ATTESTED`** (protocol).  
**Not** `EXECUTION_VERIFIED` (no logs tying hp to the 0.84 AUCs).

## 4. Other GKT30 artifacts (exist, but outside extension pairing)

Nine GKT30 fold rows exist (seeds 17, 42, 1234 × 3 folds) at ~0.83–0.84 AUC.  
They support a **multi-seed GKT@30 vs simpleKT** comparison (S22’s current numeric content), **not** a nine-fold GKT10↔GKT30 epoch-extension.

## 5. DDR GKT (author note; out of +0.003 path)

Author: DDR downstream GKT uses **10 / 4**. Runner defaults to `configs/xes3g5m.yaml`. Recorded as `SERVER_ATTESTED` in the run matrix; not used for epoch-gain pairs.

## 6. Stop for author confirmation

Please confirm or correct `targeted_gkt30_run_matrix.csv` before any manuscript remediation, especially:

1. Is the +0.003 claim **only** seed-42 three-fold (as artifact pairing shows)?  
2. What **batch size** should be stated for GKT30 seed-42 (16 per config@`b02afca9`, or 32 per S21 text, or 4)?  
3. Should seeds 17/1234 GKT30 rows remain as a **separate** vs-simpleKT multi-seed note, or be dropped from the paper narrative?
