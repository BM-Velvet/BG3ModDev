from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ModMeta:
    name: str | None = None
    folder: str | None = None
    author: str | None = None
    uuid: str | None = None


@dataclass(slots=True)
class GitStatus:
    is_repo: bool = False
    branch: str | None = None
    dirty: bool = False
    summary: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DeployStatus:
    exists: bool = False
    correct: bool = False
    target: Path | None = None
    current_target: str | None = None
    problem: str | None = None


@dataclass(slots=True)
class ModInfo:
    name: str
    path: Path
    mod_dir: Path
    meta_path: Path
    se_config_path: Path
    template_type: str | None
    meta: ModMeta
    mod_table: str | None
    git: GitStatus
    deploy: DeployStatus
    has_tests: bool
    has_placeholders: bool
    is_bg3_ready: bool

