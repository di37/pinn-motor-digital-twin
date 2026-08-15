# UL Report Hypotheses - Structure in the Permanent Magnet Synchronous Motor (PMSM) Operating Space

**Frozen: 2026-08-15. This file is the pre-registration of record for this study.**

Freeze rule: no silent edits, ever. If a hypothesis turns out ill-posed, the correction is a dated entry under Amendments, disclosed in the report. Evidence available at freeze time: the study plans, the dataset first-look scan (row and session counts, units, value ranges), and the literature index. No EDA notebook had run and no line of model code existed.

## Hypotheses

- **H1:** the strongest cluster structure follows control mode, not thermal state. Silhouette-selected k lands at 2-4 (MTPA vs field weakening and load splits), and alignment with thermal-state annotations stays weak (NMI below 0.2).
- **H2:** PCA compresses hard. 3-4 components reach 95 % variance because the dq equations couple the electrical signals.
- **H3:** at matched dimensionality ICA components align better with physical drivers (loss terms, excitation) than PCA components, measured by correlation against physics-derived features.
- **H4:** DR costs temperature more than torque downstream. `pm` MAE rises by over 15 % under RP at the shared dimension while torque rises by under 5 %.
- **H5:** GMM with full covariance beats K-Means on likelihood-based selection but not on regime alignment. The envelope is elliptical, not spherical, yet regimes are what labels care about.
- **H6:** temporal smoothing pays. The HMM's regimes align with the thermal-state annotations at least 0.1 NMI better than the best pointwise method, because heating and cooling are properties of trajectories, not points.

## Resolution protocol

Each hypothesis is resolved accept, reject, or qualify in the study's closing notebook, with the numeric criteria above taken literally. A claim stands only if the three-seed spread supports it. The foundation script verifies this file is unchanged since the freeze (amendments excepted), and the invariant suite checks it exists and contains every hypothesis.

## Amendments

None.
