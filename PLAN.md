# PINN Project - Master Plan: Five Studies on a Permanent Magnet Synchronous Motor (PMSM) Digital Twin

**Status: PLANS - awaiting approval. No code has been written yet. The raw dataset is downloaded.**
**Date: 2026-08-15**

Umbrella research question:

> **Can Physics-Informed Neural Networks build accurate PMSM digital twins under scarce supervision?**

The project is split into five sibling studies, mirroring the CS 7641 repository layout (`sl-report` / `ol-report` / `ul-report` side by side in one repo, each self-contained, later studies carrying the earlier data foundation over unchanged). Each study has its own `PLAN.md`, scripts, notebooks, invariants, and report. This file is the map.

## The five studies

| Report | Study | Research question | Depends on |
|---|---|---|---|
| [sl-report](sl-report/PLAN.md) | Supervised Learning | Which of eight rungs, from a pure-physics LPTN to a structured-coupled hybrid, predicts torque and temperatures best when labels are abundant? | nothing |
| [ol-report](ol-report/PLAN.md) | Optimization & Uncertainty | How do physics-loss weighting, term ablation, collocation, and label scarcity move the fixed models, and do conformal intervals stay honest as labels shrink? The headline sparsity ladder lives here | sl (data, recipes, checkpoints) |
| [ul-report](ul-report/PLAN.md) | Unsupervised Learning | What structure exists in the PMSM operating space before labels are used, pointwise and temporal, and what do compressed representations cost downstream? | sl (data) |
| [fe-report](fe-report/PLAN.md) | Feature Engineering | Which engineered, selected, and transformed feature sets earn their place, and can physics-derived features replace temporal memory? | sl (data, recipes) |
| [xai-report](xai-report/PLAN.md) | Explainable AI | What did each model actually learn, and do explanations survive sparsity? | sl + ol (checkpoints) |

Execution order for the paper: **sl → ol → xai**. ul and fe are deferred to post-paper execution (2026-08-15, second reviewer, scope): they run after xai completes, in either order, with their plans and frozen hypotheses unchanged.

## Shared spine (fixed across all five studies)

- **Dataset:** Kaggle `wkirgsn/electric-motor-temperature` (Paderborn LEA test bench), version 3, `measures_v2.csv`, 300 MB. Downloaded 2026-08-15 to `sl-report/data/raw/`. First-look confirmed: 1,330,816 rows × 13 columns, 69 sessions, 184.8 h at 2 Hz, physical units (°C, V, A, rpm, Nm), torque 100 % present, zero NaNs, zero duplicates. sl-report owns the foundation. Every other study reads `../sl-report/data/processed/` and never re-samples or re-splits, exactly how ol/ul carried sl's Covertype sample.
- **Working sample (revised 2026-08-15, ~100k rows):** about 10 % of the full file (~14 h). Forty sessions are drawn stratified by duration and envelope coverage with `SAMPLING_SEED = 746601`, then one seeded contiguous block per session, block length proportional to session length, scaled to `SAMPLE_TARGET_ROWS = 100,000`. Blocks preserve the native 2 Hz continuity the residuals and windows need, and all forty sessions stay represented, so the grouped splits are 19 train / 3 stopping (`VAL_STOP`) / 9 conformal-calibration (`VAL_CAL`) / 9 test sessions with `SPLIT_SEED = 746602`. Nine calibration sessions is the theoretical minimum for finite 90 % split-conformal intervals, and nine test sessions make session-level coverage assessable in 11.1 % steps. State-bearing rungs initialize from measured block-start temperatures at full supervision, and from mask-visible labels only under ol's sparsity masks (ol invariant 12). A pre-registered adequacy gate in sl notebook 02 (envelope, thermal-arc capture, curvature) decides whether the 100k spec stands. If it fails, execution pauses and the decision returns to the user: keep 100k with disclosed limitations, or the full dataset. No intermediate fallback is pre-committed. **Outcome (2026-08-16): the gate failed (G1 coolant shift 0.122, G2 arc capture 0.253, G3 passed), the user chose the full dataset, and the operative grouped split is 32/5/16/16, frozen in `split_manifest.json`.**
- **Seeds:** base **7466** ("PINN" on a phone keypad). `SAMPLING_SEED = 746601`, `SPLIT_SEED = 746602`, `SEEDS = (7466, 7467, 7468)` everywhere, widened to five seeds (7466-7470) at ol's 3 % and 1 % sparsity levels (2026-08-15, third reviewer).
- **Physics:** one authoritative module, `sl-report/src/pmsm_physics.py` (dq voltage equations, torque equation, LPTN thermal ODEs, residuals). Studies that need it copy it into their own `src/` and disclose the copy, matching the family's self-contained-`src` convention.
- **Targets:** `torque`, `pm`, `stator_winding` from free inverter inputs (`u_d, u_q, i_d, i_q, motor_speed, ambient, coolant`). Headline targets `pm` and `torque`. `stator_tooth` and `stator_yoke` were dropped as modeling targets on 2026-08-15 (second reviewer, scope) and remain audited signals in the EDA.
- **Model ladder (fixed across studies):** B0 LPTN (pure physics) → B1 XGBoost → B2 MLP → B3 LSTM → B4 Transformer → B5 TNN (learned thermal state, the published SOTA family on this dataset) → P PINN (soft coupled physics) → P2 structured hybrid (TNN backbone + soft electromagnetic residuals + affine parameter head). Eight rungs. The grid spans thermal injection {soft, hard} by electromagnetic coupling {absent, present as soft residuals}: B5 = (hard, absent), P = (soft, present), P2 = (hard, present), and no rung has hard electromagnetic structure. P2 minus B5 isolates the coupling, P2 minus P isolates the thermal mechanism.
- **Primary metric:** validation MAE on `pm`, declared once per study in `constants.py`, used for every selection. Reported metrics: MAE, RMSE, $R^2$, max absolute error.
- **House conventions (from CS 7641):** `constants.py` single source of truth. `run_logging.py` with `banner(phase=...)`, `logged_run`, `tee_to_logfile`, 7-day log pruning. a/b script split with one test contact per part. Pilot-then-freeze for method knobs. Per-study pre-registered hypotheses frozen at plan time (2026-08-15) in `reports/HYPOTHESES.md`, verified unchanged by the foundation script and an invariant, amendments dated and disclosed. Make-figures / build-repro / verify-invariants script tail numbered exactly `06`/`07`/`08` in every study, as in ol and ul, with PASS/FAIL and non-zero exit. Experiment scripts stay within `00`-`05`, carry part names in their filenames (`01a_part1_lambda_train.py`), and cover a whole part's grid in one a/b pair via condition builders (the ul `04a` pattern). Letter suffixes mark pilots and variants (`01c`, `04c`), the ol/ul way. Three-seed stability. Deterministic torch. Google-style docstrings with `# region` markers. sl-style notebooks: numbered sections, `### Observations` after every figure, hypothesis up front, verdict at the close, predicted-vs-measured overlay at the end.
- **Writing voice (all prose, everywhere):** short declarative sentences in active voice, claim-first Observation headings with numbers inline, honest scope statements, no hype adjectives. **No em dashes** (spaced hyphen or restructure). **Semicolons rare** (split the sentence instead). **No typographic shorthand symbols** (§, ¶, †, and the like): write the word, "section 5" not "§5". **Math is LaTeX**: display equations as `$$` blocks, physical quantities inline as `$...$`, while dataset column names stay in code backticks (`u_d`, `i_d`, `pm`), so formatting distinguishes quantity from column. Titles spell out Permanent Magnet Synchronous Motor (PMSM) in full, and the acronym is used everywhere after.
- **Environments:** one conda env per study (`pinn-sl`, `pinn-ol`, `pinn-ul`, `pinn-fe`, `pinn-xai`), macOS run of record plus Linux spec, pins recorded per study by its repro script. The pins are expected to be near-identical. Per-study envs mirror the family convention (`cs7641-a1`, `cs7641-a2`, `cs7641-ul`).

