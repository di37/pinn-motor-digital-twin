# OL Report - Optimization & Uncertainty: Permanent Magnet Synchronous Motor (PMSM) Physics under Label Scarcity

The project's headline study. The exact working sample, splits, preprocessing, tuned recipes, and checkpoints are carried over unchanged from `../sl-report`, so every result is attributable to the intervention. Five parts: $\lambda$-weighting pilot and comparison on the fixed PINN, physics-term ablation, collocation density, the 105-condition sparsity ladder (7 rungs × 5 label levels × 3 seeds), and predictive uncertainty via seed ensembles with split-conformal intervals.

**Status: planned, not yet executed. Runs after sl-report. Design in [PLAN.md](PLAN.md).**

## Setup

```bash
conda env create -f environment-macos.yaml
conda activate pinn-ol
```

## Data (carried over from sl-report)

This study does not resample or re-split. Scripts read `../sl-report/data/processed/` and the sl frozen recipes and checkpoints. Sparsity masks are generated here, manifest-hashed, and shared across all seven rungs.

## Run

```bash
python scripts/00_confirm_foundation.py                                                          # foundation check + verify frozen HYPOTHESES.md
python scripts/01c_part1_lambda_pilot.py                                                         # pilot on val, freeze winner
python scripts/01a_part1_lambda_train.py          && python scripts/01b_part1_lambda_test.py     # Part 1
python scripts/02a_part2_ablation_train.py        && python scripts/02b_part2_ablation_test.py   # Part 2
python scripts/03a_part3_collocation_train.py     && python scripts/03b_part3_collocation_test.py  # Part 3
python scripts/04a_part4_sparsity_train.py        && python scripts/04b_part4_sparsity_test.py   # Part 4 (headline)
python scripts/04c_part4_sensor_ablation.py                                                      # Part 4 EC variant
python scripts/05a_part5_uncertainty_calibrate.py && python scripts/05b_part5_uncertainty_test.py  # Part 5

python scripts/06_make_report_figures.py
python scripts/07_build_repro_artifacts.py
python scripts/08_verify_invariants.py            # prints PASS/FAIL, 11 invariants
```

Notebooks 00-05 present the results (00 protocol, 01 weighting, 02 ablation, 03 collocation, 04 sparsity ladder, 05 uncertainty and synthesis).

## Outputs

`reports/figures/`, `reports/tables/`, `reports/logs/`, `reports/repro/`, `checkpoints/`, `artifacts/` (masks, frozen $\lambda$, calibration).
