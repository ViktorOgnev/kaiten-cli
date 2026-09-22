"""CLI entrypoint."""

from __future__ import annotations

import os
import sys
import time
from collections import defaultdict
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from typing import Any

import click
from click.exceptions import NoArgsIsHelpError

from kaiten_cli import __version__
from kaiten_cli.completion import (
    SUPPORTED_SHELLS,
    completion_status,
    generate_completion_source,
    install_completion,
    uninstall_completion,
)
from kaiten_cli.discovery import describe_tool, search_tools, tool_examples
from kaiten_cli.errors import (
    BatchExecutionError,
    CliError,
    ConfigError,
    InternalError,
    ValidationError,
)
from kaiten_cli.i18n import get_locale, tr, use_locale
from kaiten_cli.localized_click import LocalizedCommand, LocalizedGroup, resolve_locale
from kaiten_cli.models import GlobalOptions, ToolSpec
from kaiten_cli.profiles import (
    add_profile,
    list_profiles,
    remove_profile,
    resolve_profile,
    show_profile,
    use_profile,
)
from kaiten_cli.registry import iter_module_tools, iter_tools, resolve_tool
from kaiten_cli.registry.module_docs import MODULE_SPECS_BY_KEY
from kaiten_cli.runtime.executor import execute_tool_sync_with_diagnostics, read_only_enabled
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.output import render_error, render_success
from kaiten_cli.runtime.trace import (
    ExecutionStats,
    TraceRecorder,
    bulk_trace_meta,
    summarize_trace,
)
from kaiten_cli.update_check import maybe_offer_update

_ARGV: ContextVar[list[str] | None] = ContextVar("kaiten_argv", default=None)
CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
REPOSITORY_URL = "https://github.com/ViktorOgnev/kaiten-cli"
README_URL = f"{REPOSITORY_URL}/blob/master/README.md"
COMMAND_REFERENCE_URL = f"{REPOSITORY_URL}/blob/master/COMMAND_REFERENCE.md"
ARCHITECTURE_URL = f"{REPOSITORY_URL}/blob/master/ARCHITECTURE.md"
AGENTS_URL = f"{REPOSITORY_URL}/blob/master/AGENTS.md"
HEAVY_DATA_SKILL_URL = f"{REPOSITORY_URL}/blob/master/skills/kaiten-cli-heavy-data/SKILL.md"
METRICS_SKILL_URL = f"{REPOSITORY_URL}/blob/master/skills/kaiten-cli-metrics/SKILL.md"
MUTATIONS_SKILL_URL = f"{REPOSITORY_URL}/blob/master/skills/kaiten-cli-mutations/SKILL.md"
CLI_HELP = """Kaiten API CLI optimized for humans and agents.

\b
Quick start:
  kaiten search-tools "wip cards"
  kaiten describe cards.list-all
  kaiten examples cards.list-all
  kaiten snapshot build --name team-basic --space-id 10 --preset basic
  kaiten query cards --snapshot team-basic --view summary --fields id,title,state
  kaiten --json spaces list --compact --fields id,title
  kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active
  kaiten --json --profile main --read-only profile probe
  kaiten --json trace summarize --file ./kaiten-trace.jsonl

\b
Principles:
  - use --json for automation and LLM workflows
  - omit --cache-mode for normal workflows: auto reuses cacheable safe reads
  - use refresh once at a freshness boundary, off for diagnostics/privacy/polling,
    and readwrite only with an explicit fixed TTL
  - run search-tools -> describe -> examples once per unfamiliar family, mutation,
    or heavy command
  - for repeated analytics/report reads, prefer snapshot build -> query cards/query metrics
  - keep local queries summary-first; escalate to detail/evidence only after candidate reduction
  - use a bulk alternative for two or more IDs; never put refresh in an entity loop
  - use --compact and --fields to shrink payloads
  - live validation runs only when KAITEN_LIVE=1|true
  - use --trace-file for wrappers with 3+ CLI commands, >10 expected HTTP requests,
    or an unavoidable loop

\b
More guided onboarding:
  kaiten agent-help
"""
CLI_EPILOG = f"""\b
Documentation:
  Repo: {REPOSITORY_URL}
  README: {README_URL}
  Command reference: {COMMAND_REFERENCE_URL}
  Architecture: {ARCHITECTURE_URL}
  Agent guide: {AGENTS_URL}
  Skills:
    heavy-data: {HEAVY_DATA_SKILL_URL}
    metrics: {METRICS_SKILL_URL}
    mutations: {MUTATIONS_SKILL_URL}
"""


def _ctx_options(ctx: click.Context) -> GlobalOptions:
    return ctx.ensure_object(GlobalOptions)


def _discard_result_stats(ctx: click.Context) -> None:
    ctx.meta.pop("last_stats_payload", None)


def _echo_result(ctx: click.Context, command: str, data: Any) -> None:
    options = _ctx_options(ctx)
    stats = ctx.meta.pop("last_stats_payload", None)
    click.echo(render_success(command, data, options.json_mode, stats=stats))


def _echo_human_result(ctx: click.Context, text: str) -> None:
    _discard_result_stats(ctx)
    click.echo(text)


def _render_completion_text(action: str, data: dict[str, Any]) -> str:
    configured = _yes_no(data.get("configured"))
    headline = (
        tr("Shell completion dry run for {value_0}.", value_0=data["shell"])
        if data.get("dry_run")
        else tr(
            "Shell completion {value_0} for {value_1}.", value_0=tr(action), value_1=data["shell"]
        )
    )
    lines = [
        headline,
        tr("Configured: {value_0}", value_0=configured),
        tr("Script: {value_0}", value_0=data["script_path"]),
        tr("Shell config: {value_0}", value_0=data["config_path"]),
    ]
    if data.get("dry_run"):
        lines.append(tr("Dry run: no files were changed."))
    elif action == "installed":
        lines.append(tr("Restart the shell: {value_0}", value_0=data["restart_command"]))
    warnings = data.get("warnings") or []
    if warnings:
        lines.append(tr("Warnings:"))
        lines.extend(tr("  - {value_0}", value_0=warning) for warning in warnings)
    return "\n".join(lines)


def _echo_completion_result(
    ctx: click.Context, command: str, action: str, data: dict[str, Any]
) -> None:
    if _ctx_options(ctx).json_mode:
        _echo_result(ctx, command, data)
    else:
        _echo_human_result(ctx, _render_completion_text(action, data))


def _fail(ctx: click.Context, command: str | None, error: CliError) -> None:
    options = _ctx_options(ctx)
    stats = ctx.meta.pop("last_stats_payload", None)
    click.echo(
        render_error(command, error, options.json_mode, stats=stats), err=not options.json_mode
    )
    ctx.exit(error.exit_code)


def _emit_internal(ctx: click.Context, command: str | None, exc: Exception) -> None:
    _fail(
        ctx,
        command,
        InternalError(tr("{value_0}: {value_1}", value_0=type(exc).__name__, value_1=exc)),
    )


