from __future__ import annotations

import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from kaiten_cli import completion
from kaiten_cli.app import cli


@pytest.fixture
def completion_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data_dir = tmp_path / "completion data"
    monkeypatch.setattr(completion, "completion_data_dir", lambda: data_dir)
    monkeypatch.setattr(completion, "_command_path", lambda: "/tmp/bin/kaiten")
    monkeypatch.setattr(
        completion,
        "_shell_support",
        lambda shell: (True, f"/bin/{shell}", None),
    )
    return data_dir


def test_completion_source_exposes_click_scripts(runner):
    zsh = runner.invoke(cli, ["completion", "source", "zsh"])
    bash = runner.invoke(cli, ["--json", "completion", "source", "bash"])

    assert zsh.exit_code == 0
    assert zsh.output.startswith("#compdef kaiten\n")
    assert "_KAITEN_COMPLETE=zsh_complete kaiten" in zsh.output

    assert bash.exit_code == 0
    payload = json.loads(bash.output)
    assert payload["success"] is True
    assert payload["command"] == "completion.source"
    assert payload["data"]["shell"] == "bash"
    assert "complete -o nosort -F _kaiten_completion kaiten" in payload["data"]["source"]


def test_zsh_install_migrates_legacy_block_and_is_idempotent(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    config.write_text(
        "export BEFORE=1\n\n"
        + completion.LEGACY_ZSH_BLOCK
        + "# Yandex Cloud resets the completion table\n"
        + "autoload -U +X compinit && compinit\n",
        encoding="utf-8",
    )
    config.chmod(0o640)

    first = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )

    assert first.exit_code == 0, first.output
    first_payload = json.loads(first.output)["data"]
    text = config.read_text(encoding="utf-8")
    script = completion_env / "kaiten-complete.zsh"
    assert first_payload["configured"] is True
    assert first_payload["legacy_migrated"] is True
    assert first_payload["config_changed"] is True
    assert first_payload["script_changed"] is True
    assert completion.LEGACY_ZSH_BLOCK not in text
    assert text.count(completion.MANAGED_BLOCK_BEGIN) == 1
    assert text.index("compinit") < text.index(completion.MANAGED_BLOCK_BEGIN)
    assert stat.S_IMODE(config.stat().st_mode) == 0o640
    assert stat.S_IMODE(script.stat().st_mode) == 0o600
    assert stat.S_IMODE(script.parent.stat().st_mode) == 0o700
    config_inode = config.stat().st_ino
    script_inode = script.stat().st_ino

    second = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )

    assert second.exit_code == 0, second.output
    second_payload = json.loads(second.output)["data"]
    assert second_payload["configured"] is True
    assert second_payload["config_changed"] is False
    assert second_payload["script_changed"] is False
    assert config.stat().st_ino == config_inode
    assert script.stat().st_ino == script_inode


