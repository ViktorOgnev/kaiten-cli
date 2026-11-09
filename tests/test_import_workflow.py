from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import httpx
import pytest

from kaiten_cli.app import cli
from kaiten_cli.errors import TransportError, ValidationError
from kaiten_cli.runtime.client import KaitenClient
from kaiten_cli.runtime.imports import convertinator, storage, trello

BOARD = "655000000000000000000001"
LIST = "655000000000000000000002"
CARD = "655000000000000000000003"
SPACE_UID = "11111111-1111-4111-8111-111111111111"


def export():
    return {
        "id": BOARD,
        "name": "Migration",
        "dateLastActivity": "2026-11-09T10:00:00Z",
        "lists": [{"id": LIST, "name": "Doing", "pos": 10, "closed": False}],
        "cards": [
            {
                "id": CARD,
                "idList": LIST,
                "name": "First",
                "desc": "**Sample**",
                "pos": 5,
                "due": "2026-12-15T00:00:00Z",
                "labels": [{"name": "Priority"}, {"name": "priority"}],
                "badges": {"attachments": 1},
            },
            {"id": "655000000000000000000004", "idList": LIST, "name": "Archived", "closed": True},
        ],
    }


@pytest.fixture
def command(runner, monkeypatch, tmp_path):
    monkeypatch.setenv("KAITEN_DOMAIN", "http://localhost:3100")
    monkeypatch.setenv("KAITEN_TOKEN", "test-kaiten-token")
    monkeypatch.delenv("KAITEN_CLI_READ_ONLY", raising=False)
    monkeypatch.delenv("KAITEN_CLI_STORAGE_READ_ONLY", raising=False)
    monkeypatch.delenv(convertinator.RUNNER_ENV, raising=False)
    company = {"id": 17}

    async def get(_self, path, **_kwargs):
        return {
            "/users/current": {"id": 42, "email": "tester@example.test"},
            "/spaces/7": {"id": 7, "uid": SPACE_UID, "title": "Test", "company_id": company["id"]},
            "/spaces/7/boards": [{"id": 10, "external_id": f"trello:{BOARD}"}],
            "/boards/10/columns": [{"id": 22, "external_id": f"trello:{LIST}"}],
            "/cards": [{"id": 100, "external_id": f"trello:{CARD}"}],
        }[path]

    monkeypatch.setattr(KaitenClient, "get", get)
    monkeypatch.setattr(convertinator, "desktop_app", lambda: None)
    monkeypatch.setattr(convertinator, "has_desktop", lambda: False)
    source = tmp_path / "trello.json"
    storage.atomic_json(source, export())
    root = tmp_path / "import workspace"

    def invoke(*args, expected=0, read_only=False):
        prefix = ["--locale", "en", "--json"] + (["--read-only"] if read_only else [])
        result = runner.invoke(cli, [*prefix, "import", *args, "--work-dir", str(root)])
        assert result.exit_code == expected, result.output
        data = json.loads(result.output)
        return data["data"] if expected == 0 else data["error"]

    return invoke, source, company


def _prepare(command):
    invoke, source, _company = command
    planned = invoke(
        "plan",
        "--source",
        "trello",
        "--space-id",
        "7",
        "--input",
        str(source),
        "--column-types",
        json.dumps({LIST: "in_progress"}),
    )
    run = planned["run_id"]
    return run, invoke("prepare", "--run", run, "--no-install")