def _make_debug_reporter(ctx: click.Context):
    options = _ctx_options(ctx)
    if not options.verbose:
        return None

    def reporter(message: str) -> None:
        click.echo(tr("[verbose] {value_0}", value_0=message), err=True)

    return reporter


def _trace_recorder(ctx: click.Context) -> TraceRecorder | None:
    options = _ctx_options(ctx)
    if not options.trace_file:
        return None
    return TraceRecorder(options.trace_file)


def _current_argv(ctx: click.Context) -> list[str]:
    root = ctx.find_root()
    argv = root.meta.get("argv")
    if isinstance(argv, list):
        return list(argv)
    return list(_ARGV.get() or sys.argv[1:])


def _trace_bulk_meta(data: Any) -> dict[str, Any]:
    if isinstance(data, BatchExecutionError):
        return bulk_trace_meta(data.data)
    return bulk_trace_meta(data)


def _stats_payload(stats: ExecutionStats | None, *, duration_ms: float) -> dict[str, Any]:
    return (stats or ExecutionStats()).to_payload(command_duration_ms=duration_ms)


def _emit_stats_summary(ctx: click.Context, stats_payload: dict[str, Any]) -> None:
    options = _ctx_options(ctx)
    if not options.verbose:
        return
    cache_hits = stats_payload.get("cache_hits", {})
    click.echo(
        tr(
            "[verbose] stats: duration_ms={value_0:.2f} http_requests={value_1} api_wait_ms={value_2:.2f} cache_hits={value_3}",
            value_0=stats_payload.get("command_duration_ms", 0),
            value_1=stats_payload.get("http_request_count", 0),
            value_2=stats_payload.get("api_wait_ms", 0),
            value_3=cache_hits,
        ),
        err=True,
    )


def _cli_command_from_canonical(canonical_name: str) -> str:
    return "kaiten " + canonical_name.replace(".", " ")


def _cli_option_name(argument_name: str) -> str:
    return "--" + argument_name.replace("_", "-")


def _yes_no(value: Any) -> str:
    return tr("yes") if bool(value) else tr("no")


def _format_enum(values: Any) -> str:
    if not values:
        return ""
    return " enum=" + "|".join(str(value) for value in values)


def _format_short_help(text: str) -> str:
    first_line = text.strip().splitlines()[0] if text.strip() else "Kaiten command group."
    first_sentence = first_line.split(". ")[0].rstrip(".")
    return first_sentence + "."


def _build_namespace_help() -> dict[tuple[str, ...], tuple[str, str]]:
    buckets: dict[tuple[str, ...], dict[str, Any]] = defaultdict(
        lambda: {"modules": set(), "children": set(), "total": 0}
    )
    for module_key, tools in iter_module_tools():
        for tool in tools:
            namespace_segments = tool.namespace_segments
            for index in range(1, len(namespace_segments) + 1):
                path = namespace_segments[:index]
                buckets[path]["modules"].add(module_key)
                buckets[path]["total"] += 1
                if index == len(namespace_segments):
                    buckets[path]["children"].add(tool.action)
                else:
                    buckets[path]["children"].add(namespace_segments[index])

    help_by_path: dict[tuple[str, ...], tuple[str, str]] = {}
    for path, bucket in buckets.items():
        modules = sorted(bucket["modules"])
        specs = [MODULE_SPECS_BY_KEY[module] for module in modules if module in MODULE_SPECS_BY_KEY]
        if len(specs) == 1:
            summary = tr(specs[0].description)
        elif specs:
            labels = ", ".join(tr(spec.label) for spec in specs)
            summary = tr("Commands from these Kaiten areas: {labels}.", labels=labels)
        else:
            summary = tr("Kaiten command group for {path}.", path=".".join(path))

        children = sorted(bucket["children"])
        child_sample = ", ".join(children[:8])
        if len(children) > 8:
            child_sample += tr(", and {count} more", count=len(children) - 8)
        detail = (
            summary
            + "\n\n"
            + tr(
                "Contains {count} commands under: {children}.",
                count=bucket["total"],
                children=child_sample,
            )
        )
        help_by_path[path] = (detail, _format_short_help(summary))
    return help_by_path


@lru_cache(maxsize=2)
def _namespace_help(locale: str):
    with use_locale(locale):
        return _build_namespace_help()


NAMESPACE_HELP = _namespace_help("en")


def _render_search_tools_text(query: str, results: list[dict[str, Any]]) -> str:
    lines = [tr("Search results for: {value_0}", value_0=query), ""]
    if not results:
        lines.extend(
            [
                tr("No matching commands found."),
                "",
                tr("Try a broader query or inspect the full command list with: kaiten --help"),
            ]
        )
        return "\n".join(lines)

    for index, item in enumerate(results, start=1):
        canonical_name = item["canonical_name"]
        flags = [
            str(item.get("method", "GET")),
            tr("mutation") if item.get("mutation") else tr("read"),
            "read-only=allowed" if item.get("read_only_allowed") else "read-only=blocked",
            "remote-effects=yes" if item.get("remote_side_effects") else "remote-effects=no",
            str(item.get("execution_mode", "direct_http")),
            f"cache={item.get('cache_policy', 'unknown')}",
        ]
        if item.get("heavy"):
            flags.append(tr("heavy"))

        lines.append(tr("{value_0}. {value_1}", value_0=index, value_1=canonical_name))
        lines.append(tr("   CLI: {value_0}", value_0=_cli_command_from_canonical(canonical_name)))
        lines.append(tr("   {value_0}", value_0=item.get("description", "").strip()))
        lines.append(tr("   {value_0}", value_0=" | ".join(flags)))
        if item.get("bulk_alternative"):
            lines.append(tr("   Bulk alternative: {value_0}", value_0=item["bulk_alternative"]))
        notes = item.get("usage_notes") or []
        if notes:
            lines.append(tr("   Note: {value_0}", value_0=notes[0]))
        lines.append(
            tr(
                "   Next: kaiten describe {value_0}; kaiten examples {value_1}",
                value_0=canonical_name,
                value_1=canonical_name,
            )
        )
        lines.append("")

    lines.append(tr("Use --json before the command for machine-readable output."))
    return "\n".join(lines).rstrip()


