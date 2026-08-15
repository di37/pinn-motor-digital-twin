"""Part 0a: verify the raw file, write the fingerprint, inventory the sessions.

Runs no models and touches no split. The raw CSV is expected in ``data/raw``
(downloaded 2026-08-15); if it is missing, this script fetches it via
kagglehub using the user's stored credentials, then verifies either way. The
fingerprint this writes is what invariant 1 checks every later run against,
so no script ever proceeds on a silently different dataset.
"""

# region Imports & setup
from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from constants import PROCESSED_DIR, RAW_FILE  # noqa: E402
from common import (  # noqa: E402
    fingerprint_raw,
    load_raw,
    quiet_common_warnings,
    session_inventory,
    verify_fingerprint,
    write_json,
    write_summary_table,
)
from run_logging import banner, log_detail, logged_run, tee_to_logfile  # noqa: E402

# endregion

# region Steps
def fetch_if_missing() -> None:
    """Fetch the Kaggle dataset into data/raw when the CSV is absent."""
    if RAW_FILE.exists():
        log_detail(f"raw file present: {RAW_FILE.name} ({RAW_FILE.stat().st_size/1e6:.0f} MB)")
        return
    import kagglehub

    cache = Path(kagglehub.dataset_download("wkirgsn/electric-motor-temperature"))
    src = next(cache.rglob("measures_v2.csv"))
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, RAW_FILE)
    log_detail(f"fetched via kagglehub -> {RAW_FILE}")


def fingerprint_and_inventory() -> tuple[None, dict]:
    """Fingerprint the raw file, fail on mismatch, save the session inventory."""
    df = load_raw()
    fp = fingerprint_raw(df)
    problems = verify_fingerprint(fp)
    if problems:
        raise SystemExit("fingerprint mismatch: " + "; ".join(problems))
    write_json(fp, PROCESSED_DIR / "fingerprint.json", "fingerprint")
    inv = session_inventory(df)
    write_summary_table(inv.to_dict("records"), "part0_session_inventory.csv")
    return None, {"rows": fp["rows"], "sessions": fp["sessions"]}


# endregion

# region Entry point
def main() -> None:
    """Verify or fetch the raw file, then fingerprint and inventory it."""
    banner(
        "Part 0a - Fetch and fingerprint",
        "raw file verification, sha256 fingerprint, per-session inventory",
        phase="diagnostic",
    )
    quiet_common_warnings()
    fetch_if_missing()
    logged_run("fingerprint + session inventory", fingerprint_and_inventory, verb="audit")


if __name__ == "__main__":
    tee_to_logfile()
    main()
# endregion
