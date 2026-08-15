# SL Report Hypotheses - the Permanent Magnet Synchronous Motor (PMSM) Model Ladder at Full Supervision

**Frozen: 2026-08-15. This file is the pre-registration of record for this study.**

Freeze rule: no silent edits, ever. If a hypothesis turns out ill-posed, the correction is a dated entry under Amendments, disclosed in the report. Evidence available at freeze time: the study plans, the dataset first-look scan (row and session counts, units, value ranges), and the literature index. No EDA notebook had run and no line of model code existed.

## Hypotheses

- **H1:** at full supervision the stateful models (LSTM, Transformer, TNN) match or beat the PINN on `pm` (thermal memory wins when labels are abundant), and every neural model beats XGBoost on `pm`.
- **H2:** torque is near-algebraic given currents: every model reaches $R^2$ above 0.98 on it.
- **H3:** the PINN recovers synthetic ground-truth $R_s, L_d, L_q, \psi_f$ within 5 % relative error at full labels.
- **H4:** at full supervision the PINN neither beats nor trails its MLP control on `pm` by more than 10 % MAE. Physics is insurance, not a data substitute, when data is plentiful.
- **H5:** the physics floor and ceiling bracket the field. B0 trails every learned model on `pm` by over 20 % MAE at full supervision, and the TNN is the strongest non-PINN temperature model.

## Resolution protocol

Each hypothesis is resolved accept, reject, or qualify in the study's closing notebook, with the numeric criteria above taken literally. A claim stands only if the three-seed spread supports it. The foundation script verifies this file is unchanged since the freeze (amendments excepted), and the invariant suite checks it exists and contains every hypothesis.

## Amendments

- **2026-08-15 - H3 tolerances made per-parameter.** Novelty-review input: at 2 Hz the electrical residuals are quasi-static, so $L_d$ and $L_q$ are identified only through the speed cross-coupling terms and recover more weakly than $R_s$ and $\psi_f$. H3 now reads: from full-rate synthetic data the PINN recovers all four parameters within 5 % relative error at full labels. From 2 Hz-downsampled synthetic data it recovers $R_s$ and $\psi_f$ within 5 % and $L_d$ and $L_q$ within 15 %. The comparison between the two rates is itself a reported identifiability result. The original uniform 5 % claim stands recorded above, unedited.
- **2026-08-15 - Notation converted to LaTeX math.** Typographic conversion only, no claim, threshold, or wording of any hypothesis changed.
- **2026-08-15 - Eighth rung, target trim, and H6 (second reviewer: scope and inductive bias).** The ladder gains P2, a structured-coupled hybrid (TNN backbone, electromagnetic residuals, affine parameter head), completing the two-by-two of injection mechanism by physics coverage. Targets are trimmed to `torque`, `pm`, `stator_winding` (`stator_tooth` and `stator_yoke` stay as audited EDA signals, and no frozen hypothesis referenced them). H1-H5 read on the original seven rungs as written. New pre-registered **H6**: structure and coupling stack, at full supervision P2 matches or beats both B5 and P on `pm` MAE.
- **2026-08-15 - H5 clause restated and P2 brought under synthetic validation (third reviewer).** H5's second clause becomes: the TNN is the strongest rung without electromagnetic coupling. That scopes cleanly on the eight-rung ladder, since P2 beating the TNN no longer falsifies it. P2's learnable $R_s, L_d, L_q, \psi_f$ join Part 1's closed-loop synthetic validation under the same per-parameter tolerances as the amended H3, so every estimator in xai's four-way cross-check is validated against ground truth. The original phrasings stand recorded above, unedited.
- **2026-08-15 - Terminology precision (fifth review).** P2's electromagnetic physics enters as soft residuals and its thermal physics as hard structure, so the earlier 'hard/coupled' framing reads correctly as: hard thermal structure with soft electromagnetic coupling. No rung carries hard electromagnetic structure. No claim, threshold, or comparison changes.
