from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from kaiten_cli.app import cli
from kaiten_cli.profiles import load_config
from kaiten_cli.registry import iter_tools, resolve_tool
from kaiten_cli.registry.live_contracts import LIVE_POLICY_EXCLUSIONS

NORMAL_PAUSE_SECONDS = 0.5
HEAVY_PAUSE_SECONDS = 1.0


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _require_live_env() -> dict[str, str]:
    env: dict[str, str] = {}
    config_override = os.environ.get("KAITEN_CLI_CONFIG_PATH")
    domain = os.environ.get("KAITEN_DOMAIN")
    token = os.environ.get("KAITEN_TOKEN")
    if not _truthy_env("KAITEN_LIVE"):
        pytest.skip("Live suite is opt-in. Set KAITEN_LIVE=1|true to run it on explicit credentials or an active CLI profile.")
    if config_override:
        env["KAITEN_CLI_CONFIG_PATH"] = config_override
    if domain and token:
        env["KAITEN_DOMAIN"] = domain
        env["KAITEN_TOKEN"] = token
        return env
    config = load_config()
    active = config.get("active_profile")
    if active and active in config.get("profiles", {}):
        return env
    pytest.skip("Set KAITEN_LIVE=1|true and provide KAITEN_DOMAIN/KAITEN_TOKEN or an active CLI profile.")


class LiveHarness:
    def __init__(self, runner: CliRunner, env: dict[str, str]):
        self.runner = runner
        self.env = env
        self.run_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        self.covered: set[str] = set()
        self.exclusions: dict[str, str] = dict(LIVE_POLICY_EXCLUSIONS)
        self.cleanup_stack: list[tuple[str, Callable[[], None], str | None]] = []
        self.state: dict[str, Any] = {}

    def name(self, kind: str) -> str:
        return f"codex-live-{self.run_id}-{kind}"

    def exclude(self, canonical_name: str, reason: str) -> None:
        self.exclusions[canonical_name] = reason

    def cover(self, canonical_name: str) -> None:
        self.covered.add(canonical_name)

    def _pause_for(self, canonical_name: str) -> None:
        tool = resolve_tool(canonical_name)
        time.sleep(HEAVY_PAUSE_SECONDS if tool.response_policy.heavy else NORMAL_PAUSE_SECONDS)

    def _invoke(self, args: list[str], label: str):
        result = self.runner.invoke(cli, ["--json", *args], env=self.env)
        assert result.output, f"{label}: empty output"
        payload = json.loads(result.output)
        return result, payload

    def _option_args(self, kwargs: dict[str, Any]) -> list[str]:
        args: list[str] = []
        for key, value in kwargs.items():
            option_name = f"--{key.replace('_', '-')}"
            if isinstance(value, bool):
                args.append(option_name if value else f"--no-{key.replace('_', '-')}")
                continue
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                args.extend([option_name, json.dumps(value)])
                continue
            args.extend([option_name, str(value)])
        return args

    def run_tool(self, canonical_name: str, /, **kwargs: Any) -> dict[str, Any]:
        tool = resolve_tool(canonical_name)
        result, payload = self._invoke([*tool.command_segments, *self._option_args(kwargs)], canonical_name)
        assert result.exit_code == 0, f"{canonical_name}: {result.output}"
        assert payload["success"] is True, f"{canonical_name}: {result.output}"
        self.cover(canonical_name)
        self._pause_for(canonical_name)
        return payload["data"]

    def run_tool_expect_api_error(
        self,
        canonical_name: str,
        expected_statuses: set[int] | tuple[int, ...] | list[int],
        /,
        **kwargs: Any,
    ) -> dict[str, Any]:
        statuses = set(expected_statuses)
        tool = resolve_tool(canonical_name)
        result, payload = self._invoke([*tool.command_segments, *self._option_args(kwargs)], canonical_name)
        assert payload["success"] is False, f"{canonical_name}: expected error, got {result.output}"
        status = payload.get("error", {}).get("status_code")
        assert status in statuses, f"{canonical_name}: expected {sorted(statuses)}, got {result.output}"
        self.cover(canonical_name)
        self._pause_for(canonical_name)
        return payload["error"]

    def run_tool_maybe(
        self,
        canonical_name: str,
        /,
        *,
        expected_error_statuses: set[int] | tuple[int, ...] | list[int],
        **kwargs: Any,
    ) -> tuple[bool, dict[str, Any]]:
        statuses = set(expected_error_statuses)
        tool = resolve_tool(canonical_name)
        result, payload = self._invoke([*tool.command_segments, *self._option_args(kwargs)], canonical_name)
        self.cover(canonical_name)
        self._pause_for(canonical_name)
        if payload["success"] is True:
            assert result.exit_code == 0, f"{canonical_name}: {result.output}"
            return True, payload["data"]
        status = payload.get("error", {}).get("status_code")
        assert status in statuses, f"{canonical_name}: expected success or {sorted(statuses)}, got {result.output}"
        return False, payload["error"]

    def run_non_tool(self, command: str, *args: str) -> dict[str, Any]:
        result, payload = self._invoke([command, *args], command)
        assert result.exit_code == 0, f"{command}: {result.output}"
        assert payload["success"] is True, f"{command}: {result.output}"
        return payload["data"]

    def push_cleanup(self, label: str, canonical_name: str, /, **kwargs: Any) -> None:
        def action() -> None:
            self.run_tool(canonical_name, **kwargs)

        self.cleanup_stack.append((label, action, canonical_name))

    def push_cleanup_expect_error(
        self,
        label: str,
        canonical_name: str,
        expected_statuses: set[int] | tuple[int, ...] | list[int],
        /,
        **kwargs: Any,
    ) -> None:
        def action() -> None:
            self.run_tool_expect_api_error(canonical_name, expected_statuses, **kwargs)

        self.cleanup_stack.append((label, action, canonical_name))

    def cleanup(self) -> None:
        errors: list[str] = []
        while self.cleanup_stack:
            label, action, canonical_name = self.cleanup_stack.pop()
            try:
                action()
            except Exception as exc:  # pragma: no cover - live-only cleanup path
                suffix = f" ({canonical_name})" if canonical_name else ""
                errors.append(f"{label}{suffix}: {exc}")
        if errors:
            pytest.fail("Live cleanup failed:\n" + "\n".join(errors))

    def assert_full_coverage(self) -> None:
        expected = {tool.canonical_name for tool in iter_tools()}
        missing = sorted(expected - self.covered - set(self.exclusions))
        assert not missing, "Missing live coverage for commands:\n" + "\n".join(missing)


@pytest.fixture
def live_env(tmp_path: Path) -> dict[str, str]:
    env = _require_live_env()
    env["KAITEN_CLI_CONFIG_PATH"] = str(tmp_path / "live-config.json")
    return env


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def live_harness(runner: CliRunner, live_env: dict[str, str], socket_enabled, request) -> LiveHarness:
    harness = LiveHarness(runner, live_env)
    yield harness
    harness.cleanup()
    report = getattr(request.node, "rep_call", None)
    if report is not None and report.passed and request.node.get_closest_marker("full_live_coverage"):
        harness.assert_full_coverage()
