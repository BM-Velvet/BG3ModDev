#!/usr/bin/env python3
"""BG3 Script Extender log watcher — shared tool for BG3ModDev.

Tails the most recent gold.*.log file in the BG3 bin\ directory.
Filters to lines matching a configurable handle, color-codes severity,
and writes filtered output to a session log file.

Usage:
    python tools/shared/watch_log.py                         # filter [BG3ModName]
    python tools/shared/watch_log.py --filter "[Armory]"     # subsystem filter
    python tools/shared/watch_log.py --filter ""             # all SE output
    python tools/shared/watch_log.py --mod MyMod             # shorthand: filter [MyMod]

Output log defaults to ./last_session.log (relative to CWD).
Pass --output to override.
"""

import argparse
import glob
import os
import sys
import time
from pathlib import Path

RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

DEFAULT_BG3_BIN = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\bin")
POLL_MS = 200


def find_latest_log(bin_dir: Path) -> Path | None:
    pattern = str(bin_dir / "gold.*.log")
    matches = glob.glob(pattern)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def colorize(line: str) -> str:
    lower = line.lower()
    if "error" in lower or "failed" in lower or "exception" in lower:
        return RED + line + RESET
    if "warn" in lower:
        return YELLOW + line + RESET
    return line


def tail(log_path: Path, handle: str, out_path: Path):
    print(f"[watch_log] Watching: {log_path}", flush=True)
    print(f"[watch_log] Filter  : '{handle}' (empty = all)", flush=True)
    print(f"[watch_log] Output  : {out_path}", flush=True)
    print("[watch_log] Ctrl+C to stop\n", flush=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "r", encoding="utf-8", errors="replace") as f, \
         open(out_path, "w", encoding="utf-8") as out_file:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(POLL_MS / 1000)
                continue
            line = line.rstrip("\n")
            if handle and handle not in line:
                continue
            ts = time.strftime("%H:%M:%S")
            output_line = f"[{ts}] {line}"
            print(colorize(output_line), flush=True)
            out_file.write(output_line + "\n")
            out_file.flush()


def main():
    parser = argparse.ArgumentParser(description="Tail BG3 SE log filtered to mod output.")
    parser.add_argument("--filter", default=None,
                        help="Substring filter. Default: '[<mod>]' if --mod set, else empty.")
    parser.add_argument("--mod", default=None,
                        help="Mod name — sets filter to '[<name>]' (shorthand).")
    parser.add_argument("--bin", default=str(DEFAULT_BG3_BIN),
                        help="Path to BG3 bin\\ directory.")
    parser.add_argument("--output", default=None,
                        help="Output log path. Default: ./last_session.log")
    args = parser.parse_args()

    # Resolve filter
    if args.filter is not None:
        handle = args.filter
    elif args.mod:
        handle = f"[{args.mod}]"
    else:
        handle = ""

    out_path = Path(args.output) if args.output else Path("last_session.log")
    bin_dir  = Path(args.bin)

    if not bin_dir.exists():
        print(f"[watch_log] ERROR: BG3 bin dir not found: {bin_dir}", file=sys.stderr)
        sys.exit(1)

    log_path = find_latest_log(bin_dir)
    if not log_path:
        print("[watch_log] No gold.*.log found — waiting for game launch...", flush=True)
        while not log_path:
            time.sleep(1)
            log_path = find_latest_log(bin_dir)

    try:
        tail(Path(log_path), handle, out_path)
    except KeyboardInterrupt:
        print("\n[watch_log] Stopped.", flush=True)


if __name__ == "__main__":
    main()
