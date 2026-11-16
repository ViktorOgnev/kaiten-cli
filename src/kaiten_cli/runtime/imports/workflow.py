"""Plan, stage, authorize and reconcile a single migration run."""

from __future__ import annotations

import json
import re
import shutil
import shlex
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4
from zipfile import BadZipFile, ZipFile

import click

from kaiten_cli.errors import CliError, ValidationError
from kaiten_cli.i18n import get_locale, tr
from kaiten_cli.runtime.fs_security import open_private_append, secure_directory
from kaiten_cli.runtime.imports import convertinator, trello
from kaiten_cli.runtime.imports.storage import (
    atomic_json,
    fingerprint,
    free_bytes,
    inspect_package,
    load_run,
    lock_run,
    read_json,
    read_secrets,
    require_disk,
    require_writable,
    root_dir,
    run_dir,
    writable,
)

FAQ = "https://faq-ru.kaiten.site/"
SOURCES = {
    "trello": ("package", "kak-perenesti-zadachi-iz-trello-v-kaiten", None),
    "package": ("package", "universalnyy-import-v-kaiten-iz-lyubyh-sistem", "external_profile"),
    "jira-zip": ("convertinator", "import-iz-jira-cherez-convertinator", "jira_backup"),
    "clickup": ("convertinator", "kak-perenesti-dannye-iz-clickup-v-kaiten", "clickup_api_token"),
    "notion": ("convertinator", "kak-perenesti-dannye-iz-notion-v-kaiten", "notion_export"),
    "yougile": ("convertinator", "kak-perenesti-dannye-iz-yougile-v-kaiten", "yougile_login"),
    "jira": ("web", "kak-perenesti-zadachi-iz-jira-v-kaiten-confluence", "jira_access"),
    "confluence": ("web", "import-zadach1", "confluence_access"),
    "asana": ("web", "kak-perenesti-zadachi-iz-asana-v-kaiten", "asana_api_token"),
    "csv": ("web", "import-zadach1", "csv_xls_file"),
}
FILE_SOURCES = {"package", "jira-zip", "notion", "csv"}
TERMINAL = {"completed", "completed_with_losses", "failed", "cancelled"}
REPORT_NAME = re.compile(
    r"kaiten-company-import-(completed|partial|failed|cancelled)-([a-f0-9-]{36})\.json"
)


def sources() -> dict:
    return {
        "sources": [
            {"source": name, "mode": mode, "input": required, "instructions": FAQ + guide}
            for name, (mode, guide, required) in SOURCES.items()
        ],
        "custom_format": "https://developers.kaiten.ru/imports/bundle-format",
    }


def _command(path: Path, action: str, profile: str | None = None) -> str:
    profile_arg = f" --profile {shlex.quote(profile)}" if profile else ""
    command = f"kaiten --locale {get_locale()}{profile_arg} import {action} --run {path.name}"
    return (
        command
        if path.parent == root_dir()
        else f"{command} --work-dir {shlex.quote(str(path.parent))}"
    )


def _save(path: Path, run: dict, state: str, action: str | None = None) -> dict:
    run["state"] = state
    run["next_action"] = (
        {"command": _command(path, action, run.get("profile_name"))} if action else None
    )
    atomic_json(path / "run.json", run)
    with open_private_append(path / "events.jsonl") as log:
        log.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "state": state}) + "\n")
    return _public(run)


def _public(run: dict) -> dict:
    return {
        key: value
        for key, value in run.items()
        if key not in {"owner_email", "operator_id", "approval_context"}
    }


def _input_path(value: str) -> Path:
    path = Path(value).expanduser().absolute()
    if path.is_symlink() or not (path.is_file() or path.is_dir()):
        raise ValidationError(tr("Select an existing import file or directory."))
    return path.resolve()