def _render_describe_text(description: dict[str, Any]) -> str:
    canonical_name = description["canonical_name"]
    lines = [
        canonical_name,
        "",
        tr("Description: {value_0}", value_0=description.get("description", "")),
        tr("CLI: {value_0}", value_0=_cli_command_from_canonical(canonical_name)),
        tr("MCP alias: {value_0}", value_0=description.get("mcp_alias", "")),
        (
            tr(
                "API: {value_0} {value_1} | mutation={value_2} | read-only={value_3} | remote-effects={value_4} | mode={value_5}",
                value_0=description.get("method", ""),
                value_1=description.get("path_template", ""),
                value_2=_yes_no(description.get("mutation")),
                value_3=tr("allowed") if description.get("read_only_allowed") else tr("blocked"),
                value_4=_yes_no(description.get("remote_side_effects")),
                value_5=description.get("execution_mode", ""),
            )
        ),
        (
            tr(
                "Cache: {value_0} ({value_1})",
                value_0=description.get("cache_policy", ""),
                value_1=description.get("cache_guidance", {}).get("strategy", "unknown"),
            )
        ),
        (
            tr("Cache modes: ")
            + ", ".join(description.get("cache_guidance", {}).get("available_modes", []))
            + tr(" | default=")
            + str(description.get("cache_guidance", {}).get("default_mode", "auto"))
            + tr(" | recommended=")
            + str(description.get("cache_guidance", {}).get("recommended_mode", "auto"))
        ),
    ]

    response_policy = description.get("response_policy", {})
    lines.append(
        tr(
            "Response: kind={value_0} | compact={value_1} | fields={value_2} | heavy={value_3}",
            value_0=response_policy.get("result_kind", "unknown"),
            value_1=_yes_no(response_policy.get("compact_supported")),
            value_2=_yes_no(response_policy.get("fields_supported")),
            value_3=_yes_no(response_policy.get("heavy")),
        )
    )

    if description.get("bulk_alternative"):
        lines.append(tr("Bulk alternative: {value_0}", value_0=description["bulk_alternative"]))
    if live_contract := description.get("live_contract"):
        statuses = ", ".join(str(status) for status in live_contract.get("expected_statuses", []))
        lines.append(
            tr(
                "Live contract: {value_0} ({value_1})",
                value_0=live_contract.get("status"),
                value_1=statuses or tr("no statuses"),
            )
        )
        lines.append(tr("Live note: {value_0}", value_0=live_contract.get("note")))

    arguments = description.get("arguments") or []
    lines.extend(["", tr("Arguments:")])
    if arguments:
        for argument in arguments:
            required = tr("required") if argument.get("required") else tr("optional")
            type_display = argument.get("type_display") or argument.get("type") or "unknown"
            option_name = _cli_option_name(str(argument.get("name")))
            enum_display = _format_enum(argument.get("enum"))
            minimum = argument.get("minimum")
            maximum = argument.get("maximum")
            if minimum is not None and maximum is not None:
                bounds_display = tr(
                    ", range={value_0}..{value_1}", value_0=minimum, value_1=maximum
                )
            elif minimum is not None:
                bounds_display = tr(", minimum={value_0}", value_0=minimum)
            elif maximum is not None:
                bounds_display = tr(", maximum={value_0}", value_0=maximum)
            else:
                bounds_display = ""
            arg_description = argument.get("description") or tr("No description.")
            lines.append(
                tr(
                    "  {value_0} ({value_1}, {value_2}{value_3}{value_4}): {value_5}",
                    value_0=option_name,
                    value_1=type_display,
                    value_2=required,
                    value_3=enum_display,
                    value_4=bounds_display,
                    value_5=arg_description,
                )
            )
    else:
        lines.append(tr("  No tool-specific arguments."))

    from kaiten_cli.schema_docs import schema_rows

    nested = [
        (path, definition, required)
        for path, definition, required in schema_rows(description.get("input_schema", {}))
        if "." in path or "<" in path or "[]" in path
    ]
    if nested:
        lines.extend(["", tr("Nested schemas (unknown extension fields are preserved):")])
        for path, definition, required in nested:
            kinds = definition.get("type", "any")
            kinds = "|".join(kinds) if isinstance(kinds, list) else kinds
            enum = _format_enum(definition.get("enum"))
            limits = ", ".join(
                f"{key}={definition[key]}"
                for key in ("minItems", "maxItems", "minLength", "maxLength")
                if key in definition
            )
            lines.append(
                tr(
                    "  {value_0} ({value_1}, {value_2}{value_3}{value_4}): {value_5}",
                    value_0=path,
                    value_1=kinds,
                    value_2=tr("required") if required else tr("optional"),
                    value_3=enum,
                    value_4=", " + limits if limits else "",
                    value_5=definition.get("description", ""),
                )
            )

    examples = description.get("examples") or []
    if examples:
        lines.extend(["", tr("Examples:")])
        for example in examples:
            lines.append(tr("  {value_0}", value_0=example))

    notes = description.get("usage_notes") or []
    cache_guidance = description.get("cache_guidance") or {}
    rendered_notes = [
        cache_guidance.get("guidance"),
        cache_guidance.get("refresh_hint"),
        cache_guidance.get("off_hint"),
        cache_guidance.get("readwrite_hint"),
        *notes,
    ]
    rendered_notes = [note for note in rendered_notes if note]
    if rendered_notes:
        lines.extend(["", tr("Notes:")])
        for note in rendered_notes:
            lines.append(tr("  - {value_0}", value_0=note))

    lines.extend(
        [
            "",
            tr("Next: kaiten examples {value_0}", value_0=canonical_name),
            tr("Use --json before the command for machine-readable output."),
        ]
    )
    return "\n".join(lines)


def _render_examples_text(identifier: str, examples: list[str]) -> str:
    lines = [tr("Examples for: {value_0}", value_0=identifier), ""]
    if not examples:
        lines.append(tr("No examples registered for this command."))
    else:
        for index, example in enumerate(examples, start=1):
            lines.append(tr("{value_0}. {value_1}", value_0=index, value_1=example))
    lines.extend(["", tr("Next: kaiten describe {value_0}", value_0=identifier)])
    return "\n".join(lines)


