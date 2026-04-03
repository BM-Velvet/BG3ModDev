from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


APP_CONFIG_NAME = ".bg3dev.local.toml"
LEGACY_ENV_NAME = ".env.ps1"


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def default_divine_path(repo_root: Path) -> Path:
    return repo_root / "lslib" / "Packed" / "Tools" / "Divine.exe"


def _resolve_divine_path(repo_root: Path, configured: str | None) -> Path:
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured))

    # Prefer the bundled LSlib layout, but still accept the legacy local folder.
    candidates.extend(
        [
            default_divine_path(repo_root),
            repo_root / "divine" / "divine.exe",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


@dataclass(slots=True)
class AppConfig:
    bg3_game_path: Path
    bg3_appdata_path: Path
    divine_path: Path
    multitool_path: Path | None = None
    deploy_mode: str = "junction"
    release_dir: Path | None = None
    source: str = "app"

    @property
    def deploy_target_dir(self) -> Path:
        return self.bg3_game_path / "Data" / "Mods"

    @property
    def appdata_mods_dir(self) -> Path:
        return self.bg3_appdata_path / "Mods"


def config_path(repo_root: Path) -> Path:
    return repo_root / APP_CONFIG_NAME


def legacy_env_path(repo_root: Path) -> Path:
    return repo_root / LEGACY_ENV_NAME


def load_config(repo_root: Path) -> AppConfig | None:
    path = config_path(repo_root)
    if path.exists():
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        app = data.get("app", {})
        paths = data.get("paths", {})
        configured_divine = paths.get("divine_path")
        return AppConfig(
            bg3_game_path=Path(paths["bg3_game_path"]),
            bg3_appdata_path=Path(paths["bg3_appdata_path"]),
            divine_path=_resolve_divine_path(repo_root, configured_divine),
            multitool_path=Path(paths["multitool_path"]) if paths.get("multitool_path") else None,
            deploy_mode=app.get("deploy_mode", "junction"),
            release_dir=Path(paths["release_dir"]) if paths.get("release_dir") else None,
            source="app",
        )
    legacy = load_legacy_env(repo_root)
    if legacy:
        legacy.source = "legacy"
    return legacy


def load_legacy_env(repo_root: Path) -> AppConfig | None:
    path = legacy_env_path(repo_root)
    if not path.exists():
        return None

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("$") or "=" not in line:
            continue
        left, right = line.split("=", 1)
        key = left.strip().lstrip("$")
        value = right.strip().strip('"')
        values[key] = value

    required = {"BG3_GAME_PATH", "BG3_APPDATA_PATH"}
    if not required.issubset(values):
        return None

    return AppConfig(
        bg3_game_path=Path(values["BG3_GAME_PATH"]),
        bg3_appdata_path=Path(values["BG3_APPDATA_PATH"]),
        divine_path=_resolve_divine_path(repo_root, values.get("DIVINE_PATH")),
        multitool_path=Path(values["MULTITOOL_PATH"]) if values.get("MULTITOOL_PATH") else None,
        deploy_mode="junction",
        source="legacy",
    )


def write_config(repo_root: Path, config: AppConfig) -> Path:
    path = config_path(repo_root)
    release_dir = config.release_dir or (repo_root / "releases")
    divine_path = _resolve_divine_path(repo_root, str(config.divine_path) if config.divine_path else None)
    text = "\n".join(
        [
            "[app]",
            f"deploy_mode = {_quote(config.deploy_mode)}",
            "",
            "[paths]",
            f"bg3_game_path = {_quote(str(config.bg3_game_path))}",
            f"bg3_appdata_path = {_quote(str(config.bg3_appdata_path))}",
            f"divine_path = {_quote(str(divine_path))}",
            f"multitool_path = {_quote(str(config.multitool_path)) if config.multitool_path else '\"\"'}",
            f"release_dir = {_quote(str(release_dir))}",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")
    return path