async def _target(
    client, space_id: int, company_id: int | None = None, space_uid: str | None = None
) -> tuple[dict, dict]:
    user = await client.get("/users/current")
    space = await client.get(f"/spaces/{space_id}")
    if (
        not isinstance(user, dict)
        or type(user.get("id")) is not int
        or not isinstance(space, dict)
        or space.get("id") != space_id
    ):
        raise ValidationError(tr("Kaiten did not identify the selected user and space."))
    actual_uid = space.get("uid")
    if space_uid is not None:
        try:
            space_uid = str(UUID(space_uid))
        except (TypeError, ValueError, AttributeError):
            raise ValidationError(tr("Invalid target space UUID.")) from None
        if actual_uid and space_uid != actual_uid:
            raise ValidationError(
                tr("The Kaiten target or authenticated user changed. Create a new import plan.")
            )
    actual_company = space.get("company_id") or user.get("company_id")
    if company_id is not None and actual_company is not None and company_id != actual_company:
        raise ValidationError(tr("The selected space belongs to a different Kaiten company."))
    return {
        "origin": client.root_url,
        "company_id": actual_company or company_id,
        "space_id": space_id,
        "space_uid": actual_uid or space_uid,
        "space_title": space.get("title"),
        "url": f"{client.root_url}/space/{space_id}",
    }, user


async def _check_target(client, run: dict) -> None:
    expected = run["target"]
    if client.root_url != expected["origin"]:
        raise ValidationError(
            tr("The Kaiten target or authenticated user changed. Create a new import plan.")
        )
    actual, user = await _target(
        client, expected["space_id"], expected["company_id"], expected["space_uid"]
    )
    if (
        any(actual.get(key) != expected.get(key) for key in ("company_id", "space_id", "space_uid"))
        or user.get("id") != run["operator_id"]
    ):
        raise ValidationError(
            tr("The Kaiten target or authenticated user changed. Create a new import plan.")
        )


def infer_source(options: dict) -> str | None:
    if source := options.get("source"):
        return source
    if options.get("boards"):
        return "trello"
    if not options.get("input"):
        return None
    path = _input_path(options["input"])
    if path.is_dir():
        return "package" if (path / "meta-data.json").is_file() else None
    if path.suffix.lower() in {".csv", ".xls", ".xlsx"}:
        return "csv"
    if path.suffix.lower() == ".zip":
        try:
            with ZipFile(path) as archive:
                names = set(archive.namelist())
        except (OSError, BadZipFile):
            return None
        if "meta-data.json" in names:
            return "package"
        if "entities.xml" in names:
            return "jira-zip"
    return None


