#!/usr/bin/env python3
"""BG3 mod XAML + Lua linter — shared tool for BG3ModDev.

Usage:
    python tools/shared/lint.py --mod-root mods/MyMod [file1 file2 ...]
    python tools/shared/lint.py --mod-root mods/MyMod      # lint all Mod/ files

Exit code:
    0 = clean (errors=0; warnings don't block)
    1 = one or more errors found
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

def resolve_roots(mod_root_arg: str | None):
    if mod_root_arg:
        repo_root = Path(mod_root_arg).resolve()
    else:
        # Fall back: assume called from the mod root (CWD)
        repo_root = Path.cwd()
    return repo_root, repo_root / "Mod"

# Known valid pack:// assembly names in Noesis/BG3
KNOWN_ASSEMBLIES = {"Core", "MainUI", "Noesis.GUI.Extensions"}

errors   = []
warnings = []


def _e(path, line, msg):
    errors.append(f"[ERROR] {path}:{line}  {msg}")


def _w(path, line, msg):
    warnings.append(f"[WARN]  {path}:{line}  {msg}")


# ---------------------------------------------------------------------------
# XAML rules
# ---------------------------------------------------------------------------

def _strip_ns(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def lint_xaml(path: Path, repo_root: Path):
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        _e(path, "?", f"XML parse error: {exc}")
        return

    root = tree.getroot()
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path

    raw = path.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(raw.splitlines(), 1):
        if "https://schemas.microsoft.com" in line:
            _e(rel, lineno, "https:// in xmlns — must be http:// (crashes game)")
        for m in re.finditer(r'pack://application:,,,/([^;]+);', line):
            assembly = m.group(1)
            if assembly not in KNOWN_ASSEMBLIES:
                _w(rel, lineno, f"Unknown pack:// assembly '{assembly}' — expected one of {sorted(KNOWN_ASSEMBLIES)}")

    has_lstooltip = False
    has_itemscontrol = False
    _seen_wrapanel_warn = {}

    for elem in root.iter():
        tag = _strip_ns(elem.tag)

        if tag == "LSTooltip":
            has_lstooltip = True

        if tag == "ItemsControl":
            has_itemscontrol = True

        if tag == "ToolTip":
            for child in elem:
                if _strip_ns(child.tag) == "LSTooltip":
                    approx = _find_line(raw, "<ToolTip")
                    _w(rel, approx, "<ToolTip> wrapping ls:LSTooltip — verify this is inside LSEntityObject.ToolTip (valid) not ToolTipService.ToolTip (crashes)")

        if tag == "DataTrigger":
            binding = elem.get("Binding", "")
            if "Tag" in binding:
                approx = _find_line(raw, "DataTrigger")
                _w(rel, approx, "DataTrigger on Tag — use Trigger Property=\"Tag\" instead (Noesis binding-driven Tag)")

        if tag == "StackPanel" and elem.get("Orientation") == "Horizontal":
            if re.search(r'Width="\*"', raw) and not _seen_wrapanel_warn.get(str(rel)):
                _seen_wrapanel_warn[str(rel)] = True
                approx = _find_line(raw, 'StackPanel Orientation="Horizontal"')
                _w(rel, approx, "Horizontal StackPanel in file that has Grid Width=\"*\" columns — use WrapPanel with fixed Width instead")

    if has_itemscontrol and has_lstooltip:
        _w(rel, "?", "ItemsControl present in same file as ls:LSTooltip — prefer ListBox for tooltip compatibility")


def _find_line(text: str, needle: str) -> int:
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i
    return "?"


# ---------------------------------------------------------------------------
# Lua rules
# ---------------------------------------------------------------------------

def lint_lua(path: Path, repo_root: Path):
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    pcall_depth   = 0
    in_pcall_func = False

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        if 'https://' in line:
            _e(rel, lineno, 'https:// in Lua string — use http:// (Noesis namespace)')

        if re.search(r'\.Inventory(?![a-zA-Z0-9_])', line):
            _w(rel, lineno, "'.Inventory' (not .Inventories) — did you mean .Inventories?")

        if re.search(r'\bpcall\s*\(\s*function\s*\(', line):
            in_pcall_func = True
            pcall_depth   = line.count("{") - line.count("}") + line.count("(") - line.count(")")

        if in_pcall_func:
            if lineno > 1:
                pcall_depth += line.count("(") - line.count(")")
            if stripped.startswith("return") and pcall_depth > 0:
                _w(rel, lineno, "bare 'return' inside pcall(function()) — value is discarded; use a local variable instead")
            if pcall_depth <= 0:
                in_pcall_func = False
                pcall_depth   = 0


# ---------------------------------------------------------------------------
# Net message consistency check (cross-file)
# ---------------------------------------------------------------------------

_SEND_PATTERNS          = [re.compile(r'PostMessageToServer\s*\(\s*["\']([^"\']+)["\']')]
_SERVER_LISTEN_PATTERNS = [re.compile(r'Ext\.RegisterNetListener\s*\(\s*["\']([^"\']+)["\']')]
_CLIENT_LISTEN_PATTERNS = [re.compile(r'Ext\.RegisterNetListener\s*\(\s*["\']([^"\']+)["\']')]
_BROADCAST_PATTERNS     = [re.compile(r'BroadcastMessage\s*\(\s*["\']([^"\']+)["\']')]


def collect_net_messages(lua_files, repo_root: Path):
    client_sends = {}
    server_listens = {}
    server_broadcasts = {}
    client_listens = {}

    for path in lua_files:
        try:
            rel = path.relative_to(repo_root)
        except ValueError:
            rel = path
        text = path.read_text(encoding="utf-8", errors="replace")
        is_server = "Server" in str(path) or "BootstrapServer" in path.name

        for lineno, line in enumerate(text.splitlines(), 1):
            ref = f"{rel}:{lineno}"
            for pat in _SEND_PATTERNS:
                for m in pat.finditer(line):
                    client_sends.setdefault(m.group(1), ref)
            if is_server:
                for pat in _SERVER_LISTEN_PATTERNS:
                    for m in pat.finditer(line):
                        server_listens.setdefault(m.group(1), ref)
                for pat in _BROADCAST_PATTERNS:
                    for m in pat.finditer(line):
                        server_broadcasts.setdefault(m.group(1), ref)
            else:
                for pat in _CLIENT_LISTEN_PATTERNS:
                    for m in pat.finditer(line):
                        client_listens.setdefault(m.group(1), ref)

    return client_sends, server_listens, server_broadcasts, client_listens


def check_net_messages(lua_files, repo_root: Path):
    cs, sl, sb, cl = collect_net_messages(lua_files, repo_root)
    for name, ref in cs.items():
        if name not in sl:
            _e(ref, "", f"Net message mismatch: client sends '{name}' but no server listener found")
    for name, ref in sb.items():
        if name not in cl:
            _e(ref, "", f"Net message mismatch: server broadcasts '{name}' but no client listener found")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def gather_files(args, mod_root: Path):
    if args:
        return [Path(f).resolve() for f in args if Path(f).exists()]
    return list(mod_root.rglob("*.lua")) + list(mod_root.rglob("*.xaml"))


def main():
    parser = argparse.ArgumentParser(description="BG3 XAML + Lua linter")
    parser.add_argument("--mod-root", default=None,
                        help="Root of the mod repo (parent of Mod/). Defaults to CWD.")
    parser.add_argument("files", nargs="*", help="Specific files to lint (optional)")
    parsed = parser.parse_args()

    repo_root, mod_root = resolve_roots(parsed.mod_root)

    files = gather_files(parsed.files, mod_root)
    xaml_files = [f for f in files if f.suffix.lower() == ".xaml"]
    lua_files  = [f for f in files if f.suffix.lower() == ".lua"]

    for f in xaml_files:
        lint_xaml(f, repo_root)
    for f in lua_files:
        lint_lua(f, repo_root)

    all_lua = list(mod_root.rglob("*.lua"))
    if all_lua:
        check_net_messages(all_lua, repo_root)

    for msg in errors + warnings:
        print(msg)

    if errors or warnings:
        print("---")
        print(f"{len(errors)} error{'s' if len(errors) != 1 else ''}, "
              f"{len(warnings)} warning{'s' if len(warnings) != 1 else ''}"
              + (" — commit blocked" if errors else ""))

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
