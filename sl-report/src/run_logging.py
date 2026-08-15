"""Consistent, human-readable progress logging for the SL study's scripts.

Kept in one module so every part logs identically: a run banner naming the
part and its scope, a per-seed group header, a timed start/finish line per
condition carrying that condition's result fields, and a save confirmation
naming the table and its row count. Depends only on the standard library and
the leaf ``constants`` module (for the logs directory), so it is safe to
import from ``common`` without any risk of a circular import.

Every print flushes immediately so the log streams in real time during the
longer multi-seed runs rather than appearing all at once at the end.
``tee_to_logfile`` additionally mirrors the whole run to
``reports/logs/<script>__<timestamp>.log`` so a saved copy is always
available for review, pruned automatically after a week.
"""

# region Imports
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys
import time
from typing import Callable, TextIO

from constants import LOGS_DIR

# Saved run logs are transient debugging aids, not results, so they are kept
# for a week and then pruned. Retention is enforced lazily: each run deletes
# any log older than this before writing its own, no daemon required.
LOG_RETENTION_DAYS = 7

# endregion

# region Formatting helpers
_BAR = "=" * 64


def now() -> str:
    """Return a wall-clock ``HH:MM:SS`` stamp for the current moment."""
    return datetime.now().strftime("%H:%M:%S")


# The fixed data protocol, surfaced in every run banner so a reader can
# confirm the methodology from the log alone, without opening the code.
_SPLIT = (
    "full dataset per gate decision 2026-08-16 (1,330,816 rows, 69 sessions) | "
    "grouped split 32 train / 5 VAL_STOP / 16 VAL_CAL / 16 test | preprocessing fit on train only"
)
_PHASE = {
    # Part 0 and Part 1: no model selection, no real-data test contact.
    "diagnostic": "foundation/consistency check only -- no tuning, no test contact",
    # a-scripts: selection on CV folds within train, stopping on VAL_STOP.
    "trainval": (
        "select on GroupKFold folds within train, stop on VAL_STOP -- "
        "VAL_CAL reserved, held-out test never touched here"
    ),
    # b-scripts: the single test contact for the part.
    "test": "held-out test only -- final reporting, no tuning or selection",
}


def banner(title: str, subtitle: str | None = None, phase: str | None = None) -> None:
    """Print a run header naming the part, its scope, and the leakage protocol.

    Args:
        title: Part name and stage, e.g. "Part 2 - Ladder (train/val)".
        subtitle: Optional scope line (rungs, seed list, condition counts).
        phase: One of ``"diagnostic"``, ``"trainval"``, ``"test"``. When given,
            a ``protocol:`` line states the fixed split, that execution is
            deterministic, and whether the run touches the test set, so a
            reader can verify compliance from the log alone.

    Returns:
        None.
    """
    lines = [f"\n{_BAR}", title]
    if subtitle:
        lines.append(subtitle)
    if phase:
        lines.append(f"protocol: {_SPLIT} | deterministic execution ON | {_PHASE.get(phase, phase)}")
    lines.append(_BAR)
    print("\n".join(lines), flush=True)


def seed_header(seed: int, index: int, total: int) -> None:
    """Print a per-seed group header (``index`` is 1-based within the seed list)."""
    print(f"\n--- seed {seed} ({index}/{total}) ---", flush=True)


def _result_fields(summary: dict) -> str:
    """Format a result line compactly, adapting to the keys present.

    Handles fingerprint, sampling, gate, synthetic-recovery, training, and
    test summaries with one helper, so a single :func:`logged_run` wrapper
    works for every part's script.

    Args:
        summary: The summary dict returned by a condition's run function.

    Returns:
        A compact, space-separated string of the fields present in ``summary``.
    """
    fields = []
    if "rows" in summary:                  # fingerprint / sampling
        fields.append(f"rows={summary['rows']:,}")
    if "sessions" in summary:
        fields.append(f"sessions={summary['sessions']}")
    if "g1_jaccard" in summary:            # adequacy gate
        fields.append(f"g1={summary['g1_jaccard']:.3f}")
    if "g2_arc_capture" in summary:
        fields.append(f"g2={summary['g2_arc_capture']:.2f}")
    if "g3_curved_frac" in summary:
        fields.append(f"g3={summary['g3_curved_frac']:.2f}")
    if "max_param_err_pct" in summary:     # synthetic closed-loop recovery
        fields.append(f"param_err={summary['max_param_err_pct']:.1f}%")
    if "val_mae_pm" in summary:            # train/val conditions
        fields.append(f"val_mae_pm={summary['val_mae_pm']:.3f}")
    if "best_epoch" in summary:
        fields.append(f"best_epoch={summary['best_epoch']}")
    if "alpha_cu" in summary:              # coupling diagnostic
        fields.append(f"a_cu={summary['alpha_cu']:+.5f}")
    if "alpha_mag" in summary:
        fields.append(f"a_mag={summary['alpha_mag']:+.5f}")
    if "test_mae_pm" in summary:           # the single test contact
        fields.append(f"test_mae_pm={summary['test_mae_pm']:.3f}")
    if "test_mae_torque" in summary:
        fields.append(f"test_mae_torque={summary['test_mae_torque']:.3f}")
    return "  ".join(fields)

