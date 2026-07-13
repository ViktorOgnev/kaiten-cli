from __future__ import annotations

import json
import stat
import subprocess
from dataclasses import replace

import click
import pytest

from kaiten_cli import update_check
from kaiten_cli.update_check import (
    InstallSource,
    UpdateCandidate,
    build_update_command,
    check_for_update,
    detect_install_source,
    maybe_offer_update,
    should_check_for_updates,
)


class FakeDistribution:
    def __init__(self, version: str, direct_url: dict | None):
        self.version = version
        self.direct_url = direct_url

    def read_text(self, filename: str) -> str | None:
        if filename != "direct_url.json" or self.direct_url is None:
            return None
        return json.dumps(self.direct_url)


class TtyStream:
    def __init__(self, tty: bool):
        self.tty = tty

    def isatty(self) -> bool:
        return self.tty


def _direct_url(
    url: str = "ssh://git@github.com/ViktorOgnev/kaiten-cli.git",
    revision: str | None = None,
    **extra,
) -> dict:
    vcs_info = {"vcs": "git", "commit_id": "a" * 40}
    if revision is not None:
        vcs_info["requested_revision"] = revision
    return {"url": url, "vcs_info": vcs_info, **extra}


def _source(**changes) -> InstallSource:
    source = InstallSource(
        manager="pipx",
        manager_executable="/usr/local/bin/pipx",
        git_url="ssh://git@github.com/ViktorOgnev/kaiten-cli.git",
        installed_version="0.1.9",
    )
    return replace(source, **changes)


def _completed(args, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args, returncode, stdout=stdout, stderr=stderr)


