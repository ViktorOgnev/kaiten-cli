from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import CliError, ConfigError, MutationBlockedError, ValidationError
from kaiten_cli.i18n import use_locale
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import build_request, execute_tool, execute_tool_with_diagnostics
from kaiten_cli.runtime.support import document_sync
from kaiten_cli.runtime.trace import ExecutionStats

DATA = {
    "type": "doc",
    "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Привет"}]}],
}
UID = "test-doc"
URL = f"https://sandbox.kaiten.ru/api/latest/documents/{UID}"


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "private-api-token")


@pytest.mark.parametrize(
    "field,value", [("text", "text"), ("text", ""), ("data", DATA), ("data", {})]
)
@pytest.mark.parametrize("mode", ["args", "file", "stdin"])
@respx.mock
def test_content_guard_blocks_all_input_modes_without_http(runner, tmp_path, field, value, mode):
    command = ["documents", "update"]
    args = ["--locale", "ru", "--json", "--no-update-check"]
    payload = {"document_uid": UID, field: value}
    stdin = None
    if mode == "args":
        args += command + [
            "--document-uid",
            UID,
            f"--{field}",
            json.dumps(value) if field == "data" else value,
        ]
    elif mode == "file":
        source = tmp_path / "request.json"
        source.write_text(json.dumps(payload))
        args += ["--from-file", str(source), *command]
    else:
        args += ["--stdin-json", *command]
        stdin = json.dumps(payload)
    result = runner.invoke(cli, args, input=stdin)
    assert result.exit_code == 6, result.output
    error = json.loads(result.stdout)["error"]
    assert error["type"] == "mutation_blocked"
    assert "может создать дубль всего документа" in error["message"]
    assert "Запись не выполнялась" in error["message"]
    assert not respx.calls


@pytest.mark.asyncio
@pytest.mark.parametrize("allow", [None, False])
@respx.mock
async def test_programmatic_and_mixed_requests_are_guarded_even_without_credentials(
    monkeypatch, allow
):
    monkeypatch.delenv("KAITEN_DOMAIN")
    monkeypatch.delenv("KAITEN_TOKEN")
    payload = {"document_uid": UID, "data": DATA, "title": "Metadata"}
    if allow is not None:
        payload["allow_unsafe_content_replace"] = allow
    with pytest.raises(MutationBlockedError):
        await execute_tool(resolve_tool("documents.update"), payload)
    assert not respx.calls


@pytest.mark.parametrize(
    "locale,warning",
    [("ru", "может создать дубль всего документа"), ("en", "may duplicate the entire document")],
)
@respx.mock
def test_unsafe_api_permission_warns_on_stderr_and_keeps_json_clean(runner, locale, warning):
    route = respx.patch(URL).mock(return_value=Response(200, json={"uid": UID}))
    result = runner.invoke(
        cli,
        [
            "--locale",
            locale,
            "--json",
            "--no-update-check",
            "documents",
            "update",
            "--document-uid",
            UID,
            "--data",
            json.dumps(DATA),
            "--allow-unsafe-content-replace",
        ],
    )
    assert result.exit_code == 0, result.output
    assert warning in result.stderr
    assert json.loads(result.stdout)["data"] == {"uid": UID}
    assert json.loads(route.calls.last.request.content) == {"data": DATA}
    assert not route.calls.last.request.url.query


@pytest.mark.asyncio
@respx.mock
async def test_metadata_and_create_do_not_require_node_or_permission(monkeypatch):
    monkeypatch.setattr(document_sync.shutil, "which", lambda _: None)
    update = respx.patch(URL).mock(return_value=Response(200, json={"uid": UID}))
    create = respx.post("https://sandbox.kaiten.ru/api/latest/documents").mock(
        return_value=Response(200, json={"uid": "new"})
    )
    await execute_tool(resolve_tool("documents.update"), {"document_uid": UID, "title": "Title"})
    await execute_tool(resolve_tool("documents.create"), {"title": "Title", "data": DATA})
    assert update.called and create.called