def test_trello_export_and_gui_handoff(command):
    invoke, source, _company = command
    run, prepared = _prepare(command)
    path = Path(prepared["work_path"])
    package = Path(prepared["package"])
    cards = json.loads(next((package / "resources").glob("cards-*.json")).read_text())
    columns = json.loads((package / "resources/columns.json").read_text())
    assert cards[0]["external_id"] == f"trello:{CARD}"
    assert cards[0]["description"]["text"] == "**Sample**"
    assert cards[0]["due_date"]["precision"] == "date_time"
    assert len(cards[0]["tag_refs"]) == 1
    assert columns[0]["type"] == "in_progress"
    assert prepared["package_summary"]["omitted_observed"]["archived_cards"] == 1
    assert prepared["package_summary"]["omitted_observed"]["attachments"] == 1
    assert invoke("prepare", "--run", run)["package_sha256"] == prepared["package_sha256"]
    assert invoke("preflight", "--run", run)["state"] == "needs_preflight_approval"
    assert (
        invoke(
            "preflight",
            "--run",
            run,
            "--approval",
            prepared["approval"],
            expected=6,
            read_only=True,
        )["type"]
        == "mutation_blocked"
    )
    launched = invoke("preflight", "--run", run, "--approval", prepared["approval"])
    assert launched["state"] == "gui_pending"
    assert launched["handoff"]["app_opened"] is False
    assert invoke("status", "--run", run)["reconciliation"]["state"] == "matched"
    assert invoke("start", "--run", run, expected=6, read_only=True)["type"] == "mutation_blocked"
    report = path / f"kaiten-company-import-completed-{uuid4()}.json"
    storage.atomic_json(report, {"report_complete": True})
    status = invoke("status", "--run", run, "--report", str(report))
    assert status["state"] == "operator_reported"
    assert not status["operator_report"]["verified_target"]
    assert invoke("cleanup", "--run", run)["state"] == "cleaned"
    assert source.exists() and not package.exists()
    assert (path / "operator-report.json").exists()
    assert (path / "events.jsonl").exists()


def test_target_and_package_mutation_invalidate_approval(command):
    invoke, _source, company = command
    run, prepared = _prepare(command)
    company["id"] = 18
    assert (
        invoke("preflight", "--run", run, "--approval", prepared["approval"], expected=2)["type"]
        == "validation_error"
    )
    company["id"] = 17
    package = Path(prepared["package"])
    (package / "resources/boards.json").write_text("[]")
    assert (
        invoke("preflight", "--run", run, "--approval", prepared["approval"], expected=2)["type"]
        == "validation_error"
    )


def test_machine_preflight_and_ambiguous_start_resume(command, monkeypatch):
    invoke, _source, _company = command
    run, prepared = _prepare(command)
    monkeypatch.setenv(convertinator.RUNNER_ENV, "/local/test-runner")
    job = str(uuid4())
    calls = []

    async def machine(action, payload, *, token):
        assert token == "test-kaiten-token"
        assert payload["target"]["space_uid"] == SPACE_UID
        calls.append(action)
        if action == "start":
            assert payload["tolerate_warnings"] is True
            assert payload["job_id"] == job
            raise TransportError("Lost response")
        states = {"capabilities": "supported", "preflight": "warnings", "status": "completed"}
        return {
            "state": states[action],
            "target": payload["target"],
            "job_id": job,
            "report": {"has_warning_violations": True},
        }

    monkeypatch.setattr(convertinator, "machine", machine)
    checked = invoke("preflight", "--run", run, "--approval", prepared["approval"])
    assert checked["state"] == "awaiting_start"
    assert checked["approval"] != prepared["approval"]
    assert (
        invoke("start", "--run", run, "--approval", prepared["approval"])["state"]
        == "needs_start_approval"
    )
    invoke("start", "--run", run, "--approval", checked["approval"], expected=5)
    resumed = invoke("start", "--run", run, "--approval", checked["approval"])
    assert resumed["state"] == "completed"
    assert resumed["job_id"] == job
    assert resumed["reconciliation"]["state"] == "matched"
    assert calls == ["capabilities", "preflight", "start", "status"]


def test_secret_instructions_and_read_only_gateway(command, monkeypatch):
    invoke, _source, _company = command
    monkeypatch.delenv(trello.KEY_ENV, raising=False)
    monkeypatch.delenv(trello.TOKEN_ENV, raising=False)
    planned = invoke(
        "plan", "--source", "trello", "--space-id", "7", "--boards", json.dumps([BOARD])
    )
    assert planned["state"] == "needs_credentials"
    run = planned["run_id"]
    assert invoke("credentials", "--run", run)["next_action"]["interactive"]
    assert invoke("prepare", "--run", run, "--no-install")["credential_env"] == [
        trello.KEY_ENV,
        trello.TOKEN_ENV,
    ]
    monkeypatch.setenv("KAITEN_CLI_STORAGE_READ_ONLY", "1")
    result = invoke(
        "plan", "--source", "trello", "--space-id", "7", "--boards", json.dumps([BOARD])
    )
    assert result["state"] == "diagnostic" and not result["run_id"]
    assert invoke("credentials", "--run", run, expected=3)["type"] == "config_error"


