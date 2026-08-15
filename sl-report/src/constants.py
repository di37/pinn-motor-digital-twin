"""Central constants for the SL study of the PMSM digital-twin project.

Single source of truth for every fixed path, seed, signal list, split count,
grid, budget, and pre-registered threshold used by the harness modules
(``common``, ``features``, the rung modules), the experiment scripts, and the
notebooks. Keeping them here prevents the drift where a value is redefined in
two places and silently diverges. This module imports only the standard
library, so it is cheap to import from anywhere, including torch-free tooling
such as the repro metadata builder.

Every number below traces to PLAN.md or EDA_PLAN.md, and several went through
dated review amendments (splits, tolerances, gate thresholds). Change them
there first, then here, never here alone.
"""

# region Imports
from __future__ import annotations

from pathlib import Path

# endregion

# region Repository layout
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
LOGS_DIR = REPORTS_DIR / "logs"
REPRO_DIR = REPORTS_DIR / "repro"
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

RAW_FILE = RAW_DIR / "measures_v2.csv"
HYPOTHESES_FILE = REPORTS_DIR / "HYPOTHESES.md"

# endregion

# region Dataset (expected fingerprint, verified by 00a against the raw file)
# First-look values from 2026-08-15. 00a fails loudly if the file on disk
# disagrees, so no later script ever runs on a silently different dataset.
EXPECTED_ROWS = 1_330_816
EXPECTED_SESSIONS = 69
SAMPLE_RATE_HZ = 2.0          # documented rate; there is no timestamp column
SESSION_KEY = "profile_id"

EXPECTED_COLUMNS = (
    "u_q", "coolant", "stator_winding", "u_d", "stator_tooth", "motor_speed",
    "i_d", "i_q", "pm", "stator_yoke", "ambient", "torque", "profile_id",
)

# Inputs are the free inverter-side signals. Targets are the expensive
# test-bench labels (trimmed to three on 2026-08-15, second reviewer). The two
# dropped stator temperatures stay in the EDA as audited signals only.
INPUT_SIGNALS = ("u_d", "u_q", "i_d", "i_q", "motor_speed", "ambient", "coolant")
TARGET_SIGNALS = ("torque", "pm", "stator_winding")
AUDIT_ONLY_SIGNALS = ("stator_tooth", "stator_yoke")

# endregion

# region Seeds
# Base 7466 spells PINN on a phone keypad, mirroring the coursework's 7641.
SAMPLING_SEED = 746601   # working-sample draw (sessions + block offsets)
SPLIT_SEED = 746602      # session-grouped splits + VAL partition + CV folds
MODEL_SEED = 7466
SEEDS = (MODEL_SEED, MODEL_SEED + 1, MODEL_SEED + 2)   # 3-seed stability set

# endregion

# region Working sample (candidate, judged by the EDA_PLAN section 8 gate)
SAMPLE_SESSIONS = 40          # stratified by duration and envelope coverage
SAMPLE_TARGET_ROWS = 100_000  # ~10 % of the file, one contiguous block per session

# Adequacy-gate thresholds (pre-registered in EDA_PLAN section 8; a failed
# gate PAUSES for the user's decision, no fallback design is pre-committed).
GATE_ENVELOPE_GRID = (20, 20)        # speed x torque occupancy grid
GATE_ENVELOPE_JACCARD_MIN = 0.90     # G1: occupied-cell overlap, sample vs full
GATE_QUANTILE_SHIFT_MAX = 0.05       # G1: p5/p95 shift as fraction of full range
GATE_ARC_CAPTURE_MIN = 0.60          # G2: median within-block pm excursion share
GATE_CURVATURE_DELTA_AIC = 10.0      # G3: first-order fit beats linear by this
GATE_CURVATURE_MIN_FRACTION = 0.50   # G3: in at least this share of blocks

# endregion

