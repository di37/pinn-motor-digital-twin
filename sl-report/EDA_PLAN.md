# SL Report - EDA Plan for the Permanent Magnet Synchronous Motor (PMSM) Dataset

**Status: PLAN - awaiting approval. Executed by notebooks 01-02 and scripts 00a-00c.**
**Date: 2026-08-15. Companion to [PLAN.md](PLAN.md). Method source: the OMSCS 7641 EDA guide (sites.gatech.edu/omscs7641, "Beginner's Guide to Exploratory Data Analysis", Jan 2026).**

The guide's core claim drives this plan: the quality and structure of the data affect performance more than the choice of algorithm, and modeling without understanding invites spurious correlations and leakage. EDA here is the open-ended investigation phase. The pre-registered hypotheses are the confirmatory side. The two never blur: H1-H5 are already frozen in `reports/HYPOTHESES.md` (2026-08-15), so EDA observations cannot silently reshape them. If EDA reveals a hypothesis was ill-posed, the change lands as a dated amendment in that file and is disclosed in the report. Nothing modeled in EDA touches the test sessions.

## 1. What this EDA must produce (the guide's four artifacts, mapped to files)

| Guide artifact | This study's file | Written by |
|---|---|---|
| Data dictionary (meaning, units, valid ranges, assumptions) | `reports/tables/eda_data_dictionary.csv` | notebook 01 |
| Data quality report (missingness, duplicates, outliers, parsing) | `reports/tables/eda_quality_report.csv` + per-session `eda_session_quality.csv` | notebook 01 |
| Risk register (leakage risks, confounds, target ambiguity) | `reports/tables/eda_risk_register.csv` | notebook 02 |
| Modeling readiness decision | closing verdict cell of notebook 02, gating Phase C | notebook 02 |

Plus the guide's final checklist items: the preprocessing plan (notebook 02, frozen into `00c`), a deliberately simple baseline benchmark (Section 5), and reproducibility (the notebooks re-run top to bottom on the committed processed data, seeds fixed).

## 2. The nine-phase workflow, adapted to sessions

The guide's ordering is kept exactly, because early issues distort downstream findings: **Shape → Types → Missingness → Duplicates → Target sanity → Leakage scan → Distributions → Relationships → Baseline**. The adaptation is that this data is 69 time-series sessions, not independent rows, so several phases get a per-session twin.