@pytest.mark.parametrize(
    "extra",
    [
        {"title": "Title"},
        {"allow_unsafe_content_replace": True},
        {"text": "Both"},
    ],
)
def test_yjs_rejects_mixed_or_conflicting_inputs(extra):
    payload = {"document_uid": UID, "content_mode": "yjs", "data": DATA, **extra}
    with pytest.raises(ValidationError):
        build_request(resolve_tool("documents.update"), payload)


@pytest.mark.parametrize(
    "url",
    [
        "https://user:password@socket.test",
        "https://socket.test?token=secret",
        "https://socket.test/path",
        "ftp://socket.test",
        "https://socket.test:bad",
    ],
)
def test_socket_url_rejects_credentials_and_ambiguous_endpoints(url):
    with pytest.raises(ValidationError):
        document_sync.socket_origin(url)


@pytest.mark.asyncio
@respx.mock
async def test_missing_node_fails_before_any_http_or_subprocess(monkeypatch):
    monkeypatch.setattr(document_sync.shutil, "which", lambda _: None)
    start = AsyncMock(side_effect=AssertionError("must not start or install anything"))
    monkeypatch.setattr(asyncio, "create_subprocess_exec", start)
    with use_locale("ru"), pytest.raises(ConfigError, match="такая запись может создать дубль"):
        await execute_tool(
            resolve_tool("documents.update"),
            {"document_uid": UID, "content_mode": "yjs", "data": DATA},
        )
    assert not respx.calls
    start.assert_not_called()


class VersionProcess:
    def __init__(self, output=b"v20.0.0\n"):
        self.output = output
        self.returncode = 0

    async def communicate(self):
        return self.output, None


@pytest.mark.asyncio
@pytest.mark.parametrize("version", [b"v18.20.0\n", b"invalid", b"v19.0.0\n"])
@respx.mock
async def test_old_or_unrecognized_node_is_explicit_config_error(monkeypatch, version):
    monkeypatch.setattr(document_sync.shutil, "which", lambda _: "/node")
    start = AsyncMock(return_value=VersionProcess(version))
    monkeypatch.setattr(asyncio, "create_subprocess_exec", start)
    with pytest.raises(ConfigError) as caught:
        await execute_tool(
            resolve_tool("documents.update"),
            {"document_uid": UID, "content_mode": "yjs", "data": DATA},
        )
    assert caught.value.exit_code == 3
    assert start.call_args.args == ("/node", "--version")
    assert not respx.calls


@pytest.mark.asyncio
@respx.mock
async def test_read_only_takes_precedence_over_yjs_or_unsafe_permission(monkeypatch):
    node = AsyncMock(side_effect=AssertionError("must not run"))
    monkeypatch.setattr(document_sync, "find_node", node)
    for extra in [{"content_mode": "yjs"}, {"allow_unsafe_content_replace": True}]:
        with pytest.raises(MutationBlockedError):
            await execute_tool(
                resolve_tool("documents.update"),
                {"document_uid": UID, "data": DATA, **extra},
                read_only=True,
            )
    assert not respx.calls
    node.assert_not_called()


@pytest.mark.asyncio
@respx.mock
async def test_yjs_routes_raw_data_and_text_without_sanitizing_or_patching(monkeypatch):
    monkeypatch.setattr(document_sync, "find_node", AsyncMock(return_value="/node"))
    respx.get(URL).mock(return_value=Response(200, json={"uid": UID, "schema_version": "v28"}))
    respx.get("https://sandbox.kaiten.ru/api/latest/token-please").mock(
        return_value=Response(200, json={"token": "private-socket-jwt"})
    )
    run = AsyncMock(return_value={"status": "verified"})
    monkeypatch.setattr(document_sync, "run_helper", run)
    data = {"type": "doc", "content": [{"type": "bullet_list", "content": []}]}
    await execute_tool(
        resolve_tool("documents.update"), {"document_uid": UID, "content_mode": "yjs", "data": data}
    )
    request = run.call_args.args[1]
    assert request["data"] == data
    assert request["token"] == "private-socket-jwt"
    assert request["socketUrl"] == "https://sandbox.kaiten.ru"
    assert request["schemaVersion"] == "v28"
    await execute_tool(
        resolve_tool("documents.update"),
        {
            "document_uid": UID,
            "content_mode": "yjs",
            "text": "# Header",
            "socket_url": "https://socket.test",
        },
    )
    request = run.call_args.args[1]
    assert request["socketUrl"] == "https://socket.test"
    assert request["data"]["content"][0]["type"] == "heading"
    assert all(call.request.method == "GET" for call in respx.calls)


