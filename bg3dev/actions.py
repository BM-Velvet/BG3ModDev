from __future__ import annotations

from pathlib import Path
import argparse
import glob
import os
import shutil
import subprocess
import time

from .config import AppConfig
from .models import ModInfo


def validate_mod(mod: ModInfo) -> list[str]:
    issues: list[str] = []
    if not mod.mod_dir.exists():
        issues.append("Missing Mod/ directory.")
    if not mod.meta_path.exists():
        issues.append("Missing Mod/meta.lsx.")
    if not mod.se_config_path.exists():
        issues.append("Missing Mod/ScriptExtender/Config.json.")
    if mod.has_placeholders:
        issues.append("Placeholder tokens are still present in the repo.")
    if not mod.meta.folder:
        issues.append("meta.lsx is missing ModuleInfo Folder.")
    if not mod.mod_table:
        issues.append("Config.json is missing ModTable.")
    return issues


def ensure_safe_deploy_target(target: Path, config: AppConfig) -> None:
    expected_parent = config.deploy_target_dir.resolve(strict=False)
    parent = target.parent.resolve(strict=False)
    if parent != expected_parent:
        raise RuntimeError(f"Refusing to modify unexpected deploy path: {target}")


def deploy_mod(mod: ModInfo, config: AppConfig, repair: bool = False) -> str:
    if not mod.meta.folder:
        raise RuntimeError("Cannot deploy mod without ModuleInfo Folder metadata.")
    source = mod.mod_dir.resolve()
    target = config.deploy_target_dir / mod.meta.folder
    ensure_safe_deploy_target(target, config)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        current = str(target.resolve(strict=False))
        if current == str(source):
            return f"Deployment already correct: {target} -> {current}"
        if not repair:
            raise RuntimeError(f"Deployment exists but points elsewhere: {target} -> {current}")
        subprocess.run(["cmd", "/c", "rmdir", str(target)], check=True)

    subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(source)], check=True)
    return f"Deployed {mod.name}: {target} -> {source}"


def undeploy_mod(mod: ModInfo, config: AppConfig) -> str:
    if not mod.meta.folder:
        raise RuntimeError("Cannot undeploy mod without ModuleInfo Folder metadata.")
    target = config.deploy_target_dir / mod.meta.folder
    ensure_safe_deploy_target(target, config)
    if not target.exists():
        return f"No deployment exists for {mod.name}."
    subprocess.run(["cmd", "/c", "rmdir", str(target)], check=True)
    return f"Removed deployment for {mod.name}: {target}"


def package_mod(mod: ModInfo, config: AppConfig, version: str, copy_to_appdata: bool = False) -> str:
    divine_path = config.divine_path
    if not divine_path.exists():
        raise RuntimeError(f"Divine not found: {divine_path}")
    if not mod.mod_dir.exists():
        raise RuntimeError("Cannot package a mod without a Mod/ directory.")

    release_dir = config.release_dir or (mod.path.parents[1] / "releases")
    release_dir.mkdir(parents=True, exist_ok=True)
    output = release_dir / f"{mod.name}_{version}.pak"

    subprocess.run(
        [
            str(divine_path),
            "--action=create-package",
            f"--source={mod.mod_dir}",
            f"--destination={output}",
            "--game=bg3",
        ],
        check=True,
    )

    message = f"Packaged {mod.name} to {output}"
    if copy_to_appdata:
        dest = config.appdata_mods_dir / output.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, dest)
        message += f"\nCopied package to {dest}"
    return message


def open_shell(mod: ModInfo) -> str:
    subprocess.Popen(["powershell", "-NoExit"], cwd=str(mod.path))
    return f"Opened PowerShell in {mod.path}"


def run_lua_tests(mod: ModInfo) -> int:
    runner = mod.path / "Tests" / "TestRunner.lua"
    tests = sorted((mod.path / "Tests").glob("test_*.lua"))
    if not runner.exists():
        raise RuntimeError("No Tests/TestRunner.lua found.")
    if not tests:
        raise RuntimeError("No test_*.lua files found.")
    cmd = ["lua", "Tests/TestRunner.lua", *[str(Path("Tests") / test.name) for test in tests]]
    return subprocess.run(cmd, cwd=mod.path, check=False).returncode


def tail_log(config: AppConfig, handle: str = "") -> int:
    bin_dir = config.bg3_game_path / "bin"
    if not bin_dir.exists():
        raise RuntimeError(f"BG3 bin directory not found: {bin_dir}")
    log_path = find_latest_log(bin_dir)
    if log_path is None:
        raise RuntimeError("No gold.*.log found. Launch BG3 first.")

    print(f"Watching {log_path}")
    print(f"Filter: {handle or '<none>'}")
    with log_path.open("r", encoding="utf-8", errors="replace") as handle_in:
        handle_in.seek(0, os.SEEK_END)
        try:
            while True:
                line = handle_in.readline()
                if not line:
                    time.sleep(0.2)
                    continue
                if handle and handle not in line:
                    continue
                print(line.rstrip())
        except KeyboardInterrupt:
            return 0


def find_latest_log(bin_dir: Path) -> Path | None:
    matches = glob.glob(str(bin_dir / "gold.*.log"))
    if not matches:
        return None
    return Path(max(matches, key=os.path.getmtime))


def choose_version(args: argparse.Namespace) -> str:
    if getattr(args, "version", None):
        return args.version
    value = input("Package version [1.0.0]: ").strip()
    return value or "1.0.0"
