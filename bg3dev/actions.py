from __future__ import annotations

from pathlib import Path
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from .config import AppConfig
from .models import ModInfo

TEXT_EXTENSIONS = {".lua", ".xaml", ".xml", ".lsx", ".json", ".md", ".py", ".ps1", ".txt"}


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


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def validate_mod_identity(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(
            "Mod internal name must be a valid Lua identifier: letters, numbers, and underscores only, "
            "and it cannot start with a number."
        )


def rename_mod(mod: ModInfo, new_name: str, display_name: str | None = None, config: AppConfig | None = None) -> str:
    validate_mod_identity(new_name)
    new_display_name = display_name or new_name
    old_repo_name = mod.name
    old_folder = mod.meta.folder or mod.mod_table or mod.name
    old_mod_table = mod.mod_table or mod.meta.folder or mod.name
    old_display_name = mod.meta.name or mod.name
    new_repo_path = mod.path.parent / new_name

    if new_repo_path.exists() and new_repo_path != mod.path:
        raise FileExistsError(f"Destination already exists: {new_repo_path}")

    old_mod_dir = mod.mod_dir.resolve(strict=False)
    redeploy = False
    old_target: Path | None = None
    if config and old_folder:
        old_target = config.deploy_target_dir / old_folder
        if old_target.exists():
            ensure_safe_deploy_target(old_target, config)
            if str(old_target.resolve(strict=False)) == str(old_mod_dir):
                redeploy = True

    if redeploy and old_target and old_target.exists():
        subprocess.run(["cmd", "/c", "rmdir", str(old_target)], check=True)

    _update_meta_file(mod.meta_path, new_name, new_display_name)
    _update_se_config(mod.se_config_path, new_name)
    _update_mcm_blueprint(mod.mod_dir / "MCM_blueprint.json", new_display_name)
    _bulk_replace_mod_references(mod.path, old_mod_table, new_name, old_display_name, new_display_name)

    mod.path.rename(new_repo_path)

    message = f"Renamed mod {old_repo_name} -> {new_name}"
    if redeploy and config:
        new_mod_dir = new_repo_path / "Mod"
        new_target = config.deploy_target_dir / new_name
        ensure_safe_deploy_target(new_target, config)
        if new_target.exists():
            raise RuntimeError(f"New deploy target already exists: {new_target}")
        subprocess.run(["cmd", "/c", "mklink", "/J", str(new_target), str(new_mod_dir.resolve(strict=False))], check=True)
        message += f"\nUpdated deployment: {new_target} -> {new_mod_dir}"
    return message


def _update_meta_file(meta_path: Path, new_folder: str, new_display_name: str) -> None:
    tree = ET.parse(meta_path)
    changed_folder = False
    changed_name = False
    for node in tree.iter():
        if _strip_ns(getattr(node, "tag", "")) != "node" or node.attrib.get("id") != "ModuleInfo":
            continue
        for attr in node:
            if _strip_ns(getattr(attr, "tag", "")) != "attribute":
                continue
            attr_id = attr.attrib.get("id")
            if attr_id == "Folder":
                attr.attrib["value"] = new_folder
                changed_folder = True
            elif attr_id == "Name":
                attr.attrib["value"] = new_display_name
                changed_name = True
        break
    if not changed_folder or not changed_name:
        raise RuntimeError(f"meta.lsx is missing ModuleInfo Folder/Name attributes: {meta_path}")
    tree.write(meta_path, encoding="utf-8", xml_declaration=True)


def _update_se_config(config_path: Path, new_mod_table: str) -> None:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data["ModTable"] = new_mod_table
    config_path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")


def _update_mcm_blueprint(path: Path, new_display_name: str) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if "ModName" in data:
        data["ModName"] = new_display_name
        path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")


def _bulk_replace_mod_references(
    mod_root: Path,
    old_mod_table: str,
    new_mod_table: str,
    old_display_name: str,
    new_display_name: str,
) -> None:
    replacements: list[tuple[str, str]] = []
    if old_mod_table != new_mod_table:
        replacements.append((old_mod_table, new_mod_table))
    if old_display_name != new_display_name:
        replacements.append((old_display_name, new_display_name))
    if not replacements:
        return

    for file_path in mod_root.rglob("*"):
        if ".git" in file_path.parts or not file_path.is_file():
            continue
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        updated = text
        for old, new in replacements:
            updated = updated.replace(old, new)
        if updated != text:
            file_path.write_text(updated, encoding="utf-8")


def package_mod(mod: ModInfo, config: AppConfig, version: str, copy_to_appdata: bool = False, beta: bool = False) -> str:
    divine_path = config.divine_path
    if not divine_path.exists():
        raise RuntimeError(f"Divine not found: {divine_path}")
    if not mod.mod_dir.exists():
        raise RuntimeError("Cannot package a mod without a Mod/ directory.")
    if not mod.meta.folder:
        raise RuntimeError("Cannot package a mod without ModuleInfo Folder metadata.")

    release_dir = config.release_dir or (mod.path.parents[1] / "releases")
    release_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-beta" if beta else ""
    output = (release_dir / f"{mod.name}_{version}{suffix}.pak").resolve(strict=False)
    staging_root = release_dir / "_bg3dev-package" / mod.name
    if staging_root.exists():
        shutil.rmtree(staging_root)
    source_root = staging_root.resolve(strict=False)
    staged_mod_dir = source_root / "Mods" / mod.meta.folder
    try:
        shutil.copytree(mod.mod_dir, staged_mod_dir)
        subprocess.run(
            [
                str(divine_path),
                "--action",
                "create-package",
                "--source",
                str(source_root),
                "--destination",
                str(output),
                "--game",
                "bg3",
            ],
            check=True,
        )
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)

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