| Phase | What to check here | Red flags specific to this dataset | Lands in |
|---|---|---|---|
| 1. Shape | 1,330,816 × 13 against the fingerprint, session count, rows per session, implied duration at 2 Hz | session row counts that imply non-2 Hz sampling, sessions under a few minutes | notebook 01, section 5 |
| 2. Schema sanity | dtypes (12 float, 1 int key), no timestamp column exists so time is implicit in row order | `profile_id` parsed as float, any non-monotonic or missing row ordering within a session | notebook 01, section 6 |
| 3. Missingness | per-column and per-session (first look found zero, verify and document) | all-or-nothing blocks inside sessions, sensor dropouts disguised as frozen values (repeated identical readings) | notebook 01, section 7 |
| 4. Duplicates & keys | exact duplicate rows (first look: zero), `profile_id` as the only key, near-duplicate sessions (same drive cycle recorded twice) | near-duplicate sessions crossing the train/test split would inflate metrics exactly as the guide warns | notebook 01, section 8 |
| 5. Target integrity | ranges and physical plausibility of all five targets, per-session torque quality, label balance analog = coverage of the operating envelope | temperatures outside [0, 200] °C, torque beyond ±300 Nm, sessions where torque freezes or contradicts `i_q` sign | notebook 01, section 9 |
| 6. Leakage scan | structural: no future-encoding features exist in the raw columns, so the risks are session overlap between splits, near-duplicate sessions, and any preprocessing fit outside train | EWMA spans or scalers fit on all sessions, any feature computed across session boundaries | notebook 01, section 10, re-checked on the sample in notebook 02 |
| 7. Distributions | histograms and boxplots per signal, per-session temperature trajectories, stationarity eyeball (temps trend, currents do not) | impossible values (`i_d` > 0 breaks the MTPA expectation from the first look, coolant above 102 °C), heavy skew worth a transform note | notebook 01, section 11, repeated on the sample in notebook 02 |
| 8. Relationships | correlation matrix, torque vs `i_q` and vs $i_d i_q$, `pm` vs coolant and vs $i_s^2$ lagged, PCA pair-plot glance (shared with ul's H2 expectation) | the guide's "too perfect" flag needs domain reading here: torque tracking `i_q` at r near 1 is physics, not leakage. Genuinely suspicious would be `pm` predictable from a single instantaneous signal | notebook 02, relationships section |
| 9. Baseline (optional in the guide, mandatory here) | Section 5 | near-perfect one-step persistence is expected for slow thermal states and must not be sold as skill | notebook 02, closing sections |

## 3. Univariate, bivariate, multivariate plan

- **Univariate:** summary statistics and histograms for all 12 signals, boxplots per signal, per-session duration and coverage bars. Skew and range notes feed the preprocessing plan.
- **Bivariate:** scatter plots for the physics pairs (torque vs `i_q`, `u_q` vs speed, `pm` vs coolant), correlation and covariance tables, cross-session comparison of the same pairs to show session-to-session spread.
- **Multivariate:** pair plot on a seeded row subsample, a first PCA variance curve (read-only glance, the real study is ul's), and speed-load envelope occupancy maps that later parts reuse (ol sparsity masks, xai residual maps).

## 4. Time-series specifics the guide's tabular framing does not cover

- **Implied clock.** There is no timestamp column. The 2 Hz rate is an assumption inherited from the dataset documentation, so it goes into the data dictionary as an assumption, checked for consistency against session row counts and the thermal time constants the trajectories display.
- **Session boundaries are hard walls.** Every rolling or lagged quantity resets per session. The leakage scan verifies no computed artifact crosses a boundary.
- **Frozen-sensor screening.** Run-length statistics per signal per session catch stuck sensors, which pointwise missingness cannot see.
- **Stationarity split.** Electrical signals should look stationary within operating points, temperatures should not. The distributions phase documents this split because it justifies the EWMA features and the thermal ODE residual later.

## 5. The baseline benchmark (kept deliberately simple)

Three baselines, all trained on training sessions only, evaluated on validation sessions, never on test:

1. **Persistence:** $\mathrm{pm}(t+\Delta) = \mathrm{pm}(t)$ at horizons of 1 step and 5 minutes. The 1-step version will look near-perfect and is the guide's leakage-smell lesson stated in advance: slow states make trivial predictors look strong.
2. **Ambient anchor:** predict each temperature as a linear function of coolant and ambient only. What "no electrical information" buys.
3. **Physics one-liner:** torque from `i_q` alone by least squares. The near-perfect fit expected here is physics, and the gap to the full torque equation quantifies what `i_d` and saturation add.

These three set the floor every Part 2 rung must clear, and they are cheap enough to live inside the EDA notebook as the guide intends.

## 6. Common traps, read against this dataset

- **Correlation vs causation:** coolant correlates with `pm` partly because load profiles drive both. The confound is noted in the risk register, not resolved in EDA.
- **Over-removing outliers:** field-weakening transients and speed reversals are true operating points, not errors. Outlier rules must cite a physical bound before removing anything, and removals are logged in the quality report.
- **Imputation without pattern inspection:** the first look found zero missing values, so the expected decision is "no imputation". If frozen-sensor screening finds disguised gaps, the pattern gets inspected before any fill.
- **Unintended leakage:** the EWMA spans chosen in notebook 02 are fit on training sessions only, and the choice is recorded in the preprocessing plan.
- **Single-visualization reliance:** every Observations cell pairs its figure with the matching statistic table, per the house notebook convention.

## 7. Execution map and gate

- Script `00a` writes the fingerprint that phase 1 checks against. Notebook 01 runs phases 1-7 on the full file and closes by designing the working sample.
- Script `00b` draws the sample. Notebook 02 re-runs the audit on the sample, adds phases 8-9, writes the risk register and preprocessing plan, and ends with the modeling readiness verdict.
- Script `00c` freezes the splits and the preprocessing stats, and verifies the frozen `HYPOTHESES.md` is unchanged. Confirmatory work starts only after the verdict cell reads ready.
- Invariant hooks: the fingerprint check (invariant 1), sample and split manifests (2), train-only preprocessing (4), and the hypotheses freeze (11) are the machine-checked shadow of this plan.
