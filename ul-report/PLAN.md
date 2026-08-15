# UL Report - Unsupervised Learning: Structure in the Permanent Magnet Synchronous Motor (PMSM) Operating Space

**Status: PLAN - awaiting approval. Deferred to post-paper execution (2026-08-15, second reviewer, scope): runs after sl, ol, and xai complete.**
**Date: 2026-08-15. Study 3 of 5, see the [master plan](../PLAN.md).**

Research question:

> **What structure exists in the PMSM sensor space before labels are used, does it align with physical operating regimes, and what does dimensionality reduction cost downstream?**

The direct analog of the CS 7641 UL study, on drive data instead of cartography. The working sample, splits, and preprocessing come from `../sl-report` unchanged. Targets are used only after unsupervised fitting, as external evidence. Within the paper scope defined in the master plan this is a supporting study: its results feed the appendix, the paper's core claims live in sl, ol, and xai. The physical labels here are not classes but regime annotations derived from the signals themselves: control mode (MTPA vs field weakening from `i_d` and speed), load terciles, and thermal state (heating, steady, cooling from the temperature trends).

## 1. Carried over from sl-report

Processed sample and splits from `../sl-report/data/processed/`, seeds `(7466, 7467, 7468)`, logging and invariant conventions. Labels (`torque`, temperatures) and regime annotations enter only post-hoc.

## 2. Parts

- **Part 0 - Foundation check (diagnostic).** Confirm carried-over data, derive and freeze the regime annotations, verify the frozen `HYPOTHESES.md` is unchanged.
- **Part 1 - Clustering on original features.** K-Means and GMM/EM over `K_VALUES = (2 … 15)`, full covariance sweep for GMM. Internal metrics (silhouette, Davies-Bouldin, Calinski-Harabasz, BIC) drive selection. Regime annotations evaluate alignment post-hoc (ARI, NMI). Noise-robustness check at relative noise levels (0, 0.05, 0.10, 0.20, 0.40). A Gaussian HMM runs alongside as the temporal method: states swept over the same range per session, transition matrix analyzed for block structure, alignment scored on the same post-hoc protocol. Pointwise clustering ignores time, and this dataset is nothing but time.
- **Part 2 - Dimensionality reduction.** PCA (variance targets 0.90/0.95/0.99), ICA (kurtosis and component stability), Randomized Projections (distance preservation over 5 RP seeds). The physics prior says the 7 inputs plus derived features live near a low-dimensional manifold because the dq equations couple them. Component counts justified per method.
- **Part 3 - Re-clustering after DR.** Same clustering protocol on PCA/ICA/RP representations, one shared protocol table, original vs reduced compared.
- **Part 4 - Downstream NN after DR.** The sl MLP recipe re-trained on {original, PCA, ICA, RP} representations, only the input dimension changing. Preprocessing and DR fit on the training split only. Held-out test touched exactly once, in `04b`.
- **Part 5 (extra credit, optional) - Nonlinear manifolds.** UMAP and Isomap on a row subsample, trustworthiness vs PCA, envelope structure visualized.

## 3. Pre-registered hypotheses

- **H1:** the strongest cluster structure follows control mode, not thermal state. Silhouette-selected k lands at 2-4 (MTPA vs field weakening and load splits), and alignment with thermal-state annotations stays weak (NMI below 0.2).
- **H2:** PCA compresses hard. 3-4 components reach 95 % variance because the dq equations couple the electrical signals.
- **H3:** at matched dimensionality ICA components align better with physical drivers (loss terms, excitation) than PCA components, measured by correlation against physics-derived features.
- **H4:** DR costs temperature more than torque downstream. `pm` MAE rises by over 15 % under RP at the shared dimension while torque rises by under 5 %.
- **H5:** GMM with full covariance beats K-Means on likelihood-based selection but not on regime alignment. The envelope is elliptical, not spherical, yet regimes are what labels care about.
- **H6:** temporal smoothing pays. The HMM's regimes align with the thermal-state annotations at least 0.1 NMI better than the best pointwise method, because heating and cooling are properties of trajectories, not points.

## 4. Scripts and notebooks

