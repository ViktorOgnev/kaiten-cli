from __future__ import annotations

import http.client
import json
import logging
import os
import signal
import subprocess
import threading
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

import pytest

import kaiten_cli.agent_gateway as agent_gateway

from kaiten_cli.agent_gateway import (
    MAX_REQUEST_BODY_BYTES,
    AgentGatewayConfig,
    build_codex_command,
    build_prompt,
    chat_response,
    make_handler,
    run_codex,
)


@contextmanager
def running_gateway(config: AgentGatewayConfig) -> Iterator[tuple[str, int]]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(config))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield str(host), int(port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request_json(
    address: tuple[str, int],
    method: str,
    path: str,
    *,
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_headers = dict(headers or {})
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    connection = http.client.HTTPConnection(*address, timeout=5)
    try:
        connection.request(method, path, body=body, headers=request_headers)
        response = connection.getresponse()
        response_body = json.loads(response.read().decode("utf-8"))
        return response.status, response_body
    finally:
        connection.close()


def test_build_prompt_includes_agent_help_skills_and_messages():
    prompt = build_prompt(
        {
            "instructions": "Use compact Kaiten CLI reads.",
            "context": {"company_id": 7},
            "messages": [{"role": "user", "content": "What is WIP?"}],
        },
        repo_root=Path(__file__).resolve().parents[1],
    )

    assert "kaiten agent-help JSON" in prompt
    assert "kaiten-cli-heavy-data" in prompt
    assert "kaiten-cli-metrics" in prompt
    assert "What is WIP?" in prompt
    assert "company_id" in prompt


def test_build_codex_command_uses_read_only_exec(tmp_path):
    config = AgentGatewayConfig(
        codex_bin="codex-test",
        codex_model="gpt-test",
        reasoning_effort="low",
        workdir=tmp_path,
        repo_root=tmp_path,
    )

    command = build_codex_command(config, tmp_path / "last.txt")

    assert command[:2] == ["codex-test", "exec"]
    assert "--sandbox" in command
    assert "read-only" in command
    assert "--ephemeral" in command
    assert "--ignore-user-config" in command
    assert "--ignore-rules" in command
    assert "--skip-git-repo-check" not in command
    assert "--model" in command
    assert command[-1] == "-"


def test_build_codex_command_can_skip_git_repo_check(tmp_path):
    config = AgentGatewayConfig(
        codex_bin="codex-test",
        reasoning_effort="low",
        workdir=tmp_path,
        repo_root=tmp_path,
        skip_git_repo_check=True,
    )

    command = build_codex_command(config, tmp_path / "last.txt")

    assert "--skip-git-repo-check" in command


def test_run_codex_reads_last_message(tmp_path):
    config = AgentGatewayConfig(
        codex_bin="codex-test",
        reasoning_effort="low",
        workdir=tmp_path,
        repo_root=tmp_path,
    )

    def runner(command, **kwargs):
        last_path = Path(command[command.index("--output-last-message") + 1])
        last_path.write_text("final answer", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="events", stderr="")

    assert run_codex("prompt", config, runner=runner) == "final answer"


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group behavior")
def test_process_group_runner_kills_group_on_timeout(monkeypatch):
    class FakeProcess:
        pid = 4321
        returncode = None
        calls = 0

        def communicate(self, input=None, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired(["codex"], timeout)
            self.returncode = -signal.SIGKILL
            return "", ""

    captured = {}
    process = FakeProcess()

    def fake_popen(command, **kwargs):
        captured.update(kwargs)
        return process

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    killed = []
    monkeypatch.setattr(os, "killpg", lambda pid, sig: killed.append((pid, sig)))

    with pytest.raises(subprocess.TimeoutExpired):
        agent_gateway._run_process_group(
            ["codex"],
            input="prompt",
            text=True,
            capture_output=True,
            env={},
            timeout=1,
            check=False,
        )

    assert captured["start_new_session"] is True
    assert killed == [(4321, signal.SIGKILL)]
    assert process.calls == 2


def test_run_codex_uses_minimal_read_only_environment(tmp_path, monkeypatch):
    config = AgentGatewayConfig(
        codex_bin="codex-test",
        reasoning_effort="low",
        workdir=tmp_path,
        repo_root=tmp_path,
    )
    captured = {}
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "kaiten-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/test-xdg-config")
    monkeypatch.setenv("KAITEN_LIVE", "1")
    monkeypatch.setenv("UNRELATED_SECRET", "must-not-leak")
    monkeypatch.setenv("KAITEN_CLI_READ_ONLY", "0")

    def runner(command, **kwargs):
        captured.update(kwargs)
        last_path = Path(command[command.index("--output-last-message") + 1])
        last_path.write_text("final answer", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="events", stderr="")

    assert run_codex("prompt", config, runner=runner) == "final answer"

    child_env = captured["env"]
    assert child_env["KAITEN_DOMAIN"] == "sandbox"
    assert child_env["KAITEN_TOKEN"] == "kaiten-secret"
    assert child_env["OPENAI_API_KEY"] == "openai-secret"
    assert child_env["XDG_CONFIG_HOME"] == "/tmp/test-xdg-config"
    assert child_env["KAITEN_CLI_READ_ONLY"] == "1"
    assert child_env["KAITEN_CLI_STORAGE_READ_ONLY"] == "1"
    assert "KAITEN_LIVE" not in child_env
    assert "UNRELATED_SECRET" not in child_env


def test_run_codex_redacts_child_credentials_from_failure(tmp_path, monkeypatch):
    config = AgentGatewayConfig(
        codex_bin="codex-test",
        reasoning_effort="low",
        workdir=tmp_path,
        repo_root=tmp_path,
    )
    monkeypatch.setenv("KAITEN_TOKEN", "kaiten-secret")

    def runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            1,
            stdout="",
            stderr="request failed with token=kaiten-secret",
        )

    with pytest.raises(RuntimeError) as exc_info:
        run_codex("prompt", config, runner=runner)

    assert "kaiten-secret" not in str(exc_info.value)
    assert "token=[REDACTED]" in str(exc_info.value)


def test_run_codex_redacts_child_credentials_from_success(tmp_path, monkeypatch):
    config = AgentGatewayConfig(
        codex_bin="codex-test",
        reasoning_effort="low",
        workdir=tmp_path,
        repo_root=tmp_path,
    )
    monkeypatch.setenv("KAITEN_TOKEN", "kaiten-secret")

    def runner(command, **kwargs):
        last_path = Path(command[command.index("--output-last-message") + 1])
        last_path.write_text("token=kaiten-secret", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    assert run_codex("prompt", config, runner=runner) == "token=[REDACTED]"


def test_chat_response_matches_kaiten_agent_contract():
    response = chat_response("hello")

    assert response["message"] == {"role": "assistant", "content": "hello"}
    assert response["usage"]["provider"] == "codex_exec"


def test_non_loopback_bind_requires_bearer_token(tmp_path):
    config = AgentGatewayConfig(host="0.0.0.0", workdir=tmp_path, repo_root=tmp_path)

    with pytest.raises(ValueError, match="bearer token is required"):
        make_handler(config)

    authenticated_config = AgentGatewayConfig(
        host="0.0.0.0",
        bearer_token="gateway-secret",
        workdir=tmp_path,
        repo_root=tmp_path,
    )
    assert make_handler(authenticated_config)


def test_loopback_gateway_remains_usable_without_authentication(tmp_path, socket_enabled):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)

    with running_gateway(config) as address:
        status, body = request_json(address, "GET", "/health")

    assert status == 200
    assert body["ok"] is True
    assert "chat" in body["capabilities"]


def test_gateway_enforces_bearer_authentication(tmp_path, socket_enabled):
    config = AgentGatewayConfig(
        bearer_token="gateway-secret",
        workdir=tmp_path,
        repo_root=tmp_path,
    )

    with running_gateway(config) as address:
        missing_status, missing_body = request_json(address, "GET", "/health")
        wrong_status, wrong_body = request_json(
            address,
            "GET",
            "/health",
            headers={"Authorization": "Bearer wrong-secret"},
        )
        ok_status, ok_body = request_json(
            address,
            "GET",
            "/health",
            headers={"Authorization": "Bearer gateway-secret"},
        )

    assert (missing_status, missing_body) == (401, {"message": "Unauthorized"})
    assert (wrong_status, wrong_body) == (401, {"message": "Unauthorized"})
    assert ok_status == 200
    assert ok_body["ok"] is True


def test_gateway_rejects_oversized_request_before_codex(tmp_path, monkeypatch, socket_enabled):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)
    called = False

    def fail_if_called(prompt, gateway_config):
        nonlocal called
        called = True
        raise AssertionError("Codex must not run for an oversized request")

    monkeypatch.setattr(agent_gateway, "run_codex", fail_if_called)

    with running_gateway(config) as address:
        connection = http.client.HTTPConnection(*address, timeout=5)
        try:
            connection.putrequest("POST", "/v1/chat")
            connection.putheader("Content-Length", str(MAX_REQUEST_BODY_BYTES + 1))
            connection.endheaders()
            response = connection.getresponse()
            response_body = json.loads(response.read().decode("utf-8"))
        finally:
            connection.close()

    assert response.status == 413
    assert "1048576-byte limit" in response_body["message"]
    assert called is False