async def plan(client, options: dict) -> dict:
    source = infer_source(options)
    if not source:
        return {"state": "needs_input", "next_action": {"input": "source"}, **sources()}
    if source not in SOURCES:
        return {"state": "needs_input", "next_action": {"input": "external_profile"}, **sources()}
    space_id = options.get("space_id")
    if not space_id:
        rows = await client.get("/spaces", params={"limit": 25})
        return {
            "state": "needs_input",
            "next_action": {"input": "space_id"},
            "spaces": [
                {k: row.get(k) for k in ("id", "title", "company_id")}
                for row in rows
                if isinstance(row, dict)
            ],
        }
    mode, guide, needed = SOURCES[source]
    selected, user = await _target(
        client, space_id, options.get("company_id"), options.get("space_uid")
    )
    path = run_dir(str(uuid4()), options.get("work_dir"))
    file = _input_path(options["input"]) if options.get("input") else None
    if file and file.is_dir() and (source != "package" or path.resolve().is_relative_to(file)):
        raise ValidationError(
            tr("Choose an import file or keep the workspace outside the source package.")
        )
    boards = list(dict.fromkeys(trello.board_id(s) for s in options.get("boards", [])))
    column_types = options.get("column_types", {})
    if any(
        trello.board_id(key) != key or not isinstance(state, str) or state not in trello.COLUMNS
        for key, state in column_types.items()
    ):
        raise ValidationError(
            tr("Column types must map Trello list IDs to queued, in_progress or done.")
        )
    if source != "trello" and (boards or column_types):
        raise ValidationError(tr("Board selectors and column types apply only to Trello."))
    if source == "trello" and file and boards:
        raise ValidationError(tr("Choose a Trello export or Trello board selectors."))
    if len(boards) > 20:
        raise ValidationError(tr("Plan at most 20 Trello boards in one run."))
    run = {
        "version": 1,
        "run_id": path.name,
        "work_path": str(path),
        "source": source,
        "mode": mode,
        "profile_name": options.get("_profile_name"),
        "input": str(file) if file else None,
        "target": selected,
        "boards": boards,
        "column_types": column_types,
        "operator_id": user["id"],
        "owner_email": user.get("email"),
        "disk_free_bytes": free_bytes(path),
        "estimated_bytes": None,
        "instructions": FAQ + guide,
        "required_input": needed,
        "permissions": [
            "target_space_read",
            "target_space_update",
            "target_entities_create",
            "company_import",
        ],
    }
    if mode == "package":
        run["permissions"].append("universal_format_2_enabled")
    if mode != "web":
        run["access_notice"] = convertinator.access_notice()
    if file and source == "package":
        run["preview"] = inspect_package(file)
        run["estimated_bytes"] = run["preview"]["bytes"]
    elif file and source == "trello":
        require_disk(path, file.stat().st_size)
        data = trello.export_data(file)
        run["preview"] = [trello.board_preview(data, column_types)]
        run["source_records_observed"] = len(data["cards"])
        run["estimated_bytes"] = file.stat().st_size * 3
    elif file and file.is_file():
        if source in {"jira-zip", "notion"} and file.suffix.lower() != ".zip":
            raise ValidationError(tr("This import source requires a ZIP export."))
        if source == "csv" and file.suffix.lower() not in {".csv", ".xls", ".xlsx"}:
            raise ValidationError(tr("Select a CSV, XLS or XLSX file."))
        run["estimated_bytes"] = file.stat().st_size
    if source == "trello":
        run["omitted_categories"] = list(trello.OMITTED)
        if not file and not boards:
            return {
                **_public(run),
                "run_id": None,
                "work_path": None,
                "state": "needs_input",
                "next_action": {"input": "boards_or_export"},
            }
        if boards and (secret := trello.credentials({})):
            api = trello.Trello(secret, client.execution_context.stats)
            async with api.http:
                run["preview"] = [
                    trello.board_preview(await api.metadata(board), column_types)
                    for board in boards
                ]
    if source in FILE_SOURCES and file is None:
        return {
            **_public(run),
            "run_id": None,
            "work_path": None,
            "state": "needs_input",
            "next_action": {"input": needed},
        }
    if not writable():
        return {
            **_public(run),
            "run_id": None,
            "work_path": None,
            "state": "diagnostic",
            "next_action": {"input": "local_cli_session"},
        }
    secure_directory(path.parent, repair_existing=not bool(options.get("work_dir")))
    secure_directory(path)
    if boards and not trello.credentials({}):
        run["credential_env"] = [trello.KEY_ENV, trello.TOKEN_ENV]
        return _save(path, run, "needs_credentials", "credentials")
    return _save(path, run, "planned", "prepare")


def credentials(path: Path, run: dict, *, interactive: bool) -> dict:
    if run["source"] != "trello" or not run["boards"]:
        raise ValidationError(tr("This run does not need Trello API credentials."))
    run["credential_env"] = [trello.KEY_ENV, trello.TOKEN_ENV]
    if run["state"] not in {"planned", "needs_credentials", "preparing"}:
        return _public(run)
    if trello.credentials(read_secrets(path)):
        return _save(
            path, run, "planned" if run["state"] == "needs_credentials" else run["state"], "prepare"
        )
    if not interactive:
        return {
            **_public(run),
            "state": "needs_credentials",
            "next_action": {
                "command": _command(path, "credentials", run.get("profile_name")),
                "interactive": True,
            },
        }
    key = click.prompt(tr("Trello API key"), hide_input=True)
    token = click.prompt(tr("Trello read-only token"), hide_input=True)
    if not trello.credentials({"key": key, "token": token}):
        raise ValidationError(tr("Invalid Trello credential format."))
    atomic_json(path / "credentials.json", {"key": key, "token": token})
    return _save(
        path, run, "planned" if run["state"] == "needs_credentials" else run["state"], "prepare"
    )


