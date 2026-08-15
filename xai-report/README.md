# xAI Report - Explaining the Permanent Magnet Synchronous Motor (PMSM) Digital Twin

What each model actually learned about the motor, and whether explanations survive label sparsity. This study trains nothing. It audits the saved checkpoints from sl (full supervision) and ol (sparsity ladder): TreeSHAP and channel-level permutation importance on shared validation windows, the four-way LPTN/TNN/PINN/P2 physical-parameter cross-check, physics-residual maps over the operating envelope, temperature-dependent parameter drift, and attribution stability across sparsity levels. The defining discipline: zero test contact anywhere.

**Status: planned, not yet executed. Runs last (needs sl and ol checkpoints). Design in [PLAN.md](PLAN.md).**

## Setup

```bash
conda env create -f environment-macos.yaml       # adds shap
conda activate pinn-xai
```

## Data (carried over)

Scripts read `../sl-report/data/processed/`, sl and ol checkpoints in place, and ol mask manifests. Every attribution is computed on validation data only.

## Run

```bash
python scripts/00_confirm_and_inventory.py        # foundation check + checkpoint inventory + verify frozen HYPOTHESES.md
python scripts/01_part1_attributions.py           # Part 1 (validation only)
python scripts/02_part2_physics_native.py         # Part 2 (parameter cross-check, residual maps, drift)
python scripts/03_part3_stability_under_sparsity.py  # Part 3 (reads ol checkpoints)
python scripts/04_part4_physics_consistency.py    # Part 4
python scripts/05_extra_credit_counterfactuals.py # EC

python scripts/06_make_report_figures.py
python scripts/07_build_repro_artifacts.py
python scripts/08_verify_invariants.py            # prints PASS/FAIL, 9 invariants
```

Notebooks 00-04 present the results (00 inventory, 01 attributions, 02 physics-native explanations, 03 stability, 04 physics consistency with synthesis).

## Outputs

`reports/figures/`, `reports/tables/`, `reports/logs/`, `reports/repro/`, `artifacts/` (importance vectors, residual-map grids, cross-check tables). No `checkpoints/`: nothing is trained here.