## Repository layout

```
pinn-project-eee/
├── PLAN.md                          # this master plan
├── WORKLOG.md                       # project-level worklog, one dated entry per task
├── .gitignore                       # raw data, caches, transient logs, reference PDFs
├── research-paper/                  # 17 reference papers (peer-reviewed venues documented per entry, 3 competing-work preprints) + index README
├── sl-report/                       # foundation + supervised model ladder (owns data/)
├── ol-report/                       # optimization, weighting, ablation, sparsity ladder
├── ul-report/                       # clustering + dimensionality reduction
├── fe-report/                       # feature engineering, selection, transformation
└── xai-report/                      # explanations and their stability
```

One git repository at the project root, matching the coursework repo (one repo, report folders inside). The repository name is **`pinn-motor-digital-twin`** (decided 2026-08-15). The local folder stays `pinn-project-eee`, local and remote names do not need to match. Folder casing is lowercase `xai-report` for consistency with the family naming.

Every report folder carries the exact ol/ul root, in the same listing order as the coursework repo on GitHub:

```
<study>-report/
├── artifacts/                    # study-specific saved artifacts (ul convention)
├── checkpoints/                  # saved models (absent only in xai-report, which trains nothing)
├── notebooks/
├── reports/
│   ├── figures/
│   ├── tables/
│   ├── logs/
│   ├── repro/
│   └── HYPOTHESES.md             # frozen at plan time, verified unchanged at run time
├── scripts/
├── src/
├── PLAN.md
├── README.md
├── WORKLOG.md
├── environment-linux.yaml
├── environment-macos.yaml        # run of record (Apple Silicon, MPS)
├── requirements-linux.txt
└── requirements-macos.txt
```

sl-report additionally owns `data/raw` (gitignored) and `data/processed` (committed), exactly as the coursework sl-report did. Each plan shows its own filled-in copy of this tree.

## Paper scope (added 2026-08-15 after the novelty review)

The five studies are the project. The paper is narrower. Its central contribution, stated once here and reused verbatim wherever the project describes itself:

> A controlled empirical study of whether coupled electromagnetic-thermal physics improves PMSM digital-twin accuracy, uncertainty, parameter stability, and interpretability as temperature labels become scarce. The paper draws from sl (the ladder and the identification), ol (the sparsity ladder and uncertainty), and xai Parts 2-3 (physics-native explanation and stability under sparsity), plus one fe result (H5, physics through the inputs vs physics through the loss). ul and the rest of fe are supporting studies, deferred to post-paper execution: they feed the appendix and the portfolio, not the paper's core claims. The reports must position against the directly-competing papers listed in `research-paper/README.md`.

## Approval and sequencing

Each study's plan carries its own phases and gates. Approving a study means its phases run start to finish before the next study begins, the same one-report-at-a-time rhythm as the coursework. The sl-report plan is the one to approve first, since everything else carries its foundation.

The target-scope question is resolved (2026-08-15): three targets, `pm` + `torque` + `stator_winding`.