class InputPipe:
    def __init__(self):
        self.writes = []
        self.closed = False

    def write(self, value):
        self.writes.append(value)

    async def drain(self):
        pass

    def close(self):
        self.closed = True


class HelperProcess:
    def __init__(self, events, *, eof=True):
        self.stdin = InputPipe()
        self.stdout = asyncio.StreamReader()
        for event in events:
            self.stdout.feed_data((json.dumps(event) + "\n").encode())
        if eof:
            self.stdout.feed_eof()
        self.returncode = None
        self.killed = False
        self.waited = False

    def kill(self):
        self.killed = True
        self.returncode = -9

    async def wait(self):
        self.waited = True
        return self.returncode


@pytest.mark.asyncio
@respx.mock
async def test_helper_permission_invalidates_cache_and_records_socket_diagnostics(monkeypatch):
    process = HelperProcess(
        [
            {"event": "connecting"},
            {"event": "write_ready"},
            {"event": "acknowledged"},
            {"event": "result", "result": {"status": "verified", "data": DATA}},
        ]
    )
    monkeypatch.setattr(document_sync, "find_node", AsyncMock(return_value="/node"))
    start = AsyncMock(return_value=process)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", start)
    respx.get(URL).mock(return_value=Response(200, json={"uid": UID, "schema_version": "v1"}))
    respx.get("https://sandbox.kaiten.ru/api/latest/token-please").mock(
        return_value=Response(200, json={"token": "secret-jwt"})
    )
    invalidations = AsyncMock()
    monkeypatch.setattr(
        "kaiten_cli.runtime.cache.ExecutionContext.invalidate_after_mutation", invalidations
    )
    _, stats = await execute_tool_with_diagnostics(
        resolve_tool("documents.update"), {"document_uid": UID, "content_mode": "yjs", "data": DATA}
    )
    assert invalidations.await_count == 2
    assert stats.http_request_count == 2
    assert stats.to_payload()["document_sync"] == {
        "transport": "socket.io",
        "connection_attempt_count": 1,
        "update_attempt_count": 1,
        "ack_count": 1,
        "verification_count": 1,
        "outcome": "verified",
    }
    assert process.killed and process.waited and process.stdin.closed
    assert len(process.stdin.writes) == 2
    assert json.loads(process.stdin.writes[1]) == {"action": "write"}
    assert "secret-jwt" not in str(start.call_args)
    assert "private-api-token" not in json.dumps(stats.to_payload())
    assert all(call.request.method == "GET" for call in respx.calls)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "events,expected_attempted,expected_ack",
    [
        ([{"event": "error", "code": "no_access"}], False, False),
        ([{"event": "write_ready"}, {"event": "error", "code": "timeout"}], True, False),
        (
            [
                {"event": "write_ready"},
                {"event": "acknowledged"},
                {"event": "error", "code": "verification_conflict"},
            ],
            True,
            True,
        ),
        ([{"event": "write_ready"}], True, False),
        ([{"event": "error", "code": "secret-jwt: arbitrary output"}], False, False),
    ],
)
async def test_failed_helper_never_retries_and_reports_uncertainty(
    monkeypatch, events, expected_attempted, expected_ack
):
    process = HelperProcess(events)
    start = AsyncMock(return_value=process)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", start)
    context = SimpleNamespace(stats=ExecutionStats(), invalidate_after_mutation=AsyncMock())
    client = SimpleNamespace(execution_context=context)
    with pytest.raises(CliError) as caught:
        await document_sync.run_helper("/node", {"token": "secret-jwt"}, client, 0.1)
    assert caught.value.details["write_attempted"] is expected_attempted
    assert caught.value.details["acknowledged"] is expected_ack
    assert "secret-jwt" not in str(caught.value)
    if expected_attempted and not expected_ack:
        assert "result is unknown" in str(caught.value)
    assert start.await_count == 1
    assert process.killed and process.waited and process.stdin.closed