def _agent_help_payload() -> dict[str, Any]:
    return {
        "summary": tr("Kaiten API CLI optimized for humans and agents."),
        "llm_bootstrap": [
            tr(
                "Use --locale ru or --locale en before every command to match the current conversation language; explicit --locale overrides KAITEN_CLI_LOCALE. Other languages use en."
            ),
            tr('Discover once per unfamiliar family: kaiten search-tools "wip cards"'),
            tr("Inspect one tool: kaiten describe cards.list-all"),
            tr("Check examples: kaiten examples cards.list-all"),
            tr("For repeated analytics or report runs, build a local snapshot first."),
            tr(
                "Use query cards --view summary by default; switch to detail/evidence only for narrowed candidates."
            ),
            tr("Use --json for automation and LLM workflows."),
            tr(
                "Read top-level JSON stats to understand API calls, wait time, cache hits, and grouped path families."
            ),
            tr(
                "Omit --cache-mode for normal workflows: auto reuses cacheable safe reads and heavy analytics."
            ),
            tr("Use refresh once at a freshness boundary; never put refresh in an entity loop."),
            tr(
                "Use off only for cache diagnostics, privacy requirements, or high-frequency polling."
            ),
            tr("Use readwrite only with a meaningful --cache-ttl-seconds."),
            tr("Use a bulk_alternative for two or more IDs."),
            tr("Shrink payloads with --compact and --fields."),
            tr(
                "Use --trace-file for wrappers with 3+ CLI commands, >10 expected HTTP requests, or an unavoidable loop."
            ),
            tr(
                "Summarize a trace locally with kaiten --json trace summarize --file <trace.jsonl>."
            ),
            tr(
                "Before mutation, run kaiten --json --profile <name> --read-only profile probe and follow the mutation skill."
            ),
            tr(
                "Treat dashboards as experimental and iterations/Restricted Access Files as beta; run discovery first and expect feature/version gates."
            ),
        ],
        "quickstart": [
            tr('Discover commands: kaiten search-tools "wip cards"'),
            tr("Inspect one tool: kaiten describe cards.list-all"),
            tr("See examples: kaiten examples cards.list-all"),
            tr(
                "Build a local read snapshot: kaiten snapshot build --name team-basic --space-id 10 --preset basic"
            ),
            tr(
                "Query locally after build: kaiten query cards --snapshot team-basic --view summary --fields id,title,state"
            ),
            tr("Prefer machine-safe output: kaiten --json spaces list --compact --fields id,title"),
            tr(
                "Configure credentials: kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active"
            ),
            tr(
                "Probe authentication safely: kaiten --json --profile main --read-only profile probe"
            ),
            tr("Summarize a trace locally: kaiten --json trace summarize --file <trace.jsonl>"),
            tr(
                "Explore dashboards safely: kaiten --json dashboards list --fields id,title,is_public,role --compact"
            ),
            tr(
                "Explore iterations safely: kaiten --json iterations list --space-uid <space_uuid> --status planned,active --compact"
            ),
        ],
        "principles": [
            tr("Use --json for automation and LLM workflows."),
            tr("Read top-level JSON stats before repeating or widening expensive workflows."),
            tr("Omit --cache-mode for normal workflows: auto is the recommended default."),
            tr(
                "Use refresh once before a freshness-critical result or use snapshot refresh; never put refresh in a loop."
            ),
            tr(
                "Use off only for cache diagnostics, privacy requirements, or high-frequency polling."
            ),
            tr("Use readwrite only with a meaningful fixed --cache-ttl-seconds."),
            tr(
                "Run search-tools -> describe -> examples once per unfamiliar command family, mutation, or heavy command."
            ),
            tr(
                "For a population used more than once, snapshot once and query locally before touching the API again."
            ),
            tr(
                "For two or more IDs, use bulk_alternative when available instead of a per-entity loop."
            ),
            tr(
                "Prefer bulk tools like cards.list-all, cards.batch-get, time-logs.batch-list, space-activity-all.get, card-children.batch-list, comments.batch-list, and card-location-history.batch-get."
            ),
            tr(
                "Keep query cards summary-first; use detail/evidence only after local candidate reduction."
            ),
            tr("Live validation runs only when KAITEN_LIVE=1|true for the current process."),
            tr("Use --compact and --fields to reduce payload and token cost."),
            tr(
                "Use --trace-file for wrappers with 3+ CLI commands, >10 expected HTTP requests, or an unavoidable loop."
            ),
            tr("Inspect trace cost with kaiten --json trace summarize --file <trace.jsonl>."),
            tr(
                "Before mutations: profile probe, read-only investigation, exact preview, authorization, resumable manifest, small batches, and field-scoped readback."
            ),
            tr(
                "Dashboards are experimental; iterations and Restricted Access Files are beta and may be unavailable on older installations or tariffs."
            ),
        ],
        "docs": {
            "repository": REPOSITORY_URL,
            "readme": README_URL,
            "command_reference": COMMAND_REFERENCE_URL,
            "architecture": ARCHITECTURE_URL,
            "agent_guide": AGENTS_URL,
            "skills": {
                "heavy_data": HEAVY_DATA_SKILL_URL,
                "metrics": METRICS_SKILL_URL,
                "mutations": MUTATIONS_SKILL_URL,
            },
        },
    }


def _agent_help_text() -> str:
    return "\n".join(
        [
            tr("Kaiten agent bootstrap"),
            "",
            tr("LLM bootstrap:"),
            tr(
                "Use --locale ru or --locale en before every command to match the current conversation language; explicit --locale overrides KAITEN_CLI_LOCALE. Other languages use en."
            ),
            tr('1. discover: kaiten search-tools "wip cards"'),
            tr("2. inspect: kaiten describe cards.list-all"),
            tr("3. examples: kaiten examples cards.list-all"),
            tr("4. use --json for automation and LLM workflows"),
            tr(
                "5. inspect JSON stats for API count, wait time, cache hits, and grouped path families"
            ),
            tr("6. omit --cache-mode for normal workflows: auto is the recommended default"),
            tr(
                "7. use refresh once at a freshness boundary, off for diagnostics/privacy/polling, and readwrite only with --cache-ttl-seconds"
            ),
            tr("8. use a bulk alternative for 2+ IDs; never put refresh in an entity loop"),
            tr("9. snapshot a population before its second use"),
            tr(
                "10. snapshot once: kaiten snapshot build --name team-basic --space-id 10 --preset basic"
            ),
            tr(
                "11. query locally: kaiten query cards --snapshot team-basic --view summary --fields id,title,state"
            ),
            tr("12. only escalate to --view detail or --view evidence after local narrowing"),
            tr("13. shrink payloads with --compact and --fields"),
            tr("14. trace wrappers with 3+ CLI commands, >10 expected HTTP requests, or a loop"),
            tr("15. summarize: kaiten --json trace summarize --file <trace.jsonl>"),
            tr("16. before mutations: kaiten --json --profile <name> --read-only profile probe"),
            tr("17. live validation only runs when KAITEN_LIVE=1|true"),
            tr(
                "18. dashboards are experimental; iterations/Restricted Access Files are beta, so discover and probe before use"
            ),
            "",
            tr("Good bulk defaults:"),
            "  kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title,state --compact",
            "  kaiten --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description",
            "  kaiten --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date",
            "  kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title",
            "  kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text",
            "  kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2 --fields changed,column_id",
            "  kaiten --json snapshot build --name team-basic --space-id 10 --preset basic",
            "  kaiten --json query metrics --snapshot team-basic --metric count --group-by board_id",
            "  kaiten --json dashboards list --fields id,title,is_public,role --compact",
            "  kaiten --json iterations list --space-uid <space_uuid> --status planned,active --compact",
            "",
            tr("Docs:"),
            tr("  repo: {value_0}", value_0=REPOSITORY_URL),
            tr("  readme: {value_0}", value_0=README_URL),
            tr("  command reference: {value_0}", value_0=COMMAND_REFERENCE_URL),
            tr("  architecture: {value_0}", value_0=ARCHITECTURE_URL),
            tr("  agents: {value_0}", value_0=AGENTS_URL),
            tr("  skills heavy-data: {value_0}", value_0=HEAVY_DATA_SKILL_URL),
            tr("  skills metrics: {value_0}", value_0=METRICS_SKILL_URL),
            tr("  skills mutations: {value_0}", value_0=MUTATIONS_SKILL_URL),
        ]
    )


