from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import uuid


PLACEHOLDERS = ("__MOD_NAME__", "__MOD_UUID__", "__AUTHOR__")
TEXT_EXTENSIONS = {".lua", ".xaml", ".xml", ".lsx", ".json", ".md", ".py", ".ps1", ".txt"}


@dataclass(slots=True)
class NewModRequest:
    mod_name: str
    template: str
    author: str


def validate_mod_name(name: str) -> None:
    invalid = '\\/:*?"<>|'
    if not name or any(ch in invalid for ch in name):
        raise ValueError(f"Invalid mod name: {name}")


def available_templates(repo_root: Path) -> list[str]:
    templates_dir = repo_root / "templates"
    return sorted([p.name for p in templates_dir.iterdir() if p.is_dir()], key=str.lower)


def create_mod(repo_root: Path, request: NewModRequest) -> Path:
    validate_mod_name(request.mod_name)
    template_dir = repo_root / "templates" / request.template
    if not template_dir.exists():
        raise FileNotFoundError(f"Template not found: {request.template}")

    dest_dir = repo_root / "mods" / request.mod_name
    if dest_dir.exists():
        raise FileExistsError(f"Destination already exists: {dest_dir}")

    shutil.copytree(template_dir, dest_dir)
    mod_uuid = str(uuid.uuid4()).lower()

    for file_path in dest_dir.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if not any(token in text for token in PLACEHOLDERS):
            continue
        text = text.replace("__MOD_NAME__", request.mod_name)
        text = text.replace("__MOD_UUID__", mod_uuid)
        text = text.replace("__AUTHOR__", request.author)
        file_path.write_text(text, encoding="utf-8")

    subprocess.run(["git", "init"], cwd=dest_dir, check=False)
    return dest_dir
