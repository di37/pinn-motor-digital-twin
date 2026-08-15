# FE Report Hypotheses - Feature Engineering for the Permanent Magnet Synchronous Motor (PMSM) Digital Twin

**Frozen: 2026-08-15. This file is the pre-registration of record for this study.**

Freeze rule: no silent edits, ever. If a hypothesis turns out ill-posed, the correction is a dated entry under Amendments, disclosed in the report. Evidence available at freeze time: the study plans, the dataset first-look scan (row and session counts, units, value ranges), and the literature index. No EDA notebook had run and no line of model code existed.

## Hypotheses

- **H1:** EWMA dominates raw. F1 beats F0 on `pm` MAE by over 30 % for every evaluator.
- **H2:** physics features substitute for memory in part. F3 closes at least half of the MLP-to-LSTM `pm` gap that exists on F1.
- **H3:** a compact set suffices. `F5` (15 features max) reaches at least 95 % of F4's performance for every evaluator.
- **H4:** physics beats blind compression. At matched dimensionality `F5` beats PCA-transformed features on `pm` for every evaluator.
- **H5:** engineered inputs help more as labels shrink, but less than physics losses do. F3's margin over F1 grows from full labels to 3 %, yet stays smaller than the PINN-over-MLP margin ol measures at the same levels.

## Resolution protocol

Each hypothesis is resolved accept, reject, or qualify in the study's closing notebook, with the numeric criteria above taken literally. A claim stands only if the three-seed spread supports it. The foundation script verifies this file is unchanged since the freeze (amendments excepted), and the invariant suite checks it exists and contains every hypothesis.

## Amendments

None.