def _run_traced(ctx: click.Context, command: str, execution_mode: str, callback):
    recorder = _trace_recorder(ctx)
    start = time.perf_counter()
    try:
        result, stats = callback()
        duration_ms = (time.perf_counter() - start) * 1000.0
        stats_payload = _stats_payload(stats, duration_ms=duration_ms)
        ctx.meta["last_stats_payload"] = stats_payload
        _emit_stats_summary(ctx, stats_payload)
        if recorder is not None:
            _write_trace_safely(
                recorder,
                canonical_name=command,
                execution_mode=execution_mode,
                argv=_current_argv(ctx),
                exit_code=0,
                duration_ms=duration_ms,
                stats=stats,
                bulk_meta=_trace_bulk_meta(result),
            )
        return result
    except CliError as error:
        duration_ms = (time.perf_counter() - start) * 1000.0
        stats = getattr(error, "_kaiten_trace_stats", None)
        ctx.meta["last_stats_payload"] = _stats_payload(stats, duration_ms=duration_ms)
        if recorder is not None:
            _write_trace_safely(
                recorder,
                canonical_name=command,
                execution_mode=execution_mode,
                argv=_current_argv(ctx),
                exit_code=error.exit_code,
                duration_ms=duration_ms,
                stats=stats,
                bulk_meta=_trace_bulk_meta(error),
            )
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000.0
        stats = getattr(exc, "_kaiten_trace_stats", None)
        ctx.meta["last_stats_payload"] = _stats_payload(stats, duration_ms=duration_ms)
        if recorder is not None:
            _write_trace_safely(
                recorder,
                canonical_name=command,
                execution_mode=execution_mode,
                argv=_current_argv(ctx),
                exit_code=70,
                duration_ms=duration_ms,
                stats=stats,
                bulk_meta={},
            )
        raise


def _write_trace_safely(recorder: TraceRecorder, **kwargs: Any) -> None:
    """Keep observability failures from changing the primary command outcome."""

    try:
        recorder.write(**kwargs)
    except Exception as error:
        click.echo(
            tr("Warning: trace record was not written ({value_0}).", value_0=type(error).__name__),
            err=True,
        )


def _dynamic_callback(tool: ToolSpec):
    @click.pass_context
    def callback(ctx: click.Context, **kwargs: Any) -> None:
        options = _ctx_options(ctx)
        stdin_text = click.get_text_stream("stdin").read() if options.stdin_json else None
        reporter = _make_debug_reporter(ctx)
        try:
            result = _run_traced(
                ctx,
                tool.canonical_name,
                tool.execution_mode,
                lambda: execute_tool_sync_with_diagnostics(
                    tool,
                    merge_inputs(
                        tool,
                        kwargs,
                        from_file=options.from_file,
                        stdin_json=options.stdin_json,
                        stdin_text=stdin_text,
                    ),
                    profile_name=options.profile_name,
                    cache_mode=options.cache_mode,
                    cache_ttl_seconds=options.cache_ttl_seconds,
                    reporter=reporter,
                    read_only=options.read_only,
                ),
            )
            _echo_result(ctx, tool.canonical_name, result)
        except CliError as error:
            _fail(ctx, tool.canonical_name, error)
        except Exception as exc:  # pragma: no cover - safety net
            _emit_internal(ctx, tool.canonical_name, exc)

    return callback


def _click_type_for(schema: dict[str, Any]) -> click.ParamType | None:
    schema_type = schema.get("type")
    allowed = schema_type if isinstance(schema_type, list) else [schema_type]
    if len(allowed) > 1:
        return click.STRING
    if "integer" in allowed and "string" not in allowed:
        return click.IntRange(min=schema.get("minimum"), max=schema.get("maximum"))
    if "number" in allowed:
        return click.FloatRange(min=schema.get("minimum"), max=schema.get("maximum"))
    if "boolean" in allowed:
        return None
    return click.STRING


def _command_params(tool: ToolSpec) -> list[click.Parameter]:
    params: list[click.Parameter] = []
    for field_name, schema in tool.input_schema.get("properties", {}).items():
        option_name = f"--{field_name.replace('_', '-')}"
        description = schema.get("description", "")
        allowed = schema.get("type")
        allowed_types = allowed if isinstance(allowed, list) else [allowed]
        if "boolean" in allowed_types and schema.get("enum") is None:
            params.append(
                click.Option(
                    [f"{option_name}/--no-{field_name.replace('_', '-')}", field_name],
                    default=None,
                    help=description,
                )
            )
            continue
        option = click.Option(
            [option_name, field_name],
            type=_click_type_for(schema),
            default=None,
            required=False,
            help=description,
        )
        params.append(option)
    return params


def _make_command(tool: ToolSpec, *, hidden: bool = False) -> click.Command:
    return LocalizedCommand(
        name=tool.action if not hidden else tool.mcp_alias,
        help=tool.description,
        short_help=tool.description,
        context_settings=CLICK_CONTEXT_SETTINGS,
        params=_command_params(tool),
        callback=_dynamic_callback(tool),
        hidden=hidden,
    )


def _ensure_group(root: click.Group, segments: tuple[str, ...]) -> click.Group:
    group = root
    current_path: tuple[str, ...] = ()
    for segment in segments:
        current_path = current_path + (segment,)
        existing = group.commands.get(segment)
        if existing is None:
            group_help, short_help = NAMESPACE_HELP.get(
                current_path,
                (
                    f"Kaiten command group for {'.'.join(current_path)}.",
                    f"Kaiten command group for {'.'.join(current_path)}.",
                ),
            )
            nested = LocalizedGroup(
                name=segment,
                no_args_is_help=True,
                help=group_help,
                short_help=short_help,
                context_settings=CLICK_CONTEXT_SETTINGS,
            )
            nested.help_factory = lambda path=current_path: _namespace_help(get_locale())[path][0]
            group.add_command(nested)
            group = nested
            continue
        if not isinstance(existing, click.Group):  # pragma: no cover - defensive
            raise RuntimeError(f"Command path collision at {segment}")
        group = existing
    return group


