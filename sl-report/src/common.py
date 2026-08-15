"""Shared data machinery for the SL study: loading, fingerprinting, sampling,
splits, folds, adequacy-gate statistics, and table IO.

Everything leakage-sensitive lives here so the discipline is enforced in one
place: the working sample is drawn as whole contiguous blocks, splits are
grouped by session, the VAL partition and CV folds come from the same seeded
assignment that ``00c`` freezes, and preprocessing statistics are only ever
fit on training sessions. Scripts orchestrate, this module implements.

Depends on ``constants`` (leaf) and ``run_logging`` only, never on the rung
modules, so it imports cheaply from every script and notebook.
"""

# region Imports
from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from constants import (
    EXPECTED_COLUMNS,
    EXPECTED_ROWS,
    EXPECTED_SESSIONS,
    GATE_ARC_CAPTURE_MIN,
    GATE_CURVATURE_DELTA_AIC,
    GATE_CURVATURE_MIN_FRACTION,
    GATE_ENVELOPE_GRID,
    GATE_ENVELOPE_JACCARD_MIN,
    GATE_QUANTILE_SHIFT_MAX,
    N_TEST_SESSIONS,
    N_TRAIN_SESSIONS,
    N_VAL_CAL_SESSIONS,
    N_VAL_STOP_SESSIONS,
    PROCESSED_DIR,
    RAW_FILE,
    SAMPLE_RATE_HZ,
    SAMPLE_SESSIONS,
    SAMPLE_TARGET_ROWS,
    SAMPLING_SEED,
    SESSION_KEY,
    SPLIT_SEED,
    TABLES_DIR,
)
from run_logging import log_saved, log_saved_artifact

# endregion

# region Small utilities
def quiet_common_warnings() -> None:
    """Silence the known-noisy warnings that would drown the run logs."""
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", message=".*Mean of empty slice.*")


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    """Return the sha256 hex digest of a file, streamed in 1 MiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def write_summary_table(rows: list[dict], file_name: str) -> pd.DataFrame:
    """Write a list of summary dicts to ``reports/tables`` and announce it."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLES_DIR / file_name, index=False)
    log_saved(file_name, len(frame))
    return frame


def write_json(obj: dict, path: Path, kind: str) -> None:
    """Write a manifest/fingerprint JSON artifact and announce it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    log_saved_artifact(str(path.relative_to(path.parents[2])), kind)

# endregion

# region Raw data and fingerprint
def load_raw() -> pd.DataFrame:
    """Load the raw CSV with sessions in file order (time is implicit in order)."""
    return pd.read_csv(RAW_FILE)


def fingerprint_raw(df: pd.DataFrame) -> dict:
    """Build the dataset fingerprint that invariant 1 checks against.

    Args:
        df: The raw dataframe as loaded from ``RAW_FILE``.

    Returns:
        A JSON-serializable dict of row count, column list, session count,
        per-session row counts, and the raw file's sha256.
    """
    sizes = df.groupby(SESSION_KEY).size()
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "sessions": int(sizes.size),
        "rows_per_session": {str(k): int(v) for k, v in sizes.items()},
        "sha256": sha256_of(RAW_FILE),
    }


def verify_fingerprint(fp: dict) -> list[str]:
    """Return a list of mismatches between a fingerprint and the expectations."""
    problems = []
    if fp["rows"] != EXPECTED_ROWS:
        problems.append(f"rows {fp['rows']} != expected {EXPECTED_ROWS}")
    if tuple(fp["columns"]) != EXPECTED_COLUMNS:
        problems.append("column set/order differs from EXPECTED_COLUMNS")
    if fp["sessions"] != EXPECTED_SESSIONS:
        problems.append(f"sessions {fp['sessions']} != expected {EXPECTED_SESSIONS}")
    return problems


def session_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Per-session inventory: rows, minutes, speed/pm coverage, torque quality flag."""
    rows = []
    for sid, g in df.groupby(SESSION_KEY):
        torque = g["torque"].to_numpy()
        change = np.flatnonzero(np.diff(torque) != 0)
        edges = np.concatenate(([-1], change, [len(torque) - 1]))
        max_const_torque_s = float(np.max(np.diff(edges)) / SAMPLE_RATE_HZ)
        rows.append({
            "profile_id": int(sid),
            "rows": int(len(g)),
            "minutes": float(len(g) / SAMPLE_RATE_HZ / 60.0),
            "speed_max": float(g["motor_speed"].max()),
            "pm_min": float(g["pm"].min()),
            "pm_max": float(g["pm"].max()),
            "pm_swing": float(g["pm"].max() - g["pm"].min()),
            "max_const_torque_s": max_const_torque_s,
        })
    return pd.DataFrame(rows).sort_values("profile_id").reset_index(drop=True)

# endregion

