# OL Report - Optimization & Uncertainty: Permanent Magnet Synchronous Motor (PMSM) Physics under Label Scarcity

**Status: PLAN - awaiting approval. Runs after sl-report completes.**
**Date: 2026-08-15. Study 2 of 5, see the [master plan](../PLAN.md).**

Research question:

> **How do physics-loss weighting, physics-term ablation, collocation, and shrinking label budgets move the fixed models, and does the PINN degrade most gracefully?**

This is the project's headline study. The exact working sample, splits, preprocessing, tuned recipes, and checkpoints are carried over unchanged from `../sl-report`, so every result is attributable to the intervention rather than to a different dataset or architecture. That is the ol discipline verbatim. The sparsity ladder answers the umbrella research question here.

## 1. Carried over from sl-report (nothing re-tuned)

- Processed data, sample and split manifests from `../sl-report/data/processed/`.
- Frozen model recipes and full-supervision checkpoints for all seven rungs.
- `pmsm_physics.py` copied into `src/` from sl-report, disclosed as a copy.
- Seeds `(7466, 7467, 7468)`, primary metric validation MAE on `pm`, budgets identical to sl.

## 2. Parts

- **Part 0 - Foundation check (diagnostic).** Confirm the carried-over sample, splits, and recipes match sl-report exactly, ul `00_confirm_foundation` style. Verify the frozen `HYPOTHESES.md` is unchanged.
- **Part 1 - $\lambda$-weighting on the fixed PINN.** Pilot (`01c`) compares fixed scale-normalized weights, uncertainty weighting (learned log-variances), and GradNorm-lite on validation only. The winner is frozen and disclosed (ol pilot-then-freeze). The comparison then runs across 3 seeds.
- **Part 2 - Physics-term ablation.** Remove $L_{vd} + L_{vq}$, $L_{\mathrm{torque}}$, and $L_{\mathrm{thermal}}$ one family at a time under the frozen weighting. Which residual carries which target.
- **Part 3 - Collocation density.** Physics residuals evaluated on {0×, 1×, 4×} unlabeled samples per labeled one. What unlabeled physics is worth.
- **Part 4 - The sparsity ladder (headline).** `SPARSITY_LEVELS = (1.00, 0.30, 0.10, 0.03, 0.01)` of training target labels. Labels removed as whole sessions first, then contiguous within-session blocks, seeded and manifest-hashed, identical masks for all seven rungs. Validation and test stay fully labeled and identical across levels. Inputs stay fully available everywhere. Unlabeled training inputs remain usable by every model as input context, and only the PINN can additionally consume them as physics collocation points. Grid: 7 rungs × 5 levels × 3 seeds = 105 conditions under fixed budgets (B0's least-squares fit is deterministic, its three rows per level differ only through the label masks).
- **Part 5 - Predictive uncertainty.** Seed-ensemble predictions assembled from the Part 4 checkpoints (3 members per condition), plus split-conformal intervals calibrated on validation sessions only. Coverage and interval width evaluated per rung and per sparsity level. A thermal-protection twin needs intervals, not just point estimates, and this part makes the study's 'Uncertainty' literal.
- **Part 4 extra (script `04c`) - Sensor ablation.** No torque supervision at all, and no coolant input, at one sparsity level. A variant of the ladder, numbered the ul way (`04c`/`04d` variants).

## 3. Pre-registered hypotheses

- **H1 (headline):** the PINN degrades most gracefully. At 3 % labels and below it beats every other rung on both `pm` and `torque`, with the margin over the data-driven models growing monotonically as labels shrink. B0 stays flat but never wins, because it cannot learn what the LPTN leaves out.
- **H2:** adaptive $\lambda$ weighting beats fixed scale-normalized weights on validation loss and cross-seed stability.
- **H3:** term ablation is target-specific. Removing $L_{\mathrm{thermal}}$ hurts `pm` under sparsity more than removing the voltage residuals hurts torque.
- **H4:** collocation earns its keep only under sparsity. At full labels 0× vs 4× differs by under 5 % MAE, at 3 % labels 4× beats 0× by over 15 %.
- **H5:** baseline degradation is not seed noise. At 1 % labels every data-driven rung's cross-seed MAE spread is smaller than its gap to the PINN.
- **H6:** intervals stay honest, and physics keeps them tight. Split-conformal coverage holds within 5 points of the 90 % target for every rung at every level, and the PINN's interval width at 1 % labels is under 1.5× its full-label width while every data-driven rung's exceeds 3×.

## 4. Scripts and notebooks

```
scripts/
├── 00_confirm_foundation.py      # carried-over data + recipes match sl (diagnostic), verify frozen HYPOTHESES.md
├── 01c_part1_lambda_pilot.py     # pilot on val only, freeze the winner (ol 04c pattern)
├── 01a_part1_lambda_train.py / 01b_part1_lambda_test.py       # Part 1 across seeds
├── 02a_part2_ablation_train.py / 02b_part2_ablation_test.py   # Part 2
├── 03a_part3_collocation_train.py / 03b_part3_collocation_test.py  # Part 3
├── 04a_part4_sparsity_train.py / 04b_part4_sparsity_test.py   # Part 4, 105 conditions
├── 04c_part4_sensor_ablation.py  # Part 4 extra credit variant
├── 05a_part5_uncertainty_calibrate.py  # Part 5: ensembles + conformal (validation only)
├── 05b_part5_uncertainty_test.py       # Part 5: coverage and width on test, single contact
├── 06_make_report_figures.py
├── 07_build_repro_artifacts.py
└── 08_verify_invariants.py

notebooks/
├── 00_baseline_and_protocol.ipynb    # foundation check, compute protocol, H1-H5
├── 01_lambda_weighting.ipynb
├── 02_physics_term_ablation.ipynb
├── 03_collocation.ipynb
├── 04_sparsity_ladder.ipynb          # headline results + sensor-ablation extra
└── 05_uncertainty.ipynb              # coverage, interval width + study synthesis and verdicts
```

`src/` follows the same contract as sl-report (stdlib-only constants leaf, `run_logging` on top, frozen configs, `run_<x>_condition` returning `(frame, summary)`).

| Module | Contents |
|---|---|
| `constants.py` | sl sibling paths, `SPARSITY_LEVELS`, collocation densities, $\lambda$-strategy grid, conformal target coverage, budgets carried from sl |
| `run_logging.py` | family pattern, `_result_fields` reads `val_mae_pm`, `test_mae_pm`, `coverage`, `width`, `grad_evals` |
| `common.py` | loaders for sl processed data, frozen-recipe import, checkpoint IO shared by every part |
| `pmsm_physics.py` | copy of the sl module, disclosed in its docstring |
| `sparsity.py` | mask generation (whole sessions first, then contiguous blocks), manifest hashing, mask IO shared by all seven rungs |
| `pinn_interventions.py` | $\lambda$ strategies (fixed, uncertainty-weighted, GradNorm-lite), term-ablation configs, collocation-density configs, each a config plus runner |
| `uncertainty.py` | seed-ensemble assembly from Part 4 checkpoints, split-conformal calibration on validation sessions, coverage and width computation |
| `metrics.py` | ladder aggregation across (rung, level, seed), degradation-curve statistics |
| `report_figures.py` | figure builders for script 06 |

### Folder structure (the ol/ul root, exactly)

```
ol-report/
├── artifacts/                    # sparsity mask manifests, frozen lambda winner, calibration tables
├── checkpoints/                  # intervention + ladder checkpoints
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

## 5. Invariants (script 08)

1. Carried-over foundation matches sl manifests exactly (no resample, no resplit).
2. Sparsity masks shared: per (level, seed) all seven rungs trained on the identical mask hash.
3. Same test set everywhere: identical test rows and sessions across all levels and models.
4. Ladder coverage: 105 rows in the Part 4 test table.
5. Test isolation: a/b column discipline holds for every part.
6. Recipes frozen: no hyperparameter differs from sl's exported recipes.
7. $\lambda$ pilot ran on validation only and its frozen winner is recorded.
8. Multi-seed coverage for every condition.
9. Deterministic torch enabled.
10. Conformal calibration used validation sessions only, and the calibration set is disjoint from every mask (source-verified).
11. `HYPOTHESES.md` contains H1-H6 and is unchanged since the 2026-08-15 freeze, dated amendments excepted.

## 6. Budgets, phases, risks

Budgets identical to sl-report, disclosed in constants. Compute accounting records epochs, gradient evaluations, boosting rounds, and wall-clock per condition. Part 4 is the expensive part (105 conditions, estimated overnight-safe on this Mac with the sl sample caps, B0 costing seconds per fit).

| Phase | Deliverable | Gate |
|---|---|---|
| A | Scaffold + foundation check (00) | invariant 1 passes |
| B | Part 1 pilot + weighting + notebook 01 | invariant 7 passes |
| C | Parts 2-3 + notebooks 02-03 | invariants 5-6 pass |
| D | Part 4 ladder + notebook 04 | invariants 2-4, 8 pass |
| E | Part 5 uncertainty + notebook 05 | invariant 10 passes |
| F | Sensor ablation (04c) + figures + repro + invariants + README | 11/11 PASS |

Risks: 105-condition wall-clock (B0 is seconds per fit, the rest mitigated by sample caps and frozen recipes, worst case drop to 4 levels, pre-registered as the only permitted shrink). PINN instability at 1 % labels (gradient clipping, best-val restore, seed spread reported honestly). Conformal exchangeability is imperfect on grouped time series, so coverage is reported per session with the caveat stated.
