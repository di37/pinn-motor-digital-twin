# SL Report - Supervised Learning: the Permanent Magnet Synchronous Motor (PMSM) Model Ladder at Full Supervision

**Status: PLAN - awaiting approval. No code written. Raw data downloaded to `data/raw/measures_v2.csv`.**
**Date: 2026-08-15. Study 1 of 5, see the [master plan](../PLAN.md).**

Research question:

> **Which model family predicts PMSM torque and internal temperatures best when labels are abundant, and does physics help or hurt when data is not the bottleneck?**

This study owns the project's data foundation (fetch, fingerprint, working sample, splits, EDA) and runs the eight-rung supervised comparison at 100 % supervision, from pure physics to pure data and back to structure: LPTN → XGBoost → MLP → LSTM → Transformer → TNN → PINN → structured-coupled hybrid. Every later study carries this foundation over unchanged, exactly how ol/ul carried sl's Covertype sample in CS 7641. The PINN enters here as the final rung with fixed scale-normalized physics weights. Its training interventions are ol-report's subject, not this study's.

## 1. Data foundation (owned here, used by all five studies)

- **Raw:** Kaggle `wkirgsn/electric-motor-temperature` v3, `measures_v2.csv` (300 MB), already in `data/raw/`. First-look confirmed 1,330,816 rows × 13 columns, 69 sessions, 184.8 h at 2 Hz, physical units, torque 100 % present, zero NaNs, zero duplicates. Script `00a` re-verifies and writes the formal fingerprint.
- **Working sample (revised 2026-08-15, ~100k rows):** `SAMPLE_SESSIONS = 40` sessions drawn from the 69 with `SAMPLING_SEED = 746601`, stratified by session duration and envelope coverage (speed and max `pm` terciles), then `SAMPLE_TARGET_ROWS = 100,000` filled by one seeded contiguous block per sampled session, block length proportional to session length (roughly 13 % of each). Contiguous blocks, never scattered rows, because the physics residuals and windows need unbroken 2 Hz runs. State-bearing rungs (B0, B5, P2) initialize from the measured temperatures at each block's first row. The known cost, disclosed: thermal arcs longer than a block are cut, which weighs on the long-memory rungs and is reported, not hidden. This spec is a candidate: the pre-registered sample-adequacy gate in [EDA_PLAN.md](EDA_PLAN.md) section 8 (envelope, thermal-arc capture, curvature) is evaluated in notebook 02. If every criterion passes, the 100k spec stands. If any fails, execution pauses at the verdict cell and the decision returns to the user: keep 100k with the failures disclosed as limitations, or move to the full dataset. No intermediate design is pre-committed. Preliminary numbers (arc capture near 0.21 against the 0.6 threshold) suggested the gate would reach that decision point, and it did: measured 0.253 with a 0.122 coolant quantile shift, and the recorded decision (2026-08-16) is the full dataset.
- **Splits (revised 2026-08-16, seventh review):** session-grouped, `SPLIT_SEED = 746602`, the 40 sampled sessions split 19 train / 3 `VAL_STOP` (early stopping, recipe export, ol's pilot) / 9 `VAL_CAL` (reserved untouched for ol's session-level conformal calibration, nine being the minimum for finite 90 % intervals, $n \geq 1/\alpha - 1$) / 9 test (nine so session-level coverage moves in 11.1 % steps and the H6 acceptance is assessable). No `profile_id` crosses splits, and calibration residuals never come from sessions that steered model selection. If the gate decision moves to the full dataset, the split re-scales with `VAL_CAL` and test each keeping at least nine sessions. **Outcome (2026-08-16): the gate failed G1 and G2, the user chose the full dataset, and the operative split is 32 train / 5 `VAL_STOP` / 16 `VAL_CAL` / 16 test, frozen in `split_manifest.json` and verified in notebook 02b.** Preprocessing (standardization, EWMA spans) fit on training sessions only. Processed parquet plus `fingerprint.json`, `sample_manifest.json`, `split_manifest.json` are committed under `data/processed/`.
- **Inputs:** `u_d, u_q, i_d, i_q, motor_speed, ambient, coolant`. **Targets:** `torque`, `pm`, `stator_winding`, headline `pm` and `torque`. `stator_tooth` and `stator_yoke` were dropped as modeling targets on 2026-08-15 (scope) and stay in the EDA as audited signals.