# region Working sample (candidate spec, judged by the EDA_PLAN section 8 gate)
def _strata(inv: pd.DataFrame) -> pd.Series:
    """Assign each session a stratum label: duration tercile x max-pm tercile."""
    dur = pd.qcut(inv["minutes"], 3, labels=False, duplicates="drop")
    hot = pd.qcut(inv["pm_max"], 3, labels=False, duplicates="drop")
    return (dur.astype(int) * 10 + hot.astype(int)).rename("stratum")


def choose_sample_sessions(inv: pd.DataFrame) -> list[int]:
    """Choose ``SAMPLE_SESSIONS`` sessions, stratified, seeded, deterministic.

    Sessions are allocated to strata proportionally (largest-remainder), then
    drawn without replacement inside each stratum with ``SAMPLING_SEED``.
    """
    rng = np.random.default_rng(SAMPLING_SEED)
    inv = inv.assign(stratum=_strata(inv).values)
    counts = inv.groupby("stratum").size()
    exact = counts / counts.sum() * SAMPLE_SESSIONS
    take = exact.astype(int)
    remainder = (exact - take).sort_values(ascending=False)
    for stratum in remainder.index[: SAMPLE_SESSIONS - int(take.sum())]:
        take[stratum] += 1
    chosen: list[int] = []
    for stratum, k in take.items():
        pool = inv.loc[inv["stratum"] == stratum, "profile_id"].to_numpy()
        k = min(int(k), len(pool))
        chosen.extend(rng.choice(pool, size=k, replace=False).tolist())
    return sorted(int(s) for s in chosen)


def draw_block_sample(df: pd.DataFrame, session_ids: list[int]) -> tuple[pd.DataFrame, dict]:
    """Draw one seeded contiguous block per chosen session, ~100k rows total.

    Block length is proportional to session length, scaled so the total hits
    ``SAMPLE_TARGET_ROWS``. Offsets are drawn with ``SAMPLING_SEED`` so the
    draw is reproducible bit for bit.

    Returns:
        The concatenated sample frame (file order preserved within blocks) and
        the manifest recording spec, per-session offsets, and lengths.
    """
    rng = np.random.default_rng(SAMPLING_SEED + 1)  # offsets: distinct stream
    sizes = df.groupby(SESSION_KEY).size()
    total = int(sizes.loc[session_ids].sum())
    frac = SAMPLE_TARGET_ROWS / total
    blocks, entries = [], {}
    for sid in session_ids:
        g = df[df[SESSION_KEY] == sid]
        n = len(g)
        length = max(2, int(round(n * frac)))
        length = min(length, n)
        offset = 0 if length >= n else int(rng.integers(0, n - length + 1))
        blocks.append(g.iloc[offset:offset + length])
        entries[str(sid)] = {"rows": n, "offset": offset, "block_len": length}
    sample = pd.concat(blocks, ignore_index=True)
    manifest = {
        "spec": "candidate-100k-block-sample",
        "sampling_seed": SAMPLING_SEED,
        "sessions": entries,
        "total_rows": int(len(sample)),
        "block_fraction": frac,
    }
    return sample, manifest

# endregion

# region Splits, VAL partition, CV folds
def assign_split_sessions(session_ids: list[int]) -> dict[str, list[int]]:
    """Assign sampled sessions to train / VAL_STOP / VAL_CAL / test, seeded.

    A plain seeded permutation with fixed counts (19/3/9/9). Deterministic
    given ``SPLIT_SEED`` and the session list, so notebook 02 can preview the
    assignment that ``00c`` later freezes, and both always agree.
    """
    rng = np.random.default_rng(SPLIT_SEED)
    order = list(rng.permutation(sorted(session_ids)))
    counts = {
        "train": N_TRAIN_SESSIONS,
        "val_stop": N_VAL_STOP_SESSIONS,
        "val_cal": N_VAL_CAL_SESSIONS,
        "test": N_TEST_SESSIONS,
    }
    if sum(counts.values()) != len(order):
        raise ValueError(f"split counts {sum(counts.values())} != sessions {len(order)}")
    out, start = {}, 0
    for name, k in counts.items():
        out[name] = sorted(int(s) for s in order[start:start + k])
        start += k
    return out


def group_kfold_folds(train_sessions: list[int], n_folds: int) -> list[list[int]]:
    """Split training sessions into seeded GroupKFold folds (session-level)."""
    rng = np.random.default_rng(SPLIT_SEED + 1)
    order = list(rng.permutation(sorted(train_sessions)))
    return [sorted(int(s) for s in order[i::n_folds]) for i in range(n_folds)]

# endregion

