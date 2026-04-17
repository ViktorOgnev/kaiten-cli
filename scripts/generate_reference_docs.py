#!/usr/bin/env python3
"""Generate registry-driven documentation files."""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kaiten_cli.models import ToolSpec, format_schema_type  # noqa: E402
from kaiten_cli.registry import iter_tools  # noqa: E402
from kaiten_cli.registry.live_contracts import get_live_contract, has_special_live_contract  # noqa: E402

README_PATH = ROOT / "README.md"
COMMAND_REFERENCE_PATH = ROOT / "COMMAND_REFERENCE.md"
README_START = "<!-- BEGIN GENERATED COMMAND SUMMARY -->"
README_END = "<!-- END GENERATED COMMAND SUMMARY -->"


@dataclass(frozen=True, slots=True)
class ModuleDocSpec:
    key: str
    label: str
    description: str


MODULE_SPECS: tuple[ModuleDocSpec, ...] = (
    ModuleDocSpec("cards", "Карточки", "Карточки, bulk reads и card-heavy workflows."),
    ModuleDocSpec("comments", "Комментарии", "Комментарии карточек и comment-heavy reads."),
    ModuleDocSpec("members", "Участники и пользователи", "Участники карточек, пользователи, группы и space users."),
    ModuleDocSpec("time_logs", "Логи времени", "Time logs, work logs и related analytics inputs."),
    ModuleDocSpec("tags", "Теги", "Теги и операции привязки тегов к карточкам."),
    ModuleDocSpec("checklists", "Чеклисты", "Чеклисты и checklist items."),
    ModuleDocSpec("blockers", "Блокировки", "Блокировки карточек и blocker relations."),
    ModuleDocSpec("card_relations", "Связи карточек", "Parent/child/planned relations between cards."),
    ModuleDocSpec("external_links", "Внешние ссылки", "External links attached to cards."),
    ModuleDocSpec("files", "Файлы карточек", "Файлы и вложения карточек."),
    ModuleDocSpec("subscribers", "Подписчики", "Подписки на карточки и колонки."),
    ModuleDocSpec("spaces", "Пространства", "Spaces and top-level workspace reads."),
    ModuleDocSpec("boards", "Доски", "Boards and board-level operations."),
    ModuleDocSpec("columns", "Колонки и подколонки", "Columns, subcolumns and related card structure."),
    ModuleDocSpec("lanes", "Дорожки", "Swimlanes and lane-level operations."),
    ModuleDocSpec("card_types", "Типы карточек", "Card types and type metadata."),
    ModuleDocSpec("custom_properties", "Кастомные свойства", "Custom properties and select values."),
    ModuleDocSpec("documents", "Документы", "Documents and document groups."),
    ModuleDocSpec("webhooks", "Вебхуки", "Webhook configuration and delivery settings."),
    ModuleDocSpec("automations", "Автоматизации и воркфлоу", "Automations, incoming webhooks and workflows."),
    ModuleDocSpec("projects", "Проекты и спринты", "Projects, project cards and sprints."),
    ModuleDocSpec("roles_and_groups", "Роли и группы", "Roles, groups and permission-related operations."),
    ModuleDocSpec("audit_and_analytics", "Аудит и аналитика", "Audit logs, activity, saved filters and analytics helpers."),
    ModuleDocSpec("service_desk", "Service Desk", "Service Desk requests, users, SLA, organizations and settings."),
    ModuleDocSpec("charts", "Графики и аналитика", "Chart endpoints and compute jobs."),
    ModuleDocSpec("tree", "Дерево сущностей", "Entity tree and tree navigation commands."),
    ModuleDocSpec("utilities", "Утилиты", "Company, calendars, timers, api keys and removed entities."),
    ModuleDocSpec("snapshot", "Локальные snapshots", "Local-first snapshot build, refresh and management commands."),
    ModuleDocSpec("query", "Локальные запросы", "Local-only query and metrics commands over snapshots."),
)


def _load_module_tools(spec: ModuleDocSpec) -> tuple[ToolSpec, ...]:
    module = importlib.import_module(f"kaiten_cli.registry.{spec.key}")
    tools = tuple(sorted(getattr(module, "TOOLS"), key=lambda tool: tool.canonical_name))
    return tools