def test_gateway_rejects_non_json_body_before_codex(tmp_path, monkeypatch, socket_enabled):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)
    called = False

    def fail_if_called(prompt, gateway_config):
        nonlocal called
        called = True
        raise AssertionError("Codex must not run for a non-JSON request")

    monkeypatch.setattr(agent_gateway, "run_codex", fail_if_called)

    with running_gateway(config) as address:
        connection = http.client.HTTPConnection(*address, timeout=5)
        try:
            connection.request(
                "POST",
                "/v1/chat",
                body=b"{}",
                headers={"Content-Type": "text/plain"},
            )
            response = connection.getresponse()
            response_body = json.loads(response.read().decode("utf-8"))
        finally:
            connection.close()

    assert response.status == 400
    assert response_body == {"message": "Content-Type must be application/json"}
    assert called is False


def test_gateway_rejects_empty_body_before_codex(tmp_path, monkeypatch, socket_enabled):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)
    called = False

    def fail_if_called(prompt, gateway_config):
        nonlocal called
        called = True
        raise AssertionError("Codex must not run for an empty request")

    monkeypatch.setattr(agent_gateway, "run_codex", fail_if_called)

    with running_gateway(config) as address:
        status, body = request_json(address, "POST", "/v1/chat")

    assert status == 400
    assert body == {"message": "Content-Type must be application/json"}
    assert called is False