```
scripts/
├── 00_confirm_foundation.py      # carried-over check + regime annotations + verify frozen HYPOTHESES.md
├── 01_part1_clustering_original.py
├── 01b_part1_hmm_regimes.py      # temporal regime discovery (Gaussian HMM per session)
├── 02_part2_dim_reduction.py
├── 03_part3_clustering_after_dr.py
├── 04a_part4_nn_train.py / 04b_part4_nn_test.py
├── 05_extra_credit_manifold.py
├── 06_make_report_figures.py
├── 07_build_repro_artifacts.py
└── 08_verify_invariants.py

notebooks/
├── 00_foundation_and_protocol.ipynb
├── 01_clustering_original.ipynb
├── 02_dimensionality_reduction.ipynb
├── 03_clustering_after_dr.ipynb
├── 04_nn_after_dr.ipynb              # + study synthesis
└── 05_extra_credit_manifold.ipynb
```

`src/` mirrors the CS 7641 ul-report module set nearly one to one, under the same contract (stdlib-only constants leaf, frozen configs, `(frame, summary)` runners).

| Module | Contents |
|---|---|
| `constants.py` | sl sibling paths, `K_VALUES`, GMM covariance types, HMM state grid, PCA variance targets, ICA and RP component grids, RP seeds, noise levels, subsample sizes |
| `run_logging.py` | family pattern, `_result_fields` reads `silhouette`, `bic`, `ari`, `nmi`, `cum_var`, `kurtosis`, `dist_ratio`, `test_mae_pm` |
| `common.py` | loaders for sl processed data, seeded row subsampling for $O(n^2)$ metrics, `write_summary_table` |
| `regimes.py` | regime annotations from inputs only (control mode, load terciles, thermal state), frozen artifact IO |
| `clustering.py` | K-Means and GMM sweep configs and runners |
| `hmm.py` | Gaussian HMM per session, state sweep, transition-matrix summaries |
| `cluster_metrics.py` | internal metrics block, external alignment block, noise-robustness harness |
| `dimensionality_reduction.py` | PCA, ICA, RP fit and transform with `fit_on="train"` discipline |
| `dr_diagnostics.py` | explained variance, kurtosis and component stability, distance-preservation ratios |
| `neural_network.py` | the sl MLP recipe re-run on each representation, `set_torch_seed` |
| `manifold.py` | UMAP and Isomap on subsamples, trustworthiness |
| `report_figures.py` | figure builders for script 06 |

### Folder structure (the ol/ul root, exactly)

```
ul-report/
├── artifacts/                    # fitted reducers, transformed representations, manifold embeddings
├── checkpoints/                  # NN-after-DR checkpoints
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

1. Carried-over foundation matches sl manifests (no resample, no resplit).
2. Regime annotations derived from inputs only, frozen before clustering, and never used for fitting or selection.
3. Clustering coverage: K-Means, GMM, and HMM all present, at least 2 internal and 1 external metric.
4. DR coverage: PCA, ICA, RP present, RP over at least 2 seeds.
5. Part 3 covers all (space × algorithm) pairs.
6. Downstream NN on all four representations with the identical sl recipe.
7. Label discipline: DR tables carry no label metrics, selection is label-free (source-verified).
8. Downstream leakage control: preprocessing and DR fit on train only.
9. Test isolation: only `04b` touches test.
10. Multi-seed coverage (NN seeds, RP seeds).
11. Deterministic execution.
12. `HYPOTHESES.md` contains H1-H6 and is unchanged since the 2026-08-15 freeze, dated amendments excepted.

## 6. Budgets, phases, risks

Clustering and DR run on the working sample (CPU, minutes per condition). Part 4 reuses the sl NN budget. Environment `pinn-ul` adds umap-learn and hmmlearn.

| Phase | Deliverable | Gate |
|---|---|---|
| A | Scaffold + foundation check + regime annotations | invariants 1-2 pass |
| B | Parts 1-2 (including HMM) + notebooks 01-02 | invariants 3-4, 7 pass |
| C | Parts 3-4 + notebooks 03-04 | invariants 5-6, 8-10 pass |
| D | Part 5 + figures + repro + invariants + README | 12/12 PASS |

Risks: silhouette on the ~100k-row sample is $O(n^2)$ (computed on seeded row subsamples, disclosed, same as the family's EC subsampling). Regime annotations could be circular if derived carelessly (they use inputs only, invariant 2 guards it).
