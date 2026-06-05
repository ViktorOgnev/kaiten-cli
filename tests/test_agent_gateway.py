from __future__ import annotations

import subprocess
from pathlib import Path

from kaiten_cli.agent_gateway import (
    AgentGatewayConfig,
    build_codex_command,
    build_prompt,
    chat_response,
    run_codex,
)


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


def test_chat_response_matches_kaiten_agent_contract():
    response = chat_response("hello")

    assert response["message"] == {"role": "assistant", "content": "hello"}
    assert response["usage"]["provider"] == "codex_exec"
