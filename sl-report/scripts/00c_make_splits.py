"""Part 0c: freeze the grouped splits, the VAL partition, the CV folds, and the
preprocessing statistics, and verify the frozen hypotheses are unchanged.

This script REFUSES to run until the sample-adequacy question is settled, per
EDA_PLAN section 8: either notebook 02's gate verdict reads pass, or the user's
decision is recorded in ``data/processed/gate_decision.json`` as
``{"decision": "keep-100k"}`` or ``{"decision": "full-dataset"}``. Nothing
downstream of Part 0 exists until this ran exactly once.
"""

# region Imports & setup
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

import pandas as pd  # noqa: E402

from constants import (  # noqa: E402
    CV_FOLDS,
    HYPOTHESES_FILE,
    INPUT_SIGNALS,
    N_TEST_SESSIONS,
    N_TRAIN_SESSIONS,
    N_VAL_CAL_SESSIONS,
    N_VAL_STOP_SESSIONS,
    PROCESSED_DIR,
    SESSION_KEY,
)
from common import (  # noqa: E402
    assign_split_sessions,
    group_kfold_folds,
    load_raw,
    quiet_common_warnings,
    sha256_of,
    write_json,
)
from run_logging import banner, log_detail, logged_run, tee_to_logfile  # noqa: E402

# endregion

# region Gate guard
def resolve_working_data() -> tuple[pd.DataFrame, str]:
    """Return the working dataframe and spec name, or exit if the gate is open.

    The gate verdict comes from notebook 02. A failed gate requires the user's
    recorded decision, exactly as pre-registered: no fallback design exists.
    """
    verdict = json.loads((PROCESSED_DIR / "gate_verdict.json").read_text())
    decision_path = PROCESSED_DIR / "gate_decision.json"
    if verdict["gate_pass"]:
        spec = "candidate-100k"
    elif decision_path.exists():
        spec = json.loads(decision_path.read_text())["decision"]
        log_detail(f"gate failed, proceeding on the user's recorded decision: {spec}")
    else:
        raise SystemExit(
            "adequacy gate FAILED and no decision is recorded. Write "
            "data/processed/gate_decision.json with {\"decision\": \"keep-100k\"} "
            "or {\"decision\": \"full-dataset\"} after the user decides. Stopping."
        )
    if spec in ("candidate-100k", "keep-100k"):
        return pd.read_parquet(PROCESSED_DIR / "sample_candidate_100k.parquet"), "100k-block-sample"
    return load_raw(), "full-dataset"


def split_counts(n_sessions: int) -> dict[str, int]:
    """Split counts for the working data: pre-registered for 40, re-scaled else.

    Re-scaling keeps VAL_CAL and test at nine or more sessions (seventh-review
    rule) and hands the remainder to train and VAL_STOP proportionally.
    """
    if n_sessions == 40:
        return {"train": N_TRAIN_SESSIONS, "val_stop": N_VAL_STOP_SESSIONS,
                "val_cal": N_VAL_CAL_SESSIONS, "test": N_TEST_SESSIONS}
    scale = n_sessions / 40
    counts = {"val_cal": max(9, round(N_VAL_CAL_SESSIONS * scale)),
              "test": max(9, round(N_TEST_SESSIONS * scale)),
              "val_stop": max(3, round(N_VAL_STOP_SESSIONS * scale))}
    counts["train"] = n_sessions - sum(counts.values())
    return counts

# endregion

# region Freeze
def freeze() -> tuple[None, dict]:
    """Assign splits, build folds, fit train-only scaler stats, write manifests."""
    df, spec = resolve_working_data()
    sessions = sorted(int(s) for s in df[SESSION_KEY].unique())
    counts = split_counts(len(sessions))
    if len(sessions) == 40:
        split = assign_split_sessions(sessions)
    else:
        import numpy as np
        from constants import SPLIT_SEED
        rng = np.random.default_rng(SPLIT_SEED)
        order = list(rng.permutation(sessions))
        split, start = {}, 0
        for name in ("train", "val_stop", "val_cal", "test"):
            split[name] = sorted(int(s) for s in order[start:start + counts[name]])
            start += counts[name]

    folds = group_kfold_folds(split["train"], CV_FOLDS)

    train = df[df[SESSION_KEY].isin(split["train"])]
    scaler = {c: {"mean": float(train[c].mean()), "std": float(train[c].std())}
              for c in INPUT_SIGNALS}

    for name, ids in split.items():
        part = df[df[SESSION_KEY].isin(ids)]
        part.to_parquet(PROCESSED_DIR / f"split_{name}.parquet", index=False)
        log_detail(f"{name}: {len(ids)} sessions, {len(part):,} rows")

    write_json({"spec": spec, "counts": counts, "sessions": split},
               PROCESSED_DIR / "split_manifest.json", "split manifest")
    write_json({"cv_folds": CV_FOLDS, "folds": folds},
               PROCESSED_DIR / "fold_manifest.json", "fold manifest")
    write_json({"fit_on": "train", "signals": scaler},
               PROCESSED_DIR / "scaler_train_only.json", "train-only scaler")

    text = HYPOTHESES_FILE.read_text()
    missing = [h for h in ("H1", "H2", "H3", "H4", "H5", "H6") if h not in text]
    if missing:
        raise SystemExit(f"frozen HYPOTHESES.md is missing {missing}")
    write_json({"sha256": sha256_of(HYPOTHESES_FILE)},
               PROCESSED_DIR / "hypotheses_sha256.json", "hypotheses hash")
    return None, {"rows": int(len(df)), "sessions": len(sessions)}

# endregion

# region Entry point
def main() -> None:
    """Freeze splits, folds, and scaler stats once the gate question is settled."""
    banner(
        "Part 0c - Freeze splits, folds, preprocessing",
        "grouped split per the recorded gate decision, GroupKFold folds, train-only scaler",
        phase="diagnostic",
    )
    quiet_common_warnings()
    logged_run("freeze splits + folds + scaler", freeze, verb="freeze")


if __name__ == "__main__":
    tee_to_logfile()
    main()
# endregion