def test_detects_pipx_git_install(monkeypatch, tmp_path):
    prefix = tmp_path / "pipx" / "venvs" / "kaiten-cli"
    prefix.mkdir(parents=True)
    (prefix / "pipx_metadata.json").write_text(
        json.dumps(
            {
                "main_package": {
                    "package": "kaiten_cli",
                    "package_or_url": "git+ssh://git@github.com/ViktorOgnev/kaiten-cli.git",
                    "suffix": "",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        update_check.metadata,
        "distribution",
        lambda _name: FakeDistribution("0.1.23", _direct_url()),
    )
    monkeypatch.setattr(update_check.sys, "prefix", str(prefix))
    monkeypatch.setattr(update_check.shutil, "which", lambda name: f"/tools/{name}")

    source = detect_install_source()

    assert source == InstallSource(
        manager="pipx",
        manager_executable="/tools/pipx",
        git_url="ssh://git@github.com/ViktorOgnev/kaiten-cli.git",
        installed_version="0.1.23",
    )


def test_detects_uv_tool_install(monkeypatch, tmp_path):
    tool_dir = tmp_path / "uv" / "tools"
    prefix = tool_dir / "kaiten-cli"
    prefix.mkdir(parents=True)
    monkeypatch.setattr(
        update_check.metadata,
        "distribution",
        lambda _name: FakeDistribution("0.1.23", _direct_url()),
    )
    monkeypatch.setattr(update_check.sys, "prefix", str(prefix))
    monkeypatch.setattr(
        update_check.shutil, "which", lambda name: "/tools/uv" if name == "uv" else None
    )

    def fake_run(command, **kwargs):
        assert command == ["/tools/uv", "tool", "dir"]
        assert kwargs["timeout"] == update_check.UV_DETECTION_TIMEOUT_SECONDS
        return _completed(command, stdout=f"{tool_dir}\n")

    monkeypatch.setattr(update_check.subprocess, "run", fake_run)

    source = detect_install_source()

    assert source is not None
    assert source.manager == "uv"
    assert source.manager_executable == "/tools/uv"


def test_falls_back_to_current_python_for_git_venv(monkeypatch, tmp_path):
    monkeypatch.setattr(
        update_check.metadata,
        "distribution",
        lambda _name: FakeDistribution("0.1.23", _direct_url()),
    )
    monkeypatch.setattr(update_check.sys, "prefix", str(tmp_path / "venv"))
    monkeypatch.setattr(update_check.sys, "executable", "/venv/bin/python")
    monkeypatch.setattr(update_check.shutil, "which", lambda _name: None)

    source = detect_install_source()

    assert source is not None
    assert source.manager == "pip"
    assert source.manager_executable == "/venv/bin/python"


@pytest.mark.parametrize(
    "direct_url",
    [
        {"url": "file:///workspace/kaiten-cli", "dir_info": {"editable": True}},
        {"url": "file:///tmp/kaiten_cli-0.1.23.whl", "archive_info": {}},
        {"url": "https://example.com/kaiten_cli.whl", "archive_info": {}},
        {"url": "file:///workspace/repo", "vcs_info": {"vcs": "git", "commit_id": "a"}},
        {"url": "https://example.com/repo", "vcs_info": {"vcs": "hg", "commit_id": "a"}},
    ],
)
def test_skips_unsupported_install_sources(monkeypatch, direct_url):
    monkeypatch.setattr(
        update_check.metadata, "distribution", lambda _name: FakeDistribution("0.1.23", direct_url)
    )

    assert detect_install_source() is None


def test_skips_missing_or_malformed_install_metadata(monkeypatch):
    monkeypatch.setattr(
        update_check.metadata, "distribution", lambda _name: FakeDistribution("0.1.23", None)
    )
    assert detect_install_source() is None

    monkeypatch.setattr(
        update_check.metadata,
        "distribution",
        lambda _name: type(
            "MalformedDistribution",
            (),
            {"version": "0.1.23", "read_text": lambda self, _filename: "{broken"},
        )(),
    )
    assert detect_install_source() is None


def test_remote_tag_check_uses_stable_semver_and_cache(monkeypatch):
    calls = []
    monkeypatch.setattr(
        update_check.shutil, "which", lambda name: "/usr/bin/git" if name == "git" else None
    )

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return _completed(
            command,
            stdout="\n".join(
                [
                    "a refs/tags/v0.1.9",
                    "b refs/tags/v0.1.10",
                    "c refs/tags/v0.2.0rc1",
                    "d refs/tags/not-a-version",
                ]
            ),
        )

    monkeypatch.setattr(update_check.subprocess, "run", fake_run)

    first = check_for_update(_source(), now=1000)
    second = check_for_update(_source(), now=1001)

    assert first is not None and first.latest_tag == "v0.1.10"
    assert second is not None and second.latest_tag == "v0.1.10"
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command == [
        "/usr/bin/git",
        "ls-remote",
        "--tags",
        "--refs",
        "ssh://git@github.com/ViktorOgnev/kaiten-cli.git",
        "refs/tags/v*",
    ]
    assert kwargs["timeout"] == update_check.GIT_CHECK_TIMEOUT_SECONDS
    assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert kwargs["env"]["SSH_ASKPASS_REQUIRE"] == "never"


@pytest.mark.parametrize(
    "tag_lines",
    [
        ["a refs/tags/v1.2.3", "b refs/tags/v2.0.0", "c refs/tags/v1.10.0"],
        ["c refs/tags/v1.10.0", "b refs/tags/v2.0.0", "a refs/tags/v1.2.3"],
    ],
)
def test_latest_release_is_invariant_to_remote_tag_order(monkeypatch, tag_lines):
    monkeypatch.setattr(update_check.shutil, "which", lambda _name: "/usr/bin/git")
    monkeypatch.setattr(
        update_check.subprocess,
        "run",
        lambda command, **_kwargs: _completed(command, stdout="\n".join(tag_lines)),
    )

    assert update_check._latest_remote_release(_source().git_url) == (True, "v2.0.0")


def test_network_failure_is_silent_and_throttled(monkeypatch):
    calls = 0
    monkeypatch.setattr(update_check.shutil, "which", lambda _name: "/usr/bin/git")

    def fake_run(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        raise subprocess.TimeoutExpired("git", 8)

    monkeypatch.setattr(update_check.subprocess, "run", fake_run)

    assert check_for_update(_source(), now=1000) is None
    assert check_for_update(_source(), now=1001) is None
    assert calls == 1


@pytest.mark.parametrize(
    ("installed_version", "revision"),
    [("0.1.10", None), ("0.2.0.dev1", None), ("0.1.9", "bfbd6959a349e2")],
)
def test_skips_current_unstable_or_commit_pinned_install(monkeypatch, installed_version, revision):
    monkeypatch.setattr(update_check, "_latest_remote_release", lambda _url: (True, "v0.1.10"))

    assert (
        check_for_update(
            _source(installed_version=installed_version, requested_revision=revision), now=1000
        )
        is None
    )


def test_prompt_snooze_expires_after_one_day(monkeypatch):
    monkeypatch.setattr(update_check, "_latest_remote_release", lambda _url: (True, "v0.1.10"))
    candidate = check_for_update(_source(), now=1000)
    assert candidate is not None
    update_check._record_prompted(candidate, now=1000)

    assert check_for_update(_source(), now=1001) is None
    assert check_for_update(_source(), now=1000 + 24 * 60 * 60 + 1) is not None


def test_cache_is_private_atomic_and_does_not_store_source_credentials(monkeypatch, tmp_path):
    cache_path = tmp_path / "private-cache" / "update-check.json"
    monkeypatch.setattr(update_check, "update_cache_path", lambda: cache_path)
    monkeypatch.setattr(update_check, "_latest_remote_release", lambda _url: (True, "v0.1.10"))
    source = _source(git_url="https://secret-token@github.com/ViktorOgnev/kaiten-cli.git")

    assert check_for_update(source, now=1000) is not None

    text = cache_path.read_text(encoding="utf-8")
    assert "secret-token" not in text
    assert "github.com" not in text
    assert stat.S_IMODE(cache_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(cache_path.parent.stat().st_mode) == 0o700


def test_corrupt_cache_is_replaced_without_failing(monkeypatch):
    path = update_check.update_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(update_check, "_latest_remote_release", lambda _url: (True, "v0.1.10"))

    candidate = check_for_update(_source(), now=1000)

    assert candidate is not None
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 1


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            _source(),
            ["/usr/local/bin/pipx", "upgrade", "kaiten-cli"],
        ),
        (
            _source(manager="uv", manager_executable="/usr/bin/uv"),
            ["/usr/bin/uv", "tool", "upgrade", "kaiten-cli"],
        ),
        (
            _source(
                manager="pip", manager_executable="/venv/bin/python", requested_revision="master"
            ),
            [
                "/venv/bin/python",
                "-m",
                "pip",
                "install",
                "--upgrade",
                "git+ssh://git@github.com/ViktorOgnev/kaiten-cli.git@master",
            ],
        ),
    ],
)
def test_builds_branch_update_commands(source, expected):
    assert build_update_command(source, "v0.1.10") == expected


@pytest.mark.parametrize(
    ("manager", "executable", "prefix"),
    [
        ("pipx", "/usr/local/bin/pipx", ["/usr/local/bin/pipx", "install", "--force"]),
        ("uv", "/usr/bin/uv", ["/usr/bin/uv", "tool", "install", "--force"]),
        (
            "pip",
            "/venv/bin/python",
            ["/venv/bin/python", "-m", "pip", "install", "--upgrade"],
        ),
    ],
)
def test_tag_pin_moves_to_new_release_and_preserves_subdirectory(manager, executable, prefix):
    source = _source(
        manager=manager,
        manager_executable=executable,
        requested_revision="v0.1.9",
        subdirectory="packages/cli",
    )

    command = build_update_command(source, "v0.1.10")

    assert command == [
        *prefix,
        "git+ssh://git@github.com/ViktorOgnev/kaiten-cli.git@v0.1.10#subdirectory=packages%2Fcli",
    ]


def test_missing_manager_executable_has_no_update_command():
    assert build_update_command(_source(manager_executable=None), "v0.1.10") is None


def test_perform_update_runs_without_shell_and_reports_success(monkeypatch, capsys):
    candidate = UpdateCandidate(_source(), "v0.1.10", "source-key")
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return _completed(command)

    monkeypatch.setattr(update_check.subprocess, "run", fake_run)

    assert update_check._perform_update(candidate) == 0
    assert calls == [(["/usr/local/bin/pipx", "upgrade", "kaiten-cli"], {"check": False})]
    assert "will be used on the next run" in capsys.readouterr().err


def test_perform_update_preserves_installer_failure(monkeypatch, capsys):
    candidate = UpdateCandidate(_source(), "v0.1.10", "source-key")
    monkeypatch.setattr(
        update_check.subprocess,
        "run",
        lambda command, **_kwargs: _completed(command, returncode=23),
    )

    assert update_check._perform_update(candidate) == 23
    assert "exit code 23" in capsys.readouterr().err


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--json", "agent-help"],
        ["--no-update-check", "agent-help"],
        ["--help"],
        ["cards", "-h"],
        ["--version"],
    ],
)
def test_update_checks_are_disabled_for_exact_output_modes(args):
    assert not should_check_for_updates(args, stdin=TtyStream(True), stderr=TtyStream(True))