# endregion

# region Timed run + save logging
def logged_run(name: str, run: Callable[[], tuple], *, verb: str = "fit") -> tuple:
    """Time one condition call and log its start and finish plus result.

    Args:
        name: Condition name shown in the log lines.
        run: Zero-argument callable returning ``(frame, summary)``. The summary
            is the second element and is passed to :func:`_result_fields`.
        verb: Short action label, e.g. ``"audit"``, ``"sample"``, ``"train"``,
            ``"test"``, or ``"fit"``.

    Returns:
        Whatever ``run()`` returns, unchanged, so the caller still gets the
        frame and summary it expects.
    """
    print(f"[{now()}] {verb:<7} start   {name}", flush=True)
    start = time.perf_counter()
    result = run()
    elapsed = time.perf_counter() - start
    summary = result[1] if isinstance(result, tuple) else result
    fields = _result_fields(summary) if isinstance(summary, dict) else ""
    print(f"[{now()}] {verb:<7} done    {name}   {fields}   ({elapsed:.1f}s)", flush=True)
    return result


def log_saved(file_name: str, n_rows: int) -> None:
    """Announce a saved table: its row count and project-relative path."""
    print(f"[{now()}] saved   {n_rows} row(s) -> reports/tables/{file_name}", flush=True)


def log_saved_artifact(name: str, kind: str = "artifact") -> None:
    """Announce a saved artifact (manifest, scaler, checkpoint, recipe)."""
    print(f"[{now()}] saved   {kind} -> {name}", flush=True)


def log_detail(text: str) -> None:
    """Print an indented sub-detail line, nested under the current run line."""
    print(f"           {text}", flush=True)

# endregion

# region Console-to-file mirroring
class _Tee:
    """A write stream that fans every write out to several underlying streams.

    Used to mirror stdout/stderr to both the console and a log file at once.
    Each write is flushed immediately so the on-disk log matches the console
    even mid-run, and ``isatty`` reports False so libraries that probe for a
    terminal behave as they would when piped to a file.
    """

    def __init__(self, *streams: TextIO) -> None:
        self._streams = streams

    def write(self, data: str) -> int:
        for stream in self._streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()

    def isatty(self) -> bool:
        return False

    def __getattr__(self, name: str):  # delegate anything else to the console stream
        return getattr(self._streams[0], name)


def _prune_expired_logs(now_ts: float) -> None:
    """Delete ``reports/logs/*.log`` files older than ``LOG_RETENTION_DAYS``."""
    cutoff = now_ts - LOG_RETENTION_DAYS * 86_400
    for path in LOGS_DIR.glob("*.log"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            pass  # a log vanished under us (concurrent run), nothing to clean


def tee_to_logfile(name: str | None = None) -> Path:
    """Mirror everything printed from here on to a per-run file in ``reports/logs/``.

    Call once at the start of a script's entry point. The console still shows
    the live output, and a copy lands in ``reports/logs/<name>__<timestamp>.log``.
    Each run gets its own timestamped file, so a re-run never overwrites an
    earlier run's log. ``name`` defaults to the running script's file stem.

    Args:
        name: Optional log-file stem. Defaults to the running script's name.

    Returns:
        The path of the log file being written.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _prune_expired_logs(time.time())
    stem = name or Path(sys.argv[0]).stem or "run"
    written = datetime.now()
    expires = written + timedelta(days=LOG_RETENTION_DAYS)
    # One timestamped file per run, no colons so the name is valid everywhere.
    log_path = LOGS_DIR / f"{stem}__{written:%Y-%m-%d_%H-%M-%S}.log"
    handle = open(log_path, "w", encoding="utf-8", buffering=1)  # line-buffered
    handle.write(
        f"# {log_path.name} | written {written:%Y-%m-%d %H:%M:%S} | "
        f"expires {expires:%Y-%m-%d} | auto-pruned after {LOG_RETENTION_DAYS} days on a later run\n"
    )
    sys.stdout = _Tee(sys.__stdout__, handle)
    sys.stderr = _Tee(sys.__stderr__, handle)  # capture tracebacks in the log too
    print(
        f"[log] saving this run to reports/logs/{log_path.name} "
        f"(kept until {expires:%Y-%m-%d}, ~{LOG_RETENTION_DAYS} days)",
        file=sys.__stdout__, flush=True,
    )
    return log_path

# endregion
