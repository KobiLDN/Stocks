"""Import every past signal run from git history into the history DB (one-off, #54 step 8).

    python -m history.import_signals

The signal bot has committed */signals-local.json on every run since May 2026, so each
committed version is one signal run that was published live at the time: provenance = 'live',
and run_id = 'git:<commit sha>' records where it came from. Placeholder files (no parseable
'updated') are skipped. Idempotent — the same keys as the live recorder with INSERT OR IGNORE,
so runs already recorded live are left alone. Needs full history (checkout fetch-depth: 0).
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta

from history.db import ROOT, HistoryError, connect_for_bot, load_universe
from history.snapshot import SIGNAL_COLS, SIGNAL_RUN_COLS, rows_from_signal_file


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL).decode()


def versions(path):
    """[(sha, commit time ISO)] for every commit that changed `path`, oldest first."""
    lines = git("log", "--reverse", "--format=%H %cI", "--", path).splitlines()
    return [tuple(line.split(" ", 1)) for line in lines if line.strip()]


def collect(sectors, warn=print):
    runs, sigs, seen, skipped = [], [], set(), 0
    for sector in sectors:
        path = f"{sector}/signals-local.json"
        for sha, committed in versions(path):
            try:
                data = json.loads(git("show", f"{sha}:{path}"))
            except (subprocess.CalledProcessError, ValueError):
                skipped += 1
                continue
            got = rows_from_signal_file(sector, data, f"git:{sha}")
            if not got:
                skipped += 1
                continue
            run, rows = got
            if run[0] in seen:                     # same run re-committed (e.g. a merge)
                continue
            seen.add(run[0])
            # sanity: a run can't be committed before it was generated
            made = datetime.fromisoformat(run[2].replace("Z", "+00:00"))
            if datetime.fromisoformat(committed) < made - timedelta(minutes=1):
                warn(f"  WARNING: {sector} {sha[:8]} committed {committed} before its 'updated' {run[2]} — skipped")
                continue
            runs.append(run)
            sigs += rows
    return runs, sigs, skipped


def main():
    universe = load_universe()
    if not git("rev-parse", "--is-shallow-repository").strip() == "false":
        print("ERROR: shallow clone — check out with fetch-depth: 0")
        return 1
    h = connect_for_bot()
    if h is None:
        return 0
    print(f"History → {h.db.name}")
    h.ensure_schema()
    runs, sigs, skipped = collect(universe["sectors"])
    run_id = h.begin_run("import_signals")
    try:
        h.write("signal_runs", SIGNAL_RUN_COLS, runs, on_conflict="IGNORE")
        h.write("signals", SIGNAL_COLS, sigs, on_conflict="IGNORE")
    except Exception as e:
        h.finish_run(run_id, "failed", note=str(e)[:500])
        raise
    h.finish_run(run_id, note=f"{len(runs)} runs, {len(sigs)} signals from git; {skipped} placeholder versions skipped")
    print(f"  {len(runs)} signal runs, {len(sigs)} signals offered ({skipped} placeholder versions skipped), {h.calls} calls")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HistoryError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