def test_update_check_requires_tty_and_honors_environment(monkeypatch):
    args = ["agent-help"]
    assert not should_check_for_updates(args, stdin=TtyStream(False), stderr=TtyStream(True))
    assert not should_check_for_updates(args, stdin=TtyStream(True), stderr=TtyStream(False))

    monkeypatch.setenv("KAITEN_CLI_UPDATE_CHECK", "0")
    assert not should_check_for_updates(args, stdin=TtyStream(True), stderr=TtyStream(True))

    monkeypatch.setenv("KAITEN_CLI_UPDATE_CHECK", "1")
    assert should_check_for_updates(args, stdin=TtyStream(True), stderr=TtyStream(True))

    monkeypatch.setenv("_KAITEN_COMPLETE", "bash_complete")
    assert not should_check_for_updates(args, stdin=TtyStream(True), stderr=TtyStream(True))


def test_declined_offer_is_recorded_without_exposing_credentials(monkeypatch, capsys):
    source = _source(git_url="https://secret-token@github.com/ViktorOgnev/kaiten-cli.git")
    candidate = UpdateCandidate(source, "v0.1.10", "source-key")
    recorded = []
    monkeypatch.setattr(update_check, "should_check_for_updates", lambda _args: True)
    monkeypatch.setattr(update_check, "detect_install_source", lambda: source)
    monkeypatch.setattr(update_check, "check_for_update", lambda _source: candidate)
    monkeypatch.setattr(update_check, "_record_prompted", recorded.append)
    monkeypatch.setattr(
        update_check.click,
        "confirm",
        lambda prompt, **_kwargs: "secret-token" not in prompt and False,
    )
    monkeypatch.setattr(
        update_check, "_perform_update", lambda _candidate: pytest.fail("must not update")
    )

    assert maybe_offer_update(["agent-help"]) == 0

    assert recorded == [candidate]
    assert "secret-token" not in capsys.readouterr().err


