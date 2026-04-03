from __future__ import annotations

from pathlib import Path
import json
import subprocess
import xml.etree.ElementTree as ET

from .config import AppConfig
from .models import DeployStatus, GitStatus, ModInfo, ModMeta


PLACEHOLDERS = ("__MOD_NAME__", "__MOD_UUID__", "__AUTHOR__")


def discover_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "templates").exists() and (candidate / "mods").exists():
            return candidate
    raise RuntimeError("Could not find BG3ModDev workspace root.")


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def parse_meta(meta_path: Path) -> ModMeta:
    if not meta_path.exists():
        return ModMeta()
    try:
        tree = ET.parse(meta_path)
    except ET.ParseError:
        return ModMeta()
    result = ModMeta()
    for attr in tree.iter():
        if _strip_ns(getattr(attr, "tag", "")) != "attribute":
            continue
        attr_id = attr.attrib.get("id")
        value = attr.attrib.get("value")
        if attr_id == "Name":
            result.name = value
        elif attr_id == "Folder":
            result.folder = value
        elif attr_id == "Author":
            result.author = value
        elif attr_id == "UUID":
            result.uuid = value
    return result


def parse_mod_table(config_path: Path) -> str | None:
    if not config_path.exists():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data.get("ModTable")


def detect_template_type(mod_path: Path) -> str | None:
    if (mod_path / "Mod" / "GUI").exists():
        return "ui-mod"
    if (mod_path / "Mod" / "ScriptExtender").exists():
        return "basic-lua-mod"
    return None


def git_status(path: Path) -> GitStatus:
    if not (path / ".git").exists():
        return GitStatus()
    branch = None
    summary: list[str] = []
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip() or None
        raw = subprocess.run(
            ["git", "status", "--short"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.splitlines()
        summary = [line.rstrip() for line in raw if line.strip()]
    except OSError:
        return GitStatus(is_repo=True, branch=branch)
    return GitStatus(is_repo=True, branch=branch, dirty=bool(summary), summary=summary)


def deploy_status(mod_path: Path, meta: ModMeta, config: AppConfig | None) -> DeployStatus:
    if not config or not meta.folder:
        return DeployStatus(problem="Missing workspace config or mod folder metadata.")

    target = config.deploy_target_dir / meta.folder
    expected = str((mod_path / "Mod").resolve())
    if not target.exists():
        return DeployStatus(target=target)

    try:
        current_target = str(target.resolve(strict=False))
    except OSError:
        current_target = None

    correct = current_target == expected
    return DeployStatus(
        exists=True,
        correct=correct,
        target=target,
        current_target=current_target,
        problem=None if correct else "Deployment target points somewhere else.",
    )


def has_placeholders(path: Path) -> bool:
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".json", ".lua", ".lsx", ".md", ".xaml", ".txt"}:
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if any(token in text for token in PLACEHOLDERS):
            return True
    return False


def discover_mods(repo_root: Path, config: AppConfig | None) -> list[ModInfo]:
    mods_dir = repo_root / "mods"
    results: list[ModInfo] = []
    if not mods_dir.exists():
        return results

    for child in sorted([p for p in mods_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        mod_dir = child / "Mod"
        meta_path = mod_dir / "meta.lsx"
        se_config_path = mod_dir / "ScriptExtender" / "Config.json"
        meta = parse_meta(meta_path)
        git = git_status(child)
        deploy = deploy_status(child, meta, config)
        results.append(
            ModInfo(
                name=child.name,
                path=child,
                mod_dir=mod_dir,
                meta_path=meta_path,
                se_config_path=se_config_path,
                template_type=detect_template_type(child),
                meta=meta,
                mod_table=parse_mod_table(se_config_path),
                git=git,
                deploy=deploy,
                has_tests=(child / "Tests" / "TestRunner.lua").exists(),
                has_placeholders=has_placeholders(child),
                is_bg3_ready=mod_dir.exists() and meta_path.exists() and se_config_path.exists(),
            )
        )
    return results


def find_mod(mods: list[ModInfo], mod_name: str) -> ModInfo:
    for mod in mods:
        if mod.name.lower() == mod_name.lower():
            return mod
    raise KeyError(f"Mod not found: {mod_name}")