async def prepare(client, path: Path, run: dict) -> dict:
    if run["state"] not in {"planned", "needs_credentials", "preparing", "prepared"}:
        return _public(run)
    await _check_target(client, run)
    if run["state"] != "prepared" and run["mode"] == "package":
        await _prepare_package(client, path, run)
        if not run.get("package"):
            return _public(load_run(path))
    return _save(path, run, "prepared", "open")


async def _prepare_package(client, path: Path, run: dict) -> None:
    package = path / "package"
    if package.exists():
        # A crash can leave a complete stage without its manifest update. Reuse only recorded stages.
        if run.get("package") and fingerprint(package) == run.get("package_sha256"):
            return
        shutil.rmtree(package)
    require_disk(path, run["estimated_bytes"] or 0)
    if run["source"] == "trello" and run["boards"]:
        secret = trello.credentials(read_secrets(path))
        if secret is None:
            run["credential_env"] = [trello.KEY_ENV, trello.TOKEN_ENV]
            _save(path, run, "needs_credentials", "credentials")
            return
    else:
        secret = None
    _save(path, run, "preparing", "prepare")
    with tempfile.TemporaryDirectory(prefix=".stage-", dir=path) as temp:
        stage = Path(temp) / "package"
        secure_directory(stage)
        if run["source"] == "package":
            run["package_summary"] = inspect_package(Path(run["input"]), stage)
            run["package_summary"] = inspect_package(stage)
        else:
            if secret:
                api = trello.Trello(secret, client.execution_context.stats)
                boards = []
                async with api.http:
                    for selector in run["boards"]:
                        checkpoints = path / f"trello-{selector}"
                        board, total = await api.download(checkpoints, selector)
                        boards.append((board, _pages(checkpoints, total)))
            else:
                board = trello.export_data(Path(run["input"]))
                cards = board.pop("cards")
                boards = [
                    (board, (cards[index : index + 100] for index in range(0, len(cards), 100)))
                ]
            run["package_summary"] = trello.write_package(
                stage,
                boards,
                run["owner_email"],
                run["column_types"],
                Path(temp),
            )
            run["package_summary"].update(inspect_package(stage))
        run["package_sha256"] = fingerprint(stage)
        stage.rename(package)
    run["package"] = str(package)
    (path / "credentials.json").unlink(missing_ok=True)
    _save(path, run, "preparing", "prepare")


def _pages(path: Path, count: int):
    for index in range(count):
        yield read_json(path / f"{index:06}.json", trello.MAX_RESPONSE * 2)["cards"]


def _check_package(run: dict) -> None:
    if run.get("package") and fingerprint(Path(run["package"])) != run["package_sha256"]:
        raise ValidationError(tr("The prepared package changed. Create a new import plan."))