## 2. Physics foundation (authoritative module lives here)

`src/pmsm_physics.py` is the single source of truth: dq voltage equations, torque equation, LPTN thermal ODEs, residual functions, and unit tests. Studies that need it (ol, xai) copy it into their own `src/` and disclose the copy.

$$
\begin{aligned}
v_d &= R_s i_d + L_d \frac{di_d}{dt} - \omega_e L_q i_q \\
v_q &= R_s i_q + L_q \frac{di_q}{dt} + \omega_e \left(L_d i_d + \psi_f\right), \qquad \omega_e = p\,\omega_m
\end{aligned}
$$

$$
T_e = \tfrac{3}{2}\, p \left[\, \psi_f\, i_q + (L_d - L_q)\, i_d\, i_q \,\right]
$$

$$
\begin{aligned}
C_r \frac{dT_r}{dt} &= P_{\mathrm{loss},r} - \frac{T_r - T_s}{R_{\mathrm{th},rs}} - \frac{T_r - T_{\mathrm{cool}}}{R_{\mathrm{th},rc}} \\
C_s \frac{dT_s}{dt} &= P_{\mathrm{loss},s} + \frac{T_r - T_s}{R_{\mathrm{th},rs}} - \frac{T_s - T_{\mathrm{cool}}}{R_{\mathrm{th},sc}}, \qquad
P_{cu} = \tfrac{3}{2} R_s \left(i_d^2 + i_q^2\right), \quad P_{fe} \propto \omega_e^{\,a}
\end{aligned}
$$

**Temperature-affine parameters (built into the PINN head, read out in xai):**

$$
R_s(T_s) = R_{s0}\left(1 + \alpha_{cu}(T_s - T_{\mathrm{ref}})\right), \qquad \psi_f(T_r) = \psi_{f0}\left(1 + \alpha_{mag}(T_r - T_{\mathrm{ref}})\right)
$$

with $\alpha_{cu} \approx +0.39\,\%/\mathrm{K}$ for copper and $\alpha_{mag} < 0$ for NdFeB remanence loss. The drift claim is then about learned coefficients, not post-hoc refits.

Timescale argument: at 2 Hz the electrical dynamics (L/R in ms) are quasi-static, so the voltage residuals take their algebraic form (di/dt ≈ 0). Thermal dynamics (minutes to hours) stay ODE-form with finite-difference dT/dt within sessions. The synthetic track exercises the full dynamic residuals at high sample rate. Identifiability: with pole pairs $p$ unknown, the voltage equations identify the products $p L_d$, $p L_q$, $p \psi_f$. Part 1 fixes which combinations are reported, and literature nameplate values (Kirchgässner et al.) are recorded with sources in `study_metadata.json`.

## 3. Parts

- **Part 0 - Foundation.** Strictly ordered: fetch and fingerprint, full-file EDA, draw the working sample, sample EDA with the sample-vs-full similarity comparison and the adequacy gate, and only then the train/val/test split. No split exists until the sample has passed the comparison or the gate decision is recorded. The EDA follows its own companion plan, [EDA_PLAN.md](EDA_PLAN.md), built on the OMSCS 7641 EDA guide's nine-phase workflow and four deliverables, adapted to time-series sessions.
- **Part 1 - Synthetic twin validation (diagnostic).** `src/synthetic_twin.py` simulates drive cycles with known ~50 kW-class parameters. Residual unit tests must pass at ground truth, and both parameter-bearing learners (P and P2) must recover $R_s, L_d, L_q, \psi_f$ in closed loop under the amended per-parameter tolerances. No real-data test contact.
- **Part 2 - The model ladder at full labels.** Fairness rule: every learned model sees the same engineered features and labels. Sequence models add raw windows (W = 128 samples = 64 s). The PINN shares the MLP's exact inputs and trunk, so physics-in-the-loss is the only difference. B2 and P additionally share an identical labeled-batch schedule (same batches, same order, same optimizer-step count on labeled data), so P's collocation batches are the disclosed intervention itself rather than a hidden optimization advantage, and per-rung gradient evaluations land in the compute accounting. Hyperparameter selection uses the same grouped CV folds for every rung, so no rung's recipe benefits from a luckier validation surface. The ladder now spans the full spectrum from pure physics to pure data, and each rung differs from its neighbors by one capability.