def _load_docs_index() -> list[tuple[ModuleDocSpec, tuple[ToolSpec, ...]]]:
    modules = [(spec, _load_module_tools(spec)) for spec in MODULE_SPECS]
    expected = {tool.canonical_name for tool in iter_tools()}
    actual = {tool.canonical_name for _, tools in modules for tool in tools}
    if expected != actual:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SystemExit(f"Docs index mismatch. Missing={missing} Extra={extra}")
    return modules


def _cli_command(tool: ToolSpec) -> str:
    return "kaiten " + " ".join(tool.command_segments)


def _module_anchor(spec: ModuleDocSpec) -> str:
    return f"module-{spec.key.replace('_', '-')}"


def _render_readme_summary(modules: list[tuple[ModuleDocSpec, tuple[ToolSpec, ...]]]) -> str:
    total_tools = sum(len(tools) for _, tools in modules)
    lines = [
        README_START,
        f"В `kaiten-cli` сейчас **{total_tools}** canonical инструментов в **{len(modules)}** registry modules. Полный список команд: [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md).",
        "",
        "| Область | Модуль | Кол-во | Справочник |",
        "|---|---|---:|---|",
    ]
    for spec, tools in modules:
        lines.append(
            f"| {spec.label} | `{spec.key}` | {len(tools)} | [Раздел](COMMAND_REFERENCE.md#{_module_anchor(spec)}) |"
        )
    lines.append(
        f"| **Итого** | **{len(modules)} modules** | **{total_tools}** | [Полный справочник](COMMAND_REFERENCE.md) |"
    )
    lines.append(README_END)
    return "\n".join(lines)


def _replace_readme_summary(readme_text: str, summary_block: str) -> str:
    pattern = re.compile(
        rf"{re.escape(README_START)}.*?{re.escape(README_END)}",
        flags=re.DOTALL,
    )
    if not pattern.search(readme_text):
        raise SystemExit("README summary markers not found.")
    return pattern.sub(summary_block, readme_text, count=1)


def _namespace_tree(tools: tuple[ToolSpec, ...]) -> str:
    grouped: dict[str, list[str]] = defaultdict(list)
    for tool in tools:
        grouped[tool.namespace or "(root)"].append(tool.action)
    lines = []
    for namespace in sorted(grouped):
        lines.append(namespace)
        for action in sorted(grouped[namespace]):
            lines.append(f"  {action}")
    return "```text\n" + "\n".join(lines) + "\n```"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _escape_table(text: str | None) -> str:
    if not text:
        return "—"
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def _format_enum(values) -> str:
    if not values:
        return "—"
    return ", ".join(f"`{value}`" for value in values)