async def open_import(client, path: Path, run: dict, options: dict) -> dict:
    if run["state"] not in {"prepared", "gui_pending"}:
        return _public(run)
    await _check_target(client, run)
    _check_package(run)
    target_url = run["target"]["url"]
    if options.get("_interactive"):
        click.echo(
            json.dumps(
                {key: run.get(key) for key in ("target", "package", "input", "access_notice")},
                ensure_ascii=False,
                indent=2,
            ),
            err=True,
        )

    app_opened = False
    browser_opened = False
    install_guide = None
    if run["mode"] == "web":
        browser_opened = convertinator.launch_browser(target_url)
        instructions = tr("Open Add → Import in the target space and select the source.")
    else:
        app = convertinator.desktop_app(options.get("app_path"))
        if app is not None:
            app_opened = convertinator.launch_desktop(app)
        if app_opened:
            instructions = (
                tr(
                    "Sign in to the displayed Kaiten company, choose Universal Import, open the prepared package, select the exact target space, and run the check before importing."
                )
                if run["mode"] == "package"
                else tr(
                    "Sign in to the displayed Kaiten company, choose the source in Convertinator and follow the linked instructions."
                )
            )
        elif app is None:
            browser_opened = convertinator.launch_browser(target_url)
            install_guide = convertinator.INSTALL_GUIDE
            instructions = tr(
                "In the target space, open Add → Import → Universal Import to download Convertinator. In a closed network, contact Kaiten support if the download links are unavailable."
            )
        else:
            instructions = tr("Open the installed Convertinator from your desktop to continue.")
    run["handoff"] = {
        "app_opened": app_opened,
        "browser_opened": browser_opened,
        "instructions": instructions,
        "installer": install_guide,
    }
    action = "status" if run["mode"] == "web" or app_opened else "open"
    return _save(path, run, "gui_pending", action)


async def status(client, path: Path, run: dict, options: dict) -> dict:
    if run["state"] not in TERMINAL | {"gui_pending", "operator_reported"} and not options.get(
        "report"
    ):
        return _public(run)
    await _check_target(client, run)
    if options.get("report"):
        _operator_report(path, run, Path(options["report"]).expanduser())
    if run["state"] in {"completed", "completed_with_losses", "gui_pending", "operator_reported"}:
        try:
            run["reconciliation"] = await _reconcile(client, run)
        except CliError:
            run["reconciliation"] = {"state": "unavailable"}
    if run["state"] == "gui_pending":
        action = "status" if run["mode"] == "web" or run["handoff"]["app_opened"] else "open"
    else:
        action = "cleanup"
    return _save(path, run, run["state"], action)


def _operator_report(path: Path, run: dict, file: Path) -> None:
    match = REPORT_NAME.fullmatch(file.name)
    if run["state"] not in {"gui_pending", "operator_reported"} or not match:
        raise ValidationError(
            tr("Select a terminal report downloaded from Convertinator for this GUI run.")
        )
    raw = read_json(file)
    if not isinstance(raw, dict) or raw.get("report_complete") is not True:
        raise ValidationError(
            tr("Select a terminal report downloaded from Convertinator for this GUI run.")
        )
    try:
        job = str(UUID(match[2]))
    except ValueError:
        raise ValidationError(
            tr("Select a terminal report downloaded from Convertinator for this GUI run.")
        ) from None
    if run.get("operator_report") and run["operator_report"]["job_id"] != job:
        raise ValidationError(tr("This run already has a report for another operation."))
    atomic_json(path / "operator-report.json", raw)
    run["report_path"] = str(path / "operator-report.json")
    run["operator_report"] = {"outcome": match[1], "job_id": job, "verified_target": False}
    run["state"] = "operator_reported"


async def _reconcile(client, run: dict) -> dict:
    package = run.get("package")
    if not package:
        return {"state": "unavailable"}
    root = Path(package)
    _check_package(run)
    manifest = read_json(root / "meta-data.json")
    expected = {}
    for file in manifest["resource_files"]:
        if file["resource"] in {"boards", "columns", "cards"}:
            expected.setdefault(file["resource"], set()).update(
                row["external_id"]
                for row in read_json(root / file["path"])
                if isinstance(row, dict) and isinstance(row.get("external_id"), str)
            )
    if not any(expected.values()):
        return {"state": "unavailable"}
    space = run["target"]["space_id"]
    boards = await client.get(f"/spaces/{space}/boards")
    matching = [
        board for board in boards if board.get("external_id") in expected.get("boards", set())
    ]
    matched = {
        "boards": {board["external_id"] for board in matching},
        "columns": set(),
        "cards": set(),
    }
    for board in matching:
        board_id = int(board["id"])
        columns = await client.get(f"/boards/{board_id}/columns")
        matched["columns"].update(
            {row.get("external_id") for row in columns} & expected.get("columns", set())
        )
        seen = set()
        for offset in range(0, 100_000, 100):
            rows = await client.get(
                "/cards", params={"board_id": board_id, "limit": 100, "offset": offset}
            )
            ids = {row["id"] for row in rows}
            if ids & seen:
                break
            seen |= ids
            matched["cards"].update(
                {row.get("external_id") for row in rows} & expected.get("cards", set())
            )
            if len(rows) < 100:
                break
    matches = {key: len(value) for key, value in matched.items()}
    totals = {key: len(expected.get(key, ())) for key in matches}
    return {
        "state": "matched" if matches == totals else "partial",
        "matched": matches,
        "expected": totals,
    }