def test_trello_pagination_429_and_durable_checkpoints(tmp_path, monkeypatch):
    monkeypatch.setattr(trello, "PAGE_SIZE", 2)
    monkeypatch.setattr(trello, "MAX_RESPONSE", 2048)
    data = export()
    rows = [
        {"id": "655000040000000000000001"},
        {"id": "655000030000000000000002"},
        {"id": "655000020000000000000003"},
    ]
    calls = []
    rate_limited = True
    fail_second = True
    real_sleep = asyncio.sleep

    async def sleep(_delay):
        await real_sleep(0)

    monkeypatch.setattr(trello.asyncio, "sleep", sleep)

    def handle(request):
        nonlocal rate_limited
        assert request.url.host == "api.trello.com"
        assert "token" not in request.url.params
        assert request.headers["Authorization"].startswith("OAuth ")
        path = request.url.path
        if path.endswith("/lists"):
            return httpx.Response(200, json=data["lists"])
        if not path.endswith("/cards"):
            return httpx.Response(
                200, json={k: v for k, v in data.items() if k not in {"lists", "cards"}}
            )
        before = request.url.params.get("before")
        calls.append(before)
        if rate_limited:
            rate_limited = False
            return httpx.Response(429, headers={"Retry-After": "0"})
        if before and fail_second:
            return httpx.Response(403)
        return httpx.Response(200, json=rows[2:] if before else rows[:2])

    async def run():
        api = trello.Trello(("testkey", "testtoken"))
        await api.http.aclose()
        api.http = httpx.AsyncClient(
            base_url=trello.API_URL,
            headers={"Authorization": "OAuth test"},
            transport=httpx.MockTransport(handle),
        )
        async with api.http:
            return await api.download(tmp_path, BOARD)

    with pytest.raises(TransportError):
        asyncio.run(run())
    assert (tmp_path / "000000.json").is_file()
    fail_second = False
    _, total = asyncio.run(run())
    assert total == 2 and calls.count(None) == 2
    assert not any("testtoken" in f.read_text() for f in tmp_path.glob("*.json"))


def test_package_path_escape_and_insufficient_space(tmp_path, monkeypatch):
    archive = tmp_path / "bad.zip"
    with ZipFile(archive, "w") as file:
        file.writestr("../escaped", "bad")
    with pytest.raises(ValidationError, match="unsafe path"):
        storage.inspect_package(archive)
    monkeypatch.setattr(storage, "free_bytes", lambda _path: 0)
    with pytest.raises(ValidationError, match="disk space"):
        storage.require_disk(tmp_path, 1)
    assert not (tmp_path.parent / "escaped").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX file permissions")
def test_workspace_files_are_private(command):
    _run, result = _prepare(command)
    path = Path(result["work_path"])
    assert path.stat().st_mode & 0o777 == 0o700
    assert (path / "run.json").stat().st_mode & 0o777 == 0o600
    assert "test-kaiten-token" not in (path / "run.json").read_text()


@pytest.mark.skipif(os.name == "nt", reason="POSIX fixture runner")
def test_machine_uses_private_session_and_does_not_inherit_credentials(tmp_path, monkeypatch):
    runner = tmp_path / "machine"
    runner.write_text(
        f"#!{sys.executable}\n"
        + """
import json, os, sys
from pathlib import Path
request = json.load(sys.stdin)
profile = Path(next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--user-data-dir=")))
assert profile.is_dir() and profile.stat().st_mode & 0o777 == 0o700
if sys.platform == "darwin":
    assert "--use-mock-keychain" in sys.argv
assert "--kaiten-import-machine" in sys.argv
assert "KAITEN_TOKEN" not in os.environ and "KAITEN_IMPORT_TRELLO_TOKEN" not in os.environ
assert "UNRELATED_SECRET" not in os.environ
assert request["kaiten_token"] == "only-stdin"
print(json.dumps({"protocol": 1, "profile": str(profile)}))
"""
    )
    runner.chmod(0o700)
    monkeypatch.setenv(convertinator.RUNNER_ENV, str(runner))
    monkeypatch.setenv("KAITEN_TOKEN", "not-inherited")
    monkeypatch.setenv(trello.TOKEN_ENV, "not-inherited")
    monkeypatch.setenv("UNRELATED_SECRET", "not-inherited")
    response = asyncio.run(convertinator.machine("capabilities", {}, token="only-stdin"))
    assert not Path(response["profile"]).exists()
