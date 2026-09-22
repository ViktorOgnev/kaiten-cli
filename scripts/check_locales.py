#!/usr/bin/env python3
"""Check translation coverage and interpolation contracts without network access."""

from __future__ import annotations

import ast
import inspect
import json
import re
import sys
from pathlib import Path
from string import Formatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kaiten_cli.i18n import catalog  # noqa: E402
from kaiten_cli.registry import cache_guidance_for, iter_tools  # noqa: E402
from kaiten_cli.registry.live_contracts import get_live_contract  # noqa: E402
from kaiten_cli.registry.module_docs import MODULE_SPECS  # noqa: E402


def schema_messages(schema):
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key in ("title", "description") and isinstance(value, str):
                yield value
            elif isinstance(value, (dict, list)):
                yield from schema_messages(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from schema_messages(value)


def required_messages():
    messages = {
        "Validation error",
        "Config error",
        "Api error",
        "Transport error",
        "Mutation blocked",
        "Internal error",
        "Batch execution error",
        "reset",
        "recreate",
        "open",
        "read",
    }
    for tool in iter_tools():
        messages.add(tool.description)
        messages.update(tool.usage_notes)
        messages.update(example.description for example in tool.examples)
        messages.update(schema_messages(tool.input_schema))
        for key, value in cache_guidance_for(tool).items():
            if key in ("guidance", "refresh_hint", "off_hint", "readwrite_hint"):
                messages.add(value)
        contract = get_live_contract(tool.canonical_name)
        if contract and contract.note:
            messages.add(contract.note)
    for module in MODULE_SPECS:
        messages.update((module.label, module.description))
    for path in (ROOT / "src/kaiten_cli").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "tr" and node.args:
                    if isinstance(node.args[0], ast.Constant):
                        messages.add(node.args[0].value)
                for kw in node.keywords:
                    if (
                        kw.arg in ("help", "short_help")
                        and isinstance(kw.value, ast.Constant)
                        and isinstance(kw.value.value, str)
                    ):
                        messages.add(kw.value.value)
    from kaiten_cli.app import CLI_EPILOG, CLI_HELP

    messages.update((CLI_HELP, CLI_EPILOG))
    from kaiten_cli.localized_click import CLICK_MODULES

    for module in CLICK_MODULES:
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in ("_", "ngettext")
            ):
                for arg in node.args[: 2 if node.func.id == "ngettext" else 1]:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        messages.add(arg.value)
    return messages - {""}


def unlocalized_message_calls(source):
    """Reject literal prose at runtime output sinks unless explicitly localized.

    Variables are allowed: they may carry API/user content which must not be
    translated. Help metadata is covered separately by required_messages().
    """
    sinks = {
        "reporter",
        "debug",
        "debug_reporter",
        "_emit_debug",
        "click.echo",
        "click.confirm",
        "ValidationError",
        "ConfigError",
        "TransportError",
        "MutationBlockedError",
        "BatchExecutionError",
        "InternalError",
        "OSError",
        "warnings.append",
        "logger.warning",
    }
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        name = ast.unparse(node.func)
        if name not in sinks and not name.endswith("._debug"):
            continue
        index = 1 if name == "_emit_debug" else 0
        if len(node.args) <= index:
            continue
        value = node.args[index]
        if isinstance(value, ast.JoinedStr) or (
            isinstance(value, ast.Constant)
            and isinstance(value.value, str)
            and re.search(r"[A-Za-zА-Яа-я]", value.value)
        ):
            yield node.lineno, name


def fields(text):
    # Source API prose may contain example JSON/braces. Only compare parseable templates.
    try:
        return sorted(
            (field, spec, conversion)
            for _, field, spec, conversion in Formatter().parse(text)
            if field is not None
        )
    except ValueError:
        return None


def check():
    translations = catalog()
    errors = []
    for message in sorted(required_messages()):
        if not translations.get(message):
            errors.append(f"Missing RU translation: {message!r}")
    for path in (ROOT / "src/kaiten_cli").rglob("*.py"):
        for line, name in unlocalized_message_calls(path.read_text()):
            errors.append(f"Unlocalized literal at {path.relative_to(ROOT)}:{line}: {name}")
    for source, target in translations.items():

        def flags(text):
            return set(re.findall(r"(?<!\w)--[a-z][a-z0-9-]*", text))

        if flags(source) != flags(target):
            errors.append(f"Command flag mismatch: {source!r}")

        def percent(text):
            return sorted(
                re.findall(r"%(?:\([a-zA-Z_]+\))?[#0+ .\-]*[0-9]*(?:\.[0-9]+)?[sdifgcr]", text)
            )

        if percent(source) != percent(target):
            errors.append(f"Percent interpolation mismatch: {source!r}")
        if fields(source) != fields(target):
            errors.append(f"Interpolation mismatch: {source!r}")
    return errors


def main():
    if "--list" in sys.argv:
        print(json.dumps(sorted(required_messages()), ensure_ascii=False, indent=2))
        return 0
    errors = check()
    print(
        "\n".join(errors)
        if errors
        else f"EN/RU catalog verified: {len(required_messages())} messages."
    )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