@click.group(
    cls=LocalizedGroup,
    context_settings=CLICK_CONTEXT_SETTINGS,
    no_args_is_help=True,
    help=CLI_HELP,
    epilog=CLI_EPILOG,
)
@click.option(
    "--locale", type=click.Choice(["en", "ru"]), help="Language for CLI messages (default: en)."
)
@click.version_option(version=__version__, prog_name="kaiten")
@click.option(
    "--json", "json_mode", is_flag=True, default=False, help="Emit machine-readable JSON output."
)
@click.option(
    "--profile",
    "profile_name",
    type=click.STRING,
    default=None,
    help="Configuration profile to use.",
)
@click.option(
    "--from-file",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default=None,
    help="Load the full JSON payload from a file.",
)
@click.option(
    "--stdin-json", is_flag=True, default=False, help="Read the full JSON payload from stdin."
)
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose diagnostics.")
@click.option(
    "--cache-mode",
    type=click.Choice(["auto", "off", "readwrite", "refresh"]),
    default=None,
    help="Persistent cache mode. Default auto adapts TTL by tool cost; request-scoped cache stays enabled for safe GETs.",
)
@click.option(
    "--cache-ttl-seconds",
    type=click.INT,
    default=None,
    help="TTL for persistent cache entries in seconds.",
)
@click.option(
    "--trace-file",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Append compact execution traces as JSONL.",
)
@click.option(
    "--read-only",
    is_flag=True,
    default=False,
    help="Block commands that mutate Kaiten; KAITEN_CLI_READ_ONLY=1 enables the same policy.",
)
@click.option(
    "--no-update-check",
    is_flag=True,
    default=False,
    help="Skip the post-command check for a newer kaiten-cli release.",
)
@click.option("--no-color", is_flag=True, default=False, help="Disable colorized output.")
@click.pass_context
def cli(
    ctx: click.Context,
    locale: str | None,
    json_mode: bool,
    profile_name: str | None,
    from_file: str | None,
    stdin_json: bool,
    verbose: bool,
    cache_mode: str | None,
    cache_ttl_seconds: int | None,
    trace_file: str | None,
    read_only: bool,
    no_update_check: bool,
    no_color: bool,
) -> None:
    if no_color:
        ctx.color = False
    ctx.meta["argv"] = list(_ARGV.get() or sys.argv[1:])
    ctx.obj = GlobalOptions(
        locale=get_locale(),
        json_mode=json_mode,
        profile_name=profile_name,
        from_file=from_file,
        stdin_json=stdin_json,
        verbose=verbose,
        no_color=no_color,
        cache_mode=cache_mode,
        cache_ttl_seconds=cache_ttl_seconds,
        trace_file=trace_file or os.environ.get("KAITEN_TRACE_FILE"),
        read_only=read_only or read_only_enabled(),
        update_check=not no_update_check,
    )


@cli.command(
    "search-tools",
    help="Search the command registry and show ranked commands with usage guidance.",
    short_help="Search commands with usage guidance.",
)
@click.argument("query", type=click.STRING, metavar="QUERY")
@click.pass_context
def search_tools_command(ctx: click.Context, query: str) -> None:
    try:
        result = _run_traced(ctx, "search-tools", "meta", lambda: (search_tools(query), None))
        if _ctx_options(ctx).json_mode:
            _echo_result(ctx, "search-tools", result)
        else:
            _echo_human_result(ctx, _render_search_tools_text(query, result))
    except CliError as error:
        _fail(ctx, "search-tools", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "search-tools", exc)


@cli.command(
    "describe",
    help="Describe one command: API path, arguments, cache behavior, examples and notes.",
    short_help="Describe one command.",
)
@click.argument("identifier", type=click.STRING, metavar="IDENTIFIER")
@click.pass_context
def describe_command(ctx: click.Context, identifier: str) -> None:
    try:
        result = _run_traced(ctx, "describe", "meta", lambda: (describe_tool(identifier), None))
        if _ctx_options(ctx).json_mode:
            _echo_result(ctx, "describe", result)
        else:
            _echo_human_result(ctx, _render_describe_text(result))
    except KeyError:
        _fail(ctx, "describe", ConfigError(tr("Unknown command: {value_0}", value_0=identifier)))
    except CliError as error:
        _fail(ctx, "describe", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "describe", exc)


@cli.command(
    "examples",
    help="Show runnable examples for one command.",
    short_help="Show command examples.",
)
@click.argument("identifier", type=click.STRING, metavar="IDENTIFIER")
@click.pass_context
def examples_command(ctx: click.Context, identifier: str) -> None:
    try:
        result = _run_traced(
            ctx, "examples", "meta", lambda: ({"examples": tool_examples(identifier)}, None)
        )
        if _ctx_options(ctx).json_mode:
            _echo_result(ctx, "examples", result)
        else:
            _echo_human_result(ctx, _render_examples_text(identifier, result["examples"]))
    except KeyError:
        _fail(ctx, "examples", ConfigError(tr("Unknown command: {value_0}", value_0=identifier)))
    except CliError as error:
        _fail(ctx, "examples", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "examples", exc)


@cli.command(
    "agent-help",
    help="Show an agent-oriented bootstrap with discovery, bulk-read and snapshot guidance.",
    short_help="Show agent-oriented bootstrap guidance.",
)
@click.pass_context
def agent_help_command(ctx: click.Context) -> None:
    try:
        result = _run_traced(ctx, "agent-help", "meta", lambda: (_agent_help_payload(), None))
        options = _ctx_options(ctx)
        if options.json_mode:
            _echo_result(ctx, "agent-help", result)
        else:
            click.echo(_agent_help_text())
    except CliError as error:
        _fail(ctx, "agent-help", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "agent-help", exc)


@cli.group(
    "trace",
    no_args_is_help=True,
    help="Inspect compact local execution traces without calling Kaiten.",
    short_help="Inspect local execution traces.",
    context_settings=CLICK_CONTEXT_SETTINGS,
)
def trace_group() -> None:
    """Inspect local traces."""


@trace_group.command(
    "summarize",
    help="Stream a JSONL trace and report aggregate cost and workflow recommendations.",
    short_help="Summarize a local JSONL trace.",
)
@click.option(
    "--file",
    "trace_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Trace JSONL file created with --trace-file.",
)
@click.pass_context
def trace_summarize_command(ctx: click.Context, trace_path: str) -> None:
    try:
        _echo_result(ctx, "trace.summarize", summarize_trace(trace_path))
    except CliError as error:
        _fail(ctx, "trace.summarize", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "trace.summarize", exc)


@cli.group(
    "completion",
    no_args_is_help=True,
    help="Install, inspect, generate or remove shell completion for Kaiten CLI.",
    short_help="Manage Bash and Zsh completion.",
    context_settings=CLICK_CONTEXT_SETTINGS,
)
def completion_group() -> None:
    """Manage shell completion."""


def _completion_config_option(function):
    return click.option(
        "--config",
        "config_path",
        type=click.Path(dir_okay=False, path_type=Path),
        default=None,
        help="Override the shell startup file to update or inspect.",
    )(function)


def _completion_shell_option(function):
    return click.option(
        "--shell",
        type=click.Choice(SUPPORTED_SHELLS),
        default=None,
        help="Target shell. Defaults to the basename of SHELL.",
    )(function)


