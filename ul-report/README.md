# UL Report - Unsupervised Learning: Structure in the Permanent Magnet Synchronous Motor (PMSM) Operating Space

What structure exists in the PMSM sensor space before labels are used, and what compressed representations cost downstream. K-Means and GMM/EM on the original features, a Gaussian HMM as the temporal method, PCA / ICA / Randomized Projections, re-clustering after each reduction, and the sl MLP re-trained per representation. Targets and physically derived regime annotations (control mode, load, thermal state) enter only after fitting, as external evidence.

**Status: planned, not yet executed. Runs after sl-report (needs only its data). Design in [PLAN.md](PLAN.md).**

## Setup

```bash
conda env create -f environment-macos.yaml       # adds umap-learn and hmmlearn
conda activate pinn-ul
```

## Data (carried over from sl-report)

Scripts read `../sl-report/data/processed/`. No resampling, no re-splitting. Regime annotations are derived from inputs only and frozen before any clustering.

## Run

```bash
python scripts/00_confirm_foundation.py           # foundation check + regime annotations + verify frozen HYPOTHESES.md
python scripts/01_part1_clustering_original.py    && python scripts/01b_part1_hmm_regimes.py     # Part 1
python scripts/02_part2_dim_reduction.py                                                         # Part 2
python scripts/03_part3_clustering_after_dr.py                                                   # Part 3
python scripts/04a_part4_nn_train.py              && python scripts/04b_part4_nn_test.py         # Part 4 (one test contact)
python scripts/05_extra_credit_manifold.py                                                       # Part 5 EC

python scripts/06_make_report_figures.py
python scripts/07_build_repro_artifacts.py
python scripts/08_verify_invariants.py            # prints PASS/FAIL, 12 invariants
```

Notebooks 00-05 present the results (00 protocol, 01 clustering, 02 DR, 03 re-clustering, 04 NN after DR with synthesis, 05 manifold extra credit).

## Outputs

`reports/figures/`, `reports/tables/`, `reports/logs/`, `reports/repro/`, `checkpoints/`, `artifacts/` (reducers, representations, embeddings).
