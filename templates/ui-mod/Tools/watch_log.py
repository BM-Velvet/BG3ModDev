#!/usr/bin/env python3
"""Thin wrapper — delegates to the shared log watcher in BG3ModDev.

Usage:
    python Tools/watch_log.py
    python Tools/watch_log.py --filter "[SubSystem]"
    python Tools/watch_log.py --filter ""              # all SE output
"""

import subprocess
import sys
from pathlib import Path

SHARED_WATCHER = Path(__file__).parent.parent.parent.parent / "tools" / "shared" / "watch_log.py"
OUTPUT_LOG     = Path(__file__).parent / "last_session.log"

if not SHARED_WATCHER.exists():
    print(f"[watch_log] Shared watcher not found at {SHARED_WATCHER}")
    sys.exit(1)

extra_args = sys.argv[1:]
if not any(a.startswith("--filter") or a.startswith("--mod") for a in extra_args):
    extra_args = ["--mod", "__MOD_NAME__"] + extra_args

result = subprocess.run(
    [sys.executable, str(SHARED_WATCHER),
     "--output", str(OUTPUT_LOG)] + extra_args
)
sys.exit(result.returncode)