def cleanup(path: Path, run: dict) -> dict:
    if run["state"] not in TERMINAL | {
        "operator_reported",
        "cleaned",
        "blocked",
        "planned",
        "needs_credentials",
        "preparing",
        "prepared",
    }:
        raise ValidationError(tr("Cleanup is available before upload or after an import result."))
    for child in path.iterdir():
        if child.name == "package" or child.name.startswith(("trello-", ".stage-")):
            if child.is_symlink() or not child.is_dir():
                child.unlink()
            else:
                shutil.rmtree(child)
    (path / "credentials.json").unlink(missing_ok=True)
    run.pop("package", None)
    return _save(path, run, "cleaned")


async def wizard(client, options: dict) -> dict:
    if not options.get("_interactive"):
        return {
            "state": "needs_input",
            "next_action": {"command": f"kaiten --locale {get_locale()} --json import plan"},
        }
    require_writable()
    options = dict(options)
    if inferred := infer_source(options):
        options["source"] = inferred
    if not options.get("source"):
        options["source"] = click.prompt(tr("Import source"), type=click.Choice(list(SOURCES)))
    if not options.get("space_id"):
        available = await plan(client, options)
        click.echo(json.dumps(available.get("spaces", []), ensure_ascii=False, indent=2), err=True)
        options["space_id"] = click.prompt(tr("Target Kaiten space ID"), type=click.IntRange(min=1))
    source = options["source"]
    if source == "trello" and not (options.get("input") or options.get("boards")):
        mode = click.prompt(tr("Trello input mode"), type=click.Choice(["api", "json"]))
        if mode == "api":
            options["boards"] = [click.prompt(tr("Trello board ID or URL"))]
        else:
            options["input"] = click.prompt(tr("Path to the source export or package."))
    elif source in FILE_SOURCES and not options.get("input"):
        options["input"] = click.prompt(tr("Path to the source export or package."))
    result = await plan(client, options)
    if not result.get("run_id"):
        return result
    click.echo(json.dumps(result, ensure_ascii=False, indent=2), err=True)
    path = run_dir(result["run_id"], options.get("work_dir"))
    with lock_run(path):
        run = load_run(path)
        if run["state"] == "needs_credentials":
            credentials(path, run, interactive=True)
        result = await prepare(client, path, run)
        if result["state"] != "prepared":
            return result
        return await open_import(client, path, run, options)


async def execute(client, tool, options, _request, _query, _body, _timeout, _reporter):
    action = tool.action
    if action == "sources":
        return sources()
    if action == "plan":
        return await plan(client, options)
    if action == "run":
        return await wizard(client, options)
    if action == "status" and not writable():
        if options.get("report"):
            require_writable()
        return _public(load_run(run_dir(options["run"], options.get("work_dir"))))
    path = run_dir(options["run"], options.get("work_dir"))
    with lock_run(path):
        run = load_run(path)
        if action == "prepare":
            return await prepare(client, path, run)
        if action == "open":
            return await open_import(client, path, run, options)
        if action == "status":
            return await status(client, path, run, options)
        if action == "credentials":
            return credentials(path, run, interactive=options.get("_interactive", False))
        if action == "cleanup":
            return cleanup(path, run)
        raise AssertionError(action)
