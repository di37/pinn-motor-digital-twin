# Worklog - sl-report

Newest day first. Every task that changes this folder gets an entry the same day: what was done, why when it matters, and the files touched. If it happened and left no worklog line, it did not happen.

## 2026-08-15

- **H3 amended and the PINN head upgraded.** H3 tolerances made per-parameter via a dated amendment (2 Hz identifiability, novelty-review input). The PINN spec now carries a temperature-affine parameter head with learnable `α_cu` and `α_mag`, so drift is learned, not refit.
- **Hypotheses frozen.** `reports/HYPOTHESES.md` written and frozen with the study's pre-registered hypotheses. The foundation script now verifies it unchanged instead of writing it. Amendments must be dated, never silent.
- **README.md written.** Family structure, plan-stage status, run-of-record script sequence.
- **EDA_PLAN.md written.** Nine-phase workflow from the OMSCS 7641 EDA guide mapped to notebooks 01-02 and scripts 00a-00c, with time-series adaptations (implied 2 Hz clock, session walls, frozen-sensor screening, stationarity split) and three floor baselines.
- **PLAN.md restructured to the exact ol/ul frame.** Ladder collapsed to one a/b pair (`02a/02b`) with condition builders, learning curves (03) and complexity curves (04) promoted to first-class diagnostics, activation study as extra credit (05), tail at 06/07/08. Folder tree and `src/` module table added.
- **Ladder extended to seven rungs.** B0 LPTN pure-physics floor and B5 TNN (published state of the art on this dataset) added, H5 pre-registered.
- **PLAN.md created.** Foundation ownership (fingerprint, 40-session sample, grouped splits), synthetic twin validation, physics module as single source of truth, H1-H4, 11 invariants.
- **Data landed.** `data/raw/measures_v2.csv` downloaded (300 MB, Kaggle v3) and first-look verified.
