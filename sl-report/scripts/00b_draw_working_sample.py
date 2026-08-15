"""Part 0b: draw the candidate working sample (40-session block sample, ~100k rows).

Stratified session selection (duration tercile x max-pm tercile) with
``SAMPLING_SEED``, then one seeded contiguous block per session, length
proportional to session length, scaled to ``SAMPLE_TARGET_ROWS``. The sample
is a CANDIDATE: notebook 02 evaluates the pre-registered adequacy gate on it,
and ``00c`` refuses to split until that verdict (or the user's recorded
decision) exists. Touches no split and no model.
"""

# region Imports & setup
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from constants import PROCESSED_DIR, SAMPLE_SESSIONS  # noqa: E402
from common import (  # noqa: E402
    choose_sample_sessions,
    draw_block_sample,
    load_raw,
    quiet_common_warnings,
    session_inventory,
    write_json,
)
from run_logging import banner, log_detail, logged_run, tee_to_logfile  # noqa: E402

# endregion

# region Steps
def draw() -> tuple[None, dict]:
    """Choose sessions, cut blocks, save the parquet and the manifest."""
    df = load_raw()
    inv = session_inventory(df)
    chosen = choose_sample_sessions(inv)
    log_detail(f"chosen sessions ({len(chosen)}): {chosen}")
    sample, manifest = draw_block_sample(df, chosen)
    out = PROCESSED_DIR / "sample_candidate_100k.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(out, index=False)
    write_json(manifest, PROCESSED_DIR / "sample_manifest.json", "sample manifest")
    return None, {"rows": int(len(sample)), "sessions": len(chosen)}


# endregion

# region Entry point
def main() -> None:
    """Draw the candidate block sample and persist it with its manifest."""
    banner(
        "Part 0b - Draw working sample (candidate)",
        f"{SAMPLE_SESSIONS} stratified sessions, one contiguous block each, ~100k rows",
        phase="diagnostic",
    )
    quiet_common_warnings()
    logged_run("stratified block sample", draw, verb="sample")


if __name__ == "__main__":
    tee_to_logfile()
    main()
# endregion
