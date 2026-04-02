#!/usr/bin/env python3
"""Thin wrapper — delegates to the shared linter in BG3ModDev.

Usage:
    python Tools/lint.py [file1 file2 ...]
    python Tools/lint.py                      # lint all Mod/ files
"""

import subprocess
import sys
from pathlib import Path

SHARED_LINT = Path(__file__).parent.parent.parent.parent / "tools" / "shared" / "lint.py"
MOD_ROOT    = Path(__file__).parent.parent

if not SHARED_LINT.exists():
    print(f"[lint] Shared linter not found at {SHARED_LINT}")
    print("[lint] Run Setup-Env.ps1 in BG3ModDev or place lint.py here directly.")
    sys.exit(1)

result = subprocess.run(
    [sys.executable, str(SHARED_LINT), "--mod-root", str(MOD_ROOT)] + sys.argv[1:],
    cwd=str(MOD_ROOT),
)
sys.exit(result.returncode)