def test_completion_install_dry_run_does_not_write(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"

    result = runner.invoke(
        cli,
        [
            "--json",
            "completion",
            "install",
            "--shell",
            "zsh",
            "--config",
            str(config),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)["data"]
    assert data["dry_run"] is True
    assert data["config_changed"] is True
    assert data["script_changed"] is True
    assert data["configured"] is False
    assert not config.exists()
    assert not completion_env.exists()


def test_completion_status_reports_unmanaged_registration(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    config.write_text('eval "$(_KAITEN_COMPLETE=zsh_source kaiten)"\n', encoding="utf-8")

    result = runner.invoke(
        cli,
        ["--json", "completion", "status", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)["data"]
    assert data["configured"] is False
    assert data["unmanaged_registration"] is True
    assert data["managed_block"] is False
    assert any("unmanaged" in warning for warning in data["warnings"])
    assert not completion_env.exists()


def test_completion_status_reports_legacy_zsh_registration(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    config.write_text(completion.LEGACY_ZSH_BLOCK, encoding="utf-8")

    result = runner.invoke(
        cli,
        ["--json", "completion", "status", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)["data"]
    assert data["configured"] is False
    assert data["legacy_registration"] is True
    assert data["unmanaged_registration"] is False
    assert any("legacy dynamic" in warning for warning in data["warnings"])
    assert not completion_env.exists()


def test_completion_uninstall_removes_only_managed_artifacts(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    original = "export KEEP_ME=1\n"
    config.write_text(original, encoding="utf-8")
    install = runner.invoke(
        cli,
        ["completion", "install", "--shell", "zsh", "--config", str(config)],
    )
    assert install.exit_code == 0, install.output

    result = runner.invoke(
        cli,
        ["--json", "completion", "uninstall", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)["data"]
    assert data["configured"] is False
    assert data["removed_blocks"] == 1
    assert data["config_changed"] is True
    assert config.read_text(encoding="utf-8") == original
    assert not (completion_env / "kaiten-complete.zsh").exists()


def test_completion_install_preserves_config_symlink_and_target_mode(
    runner, completion_env: Path, tmp_path: Path
):
    target = tmp_path / "dotfiles" / "zshrc"
    target.parent.mkdir()
    target.write_text("export LINKED=1\n", encoding="utf-8")
    target.chmod(0o644)
    config = tmp_path / ".zshrc"
    config.symlink_to(target)

    result = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)["data"]
    assert data["configured"] is True
    assert data["config_path"] == str(config)
    assert data["config_target_path"] == str(target)
    assert config.is_symlink()
    assert completion.MANAGED_BLOCK_BEGIN in target.read_text(encoding="utf-8")
    assert stat.S_IMODE(target.stat().st_mode) == 0o644


def test_completion_install_repairs_insecure_script_mode(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    first = runner.invoke(
        cli,
        ["completion", "install", "--shell", "zsh", "--config", str(config)],
    )
    assert first.exit_code == 0, first.output
    script = completion_env / "kaiten-complete.zsh"
    script.chmod(0o644)

    status = runner.invoke(
        cli,
        ["--json", "completion", "status", "--shell", "zsh", "--config", str(config)],
    )
    status_data = json.loads(status.output)["data"]
    assert status_data["configured"] is False
    assert status_data["script_secure"] is False

    reinstall = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )
    assert reinstall.exit_code == 0, reinstall.output
    reinstall_data = json.loads(reinstall.output)["data"]
    assert reinstall_data["script_changed"] is True
    assert reinstall_data["script_secure"] is True
    assert stat.S_IMODE(script.stat().st_mode) == 0o600


def test_atomic_write_rejects_concurrent_config_change(tmp_path: Path):
    config = tmp_path / ".zshrc"
    config.write_text("original\n", encoding="utf-8")
    _, signature, mode = completion._read_edit_state(config)
    config.write_text("changed elsewhere\n", encoding="utf-8")

    with pytest.raises(Exception, match="changed before atomic replacement"):
        completion._write_text_atomic(
            config,
            "agent change\n",
            mode=mode,
            expected_signature=signature,
            verify_signature=True,
        )

    assert config.read_text(encoding="utf-8") == "changed elsewhere\n"
    assert not list(tmp_path.glob(".zshrc.*"))


def test_completion_install_rejects_symlinked_generated_script(
    runner, completion_env: Path, tmp_path: Path
):
    completion_env.mkdir(parents=True)
    target = tmp_path / "unrelated"
    target.write_text("keep\n", encoding="utf-8")
    script = completion_env / "kaiten-complete.zsh"
    script.symlink_to(target)
    config = tmp_path / ".zshrc"

    result = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 3
    assert "symlinked completion script" in json.loads(result.output)["error"]["message"]
    assert target.read_text(encoding="utf-8") == "keep\n"
    assert not config.exists()


def test_incomplete_managed_block_fails_without_writing_script(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    original = f"export SAFE=1\n{completion.MANAGED_BLOCK_BEGIN}\n"
    config.write_text(original, encoding="utf-8")

    result = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 3
    payload = json.loads(result.output)
    assert payload["error"]["type"] == "config_error"
    assert "incomplete" in payload["error"]["message"]
    assert config.read_text(encoding="utf-8") == original
    assert not completion_env.exists()


def test_install_rejects_missing_entrypoint_without_writes(
    runner, completion_env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(completion, "_command_path", lambda: None)
    config = tmp_path / ".zshrc"

    result = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "zsh", "--config", str(config)],
    )

    assert result.exit_code == 3
    assert "not available on PATH" in json.loads(result.output)["error"]["message"]
    assert not config.exists()
    assert not completion_env.exists()


def test_install_rejects_unsupported_bash_without_writes(
    runner, completion_env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        completion,
        "_shell_support",
        lambda shell: (False, "/bin/bash", "Bash 3.2 is unsupported; Click requires Bash 4.4+."),
    )
    config = tmp_path / ".bashrc"

    result = runner.invoke(
        cli,
        ["--json", "completion", "install", "--shell", "bash", "--config", str(config)],
    )

    assert result.exit_code == 2
    assert "Bash 3.2" in json.loads(result.output)["error"]["message"]
    assert not config.exists()
    assert not completion_env.exists()


def test_shell_detection_uses_shell_basename(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SHELL", "/opt/homebrew/bin/zsh")
    assert completion.detect_shell() == "zsh"

    monkeypatch.setenv("SHELL", "/bin/fish")
    with pytest.raises(Exception, match="Unsupported shell"):
        completion.detect_shell()


@pytest.mark.skipif(shutil.which("zsh") is None, reason="zsh is not installed")
def test_generated_zsh_registration_is_visible_to_compinit(
    runner, completion_env: Path, tmp_path: Path
):
    config = tmp_path / ".zshrc"
    result = runner.invoke(
        cli,
        ["completion", "install", "--shell", "zsh", "--config", str(config)],
    )
    assert result.exit_code == 0, result.output

    probe = subprocess.run(
        [
            shutil.which("zsh") or "zsh",
            "-f",
            "-c",
            f'autoload -Uz compinit; compinit -d {shlex_quote(tmp_path / "zcompdump")}; '
            f'. {shlex_quote(config)}; print -r -- "${{_comps[kaiten]-missing}}"',
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert probe.returncode == 0, probe.stderr
    assert probe.stdout.strip() == "_kaiten_completion"


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash is not installed")
def test_generated_bash_registration_returns_real_candidates(
    runner, completion_env: Path, tmp_path: Path
):
    bash = shutil.which("bash") or "bash"
    version = completion._bash_version(bash)
    if version is None or version < (4, 4):
        pytest.skip("Click completion requires Bash 4.4+")

    config = tmp_path / ".bashrc"
    result = runner.invoke(
        cli,
        ["completion", "install", "--shell", "bash", "--config", str(config)],
    )
    assert result.exit_code == 0, result.output

    root = Path(__file__).resolve().parents[1]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    wrapper = bin_dir / "kaiten"
    wrapper.write_text(
        "#!/bin/sh\n"
        f"PYTHONPATH={shlex.quote(str(root / 'src'))} "
        f"exec {shlex.quote(sys.executable)} -m kaiten_cli \"$@\"\n",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    probe = subprocess.run(
        [
            bash,
            "--noprofile",
            "--norc",
            "-c",
            f'. {shlex.quote(str(config))}; '
            "COMP_WORDS=(kaiten cards ''); COMP_CWORD=2; "
            "_kaiten_completion kaiten; printf '%s\\n' \"${COMPREPLY[@]}\"",
        ],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert probe.returncode == 0, probe.stderr
    assert "list" in probe.stdout.splitlines()
    assert "batch-get" in probe.stdout.splitlines()


def shlex_quote(path: os.PathLike[str] | str) -> str:
    return shlex.quote(str(path))