def test_gateway_times_out_incomplete_request_body(tmp_path, monkeypatch, socket_enabled):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)
    monkeypatch.setattr(agent_gateway, "REQUEST_READ_TIMEOUT_SECONDS", 0.05)

    with running_gateway(config) as address:
        connection = http.client.HTTPConnection(*address, timeout=5)
        try:
            connection.putrequest("POST", "/v1/chat")
            connection.putheader("Content-Type", "application/json")
            connection.putheader("Content-Length", "10")
            connection.endheaders()
            response = connection.getresponse()
            response_body = json.loads(response.read().decode("utf-8"))
        finally:
            connection.close()

    assert response.status == 408
    assert response_body == {"message": "Request body timed out"}


def test_gateway_limits_concurrent_codex_executions(tmp_path, monkeypatch, socket_enabled):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)
    release = threading.Event()
    both_started = threading.Event()
    call_lock = threading.Lock()
    call_count = 0
    responses: list[tuple[int, dict]] = []

    def blocking_codex(prompt, gateway_config):
        nonlocal call_count
        with call_lock:
            call_count += 1
            if call_count == 2:
                both_started.set()
        if not release.wait(timeout=5):
            raise TimeoutError("test did not release blocked Codex execution")
        return "done"

    monkeypatch.setattr(agent_gateway, "run_codex", blocking_codex)

    with running_gateway(config) as address:
        threads = [
            threading.Thread(
                target=lambda: responses.append(
                    request_json(address, "POST", "/v1/chat", payload={"messages": []})
                )
            )
            for _ in range(2)
        ]
        try:
            for thread in threads:
                thread.start()
            assert both_started.wait(timeout=5)

            rejected_status, rejected_body = request_json(
                address, "POST", "/v1/chat", payload={"messages": []}
            )
            with call_lock:
                calls_after_rejection = call_count
        finally:
            release.set()
            for thread in threads:
                thread.join(timeout=5)

    assert rejected_status == 429
    assert rejected_body == {"message": "Too many concurrent agent requests"}
    assert calls_after_rejection == 2
    assert sorted(status for status, _ in responses) == [200, 200]


def test_gateway_redacts_codex_errors_from_http_response(
    tmp_path, monkeypatch, socket_enabled, caplog
):
    config = AgentGatewayConfig(workdir=tmp_path, repo_root=tmp_path)
    subprocess_detail = "private stderr: token=do-not-return"
    attempt = 0

    def failing_codex(prompt, gateway_config):
        nonlocal attempt
        attempt += 1
        if attempt == 1:
            raise RuntimeError(subprocess_detail)
        return "recovered"

    monkeypatch.setattr(agent_gateway, "run_codex", failing_codex)

    with caplog.at_level(logging.ERROR, logger="kaiten_cli.agent_gateway"):
        with running_gateway(config) as address:
            status, body = request_json(address, "POST", "/v1/chat", payload={})
            recovery_status, recovery_body = request_json(address, "POST", "/v1/chat", payload={})

    assert status == 502
    assert body == {"message": "Agent execution failed"}
    assert subprocess_detail not in json.dumps(body)
    assert subprocess_detail not in caplog.text
    assert "RuntimeError" in caplog.text
    assert recovery_status == 200
    assert recovery_body["message"]["content"] == "recovered"
