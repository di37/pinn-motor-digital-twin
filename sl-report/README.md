# SL Report - Supervised Learning: the Permanent Magnet Synchronous Motor (PMSM) Model Ladder at Full Supervision

Seven-rung supervised comparison on the PMSM test-bench dataset, spanning pure physics to pure data: LPTN → XGBoost → MLP → LSTM → Transformer → TNN → PINN. This study owns the project's data foundation (fingerprint, 40-session stratified working sample, session-grouped splits, leakage-safe preprocessing) and every sibling study carries it over unchanged. The PINN enters with fixed scale-normalized physics weights, so its training interventions stay in ol-report. A synthetic twin with known parameters validates the physics residuals and the parameter recovery before any real-data run.

**Status: planned, not yet executed. Design in [PLAN.md](PLAN.md), EDA method in [EDA_PLAN.md](EDA_PLAN.md).**

## Setup

```bash
conda env create -f environment-macos.yaml   # run of record (Apple Silicon, MPS)
conda activate pinn-sl
```

(`environment-linux.yaml` and the requirements files arrive in Phase A.)

## Data

`data/raw/measures_v2.csv` (Kaggle `wkirgsn/electric-motor-temperature` v3, 300 MB, already downloaded, not committed). Script `00a` verifies it against the committed fingerprint. Processed sample and splits land in `data/processed/` and are committed so a clean checkout reproduces everything downstream.

## Run

The pipeline is the numbered scripts in `scripts/`, run in order:

```bash
python scripts/00a_fetch_and_fingerprint.py       && python scripts/00b_draw_working_sample.py   # Part 0
python scripts/00c_make_splits.py                                                                # Part 0 + verify frozen HYPOTHESES.md
python scripts/01a_part1_generate_synthetic.py    && python scripts/01b_part1_synthetic_validation.py  # Part 1
python scripts/02a_part2_ladder_train.py          && python scripts/02b_part2_ladder_test.py     # Part 2 (7 rungs x 3 seeds)
python scripts/03_part2_learning_curves.py        && python scripts/04_part2_complexity_curves.py  # Part 2 diagnostics
python scripts/05_extra_credit_activations.py                                                    # Part 3 EC

python scripts/06_make_report_figures.py
python scripts/07_build_repro_artifacts.py
python scripts/08_verify_invariants.py            # prints PASS/FAIL, 11 invariants
```

Notebooks 01-12 present the same results with narrative (01 full-dataset EDA, 02 sample EDA and protocol, 03 synthetic validation, 04-10 one per rung, 11 activation extra credit, 12 discussion). Open from `notebooks/` and run top to bottom.

## Outputs

`reports/figures/` (PNG), `reports/tables/` (CSV/JSON), `reports/logs/` (auto-pruned run logs), `reports/repro/` (seeds, commands, compute accounting, environment versions), `checkpoints/`, `artifacts/`.