# region Splits (revised 2026-08-16, seventh review)
# 19 train / 3 VAL_STOP / 9 VAL_CAL / 9 test sessions. Nine calibration
# sessions is the minimum for finite 90 % session-level conformal intervals
# (n >= 1/alpha - 1), nine test sessions make session-level coverage
# assessable. Any full-dataset gate outcome keeps VAL_CAL and test >= 9.
N_TRAIN_SESSIONS = 19
N_VAL_STOP_SESSIONS = 3      # early stopping, recipe export, ol's pilot
N_VAL_CAL_SESSIONS = 9       # reserved untouched for ol's conformal calibration
N_TEST_SESSIONS = 9

# endregion

# region Features
# Candidate EWMA spans in samples at 2 Hz (4 s to ~8.5 min). The final set is
# justified on training sessions only, in notebook 02, and frozen there.
EWMA_SPAN_GRID = (8, 64, 256, 1024)
WINDOW_LEN = 128             # raw-window length for sequence rungs (64 s at 2 Hz)

# endregion

# region The ladder (eight rungs, fixed across studies)
RUNGS = (
    "lptn",             # B0  pure physics, least-squares fit
    "xgboost",          # B1
    "mlp",              # B2  the no-physics control for P
    "lstm",             # B3
    "transformer",      # B4
    "tnn",              # B5  hard thermal structure, no electromagnetics
    "pinn",             # P   soft coupled physics on the B2 trunk
    "structured_pinn",  # P2  hard thermal structure + soft electromagnetic residuals
)

# endregion

# region Tuning grids (pre-registered, selected by grouped CV, then frozen)
CV_FOLDS = 5                 # GroupKFold over the 19 training sessions

XGB_GRID = {"max_depth": (4, 6, 8), "learning_rate": (0.05, 0.10)}
MLP_GRID = {"width": (48, 64, 96), "lr": (3e-4, 1e-3), "dropout": (0.0, 0.1)}
LSTM_GRID = {"hidden": (32, 64), "lr": (3e-4, 1e-3)}
TRANSFORMER_GRID = {"d_model": (32, 64), "layers": (2, 3), "lr": (3e-4, 1e-3)}
TNN_GRID = {"lr": (3e-4, 1e-3), "tbptt_len": (128, 256)}
# P shares the MLP trunk grid so physics stays the only difference vs B2.
# P2 shares the TNN grid so structure comparisons stay clean vs B5.

# endregion

# region Budgets (fixed, identical across the ladder and carried into ol)
NN_MAX_EPOCHS = 150
NN_ES_PATIENCE = 20          # early stop on VAL_STOP loss, best-val restore
NN_BATCH_SIZE = 128
XGB_MAX_ROUNDS = 2000
XGB_ES_ROUNDS = 100
PER_EPOCH_SAMPLE_CAP = 50_000   # seeded sampler cap, keeps epochs bounded

# endregion

# region Physics priors and pre-registered tolerances
ALPHA_CU_PER_K = 0.00393     # copper resistivity coefficient, the coupling target
T_REF_C = 20.0               # reference temperature for the affine parameter head

# Amended H3 per-parameter recovery tolerances (relative error, synthetic track).
H3_TOL_FULLRATE = 0.05           # all four parameters, full-rate synthetic data
H3_TOL_2HZ_RS_PSI = 0.05         # R_s and psi_f from 2 Hz-downsampled data
H3_TOL_2HZ_LDQ = 0.15            # L_d and L_q from 2 Hz-downsampled data

# Dimensionality tripwire (recalibrated 2026-08-15): a learned rung fires if
# its train-validation pm MAE gap exceeds this multiple of the cross-rung
# median gap. Response is a correlation-pruned feature subset, not fe.
TRIPWIRE_GAP_MULTIPLIER = 3.0
TRIPWIRE_PRUNE_CORR = 0.95

# endregion

# region Metrics
# The single selection criterion everywhere (sl convention: declared once,
# never shopped). Reported metrics ride along, never selected on.
PRIMARY_METRIC = "val_mae_pm"
REPORT_METRICS = ("mae", "rmse", "r2", "max_abs_err")

# endregion