@completion_group.command(
    "install",
    help="Generate a static completion script and register it in the shell startup file.",
    short_help="Install shell completion safely.",
)
@_completion_shell_option
@_completion_config_option
@click.option("--dry-run", is_flag=True, help="Show intended changes without writing files.")
@click.pass_context
def completion_install_command(
    ctx: click.Context,
    shell: str | None,
    config_path: Path | None,
    dry_run: bool,
) -> None:
    try:
        result = install_completion(
            ctx.find_root().command,
            shell=shell,
            config_path=config_path,
            dry_run=dry_run,
        )
        _echo_completion_result(ctx, "completion.install", "installed", result)
    except CliError as error:
        _fail(ctx, "completion.install", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "completion.install", exc)


@completion_group.command(
    "status",
    help="Inspect whether the current completion script and shell registration are ready.",
    short_help="Check shell completion status.",
)
@_completion_shell_option
@_completion_config_option
@click.pass_context
def completion_status_command(
    ctx: click.Context,
    shell: str | None,
    config_path: Path | None,
) -> None:
    try:
        result = completion_status(
            ctx.find_root().command,
            shell=shell,
            config_path=config_path,
        )
        _echo_completion_result(ctx, "completion.status", "status", result)
    except CliError as error:
        _fail(ctx, "completion.status", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "completion.status", exc)


@completion_group.command(
    "source",
    help="Print the Click completion source script without modifying shell files.",
    short_help="Print a completion script.",
)
@click.argument("shell", type=click.Choice(SUPPORTED_SHELLS), metavar="SHELL")
@click.pass_context
def completion_source_command(ctx: click.Context, shell: str) -> None:
    try:
        result = generate_completion_source(ctx.find_root().command, shell)
        if _ctx_options(ctx).json_mode:
            _echo_result(ctx, "completion.source", {"shell": shell, "source": result})
        else:
            _discard_result_stats(ctx)
            click.echo(result, nl=False)
    except CliError as error:
        _fail(ctx, "completion.source", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "completion.source", exc)


@completion_group.command(
    "uninstall",
    help="Remove only the managed shell registration and generated completion script.",
    short_help="Uninstall managed shell completion.",
)
@_completion_shell_option
@_completion_config_option
@click.option("--dry-run", is_flag=True, help="Show intended changes without writing files.")
@click.pass_context
def completion_uninstall_command(
    ctx: click.Context,
    shell: str | None,
    config_path: Path | None,
    dry_run: bool,
) -> None:
    try:
        result = uninstall_completion(
            ctx.find_root().command,
            shell=shell,
            config_path=config_path,
            dry_run=dry_run,
        )
        _echo_completion_result(ctx, "completion.uninstall", "uninstalled", result)
    except CliError as error:
        _fail(ctx, "completion.uninstall", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "completion.uninstall", exc)


@cli.group(
    "profile",
    no_args_is_help=True,
    help="Manage named Kaiten credential profiles and per-profile cache defaults.",
    short_help="Manage Kaiten profiles.",
    context_settings=CLICK_CONTEXT_SETTINGS,
)
def profile_group() -> None:
    """Manage profiles."""


