# xAI Report Hypotheses - Explaining the Permanent Magnet Synchronous Motor (PMSM) Digital Twin

**Frozen: 2026-08-15. This file is the pre-registration of record for this study.**

Freeze rule: no silent edits, ever. If a hypothesis turns out ill-posed, the correction is a dated entry under Amendments, disclosed in the report. Evidence available at freeze time: the study plans, the dataset first-look scan (row and session counts, units, value ranges), and the literature index. No EDA notebook had run and no line of model code existed.

## Hypotheses

- **H1:** at full supervision every model's `pm` attributions are physically plausible: coolant and current magnitude rank in the top 5 channels for all seven rungs.
- **H2 (headline):** explanations collapse before accuracy does. For every baseline the Spearman correlation between its 100 % and 1 % importance vectors falls below 0.5, while the PINN's learned parameters at 1 % stay within 25 % of their full-supervision values.
- **H3:** residual maps localize physics stress. Voltage-residual density is at least 3× higher in the field-weakening region than in MTPA, at every supervision level.
- **H4:** parameter drift follows material physics. Across temperature bands the fitted $R_s$ trend is positive and the fitted $\psi_f$ trend is negative, with signs stable across all 3 seeds.
- **H5:** the three physics-bearing models agree on the motor. LPTN, TNN, and PINN estimates of the shared thermal parameters lie within 30 % of one another at full supervision.

## Resolution protocol

Each hypothesis is resolved accept, reject, or qualify in the study's closing notebook, with the numeric criteria above taken literally. A claim stands only if the three-seed spread supports it. The foundation script verifies this file is unchanged since the freeze (amendments excepted), and the invariant suite checks it exists and contains every hypothesis.

## Amendments

- **2026-08-15 - H4 restated on learned coefficients.** The PINN's parameter head became temperature-affine by construction (sl spec change of the same date), so the primary claim is now: the learned $\alpha_{cu}$ is positive and the learned $\alpha_{mag}$ is negative, with signs stable across all 3 seeds, and per-temperature-band refits agree with the learned trends. The original band-fit phrasing stands recorded above, unedited.
- **2026-08-15 - Notation converted to LaTeX math.** Typographic conversion only, no claim, threshold, or wording of any hypothesis changed.