# region Adequacy-gate statistics (EDA_PLAN section 8)
def gate_g1_envelope(full: pd.DataFrame, sample: pd.DataFrame) -> dict:
    """G1: speed-torque occupancy Jaccard on a fixed grid plus quantile shifts."""
    bins_x = np.linspace(full["motor_speed"].min(), full["motor_speed"].max(), GATE_ENVELOPE_GRID[0] + 1)
    bins_y = np.linspace(full["torque"].min(), full["torque"].max(), GATE_ENVELOPE_GRID[1] + 1)

    def occupied(frame: pd.DataFrame) -> np.ndarray:
        h, _, _ = np.histogram2d(frame["motor_speed"], frame["torque"], bins=[bins_x, bins_y])
        return h > 0

    occ_full, occ_sample = occupied(full), occupied(sample)
    jaccard = float((occ_full & occ_sample).sum() / (occ_full | occ_sample).sum())

    shifts = {}
    for col in [c for c in full.columns if c != SESSION_KEY]:
        rng_full = full[col].max() - full[col].min()
        if rng_full == 0:
            continue
        s5 = abs(sample[col].quantile(0.05) - full[col].quantile(0.05)) / rng_full
        s95 = abs(sample[col].quantile(0.95) - full[col].quantile(0.95)) / rng_full
        shifts[col] = float(max(s5, s95))
    worst = max(shifts, key=shifts.get)
    return {
        "g1_jaccard": jaccard,
        "g1_worst_shift": shifts[worst],
        "g1_worst_shift_signal": worst,
        "g1_pass": bool(jaccard >= GATE_ENVELOPE_JACCARD_MIN
                        and shifts[worst] <= GATE_QUANTILE_SHIFT_MAX),
        "quantile_shifts": shifts,
    }


def gate_g2_arc_capture(full: pd.DataFrame, manifest: dict) -> dict:
    """G2: median share of each session's pm excursion captured by its block."""
    captures = []
    for sid, entry in manifest["sessions"].items():
        g = full[full[SESSION_KEY] == int(sid)]["pm"].to_numpy()
        swing = g.max() - g.min()
        if swing <= 0:
            continue
        block = g[entry["offset"]: entry["offset"] + entry["block_len"]]
        captures.append((block.max() - block.min()) / swing)
    median = float(np.median(captures))
    return {"g2_arc_capture": median, "g2_pass": bool(median >= GATE_ARC_CAPTURE_MIN),
            "per_session_capture": [float(c) for c in captures]}


def _aic(rss: float, n: int, k: int) -> float:
    """Gaussian AIC from a residual sum of squares."""
    return n * np.log(max(rss, 1e-12) / n) + 2 * k


def gate_g3_curvature(sample: pd.DataFrame) -> dict:
    """G3: share of blocks where a first-order response beats a line on pm."""
    from scipy.optimize import curve_fit

    def first_order(t, a, b, tau):
        return a + b * (1.0 - np.exp(-t / tau))

    curved = 0
    blocks = 0
    for _, g in sample.groupby(SESSION_KEY):
        y = g["pm"].to_numpy()
        n = len(y)
        if n < 20:
            continue
        blocks += 1
        t = np.arange(n) / SAMPLE_RATE_HZ
        lin = np.polyfit(t, y, 1)
        rss_lin = float(np.sum((y - np.polyval(lin, t)) ** 2))
        try:
            popt, _ = curve_fit(
                first_order, t, y,
                p0=[y[0], y[-1] - y[0] if abs(y[-1] - y[0]) > 1e-3 else 1.0, max(t[-1] / 3, 1.0)],
                bounds=([-200, -300, 1.0], [300, 300, 1e5]), maxfev=5000,
            )
            rss_exp = float(np.sum((y - first_order(t, *popt)) ** 2))
        except Exception:
            rss_exp = rss_lin
        if _aic(rss_lin, n, 2) - _aic(rss_exp, n, 3) >= GATE_CURVATURE_DELTA_AIC:
            curved += 1
    frac = float(curved / max(blocks, 1))
    return {"g3_curved_frac": frac, "g3_pass": bool(frac >= GATE_CURVATURE_MIN_FRACTION),
            "g3_blocks": blocks}


def evaluate_gate(full: pd.DataFrame, sample: pd.DataFrame, manifest: dict) -> dict:
    """Run all three gate criteria and combine the verdict."""
    g1 = gate_g1_envelope(full, sample)
    g2 = gate_g2_arc_capture(full, manifest)
    g3 = gate_g3_curvature(sample)
    verdict = {
        **{k: v for k, v in g1.items() if k != "quantile_shifts"},
        **{k: v for k, v in g2.items() if k != "per_session_capture"},
        **g3,
        "gate_pass": bool(g1["g1_pass"] and g2["g2_pass"] and g3["g3_pass"]),
    }
    return {"verdict": verdict, "g1_detail": g1, "g2_detail": g2}


def save_gate_verdict(verdict: dict) -> None:
    """Persist the gate verdict where 00c and the invariants can read it."""
    write_json(verdict, PROCESSED_DIR / "gate_verdict.json", "gate verdict")

# endregion