@profile_group.command(
    "add",
    help="Create or update a named profile with Kaiten domain, API token and cache defaults.",
    short_help="Create or update a profile.",
)
@click.argument("name", type=click.STRING, metavar="NAME")
@click.option(
    "--domain",
    required=True,
    type=click.STRING,
    help="Kaiten tenant subdomain or full base URL, for example acme or https://acme.kaiten.ru.",
)
@click.option(
    "--token", required=True, type=click.STRING, help="Kaiten API token for this profile."
)
@click.option(
    "--sandbox/--no-sandbox",
    default=False,
    help="Deprecated compatibility metadata. Does not affect mutations or live-test gating.",
)
@click.option(
    "--cache-mode",
    type=click.Choice(["auto", "off", "readwrite", "refresh"]),
    default=None,
    help="Default persistent cache mode to store with this profile.",
)
@click.option(
    "--cache-ttl-seconds",
    type=click.INT,
    default=None,
    help="Default persistent cache TTL in seconds for this profile.",
)
@click.option(
    "--set-active/--no-set-active",
    default=False,
    help="Make this profile the active default immediately after saving it.",
)
@click.pass_context
def profile_add_command(
    ctx: click.Context,
    name: str,
    domain: str,
    token: str,
    sandbox: bool,
    cache_mode: str | None,
    cache_ttl_seconds: int | None,
    set_active: bool,
) -> None:
    try:
        result = _run_traced(
            ctx,
            "profile.add",
            "meta",
            lambda: (
                add_profile(
                    name,
                    domain=domain,
                    token=token,
                    sandbox=sandbox,
                    cache_mode=cache_mode,
                    cache_ttl_seconds=cache_ttl_seconds,
                    set_active=set_active,
                ),
                None,
            ),
        )
        _echo_result(ctx, "profile.add", result)
    except CliError as error:
        _fail(ctx, "profile.add", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.add", exc)


@profile_group.command(
    "use",
    help="Set an existing profile as the active default for future commands.",
    short_help="Set the active profile.",
)
@click.argument("name", type=click.STRING, metavar="NAME")
@click.pass_context
def profile_use_command(ctx: click.Context, name: str) -> None:
    try:
        _echo_result(
            ctx,
            "profile.use",
            _run_traced(ctx, "profile.use", "meta", lambda: (use_profile(name), None)),
        )
    except CliError as error:
        _fail(ctx, "profile.use", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.use", exc)


@profile_group.command(
    "list",
    help="List configured profiles and show which one is active.",
    short_help="List configured profiles.",
)
@click.pass_context
def profile_list_command(ctx: click.Context) -> None:
    try:
        _echo_result(
            ctx,
            "profile.list",
            _run_traced(ctx, "profile.list", "meta", lambda: (list_profiles(), None)),
        )
    except CliError as error:
        _fail(ctx, "profile.list", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.list", exc)


@profile_group.command(
    "show",
    help="Show one profile, or the active profile when NAME is omitted.",
    short_help="Show profile details.",
)
@click.argument("name", required=False, type=click.STRING, metavar="NAME")
@click.pass_context
def profile_show_command(ctx: click.Context, name: str | None) -> None:
    try:
        _echo_result(
            ctx,
            "profile.show",
            _run_traced(ctx, "profile.show", "meta", lambda: (show_profile(name), None)),
        )
    except CliError as error:
        _fail(ctx, "profile.show", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.show", exc)


@profile_group.command(
    "probe",
    help=(
        "Verify the selected profile with a fresh read-only GET /users/current. "
        "This checks authentication, not arbitrary write permissions."
    ),
    short_help="Probe profile authentication safely.",
)
@click.pass_context
def profile_probe_command(ctx: click.Context) -> None:
    options = _ctx_options(ctx)
    try:

        def probe():
            resolved = resolve_profile(
                options.profile_name,
                cache_mode_override=options.cache_mode,
                cache_ttl_seconds_override=options.cache_ttl_seconds,
            )
            tool = resolve_tool("users.current")
            _, stats = execute_tool_sync_with_diagnostics(
                tool,
                {},
                profile_name=options.profile_name,
                cache_mode="off",
                reporter=_make_debug_reporter(ctx),
                read_only=True,
            )
            return (
                {
                    "profile": {
                        "name": resolved.name,
                        "source": resolved.source,
                        "domain_configured": bool(resolved.domain),
                        "cache_mode": resolved.cache_mode,
                        "cache_ttl_seconds": resolved.cache_ttl_seconds,
                    },
                    "authentication": {
                        "ok": True,
                        "probe_cache_mode": "off",
                    },
                    "capability_scope": "authentication_only",
                    "write_permissions": "not_checked",
                },
                stats,
            )

        result = _run_traced(ctx, "profile.probe", "direct_http", probe)
        _echo_result(ctx, "profile.probe", result)
    except CliError as error:
        _fail(ctx, "profile.probe", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.probe", exc)


@profile_group.command(
    "remove",
    help="Remove a saved profile by name.",
    short_help="Remove a profile.",
)
@click.argument("name", type=click.STRING, metavar="NAME")
@click.pass_context
def profile_remove_command(ctx: click.Context, name: str) -> None:
    try:
        _echo_result(
            ctx,
            "profile.remove",
            _run_traced(ctx, "profile.remove", "meta", lambda: (remove_profile(name), None)),
        )
    except CliError as error:
        _fail(ctx, "profile.remove", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.remove", exc)


for tool in iter_tools():
    group = _ensure_group(cli, tool.namespace_segments)
    group.add_command(_make_command(tool))
    cli.add_command(_make_command(tool, hidden=True), name=tool.canonical_name)
    cli.add_command(_make_command(tool, hidden=True), name=tool.mcp_alias)


_ROOT_OPTION_USAGE = {
    "--locale": "--locale <ru|en>",
    "--json": "--json",
    "--profile": "--profile <name>",
    "--from-file": "--from-file <path>",
    "--stdin-json": "--stdin-json",
    "--verbose": "--verbose",
    "--cache-mode": "--cache-mode <auto|off|readwrite|refresh>",
    "--cache-ttl-seconds": "--cache-ttl-seconds <seconds>",
    "--trace-file": "--trace-file <path>",
    "--read-only": "--read-only",
    "--no-update-check": "--no-update-check",
    "--no-color": "--no-color",
}
_SHAPING_OPTIONS = {"--compact", "--fields"}


def _usage_error_command(error: click.UsageError) -> tuple[str | None, ToolSpec | None]:
    context = error.ctx
    if context is None:
        return None, None
    path = context.command_path.split()
    if path and path[0] == "kaiten":
        path = path[1:]
    if not path:
        return None, None
    canonical_name = path[0] if len(path) == 1 and "." in path[0] else ".".join(path)
    try:
        return canonical_name, next(
            tool for tool in iter_tools() if tool.canonical_name == canonical_name
        )
    except StopIteration:
        return canonical_name, None


def _supported_context_options(error: click.UsageError) -> list[str]:
    context = error.ctx
    if context is None:
        return []
    return sorted(
        {
            option
            for parameter in context.command.params
            if isinstance(parameter, click.Option)
            for option in parameter.opts
            if option.startswith("--")
        }
    )


def _suggested_root_options(*, offending_option: str, supported_options: list[str]) -> list[str]:
    suggested: list[str] = []
    seen: set[str] = set()
    for token in _ARGV.get() or []:
        option = token.split("=", 1)[0]
        if option not in _ROOT_OPTION_USAGE or option in seen:
            continue
        if option in supported_options and option != offending_option:
            continue
        seen.add(option)
        suggested.append(_ROOT_OPTION_USAGE[option])
    if not suggested:
        suggested.append(_ROOT_OPTION_USAGE[offending_option])
    return suggested


def _validation_details(error: click.UsageError) -> dict[str, Any] | None:
    if not isinstance(error, click.NoSuchOption):
        return None
    option = error.option_name
    canonical_name, tool = _usage_error_command(error)
    supported_options = _supported_context_options(error)
    command = (
        " ".join(tool.command_segments)
        if tool is not None
        else (canonical_name or "<command>").replace(".", " ")
    )
    if option in _ROOT_OPTION_USAGE:
        root_options = " ".join(
            _suggested_root_options(
                offending_option=option,
                supported_options=supported_options,
            )
        )
        details: dict[str, Any] = {
            "code": "global_option_position",
            "option": option,
            "canonical_name": canonical_name,
            "suggested_usage": (f"kaiten {root_options} {command} [command options]"),
            "supported_options": supported_options,
        }
    else:
        details = {
            "code": (
                "unsupported_shaping_option"
                if option in _SHAPING_OPTIONS
                else "unsupported_tool_option"
            ),
            "option": option,
            "canonical_name": canonical_name,
            "suggested_usage": f"kaiten {command} [supported options]",
            "supported_options": supported_options,
        }
    if tool is not None:
        details["next"] = f"kaiten describe {tool.canonical_name}"
        if tool.bulk_alternative:
            details["bulk_alternative"] = tool.bulk_alternative
    elif canonical_name:
        details["next"] = f"kaiten {command} --help"
    return details


def _main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    json_mode = "--json" in args
    try:
        argv_token = _ARGV.set(list(args))
        click_result = cli.main(args=args, prog_name="kaiten", standalone_mode=False)
        if isinstance(click_result, int) and click_result != 0:
            return click_result
    except NoArgsIsHelpError as error:
        sys.stdout.write(error.format_message() + "\n")
        return 0
    except click.UsageError as error:
        cli_error = ValidationError(
            error.format_message(),
            details=_validation_details(error),
        )
        stream = sys.stdout if json_mode else sys.stderr
        stream.write(render_error(None, cli_error, json_mode) + "\n")
        return cli_error.exit_code
    except CliError as error:
        stream = sys.stdout if json_mode else sys.stderr
        stream.write(render_error(None, error, json_mode) + "\n")
        return error.exit_code
    except click.ClickException as error:
        cli_error = ConfigError(error.format_message())
        stream = sys.stdout if json_mode else sys.stderr
        stream.write(render_error(None, cli_error, json_mode) + "\n")
        return cli_error.exit_code
    finally:
        _ARGV.reset(argv_token)
    try:
        return maybe_offer_update(args)
    except Exception:  # pragma: no cover - update checks must never break the primary command
        return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        locale = resolve_locale(args)
    except click.UsageError as error:
        with use_locale("en"):
            json_mode = "--json" in args
            stream = sys.stdout if json_mode else sys.stderr
            stream.write(
                render_error(None, ValidationError(error.format_message()), json_mode) + "\n"
            )
        return 2
    with use_locale(locale):
        return _main(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