def test_confirmed_offer_returns_installer_result(monkeypatch):
    source = _source()
    candidate = UpdateCandidate(source, "v0.1.10", "source-key")
    recorded = []
    monkeypatch.setattr(update_check, "should_check_for_updates", lambda _args: True)
    monkeypatch.setattr(update_check, "detect_install_source", lambda: source)
    monkeypatch.setattr(update_check, "check_for_update", lambda _source: candidate)
    monkeypatch.setattr(update_check, "_record_prompted", recorded.append)
    monkeypatch.setattr(update_check.click, "confirm", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        update_check, "_perform_update", lambda received: 17 if received == candidate else 99
    )

    assert maybe_offer_update(["agent-help"]) == 17
    assert recorded == []


def test_successful_update_is_recorded(monkeypatch):
    source = _source()
    candidate = UpdateCandidate(source, "v0.1.10", "source-key")
    recorded = []
    monkeypatch.setattr(update_check, "should_check_for_updates", lambda _args: True)
    monkeypatch.setattr(update_check, "detect_install_source", lambda: source)
    monkeypatch.setattr(update_check, "check_for_update", lambda _source: candidate)
    monkeypatch.setattr(update_check, "_record_prompted", recorded.append)
    monkeypatch.setattr(update_check.click, "confirm", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(update_check, "_perform_update", lambda _candidate: 0)

    assert maybe_offer_update(["agent-help"]) == 0
    assert recorded == [candidate]


def test_aborted_prompt_behaves_like_decline(monkeypatch):
    source = _source()
    candidate = UpdateCandidate(source, "v0.1.10", "source-key")
    recorded = []
    monkeypatch.setattr(update_check, "should_check_for_updates", lambda _args: True)
    monkeypatch.setattr(update_check, "detect_install_source", lambda: source)
    monkeypatch.setattr(update_check, "check_for_update", lambda _source: candidate)
    monkeypatch.setattr(update_check, "_record_prompted", recorded.append)

    def abort(*_args, **_kwargs):
        raise click.Abort()

    monkeypatch.setattr(update_check.click, "confirm", abort)

    assert maybe_offer_update(["agent-help"]) == 0
    assert recorded == [candidate]


def test_main_propagates_confirmed_update_failure_and_swallows_check_bug(monkeypatch):
    from kaiten_cli import app

    monkeypatch.setattr(app, "maybe_offer_update", lambda _args: 17)
    assert app.main(["agent-help"]) == 17

    def broken_check(_args):
        raise RuntimeError("broken update checker")

    monkeypatch.setattr(app, "maybe_offer_update", broken_check)
    assert app.main(["agent-help"]) == 0


def test_main_skips_update_hook_after_callback_failure(monkeypatch, config_env):
    from kaiten_cli import app

    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)
    monkeypatch.setattr(
        app,
        "maybe_offer_update",
        lambda _args: pytest.fail("update hook must not run after command failure"),
    )

    assert app.main(["--json", "cards", "list"]) == 3


def test_no_update_check_is_a_documented_global_option(runner):
    from kaiten_cli.app import cli

    help_result = runner.invoke(cli, ["--help"])
    assert "--no-update-check" in help_result.output