| # | Model | Temporal context | Notes |
|---|---|---|---|
| B0 | LPTN (pure physics) | ODE state, no learning | the LPTN thermal network plus the algebraic torque equation, parameters fitted by least squares on train. The physics floor |
| B1 | XGBoost | EWMA features only | EWMA features follow the dataset authors' own practice, not a strawman |
| B2 | MLP | EWMA features only | the direct no-physics control for the PINN |
| B3 | LSTM | raw window + EWMA | recurrent thermal memory |
| B4 | Transformer | raw window + EWMA | small encoder, 2-4 layers |
| B5 | TNN | ODE state, learned | thermal-neural-network family, the published state of the art on this dataset: LPTN state integrated forward in time with learned conductances, trained by truncated backprop through time |
| P | PINN | identical to B2 | MLP trunk + fixed scale-normalized physics residuals + a temperature-affine parameter head ($R_{s0}, \psi_{f0}, \alpha_{cu}, \alpha_{mag}, L_d, L_q$ all learnable) |
| P2 | Structured hybrid | ODE state, learned | the TNN backbone (hard thermal structure) plus soft electromagnetic residuals and the same affine parameter head. Hard thermal structure with soft electromagnetic coupling: P2 minus B5 isolates the coupling, P2 minus P isolates the thermal injection mechanism. No rung has hard electromagnetic structure, which would mean solving the circuit inside the model |

