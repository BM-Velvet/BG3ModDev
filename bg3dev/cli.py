from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path

from .actions import (
    choose_version,
    deploy_mod,
    open_shell,
    package_mod,
    run_lua_tests,
    tail_log,
    undeploy_mod,
    validate_mod,
)
from .config import AppConfig, load_config, write_config
from .models import ModInfo
from .registry import ActionSpec, load_registry
from .templates import NewModRequest, available_templates, create_mod
from .workspace import discover_mods, discover_repo_root, find_mod


def main() -> int:
    repo_root = discover_repo_root()
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(repo_root)
    registry = load_registry(repo_root)

    if args.command == "setup":
        run_setup(repo_root, config)
        return 0

    mods = discover_mods(repo_root, config)

    if args.command is None:
        return run_interactive(repo_root, config, registry, mods)
    if args.command == "status":
        print_status(repo_root, config, mods)
        return 0
    if args.command == "new-mod":
        return cmd_new_mod(repo_root, args)
    if args.command == "deploy":
        return with_mod(args.mod, mods, lambda mod: print(deploy_mod(mod, require_config(config), repair=args.repair)))
    if args.command == "undeploy":
        return with_mod(args.mod, mods, lambda mod: print(undeploy_mod(mod, require_config(config))))
    if args.command == "package":
        return with_mod(
            args.mod,
            mods,
            lambda mod: print(package_mod(mod, require_config(config), choose_version(args), args.copy_to_appdata)),
        )
    if args.command == "validate":
        return with_mod(args.mod, mods, lambda mod: print_validation(mod))
    if args.command == "test":
        return with_mod(args.mod, mods, lambda mod: run_lua_tests(mod))
    if args.command == "watch-log":
        handle = args.filter or (f"[{args.mod}]" if args.mod else "")
        return tail_log(require_config(config), handle=handle)
    if args.command == "open-shell":
        return with_mod(args.mod, mods, lambda mod: print(open_shell(mod)))
    if args.command == "run-action":
        return cmd_run_action(args, config, mods, registry)
    raise RuntimeError(f"Unknown command: {args.command}")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="bg3dev", description="BG3 workspace terminal app")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Create or update the local workspace config")
    sub.add_parser("status", help="Show workspace and mod status")

    new_mod = sub.add_parser("new-mod", help="Create a mod from a template")
    new_mod.add_argument("--name", required=False)
    new_mod.add_argument("--template", required=False)
    new_mod.add_argument("--author", required=False)

    deploy = sub.add_parser("deploy", help="Deploy a mod to BG3 Data\\Mods")
    deploy.add_argument("--mod", required=True)
    deploy.add_argument("--repair", action="store_true")

    undeploy = sub.add_parser("undeploy", help="Remove a deployed mod from BG3 Data\\Mods")
    undeploy.add_argument("--mod", required=True)

    package = sub.add_parser("package", help="Package a mod with Divine")
    package.add_argument("--mod", required=True)
    package.add_argument("--version", required=False)
    package.add_argument("--copy-to-appdata", action="store_true")

    validate = sub.add_parser("validate", help="Validate a mod")
    validate.add_argument("--mod", required=True)

    test = sub.add_parser("test", help="Run Lua tests for a mod")
    test.add_argument("--mod", required=True)

    watch = sub.add_parser("watch-log", help="Tail the BG3 log")
    watch.add_argument("--mod", required=False)
    watch.add_argument("--filter", required=False)

    shell = sub.add_parser("open-shell", help="Open a PowerShell prompt in a mod repo")
    shell.add_argument("--mod", required=True)

    action = sub.add_parser("run-action", help="Run a registered action")
    action.add_argument("--mod", required=False)
    action.add_argument("--action", required=True)
    action.add_argument("--version", required=False)
    action.add_argument("--copy-to-appdata", action="store_true")
    action.add_argument("--repair", action="store_true")

    return parser


