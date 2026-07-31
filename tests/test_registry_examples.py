from __future__ import annotations

import shlex

from kaiten_cli.app import cli
from kaiten_cli.registry import iter_tools

_ROOT_SWITCHES = {"--json", "--read-only", "--verbose", "--no-update-check", "--stdin-json"}
_ROOT_OPTIONS_WITH_VALUE = {
    "--profile",
    "--from-file",
    "--cache-mode",
    "--cache-ttl-seconds",
    "--trace-file",
}


def _command_path(example_command: str) -> list[str]:
    tokens = shlex.split(example_command)
    if not tokens or tokens[0] != "kaiten":
        raise AssertionError(f"Unsupported example command: {example_command}")

    index = 1
    while index < len(tokens) and tokens[index].startswith("-"):
        option = tokens[index].split("=", 1)[0]
        if option in _ROOT_SWITCHES:
            index += 1
            continue
        if option in _ROOT_OPTIONS_WITH_VALUE:
            index += 1 if "=" in tokens[index] else 2
            continue
        raise AssertionError(f"Unsupported root option in example: {example_command}")

    path: list[str] = []
    for token in tokens[index:]:
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