Small pre-registered tuning grids per model, selected by 5-fold `GroupKFold` cross-validation over the 19 training sessions, with mean CV validation MAE on `pm` as the selection criterion (the family's `CV_FOLDS = 5` convention). The validation sessions are not used for selection: `VAL_STOP` (3) serves early stopping, the frozen-recipe export, and later ol's pilot, while `VAL_CAL` (9) stays reserved for ol's conformal calibration. The held-out test stays untouched until `02b`. The tuned recipes are frozen and exported for ol/fe/xai reuse.
- **Part 2 diagnostics - learning and complexity curves.** For every rung, learning curves (performance vs training-session budget) and model-complexity curves (capacity sweeps: depth for XGBoost, width for the MLP trunk, hidden size for the sequence models), computed over the same `GroupKFold` folds so every curve carries a cross-fold spread, the coursework's CV-based curve convention. These were the analytical heart of the coursework sl notebooks and they are first-class parts here.
- **Coupling diagnostic (pre-registered, the first Phase D deliverable).** The logged signals decide whether the electromagnetic residuals actually reach the temperature heads: the magnitude of $\partial L_{vd,vq} / \partial \hat{T}$ across training, and the $\alpha_{cu}$ and $\alpha_{mag}$ trajectories ($\alpha_{cu}$ converging near $+0.39\,\%/\mathrm{K}$, $\alpha_{mag}$ staying negative, neither collapsing to zero). The gradient paths run through $R_s(\hat{T}_s)$ and $\psi_f(\hat{T}_r)$, and $\psi_f(\hat{T}_r)$ is the only electromagnetic path into the rotor temperature, the headline target. Degeneration means the restated ol H1 has no mechanism. `02a` writes all signals to `reports/tables/` per rung, and the finding is reported before ol runs.
- **Dimensionality tripwire (pre-registered decision rule, recalibrated 2026-08-15, third reviewer).** The PCA glance stays a reported diagnostic without a threshold, since EWMA features are smoothings of seven signals and any fixed variance cutoff is vacuous under that collinearity. The firing trigger is self-calibrating: at full supervision, a learned rung fires if its train-validation `pm` MAE gap exceeds three times the median gap across all learned rungs, which normalizes away the ordinary session-shift gap that grouped splits produce. The response is cheap by design: a correlation-pruned feature subset (pruned at $|\rho| > 0.95$ on train) run as a small disclosed addendum. fe stays deferred either way.
- **Part 3 (extra credit, optional) - Activation study.** ReLU, GELU, SiLU, and tanh on the shared MLP trunk, the direct analog of the coursework's activation extra credit. Runs only if the schedule allows after the paper-critical parts.

## 4. Pre-registered hypotheses (frozen 2026-08-15 in `reports/HYPOTHESES.md`, verified unchanged by `00c`)

- **H1:** at full supervision the stateful models (LSTM, Transformer, TNN) match or beat the PINN on `pm` (thermal memory wins when labels are abundant), and every neural model beats XGBoost on `pm`.
- **H2:** torque is near-algebraic given currents: every model reaches $R^2$ above 0.98 on it.
- **H3 (amended 2026-08-15, see `reports/HYPOTHESES.md`):** from full-rate synthetic data the PINN recovers all four parameters within 5 % relative error at full labels. From 2 Hz-downsampled synthetic data it recovers $R_s$ and $\psi_f$ within 5 % and $L_d$ and $L_q$ within 15 %. The rate comparison is itself a reported identifiability result.
- **H4:** at full supervision the PINN neither beats nor trails its MLP control on `pm` by more than 10 % MAE. Physics is insurance, not a data substitute, when data is plentiful.
- **H5 (amended 2026-08-15, see `reports/HYPOTHESES.md`):** the physics floor and ceiling bracket the field. B0 trails every learned model on `pm` by over 20 % MAE at full supervision, and the TNN is the strongest rung without electromagnetic coupling.
- **H6 (added by dated amendment 2026-08-15):** structure and coupling stack. At full supervision P2 matches or beats both B5 and P on `pm` MAE.

## 5. Scripts and notebooks

```
scripts/
├── 00a_fetch_and_fingerprint.py  # Part 0: verify raw file, fingerprint, session inventory
├── 00b_draw_working_sample.py    # Part 0: stratified 40-session block sample, ~100k rows (SAMPLING_SEED)
├── 00c_make_splits.py            # Part 0: grouped splits, preprocessing stats, verify frozen HYPOTHESES.md
├── 01a_part1_generate_synthetic.py       # Part 1: simulate drive cycles, known parameters
├── 01b_part1_synthetic_validation.py     # Part 1: residual sanity + closed-loop recovery (diagnostic)
├── 02a_part2_ladder_train.py     # Part 2: all 8 rungs × 3 seeds via condition builders (ul 04a pattern)
├── 02b_part2_ladder_test.py      # the single test contact for Part 2
├── 03_part2_learning_curves.py   # Part 2 diagnostics: session-budget curves per rung (val only)
├── 04_part2_complexity_curves.py # Part 2 diagnostics: capacity sweeps per rung (val only)
├── 05_extra_credit_activations.py    # Part 3 EC: activation study on the shared trunk (val only)
├── 06_make_report_figures.py
├── 07_build_repro_artifacts.py
└── 08_verify_invariants.py

notebooks/
├── 01_full_dataset_eda.ipynb     # raw-file audit + sampling design (sl 01 analog)
├── 02_sample_eda_and_protocol.ipynb  # sample audit, split design, protocol, adequacy gate (sl 02 analog)
├── 02b_full_dataset_split_freeze.ipynb  # gate outcome, decision record, split verification (32/5/16/16)
├── 03_synthetic_twin_validation.ipynb
├── 04_lptn.ipynb … 11_structured_pinn.ipynb  # one per rung (04 lptn, 05 xgb, 06 mlp, 07 lstm, 08 transformer, 09 tnn, 10 pinn, 11 structured hybrid)
├── 12_extra_credit_activations.ipynb  # sl 07 analog (optional)
└── 13_discussion.ipynb           # cross-model synthesis + H1-H6 verdicts (sl 08 analog)
```

The `src/` contract is the ol/ul one exactly. `constants.py` is a stdlib-only leaf, cheap to import from anywhere, with `# region` groups and the sibling sl path resolved relative to `PROJECT_ROOT` behind an "update THIS ONE LINE" comment. `run_logging.py` imports only constants. Domain modules expose a frozen config dataclass plus a `run_<x>_condition(config)` function returning `(frame, summary)`, which is what `logged_run` times and prints. Scripts orchestrate, `src/` implements, notebooks only read saved outputs. Configs are immutable, functions return new objects, and no module holds mutable state.

| Module | Contents |
|---|---|
| `constants.py` | paths and dirs, seeds, sample/split sizes, input and target lists, EWMA spans, window length, tuning grids per rung, `CV_FOLDS = 5`, budgets, `PRIMARY_METRIC`, `REPORT_METRICS` |
| `run_logging.py` | `banner(phase=...)` with this study's protocol lines, `seed_header`, `logged_run`, `log_saved`, `log_saved_artifact`, `log_detail`, `_Tee` + `tee_to_logfile`, 7-day pruning. `_result_fields` reads this study's summary keys (`val_mae_pm`, `test_mae_pm`, `fit_s`, `param_err_pct`) |
| `common.py` | raw-file fingerprinting, session inventory, stratified session sampling, grouped splits, session-grouped `GroupKFold` fold builder with fold manifest, parquet IO, preprocessing fit on train only, `write_summary_table`, warning silencers |
| `pmsm_physics.py` | `MotorParams` frozen dataclass, algebraic and dynamic voltage residuals, torque residual, LPTN right-hand side, copper and iron loss terms, residual unit-test helpers. The authoritative copy |
| `synthetic_twin.py` | drive-cycle builders (ramps, steps, soak), ODE integration at high rate, downsampling, synthetic dataset writer with known `MotorParams` |
| `features.py` | EWMA feature builder, lag and window tensor builders, per-rung feature assembly so every rung reads one shared representation |
| `lptn.py` | `LPTNConfig`, least-squares parameter fit on train, per-session ODE rollout prediction, `run_lptn_condition` |
| `boosted.py` | `XGBConfig`, `run_xgb_condition` with `hist`, early stopping on validation, boosting-round accounting |
| `neural_network.py` | `MLPConfig`, `LSTMConfig`, `TransformerConfig`, the one shared torch training loop (budgets, patience, best-val restore, gradient-eval accounting), `set_torch_seed` enabling deterministic algorithms |
| `tnn.py` | `TNNConfig`, the LPTN-structured recurrent cell, truncated backprop through time over sessions, `run_tnn_condition` |
| `pinn.py` | `PINNConfig`, MLP trunk plus a temperature-affine softplus-positive parameter head ($R_s(T)$ and $\psi_f(T)$ through learnable $\alpha_{cu}$, $\alpha_{mag}$), composite loss with fixed scale-normalized weights, collocation hooks (exercised by ol), `run_pinn_condition` |
| `structured_pinn.py` | `StructuredPINNConfig` for P2: the TNN thermal cell plus electromagnetic residual heads plus the affine parameter head, truncated backprop through time, `run_structured_pinn_condition` |
| `metrics.py` | per-target MAE, RMSE, $R^2$, max absolute error, cross-seed aggregation, synthetic parameter-recovery errors |
| `report_figures.py` | every figure builder for script 06, one function per figure, saving to `reports/figures/` |

### Folder structure (the ol/ul root, exactly)

```
sl-report/
├── artifacts/                    # synthetic dataset, fitted scalers, exported frozen recipes
├── checkpoints/                  # ladder checkpoints (<rung>_seed<seed>.pt)
├── data/
│   ├── raw/                      # measures_v2.csv (gitignored, verified by 00a)
│   └── processed/                # working-sample + split parquet, fingerprint/sample/split manifests (committed)
├── notebooks/
├── reports/
│   ├── figures/                  # PNG, prefixed by notebook/part number
│   ├── tables/                   # CSV/JSON summary tables
│   ├── logs/                     # tee'd run logs, auto-pruned after 7 days
│   ├── repro/                    # run_commands, compute_accounting, environment_versions, study_metadata, inventory
│   └── HYPOTHESES.md             # frozen 2026-08-15, verified unchanged by 00c
├── scripts/
├── src/
├── EDA_PLAN.md                   # nine-phase EDA plan (OMSCS 7641 guide, adapted to sessions)
├── PLAN.md
├── README.md                     # living document, finalized when the study completes
├── WORKLOG.md                    # dated entry per task, newest first, updated the day work happens
├── environment-linux.yaml
├── environment-macos.yaml        # run of record (Apple Silicon, MPS)
├── requirements-linux.txt
└── requirements-macos.txt
```

`data/` exists only in this study (the coursework sl-report owned it the same way). Every sibling reads `../sl-report/data/processed/`.

## 6. Invariants (script 08)

1. Dataset fingerprint matches the raw file.
2. Working data matches `sample_manifest.json` exactly (session ids, block offsets, block lengths, row count), where the manifest records the spec the adequacy-gate decision produced, whether the 100k candidate or the full dataset.
3. Grouped split: no session crosses splits, sizes match `split_manifest.json`.
4. Preprocessing fit on training sessions only (source-verified, scaler hash matches).
5. Test isolation: a-tables carry no `test_*` columns, b-tables no `val_*` columns.
6. Synthetic residual sanity below tolerance at ground truth.
7. Synthetic parameter recovery within the amended per-parameter H3 tolerances, for both P and P2.
8. All eight rungs × 3 seeds present in the Part 2 test table (B0's fit is deterministic, its rows differ only by seed bookkeeping).
9. Recipes identical across seeds per model (no per-seed tuning).
10. Deterministic torch enabled after seeding.
11. `HYPOTHESES.md` contains H1-H6 (H6 by dated amendment) and is unchanged since the 2026-08-15 freeze, dated amendments excepted.
12. Selection by grouped CV: every tuned recipe was chosen on `GroupKFold` folds drawn from training sessions only, and no fold contains a validation or test session (source-verified against the committed fold manifest).

## 7. Budgets, phases, risks

- **Budgets:** neural 150 epochs max, early-stop patience 20 on validation loss. XGBoost 2000 rounds max, 100-round early stopping. Per-epoch sample cap by seeded sampler. Compute accounting per condition to `reports/repro/compute_accounting.csv`.
- **Environment:** conda `pinn-sl`, macOS run of record (MPS) + Linux spec. Pins: python 3.12, torch 2.7.x, numpy 2.x, pandas, scipy, scikit-learn, xgboost 2.x, matplotlib, pyarrow, jupyter, kagglehub.

| Phase | Deliverable | Gate |
|---|---|---|
| A | Scaffold: git init (project root), layout, constants, run_logging, envs | imports clean |
| B | Part 0 scripts + EDA notebooks 01-02 + frozen-hypotheses verification | invariants 1-4, 11 pass |
| C | Part 1 synthetic + notebook 03 | invariants 6-7 pass |
| D | Coupling diagnostic first, then Part 2 ladder (02a/02b) + diagnostics (03, 04) + notebooks 04-11 | invariants 5, 8-10, 12 pass |
| E | Optional extra credit (05) + figures + repro + full invariant suite + notebooks 12-13 + README | 12/12 PASS |

Risks: per-session torque quality (audited in notebook 01, flagged sessions excluded from torque supervision with disclosure). Laptop compute (sample caps, small tuned-once architectures). PINN instability (residual scale normalization, gradient clipping, synthetic unit tests first). TNN is a from-scratch implementation of a published family, mitigated by truncated backprop through time and by validating its thermal integrator on the synthetic track before real data. P2 is the least de-risked model in the project and is staged strictly after B5 passes that synthetic validation, reusing the same integrator tests plus the Part 1 parameter-recovery gate.

## 8. Open questions

1. Target scope: resolved 2026-08-15, trimmed to `pm` + `torque` + `stator_winding` (second reviewer, scope).
2. Git: one repository at the project root, initialized in Phase A. Assumed yes.
