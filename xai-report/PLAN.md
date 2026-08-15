# xAI Report - Explaining the Permanent Magnet Synchronous Motor (PMSM) Digital Twin

**Status: PLAN - awaiting approval. Runs last, audits checkpoints from sl-report and ol-report.**
**Date: 2026-08-15. Study 5 of 5, see the [master plan](../PLAN.md).**

Research question:

> **What did each model actually learn about the motor, and do explanations survive label sparsity?**

A digital twin that cannot explain itself will not be trusted with thermal protection. This study trains nothing. It audits the saved checkpoints from sl (full supervision) and ol (sparsity ladder), computes attributions on validation data only, and reads everything against the physics. The unusual property: **this study makes zero test contacts**, every number comes from validation or from the models themselves.

## 1. Carried over

- sl-report: processed data, full-supervision checkpoints for all eight rungs, `pmsm_physics.py` (copied, disclosed).
- ol-report: sparsity-ladder checkpoints and mask manifests.
- Seeds, logging, and invariant conventions from the family.

## 2. Parts

- **Part 0 - Foundation and inventory (diagnostic).** Confirm carried-over data, inventory every checkpoint this study audits (model × supervision level × seed), verify the frozen `HYPOTHESES.md` is unchanged.
- **Part 1 - Attributions on a common footing.** Exact TreeSHAP for XGBoost, channel-level permutation importance for all eight rungs on the same validation windows, so the importance vectors are directly comparable. Transformer attention maps reported descriptively only, with the attention-is-not-explanation caveat.
- **Part 2 - Physics-native explanation.** Four independent physical parameter estimates exist by this point: the LPTN least-squares fit (sl B0), the TNN's learned conductances (sl B5), the PINN's learned parameters (P), and the structured hybrid's (P2). This part cross-checks them against each other and against the literature values recorded in sl Part 0. Agreement is evidence the physics was identified, not fitted. Then the PINN-specific evidence: physics-residual maps over the speed-load envelope showing where the twin trusts its equations and where they break (saturation and field weakening are the expected hot spots), and temperature-dependent parameter drift read directly from the learned `α_cu` and `α_mag` (the parameter head is temperature-affine by construction, sl spec), with per-band refits kept as a consistency check against the same copper ($\alpha_{cu} \approx +0.39\,\%/\mathrm{K}$) and magnet ($\alpha_{mag} < 0$) physics.
- **Part 3 - Stability under sparsity (the tie to the umbrella question).** For each model and seed, Spearman rank correlation between its full-supervision importance vector and its vector at each ol sparsity level. Accuracy can degrade gracefully while explanations collapse. The PINN's version of an explanation is its parameter set, tracked the same way.
- **Part 4 - Physics-consistency reading.** Do the data-driven models rediscover the LPTN structure: importance of coolant and of the copper-loss proxy $i_d^2 + i_q^2$ for temperatures, back-EMF terms for voltage-linked targets. Evidence-based answer, read against the equations.

## 3. Pre-registered hypotheses

- **H1 (amended 2026-08-15, see `reports/HYPOTHESES.md`):** at full supervision every model's `pm` attributions are physically plausible: coolant and current magnitude rank in the top 5 channels for all eight rungs.
- **H2 (headline):** explanations collapse before accuracy does. For every baseline the Spearman correlation between its 100 % and 1 % importance vectors falls below 0.5, while the PINN's learned parameters at 1 % stay within 25 % of their full-supervision values.
- **H3:** residual maps localize physics stress. Voltage-residual density is at least 3× higher in the field-weakening region than in MTPA, at every supervision level.
- **H4 (amended 2026-08-15, see `reports/HYPOTHESES.md`):** parameter drift follows material physics. The learned $\alpha_{cu}$ is positive and the learned $\alpha_{mag}$ is negative, signs stable across all 3 seeds, and per-temperature-band refits agree with the learned trends.
- **H5 (amended 2026-08-15, see `reports/HYPOTHESES.md`):** the physics-bearing models agree on the motor. LPTN, TNN, PINN, and P2 estimates of the shared thermal parameters lie within 30 % of one another at full supervision.

