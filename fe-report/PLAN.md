# FE Report - Feature Engineering, Selection, and Transformation for the Permanent Magnet Synchronous Motor (PMSM) Digital Twin

**Status: PLAN - awaiting approval. Runs after sl-report completes (needs its data and recipes).**
**Date: 2026-08-15. Study 4 of 5, see the [master plan](../PLAN.md).**

Research question:

> **Which engineered, selected, and transformed feature sets earn their place, and can physics-derived features substitute for temporal memory and for physics-informed losses?**

The working sample, splits, and tuned model recipes come from `../sl-report` unchanged. Only the feature set varies, so every result is attributable to the features. The study asks a question the other four cannot: how far does domain knowledge go when injected through the *inputs* instead of through the loss (ol's PINN) or the architecture (LSTM memory)? Within the paper scope defined in the master plan this is a supporting study, except H5, which the paper draws on directly.

## 1. Carried over from sl-report

Processed data and manifests from `../sl-report/data/processed/`, frozen recipes for XGBoost, MLP, and LSTM (the three downstream evaluators), seeds `(7466, 7467, 7468)`, primary metric validation MAE on `pm`, sl budgets.

## 2. Feature families (Part 1, engineering)

- **F0 - Raw:** the 7 input signals as-is. The floor.
- **F1 - EWMA:** multi-span exponentially weighted means and standard deviations of the inputs (spans chosen on train only), the dataset authors' own practice, and sl's default feature set.
- **F2 - Lags and differences:** short lag stacks and first differences, the cheap way to hand a pointwise model some dynamics.
- **F3 - Physics-derived:** current magnitude $i_s = \sqrt{i_d^2 + i_q^2}$, copper-loss proxy $i_s^2$, apparent power $1.5\,(u_d i_d + u_q i_q)$, speed-current products $\omega i_d,\ \omega i_q$ (back-EMF and reluctance structure), coolant and ambient deltas $T - T_{\mathrm{cool}}$, field-weakening indicator. Every feature is a term the dq or LPTN equations say should matter.
- **F4 - Union:** F1 + F2 + F3.

## 3. Parts

- **Part 0 - Foundation check (diagnostic).** Confirm carried-over data and recipes, freeze the feature-family definitions, verify the frozen `HYPOTHESES.md` is unchanged.
- **Part 1 - Engineering.** Build F0-F4 with all fitting on train only. Downstream evaluation of each family with the frozen XGBoost, MLP, and LSTM recipes across 3 seeds.
- **Part 2 - Selection.** On F4: filter (mutual information, F-test), embedded (L1 path, tree gain), and permutation importance. A consensus compact set `F5` is chosen on validation at a pre-registered size cap of 15 features.
- **Part 3 - Transformation.** Scaling variants (standard, robust, quantile) on the winning family, and PCA-at-matched-dimension vs `F5` head-to-head. Links to ul's DR findings, but on engineered features and with supervised evaluators.
- **Part 4 - Sparsity bridge (small).** F1 vs F3 vs F5 under the ol 10 % and 3 % label masks (masks read from `../ol-report/artifacts/`, MLP evaluator only). Do engineered inputs deliver part of what physics losses deliver.

## 4. Pre-registered hypotheses

- **H1:** EWMA dominates raw. F1 beats F0 on `pm` MAE by over 30 % for every evaluator.
- **H2:** physics features substitute for memory in part. F3 closes at least half of the MLP-to-LSTM `pm` gap that exists on F1.
- **H3:** a compact set suffices. `F5` (15 features max) reaches at least 95 % of F4's performance for every evaluator.
- **H4:** physics beats blind compression. At matched dimensionality `F5` beats PCA-transformed features on `pm` for every evaluator.
- **H5:** engineered inputs help more as labels shrink, but less than physics losses do. F3's margin over F1 grows from full labels to 3 %, yet stays smaller than the PINN-over-MLP margin ol measures at the same levels.

## 5. Scripts and notebooks

```
scripts/
├── 00_confirm_foundation.py      # carried-over check, feature-family freeze, verify frozen HYPOTHESES.md
├── 01a_part1_engineering_train.py / 01b_part1_engineering_test.py  # Part 1, F0-F4 × 3 evaluators
├── 02_part2_selection.py         # Part 2, val only, writes the F5 definition
├── 03a_part3_transformation_train.py / 03b_part3_transformation_test.py  # Part 3
├── 04a_part4_sparsity_bridge_train.py / 04b_part4_sparsity_bridge_test.py  # Part 4
├── 05_extra_credit_interactions.py   # reserved EC slot: pairwise physics-feature interactions (val only)
├── 06_make_report_figures.py
├── 07_build_repro_artifacts.py
└── 08_verify_invariants.py

notebooks/
├── 00_foundation_and_protocol.ipynb
├── 01_feature_engineering.ipynb
├── 02_feature_selection.ipynb
├── 03_feature_transformation.ipynb
├── 04_sparsity_bridge.ipynb          # + study synthesis and verdicts (ul 04 pattern)
└── 05_extra_credit_interactions.ipynb
```

`src/` follows the family contract (stdlib-only constants leaf, frozen configs, `(frame, summary)` runners).

| Module | Contents |
|---|---|
| `constants.py` | sl sibling paths, family definitions' frozen names F0-F5, the 15-feature cap, selection method grid, scaling variants, bridge levels |
| `run_logging.py` | family pattern, `_result_fields` reads `family`, `evaluator`, `n_features`, `val_mae_pm`, `test_mae_pm` |
| `common.py` | loaders for sl processed data and frozen recipes, `write_summary_table` |
| `feature_families.py` | F0-F4 builders with all fitting on train only, definition freeze and IO |
| `selection.py` | mutual information, F-test, L1 path, tree gain, permutation importance, consensus ranking that writes the F5 definition |
| `transformation.py` | scaling variants (standard, robust, quantile), PCA-at-matched-dimension transform |
| `evaluators.py` | frozen XGBoost, MLP, LSTM condition runners loading sl recipes untouched |
| `metrics.py` | per-family aggregation, gap-closure statistics for H2 and H5 |
| `report_figures.py` | figure builders for script 06 |

### Folder structure (the ol/ul root, exactly)

```
fe-report/
├── artifacts/                    # feature-family definitions, the frozen F5 set, fitted transformers
├── checkpoints/                  # evaluator checkpoints per (family, evaluator, seed)
├── notebooks/
├── reports/
│   ├── figures/
│   ├── tables/
│   ├── logs/
│   ├── repro/
│   └── HYPOTHESES.md             # frozen 2026-08-15, verified unchanged by 00
├── scripts/
├── src/
├── PLAN.md
├── README.md
├── WORKLOG.md                    # dated entry per task, newest first
├── environment-linux.yaml
├── environment-macos.yaml        # run of record
├── requirements-linux.txt
└── requirements-macos.txt
```

## 6. Invariants (script 08)

1. Carried-over foundation matches sl manifests.
2. Every feature family fit on train only (source-verified), definitions frozen in Part 0.
3. Evaluator recipes identical to sl exports, no re-tuning anywhere.
4. Selection ran on validation only, `F5` respects the 15-feature cap.
5. Test isolation: a/b column discipline per part, test contacted once per part.
6. Part 4 masks are byte-identical to ol's manifests.
7. Multi-seed coverage for every condition.
8. Deterministic execution.
9. `HYPOTHESES.md` contains H1-H5 and is unchanged since the 2026-08-15 freeze, dated amendments excepted.

## 7. Budgets, phases, risks

Feature building is CPU-cheap. Downstream evaluation reuses sl budgets (5 families × 3 evaluators × 3 seeds = 45 conditions in Part 1, the rest smaller). Environment `pinn-fe`.

| Phase | Deliverable | Gate |
|---|---|---|
| A | Scaffold + foundation check + family freeze | invariants 1-2 pass |
| B | Part 1 + notebook 01 | invariants 3, 5 pass |
| C | Parts 2-3 + notebooks 02-03 | invariant 4 passes |
| D | Part 4 + extra credit + figures + repro + invariants + README | 9/9 PASS |

Risks: feature leakage through careless span fitting (spans and scalers fit on train only, invariant 2). Part 4 depends on ol artifacts (if ol has not run yet, Part 4 waits, the rest of the study does not).
