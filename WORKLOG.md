# Worklog - Project Root

Newest day first. Every task that changes this folder gets an entry the same day: what was done, why when it matters, and the files touched. If it happened and left no worklog line, it did not happen.

## 2026-08-15

- **Repository named.** `pinn-motor-digital-twin`, recorded in the master plan. The local folder stays `pinn-project-eee`. Git init still lands in sl Phase A.
- **Planning sketch retired.** `physics-informed-pmsm-digital-twin.png` moved to the Trash after its diagram, loss, and ladder were redrawn in the README. One caveat recorded: the screenshot's bottom paragraph was cut off and never recovered.
- **Stale paper counts fixed.** The master plan and root README trees said 13 peer-reviewed references while the index records 17 with mixed review status. Both now match the index. Flagged by the reviewer.
- **Novelty-review changes applied (all five).** Competing-work sweep added to the literature index (3 stored, 2 listed), umbrella framing retitled from sparse sensors to scarce supervision, sl H3 amended to per-parameter tolerances, the PINN parameter head made temperature-affine with xai H4 restated on learned coefficients, and a paper-scope section added to the master plan (paper = sl + ol + xai Parts 2-3 + fe H5).
- **PINN paper of record added to the literature base.** The published JCP version (merging arXiv Parts I and II) supplied by the user, verified, renamed, and indexed. `research-paper/` now holds 14 papers.
- **Hypotheses frozen across all five studies.** Each study's `reports/HYPOTHESES.md` written and frozen (sl H1-H5, ol H1-H6, ul H1-H6, fe H1-H5, xai H1-H5). Foundation scripts flip from writing to verifying. Plans, READMEs, and the EDA plan updated to match.
- **Architecture diagram redrawn in the README.** The planning sketch (`physics-informed-pmsm-digital-twin.png`) recreated as an ASCII diagram in the root README with the composite loss, labels aligned to the dataset's real signals.
- **Worklogs created.** This file plus one per report folder and one in `research-paper/`. The always-update rule is now standing practice for every task.
- **`.gitignore` created.** Ignores the raw CSV, caches, transient logs, and reference PDFs. Processed data and checkpoints stay committed, family convention.
- **READMEs written.** Root plus all five studies, in the family README structure (abstract, Setup, Data, Run, Outputs) with honest plan-stage status lines.
- **Literature base built.** `research-paper/` with 13 peer-reviewed papers (arXiv author copies) and a venue-documented index. Raissi Part II (discovery) added on review.
- **EDA plan written.** `sl-report/EDA_PLAN.md` following the OMSCS 7641 nine-phase EDA guide, adapted to time-series sessions.
- **Titles fixed.** Permanent Magnet Synchronous Motor (PMSM) spelled out in every title. Typographic shorthand symbols banned after a § slipped into the EDA plan.
- **`src/` contents specified.** Module-by-module tables in every plan under the ol/ul contract (stdlib-only constants leaf, frozen configs, `(frame, summary)` runners).
- **Script frame aligned to ol/ul exactly.** Experiment scripts within 00-05, part names in filenames, condition-builder grouping, tail always 06/07/08. Folder-structure trees added to every plan from the GitHub screenshot.
- **Four upgrades folded in.** Seven-rung ladder (LPTN pure-physics floor, TNN state-of-the-art family), conformal uncertainty in ol, HMM temporal regimes in ul, three-way parameter cross-check in xai.
- **Project split into five studies.** sl / ol / ul / fe / xai, each with its own PLAN.md, mirroring the coursework repo layout. Master PLAN.md as the map. Data moved to `sl-report/data/`.
- **Dataset downloaded and verified.** Kaggle `wkirgsn/electric-motor-temperature` v3, 1,330,816 × 13, 69 sessions, 184.8 h at 2 Hz, physical units, torque 100 % present. Two plan risks retired.
- **Project started.** PMSM digital twin concept reviewed from the planning screenshot. Monolithic plan drafted, then iterated: sl-report conventions absorbed (EDA audit, per-model notebooks, primary-metric rule), writing voice codified (no em dashes, rare semicolons), sample EDA stage added, explainability made a study.