## 4. Scripts and notebooks

```
scripts/
├── 00_confirm_and_inventory.py   # carried-over check + checkpoint inventory + verify frozen HYPOTHESES.md
├── 01_part1_attributions.py      # Part 1 (validation only)
├── 02_part2_physics_native.py    # Part 2: parameter cross-check (LPTN/TNN/PINN), residual maps, drift
├── 03_part3_stability_under_sparsity.py  # Part 3 (reads ol checkpoints)
├── 04_part4_physics_consistency.py       # Part 4: did the data-driven models rediscover the LPTN
├── 05_extra_credit_counterfactuals.py    # reserved EC slot: what-if operating-point probes (val only)
├── 06_make_report_figures.py
├── 07_build_repro_artifacts.py
└── 08_verify_invariants.py

notebooks/
├── 00_foundation_and_inventory.ipynb
├── 01_attributions.ipynb
├── 02_physics_native_explanations.ipynb
├── 03_stability_under_sparsity.ipynb
└── 04_physics_consistency_and_synthesis.ipynb  # Part 4 + consolidated verdicts (ul 04 pattern)
```

`src/` follows the family contract (stdlib-only constants leaf, frozen configs, `(frame, summary)` runners).

| Module | Contents |
|---|---|
| `constants.py` | sl and ol sibling paths, audited (rung, level, seed) inventory spec, permutation window subsample size, temperature bands for drift, envelope grid resolution |
| `run_logging.py` | family pattern, `_result_fields` reads `rung`, `level`, `spearman`, `coverage_of_top5`, `param_drift_pct` |
| `common.py` | checkpoint loaders for sl and ol models, validation-window sampler, `write_summary_table` |
| `pmsm_physics.py` | copy of the sl module, disclosed |
| `attributions.py` | TreeSHAP wrapper for XGBoost, channel-level permutation importance for every rung on the shared validation windows |
| `residual_maps.py` | speed-load envelope binning, per-bin residual densities, map artifact IO |
| `stability.py` | Spearman correlations across levels and seeds, parameter-drift tracking, the four-way LPTN/TNN/PINN/P2 parameter cross-check |
| `report_figures.py` | figure builders for script 06 |

### Folder structure (the ol/ul root, exactly)

```
xai-report/
├── artifacts/                    # importance vectors, residual-map grids, parameter cross-check tables
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

No `checkpoints/` here: this study trains nothing and saves no models. It reads sl and ol checkpoints in place.

## 5. Invariants (script 08)

1. Carried-over foundation matches sl manifests.
2. Checkpoint inventory complete: every (model, level, seed) this study claims to audit exists on disk with matching hashes.
3. Zero test contact anywhere: no table in this study carries `test_*` columns (the study's defining discipline).
4. Attribution coverage: importance vectors exist for all eight rungs at the full and 1 % levels.
5. Attention maps are labeled descriptive and never enter any comparison table.
6. Drift fits use validation data only, bands frozen before fitting.
7. Multi-seed coverage for every audited condition.
8. Deterministic execution.
9. `HYPOTHESES.md` contains H1-H5 and is unchanged since the 2026-08-15 freeze, dated amendments excepted.

## 6. Budgets, phases, risks

Nothing is trained, so the study costs minutes to a few hours (permutation importance is the slow part, bounded by a pre-registered window subsample). Environment `pinn-xai` adds `shap`.

| Phase | Deliverable | Gate |
|---|---|---|
| A | Scaffold + inventory (00) | invariants 1-2 pass |
| B | Parts 1-2 + notebooks 01-02 | invariants 3-5 pass |
| C | Part 3 + notebook 03 | invariants 6-7 pass |
| D | Part 4 + figures + repro + invariants + README | 9/9 PASS |

Risks: ol not finished means Part 3 waits (Parts 1-2 run on sl checkpoints alone). Permutation importance on windowed sequence models is costly (seeded subsample, size disclosed). SHAP beyond trees is out of scope, permutation importance is the cross-model method, stated plainly.
