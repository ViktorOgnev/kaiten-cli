from __future__ import annotations

import shlex

from kaiten_cli.app import cli
from kaiten_cli.registry import iter_tools


def _command_path(example_command: str) -> list[str]:
    tokens = shlex.split(example_command)
    if not tokens or tokens[0] != "kaiten":
        raise AssertionError(f"Unsupported example command: {example_command}")

    path: list[str] = []
    for token in tokens[1:]:
        if token.startswith("-"):
            break
        path.append(token)

    if not path:
        raise AssertionError(f"Example command has no CLI path: {example_command}")
    return path


def test_registry_examples_reference_real_command_paths(runner):
    for tool in iter_tools():
        for example in tool.examples:
            result = runner.invoke(cli, _command_path(example.command) + ["--help"])
            assert result.exit_code == 0, example.command