def run_interactive(
    repo_root: Path,
    config: AppConfig | None,
    registry: dict[str, ActionSpec],
    mods: list[ModInfo],
) -> int:
    while True:
        print_status(repo_root, config, mods)
        print("")
        print("Main Menu")
        print("  1. Setup workspace config")
        print("  2. Create new mod")
        print("  3. View mod details")
        print("  4. Watch BG3 log")
        print("  5. Refresh")
        print("  0. Exit")
        choice = input("> ").strip()
        if choice == "1":
            run_setup(repo_root, config)
            config = load_config(repo_root)
            mods = discover_mods(repo_root, config)
        elif choice == "2":
            cmd_new_mod(repo_root, Namespace(name=None, template=None, author=None))
            mods = discover_mods(repo_root, config)
        elif choice == "3":
            if not mods:
                print("No mods found.")
                continue
            mod = choose_mod(mods)
            if mod:
                run_mod_menu(mod, config, registry)
                mods = discover_mods(repo_root, load_config(repo_root))
        elif choice == "4":
            try:
                tail_log(require_config(config))
            except Exception as exc:  # noqa: BLE001
                print(f"ERROR: {exc}")
        elif choice == "5":
            config = load_config(repo_root)
            mods = discover_mods(repo_root, config)
        elif choice == "0":
            return 0


def run_mod_menu(mod: ModInfo, config: AppConfig | None, registry: dict[str, ActionSpec]) -> None:
    while True:
        print("")
        print_mod_detail(mod)
        available = resolve_actions(mod, config, registry)
        for index, action in enumerate(available, start=1):
            print(f"  {index}. {action.label}")
        print("  0. Back")
        choice = input("> ").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(available)):
            print("Invalid choice.")
            continue
        spec = available[int(choice) - 1]
        try:
            run_action(spec, mod, config, Namespace(version=None, copy_to_appdata=False, repair=False))
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {exc}")


def resolve_actions(mod: ModInfo, config: AppConfig | None, registry: dict[str, ActionSpec]) -> list[ActionSpec]:
    actions = []
    for spec in registry.values():
        if spec.requires_config and not config:
            continue
        if spec.requires_divine and (not config or not config.divine_path.exists()):
            continue
        if spec.requires_tests and not mod.has_tests:
            continue
        actions.append(spec)
    return actions


def cmd_run_action(
    args: Namespace,
    config: AppConfig | None,
    mods: list[ModInfo],
    registry: dict[str, ActionSpec],
) -> int:
    spec = registry.get(args.action)
    if not spec:
        raise RuntimeError(f"Unknown action: {args.action}")
    mod = find_mod(mods, args.mod) if spec.mod_required else None
    return run_action(spec, mod, config, args)


def run_action(spec: ActionSpec, mod: ModInfo | None, config: AppConfig | None, args: Namespace) -> int:
    if spec.handler == "deploy":
        print(deploy_mod(require_mod(mod), require_config(config), repair=args.repair))
        return 0
    if spec.handler == "undeploy":
        print(undeploy_mod(require_mod(mod), require_config(config)))
        return 0
    if spec.handler == "package":
        print(package_mod(require_mod(mod), require_config(config), choose_version(args), args.copy_to_appdata))
        return 0
    if spec.handler == "validate":
        return print_validation(require_mod(mod))
    if spec.handler == "run_tests":
        return run_lua_tests(require_mod(mod))
    if spec.handler == "watch_log":
        target = require_mod(mod)
        handle = f"[{target.meta.folder or target.name}]"
        return tail_log(require_config(config), handle=handle)
    if spec.handler == "open_shell":
        print(open_shell(require_mod(mod)))
        return 0
    raise RuntimeError(f"Unsupported action handler: {spec.handler}")


def require_config(config: AppConfig | None) -> AppConfig:
    if not config:
        raise RuntimeError("No app config found. Run `python -m bg3dev setup` first.")
    return config


def require_mod(mod: ModInfo | None) -> ModInfo:
    if not mod:
        raise RuntimeError("This action requires a mod.")
    return mod


def print_validation(mod: ModInfo) -> int:
    issues = validate_mod(mod)
    if not issues:
        print(f"{mod.name}: OK")
        return 0
    print(f"{mod.name}:")
    for issue in issues:
        print(f"  - {issue}")
    return 1


