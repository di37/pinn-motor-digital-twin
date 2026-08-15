# OL Report Hypotheses - Permanent Magnet Synchronous Motor (PMSM) Physics under Label Scarcity

**Frozen: 2026-08-15. This file is the pre-registration of record for this study.**

Freeze rule: no silent edits, ever. If a hypothesis turns out ill-posed, the correction is a dated entry under Amendments, disclosed in the report. Evidence available at freeze time: the study plans, the dataset first-look scan (row and session counts, units, value ranges), and the literature index. No EDA notebook had run and no line of model code existed.

## Hypotheses

- **H1 (headline):** the PINN degrades most gracefully. At 3 % labels and below it beats every other rung on both `pm` and `torque`, with the margin over the data-driven models growing monotonically as labels shrink. B0 stays flat but never wins, because it cannot learn what the LPTN leaves out.
- **H2:** adaptive λ weighting beats fixed scale-normalized weights on validation loss and cross-seed stability.
- **H3:** term ablation is target-specific. Removing `L_thermal` hurts `pm` under sparsity more than removing the voltage residuals hurts torque.
- **H4:** collocation earns its keep only under sparsity. At full labels 0× vs 4× differs by under 5 % MAE, at 3 % labels 4× beats 0× by over 15 %.
- **H5:** baseline degradation is not seed noise. At 1 % labels every data-driven rung's cross-seed MAE spread is smaller than its gap to the PINN.
- **H6:** intervals stay honest, and physics keeps them tight. Split-conformal coverage holds within 5 points of the 90 % target for every rung at every level, and the PINN's interval width at 1 % labels is under 1.5× its full-label width while every data-driven rung's exceeds 3×.

## Resolution protocol

Each hypothesis is resolved accept, reject, or qualify in the study's closing notebook, with the numeric criteria above taken literally. A claim stands only if the three-seed spread supports it. The foundation script verifies this file is unchanged since the freeze (amendments excepted), and the invariant suite checks it exists and contains every hypothesis.

## Amendments

None.
