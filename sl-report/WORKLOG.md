# Worklog - sl-report

Newest day first. Every task that changes this folder gets an entry the same day: what was done, why when it matters, and the files touched. If it happened and left no worklog line, it did not happen.

## 2026-08-16

- **Splits revised to 19/3/9/9.** GroupKFold now folds over 19 training sessions. Re-scaling rule added: VAL_CAL and test never drop below nine sessions under any gate outcome.

## 2026-08-15

- **Splits revised for conformal validity.** 22/3/9/6 sessions, GroupKFold now folds over 22 training sessions, VAL_CAL grows to nine.
- **Part 0 ordering made strict.** Sample-vs-full similarity comparison precedes the split, stated in the Part 0 bullet and the EDA execution map.
- **Fifth-review fixes.** VAL_STOP/VAL_CAL partition of the validation sessions, manifest-driven invariant 2, honest P2 labeling with a terminology-precision amendment.
- **Gate fallback removed.** Section 8 now pauses at the verdict cell on failure, user decides between 100k-with-limitations and the full dataset. No pre-committed intermediate design.
- **Grouped CV for selection.** 5-fold GroupKFold over training sessions selects every rung's recipe by mean CV validation MAE on pm. Learning and complexity curves become CV-based with cross-fold spread. Invariant 12 added, fold manifest committed.
- **Sample-adequacy gate added to the EDA plan (section 8).** Three pre-registered criteria with fixed thresholds, fallback fully specified, preliminary numbers say escalation is likely. Coupling diagnostic extended to α_mag, the only electromagnetic path into the rotor temperature.
- **Sample spec revised: 40-session block sample, ~100k rows.** Whole-session sampling replaced by proportional contiguous blocks. Invariant 2 and the sample manifest now carry block offsets and lengths.
- **Third-reviewer fixes.** H5 restated by amendment, P2 joins synthetic validation and invariant 7, coupling diagnostic pre-registered as the first Phase D deliverable, tripwire recalibrated, matched labeled-batch fairness added, P2 staged strictly after B5's synthetic gate.
- **Dimensionality tripwire added.** Pre-registered rule in the Parts section: PCA glance over 10 components for 95 % variance, or train-validation `pm` MAE gap over 30 %, pulls fe Part 2 forward before ol.
- **Eighth rung, target trim, H6.** P2 structured-coupled hybrid added (TNN backbone + electromagnetic residuals + affine head), targets trimmed to three, activation extra credit marked optional, H6 pre-registered by dated amendment.
- **Physics section converted to LaTeX.** All equation blocks, the affine parameter head, identifiability products, and hypothesis symbols now render as math. HYPOTHESES.md carries a notation-only amendment.
- **H3 amended and the PINN head upgraded.** H3 tolerances made per-parameter via a dated amendment (2 Hz identifiability, novelty-review input). The PINN spec now carries a temperature-affine parameter head with learnable `α_cu` and `α_mag`, so drift is learned, not refit.
- **Hypotheses frozen.** `reports/HYPOTHESES.md` written and frozen with the study's pre-registered hypotheses. The foundation script now verifies it unchanged instead of writing it. Amendments must be dated, never silent.
- **README.md written.** Family structure, plan-stage status, run-of-record script sequence.
- **EDA_PLAN.md written.** Nine-phase workflow from the OMSCS 7641 EDA guide mapped to notebooks 01-02 and scripts 00a-00c, with time-series adaptations (implied 2 Hz clock, session walls, frozen-sensor screening, stationarity split) and three floor baselines.
- **PLAN.md restructured to the exact ol/ul frame.** Ladder collapsed to one a/b pair (`02a/02b`) with condition builders, learning curves (03) and complexity curves (04) promoted to first-class diagnostics, activation study as extra credit (05), tail at 06/07/08. Folder tree and `src/` module table added.
- **Ladder extended to seven rungs.** B0 LPTN pure-physics floor and B5 TNN (published state of the art on this dataset) added, H5 pre-registered.
- **PLAN.md created.** Foundation ownership (fingerprint, 40-session sample, grouped splits), synthetic twin validation, physics module as single source of truth, H1-H4, 11 invariants.
- **Data landed.** `data/raw/measures_v2.csv` downloaded (300 MB, Kaggle v3) and first-look verified.