def print_status(repo_root: Path, config: AppConfig | None, mods: list[ModInfo]) -> None:
    print("BG3ModDev")
    print(f"Root: {repo_root}")
    if not config:
        print("Config: missing")
    else:
        source = "bg3dev config" if config.source == "app" else ".env.ps1 (legacy)"
        print(f"Config: {source}")
        print(f"BG3: {config.bg3_game_path}")
        print(f"AppData: {config.bg3_appdata_path}")
        print(f"Deploy target: {config.deploy_target_dir}")
        print(f"Divine: {'OK' if config.divine_path.exists() else 'missing'} ({config.divine_path})")
    print("")
    if not mods:
        print("No mods discovered under mods/.")
        return
    print("Mods")
    for mod in mods:
        deploy = "deployed" if mod.deploy.correct else ("mismatch" if mod.deploy.exists else "not deployed")
        git_state = "dirty" if mod.git.dirty else ("clean" if mod.git.is_repo else "no git")
        ready = "ready" if mod.is_bg3_ready else "incomplete"
        print(f"  - {mod.name}: {ready}, {git_state}, {deploy}")


def print_mod_detail(mod: ModInfo) -> None:
    git_line = mod.git.branch or "<detached>"
    if not mod.git.is_repo:
        git_line = "not a git repo"
    print(f"Mod: {mod.name}")
    print(f"Path: {mod.path}")
    print(f"Type: {mod.template_type or 'unknown'}")
    print(f"Display name: {mod.meta.name or '<missing>'}")
    print(f"Folder: {mod.meta.folder or '<missing>'}")
    print(f"Author: {mod.meta.author or '<missing>'}")
    print(f"UUID: {mod.meta.uuid or '<missing>'}")
    print(f"ModTable: {mod.mod_table or '<missing>'}")
    print(f"Git: {git_line}")
    if mod.git.summary:
        print(f"Git changes: {len(mod.git.summary)}")
    print(f"Deployment: {'correct' if mod.deploy.correct else mod.deploy.problem or 'not deployed'}")
    print(f"Tests: {'yes' if mod.has_tests else 'no'}")
    print(f"Placeholders: {'yes' if mod.has_placeholders else 'no'}")


def choose_mod(mods: list[ModInfo]) -> ModInfo | None:
    print("Choose mod")
    for index, mod in enumerate(mods, start=1):
        print(f"  {index}. {mod.name}")
    print("  0. Back")
    choice = input("> ").strip()
    if choice == "0":
        return None
    if not choice.isdigit() or not (1 <= int(choice) <= len(mods)):
        print("Invalid choice.")
        return None
    return mods[int(choice) - 1]


def cmd_new_mod(repo_root: Path, args: Namespace) -> int:
    templates = available_templates(repo_root)
    name = args.name or input("Mod name: ").strip()
    template = args.template or choose_template(templates)
    author = args.author or input("Author [Unknown]: ").strip() or "Unknown"
    dest = create_mod(repo_root, NewModRequest(mod_name=name, template=template, author=author))
    print(f"Created {dest}")
    return 0


def choose_template(templates: list[str]) -> str:
    print("Template")
    for index, name in enumerate(templates, start=1):
        print(f"  {index}. {name}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(templates):
            return templates[int(choice) - 1]
        print("Invalid choice.")


def run_setup(repo_root: Path, existing: AppConfig | None) -> None:
    defaults = existing or AppConfig(
        bg3_game_path=Path(r"C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3"),
        bg3_appdata_path=Path.home() / "AppData" / "Local" / "Larian Studios" / "Baldur's Gate 3",
        divine_path=repo_root / "divine" / "divine.exe",
        multitool_path=Path.home() / "Documents" / "BG3ModdersMultitool",
        release_dir=repo_root / "releases",
    )
    config = AppConfig(
        bg3_game_path=Path(prompt_path("BG3 game path", defaults.bg3_game_path)),
        bg3_appdata_path=Path(prompt_path("BG3 AppData path", defaults.bg3_appdata_path)),
        divine_path=Path(prompt_path("Divine path", defaults.divine_path)),
        multitool_path=Path(prompt_path("Multitool path", defaults.multitool_path)) if defaults.multitool_path else None,
        deploy_mode="junction",
        release_dir=repo_root / "releases",
    )
    path = write_config(repo_root, config)
    print(f"Wrote {path}")


def prompt_path(label: str, default: Path | None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or str(default or "")


def with_mod(mod_name: str, mods: list[ModInfo], fn) -> int:
    mod = find_mod(mods, mod_name)
    result = fn(mod)
    if isinstance(result, int):
        return result
    return 0
