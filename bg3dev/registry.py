from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


REGISTRY_FILE = ".bg3dev-actions.toml"


@dataclass(slots=True)
class ActionSpec:
    key: str
    label: str
    description: str
    handler: str
    mod_required: bool = True
    requires_config: bool = False
    requires_divine: bool = False
    requires_tests: bool = False


def registry_path(repo_root: Path) -> Path:
    return repo_root / REGISTRY_FILE


def load_registry(repo_root: Path) -> dict[str, ActionSpec]:
    path = registry_path(repo_root)
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    actions = {}
    for key, raw in data.get("actions", {}).items():
        actions[key] = ActionSpec(
            key=key,
            label=raw["label"],
            description=raw["description"],
            handler=raw["handler"],
            mod_required=raw.get("mod_required", True),
            requires_config=raw.get("requires_config", False),
            requires_divine=raw.get("requires_divine", False),
            requires_tests=raw.get("requires_tests", False),
        )
    return actions