def _render_argument_table(tool: ToolSpec) -> str:
    properties = tool.input_schema.get("properties", {})
    required = set(tool.input_schema.get("required", []))
    if not properties:
        return "_No tool-specific arguments._"
    lines = [
        "| Argument | Type | Required | Enum | Description |",
        "|---|---|---|---|---|",
    ]
    for name, definition in properties.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{name}`",
                    f"`{format_schema_type(definition)}`",
                    "yes" if name in required else "no",
                    _format_enum(definition.get("enum")),
                    _escape_table(definition.get("description")),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _render_examples(tool: ToolSpec) -> str:
    if not tool.examples:
        return ""
    lines = ["**Examples**", ""]
    for example in tool.examples:
        lines.append(f"- {_escape_table(example.description)}: `{example.command}`")
    return "\n".join(lines)


def _render_usage_notes(tool: ToolSpec) -> str:
    if not tool.usage_notes and tool.bulk_alternative is None and not has_special_live_contract(tool.canonical_name):
        return ""
    lines = ["**Notes**", ""]
    if tool.bulk_alternative is not None:
        lines.append(f"- Bulk alternative: `{tool.bulk_alternative}`")
    for note in tool.usage_notes:
        lines.append(f"- {note}")
    if has_special_live_contract(tool.canonical_name):
        contract = get_live_contract(tool.canonical_name)
        expected = ", ".join(f"`{status}`" for status in contract.expected_statuses)
        lines.append(f"- Live contract: `{contract.status}`; expected statuses: {expected or '—'}")
        lines.append(f"- Live note: {contract.note}")
    return "\n".join(lines)


def _render_command_metadata(tool: ToolSpec) -> str:
    return "\n".join(
        [
            "| Field | Value |",
            "|---|---|",
            f"| CLI command | `{_cli_command(tool)}` |",
            f"| MCP alias | `{tool.mcp_alias}` |",
            f"| Description | {_escape_table(tool.description)} |",
            f"| Method | `{tool.operation.method}` |",
            f"| Mutation | `{_yes_no(tool.is_mutation)}` |",
            f"| Execution mode | `{tool.execution_mode}` |",
            f"| Cache policy | `{tool.cache_policy}` |",
            f"| Path template | `{tool.operation.path_template}` |",
            f"| Compact | `{_yes_no(tool.response_policy.compact_supported)}` |",
            f"| Fields | `{_yes_no(tool.response_policy.fields_supported)}` |",
            f"| Heavy | `{_yes_no(tool.response_policy.heavy)}` |",
        ]
    )


def _render_command_reference(modules: list[tuple[ModuleDocSpec, tuple[ToolSpec, ...]]]) -> str:
    total_tools = sum(len(tools) for _, tools in modules)
    lines = [
        "# Command Reference",
        "",
        "> This file is generated from the local registry. Do not edit by hand.",
        "",
        f"`kaiten-cli` currently exposes **{total_tools}** canonical commands across **{len(modules)}** registry modules.",
        "",
        "## Conventions",
        "",
        "- Canonical CLI form is rendered as `kaiten <namespace...> <action>`.",
        "- MCP alias is shown inline for every command.",
        "- All commands support `--json`, `--from-file` and `--stdin-json`; these global input modes are not repeated per command.",
        "- `--compact` and `--fields` only apply when the command metadata says they are supported.",
        "- Use `search-tools`, `describe` and `examples` when you need interactive discovery instead of scrolling the full page.",
        "- For read-heavy workflows, prefer bulk tools and the `snapshot` / `query` local-first path over per-entity loops.",
        "",
        "## Module Index",
        "",
        "| Area | Module | Count | Section |",
        "|---|---|---:|---|",
    ]
    for spec, tools in modules:
        lines.append(f"| {spec.label} | `{spec.key}` | {len(tools)} | [Open](#{_module_anchor(spec)}) |")
    lines.extend(
        [
            "",
            "## Full Reference",
            "",
        ]
    )

    for spec, tools in modules:
        lines.extend(
            [
                f'<a id="{_module_anchor(spec)}"></a>',
                f"## {spec.label} (`{spec.key}`) — {len(tools)} commands",
                "",
                spec.description,
                "",
                "**Namespace tree**",
                "",
                _namespace_tree(tools),
                "",
            ]
        )
        for tool in tools:
            lines.extend(
                [
                    f"### `{tool.canonical_name}`",
                    "",
                    _render_command_metadata(tool),
                    "",
                    "**Arguments**",
                    "",
                    _render_argument_table(tool),
                    "",
                ]
            )
            examples = _render_examples(tool)
            if examples:
                lines.extend([examples, ""])
            notes = _render_usage_notes(tool)
            if notes:
                lines.extend([notes, ""])
    return "\n".join(lines).rstrip() + "\n"


def _write_if_changed(path: Path, content: str) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate registry-driven documentation files.")
    parser.add_argument("--check", action="store_true", help="Verify that generated docs are up to date.")
    parser.add_argument("--write", action="store_true", help="Write generated docs to the repository.")
    args = parser.parse_args()

    if args.check and args.write:
        raise SystemExit("Use either --check or --write, not both.")
    if not args.check and not args.write:
        raise SystemExit("Specify --check or --write.")

    modules = _load_docs_index()
    summary_block = _render_readme_summary(modules)
    readme = README_PATH.read_text(encoding="utf-8")
    expected_readme = _replace_readme_summary(readme, summary_block)
    expected_reference = _render_command_reference(modules)

    if args.check:
        mismatches: list[str] = []
        if readme != expected_readme:
            mismatches.append("README.md")
        current_reference = COMMAND_REFERENCE_PATH.read_text(encoding="utf-8") if COMMAND_REFERENCE_PATH.exists() else ""
        if current_reference != expected_reference:
            mismatches.append("COMMAND_REFERENCE.md")
        if mismatches:
            raise SystemExit("Generated docs are out of date: " + ", ".join(mismatches))
        return 0

    _write_if_changed(README_PATH, expected_readme)
    _write_if_changed(COMMAND_REFERENCE_PATH, expected_reference)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
