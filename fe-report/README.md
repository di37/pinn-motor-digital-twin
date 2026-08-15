# FE Report - Feature Engineering, Selection, and Transformation for the Permanent Magnet Synchronous Motor (PMSM) Digital Twin

How far domain knowledge goes when injected through the inputs instead of the loss. Five feature families from raw signals to physics-derived terms (F0-F4), a consensus-selected compact set capped at 15 features (F5), scaling and transformation comparisons, and a sparsity bridge asking whether engineered inputs deliver part of what physics losses deliver. Evaluators are the frozen sl recipes for XGBoost, MLP, and LSTM, so only the feature set varies.

**Status: planned, deferred to post-paper execution. Runs after sl, ol, and xai complete. Design in [PLAN.md](PLAN.md).**

## Setup

```bash
conda env create -f environment-macos.yaml
conda activate pinn-fe
```

## Data (carried over from sl-report)

Scripts read `../sl-report/data/processed/` and the sl frozen recipes. All feature fitting happens on training sessions only. The Part 4 bridge additionally reads sparsity masks from `../ol-report/artifacts/` once ol has run.

## Run

```bash
python scripts/00_confirm_foundation.py           # foundation check + family freeze + verify frozen HYPOTHESES.md
python scripts/01a_part1_engineering_train.py     && python scripts/01b_part1_engineering_test.py  # Part 1 (F0-F4)
python scripts/02_part2_selection.py                                                             # Part 2 (writes F5)
python scripts/03a_part3_transformation_train.py  && python scripts/03b_part3_transformation_test.py  # Part 3
python scripts/04a_part4_sparsity_bridge_train.py && python scripts/04b_part4_sparsity_bridge_test.py  # Part 4
python scripts/05_extra_credit_interactions.py                                                   # EC

python scripts/06_make_report_figures.py
python scripts/07_build_repro_artifacts.py
python scripts/08_verify_invariants.py            # prints PASS/FAIL, 9 invariants
```

Notebooks 00-05 present the results (00 protocol, 01 engineering, 02 selection, 03 transformation, 04 sparsity bridge with synthesis, 05 interactions extra credit).

## Outputs

`reports/figures/`, `reports/tables/`, `reports/logs/`, `reports/repro/`, `checkpoints/`, `artifacts/` (family and F5 definitions, fitted transformers).