@pytest.mark.asyncio
@respx.mock
async def test_missing_schema_version_is_negotiated_instead_of_guessing_v1(monkeypatch):
    monkeypatch.setattr(document_sync, "find_node", AsyncMock(return_value="/node"))
    respx.get(URL).mock(return_value=Response(200, json={"uid": UID}))
    schemas = respx.get("https://sandbox.kaiten.ru/api/latest/document-schemas/latest").mock(
        return_value=Response(200, json={"version": "v28"})
    )
    respx.get("https://sandbox.kaiten.ru/api/latest/token-please").mock(
        return_value=Response(200, json={"token": "socket-jwt"})
    )
    run = AsyncMock(return_value={"status": "verified"})
    monkeypatch.setattr(document_sync, "run_helper", run)
    await execute_tool(
        resolve_tool("documents.update"), {"document_uid": UID, "content_mode": "yjs", "data": DATA}
    )
    assert schemas.call_count == 1
    assert run.call_args.args[1]["schemaVersion"] == "v28"
    assert all(call.request.method == "GET" for call in respx.calls)


@pytest.mark.asyncio
@respx.mock
async def test_missing_schema_information_stops_before_socket_or_token(monkeypatch):
    monkeypatch.setattr(document_sync, "find_node", AsyncMock(return_value="/node"))
    respx.get(URL).mock(return_value=Response(200, json={"uid": UID}))
    respx.get("https://sandbox.kaiten.ru/api/latest/document-schemas/latest").mock(
        return_value=Response(200, json={})
    )
    run = AsyncMock(side_effect=AssertionError("must not start helper"))
    monkeypatch.setattr(document_sync, "run_helper", run)
    with pytest.raises(ValidationError, match="schema version"):
        await execute_tool(
            resolve_tool("documents.update"),
            {"document_uid": UID, "content_mode": "yjs", "data": DATA},
        )
    run.assert_not_called()
    assert len(respx.calls) == 2


@pytest.mark.asyncio
async def test_parent_timeout_kills_and_reaps_hung_child_without_resending(monkeypatch):
    process = HelperProcess([{"event": "write_ready"}], eof=False)
    start = AsyncMock(return_value=process)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", start)
    original_wait = asyncio.wait_for

    async def short_wait(awaitable, timeout):
        return await original_wait(awaitable, timeout=0.01)

    monkeypatch.setattr(asyncio, "wait_for", short_wait)
    context = SimpleNamespace(stats=ExecutionStats(), invalidate_after_mutation=AsyncMock())
    with pytest.raises(CliError) as caught:
        await document_sync.run_helper("/node", {}, SimpleNamespace(execution_context=context), 20)
    assert caught.value.details == {
        "reason": "timeout",
        "write_attempted": True,
        "acknowledged": False,
    }
    assert process.killed and process.waited and process.stdin.closed
    assert len(process.stdin.writes) == 2
    assert start.await_count == 1


@pytest.mark.asyncio
async def test_cancelling_helper_closes_process_and_invalidates_attempted_write(monkeypatch):
    process = HelperProcess([{"event": "write_ready"}], eof=False)
    monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=process))
    context = SimpleNamespace(stats=ExecutionStats(), invalidate_after_mutation=AsyncMock())
    task = asyncio.create_task(
        document_sync.run_helper("/node", {}, SimpleNamespace(execution_context=context), 20)
    )
    for _ in range(100):
        if len(process.stdin.writes) == 2:
            break
        await asyncio.sleep(0)
    assert len(process.stdin.writes) == 2
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert process.killed and process.waited and process.stdin.closed
    assert context.invalidate_after_mutation.await_count == 2
