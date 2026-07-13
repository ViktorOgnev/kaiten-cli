"""CLI entrypoint."""

from __future__ import annotations

import os
import sys
import time
from collections import defaultdict
from typing import Any

import click
from click.exceptions import NoArgsIsHelpError

from kaiten_cli import __version__
from kaiten_cli.discovery import describe_tool, search_tools, tool_examples
from kaiten_cli.errors import (
    BatchExecutionError,
    CliError,
    ConfigError,
    InternalError,
    ValidationError,
)
from kaiten_cli.models import GlobalOptions, ToolSpec
from kaiten_cli.profiles import (
    add_profile,
    list_profiles,
    remove_profile,
    show_profile,
    use_profile,
)
from kaiten_cli.registry import iter_module_tools, iter_tools
from kaiten_cli.registry.module_docs import MODULE_SPECS_BY_KEY
from kaiten_cli.runtime.executor import execute_tool_sync_with_diagnostics, read_only_enabled
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.output import render_error, render_success
from kaiten_cli.runtime.trace import ExecutionStats, TraceRecorder, bulk_trace_meta
from kaiten_cli.update_check import maybe_offer_update


_CURRENT_ARGV: list[str] | None = None
CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
REPOSITORY_URL = "https://github.com/ViktorOgnev/kaiten-cli"
README_URL = f"{REPOSITORY_URL}/blob/master/README.md"
COMMAND_REFERENCE_URL = f"{REPOSITORY_URL}/blob/master/COMMAND_REFERENCE.md"
ARCHITECTURE_URL = f"{REPOSITORY_URL}/blob/master/ARCHITECTURE.md"
AGENTS_URL = f"{REPOSITORY_URL}/blob/master/AGENTS.md"
HEAVY_DATA_SKILL_URL = f"{REPOSITORY_URL}/blob/master/skills/kaiten-cli-heavy-data/SKILL.md"
METRICS_SKILL_URL = f"{REPOSITORY_URL}/blob/master/skills/kaiten-cli-metrics/SKILL.md"
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

\b
Principles:
  - use --json for automation and LLM workflows
  - cache mode defaults to auto: repeated safe GETs may use persistent disk cache
  - prefer search-tools -> describe -> examples before heavy commands
  - for repeated analytics/report reads, prefer snapshot build -> query cards/query metrics
  - keep local queries summary-first; escalate to detail/evidence only after candidate reduction
  - prefer bulk tools over per-entity loops
  - use --compact and --fields to shrink payloads
  - live validation runs only when KAITEN_LIVE=1|true
  - use --trace-file for long investigations and report runs

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


def _fail(ctx: click.Context, command: str | None, error: CliError) -> None:
    options = _ctx_options(ctx)
    stats = ctx.meta.pop("last_stats_payload", None)
    click.echo(
        render_error(command, error, options.json_mode, stats=stats), err=not options.json_mode
    )
    ctx.exit(error.exit_code)


def _emit_internal(ctx: click.Context, command: str | None, exc: Exception) -> None:
    _fail(ctx, command, InternalError(f"{type(exc).__name__}: {exc}"))


def _make_debug_reporter(ctx: click.Context):
    options = _ctx_options(ctx)
    if not options.verbose:
        return None

    def reporter(message: str) -> None:
        click.echo(f"[verbose] {message}", err=True)

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
    return list(_CURRENT_ARGV or sys.argv[1:])


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
        "[verbose] stats: "
        f"duration_ms={stats_payload.get('command_duration_ms', 0):.2f} "
        f"http_requests={stats_payload.get('http_request_count', 0)} "
        f"api_wait_ms={stats_payload.get('api_wait_ms', 0):.2f} "
        f"cache_hits={cache_hits}",
        err=True,
    )


def _cli_command_from_canonical(canonical_name: str) -> str:
    return "kaiten " + canonical_name.replace(".", " ")


def _cli_option_name(argument_name: str) -> str:
    return "--" + argument_name.replace("_", "-")


def _yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


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
            summary = specs[0].description
        elif specs:
            labels = ", ".join(spec.label for spec in specs)
            summary = f"Commands from these Kaiten areas: {labels}."
        else:
            summary = f"Kaiten command group for {'.'.join(path)}."

        children = sorted(bucket["children"])
        child_sample = ", ".join(children[:8])
        if len(children) > 8:
            child_sample += f", and {len(children) - 8} more"
        detail = (
            f"{summary}\n\n"
            f"Contains {bucket['total']} command"
            f"{'' if bucket['total'] == 1 else 's'} under: {child_sample}."
        )
        help_by_path[path] = (detail, _format_short_help(summary))
    return help_by_path


NAMESPACE_HELP = _build_namespace_help()


def _render_search_tools_text(query: str, results: list[dict[str, Any]]) -> str:
    lines = [f"Search results for: {query}", ""]
    if not results:
        lines.extend(
            [
                "No matching commands found.",
                "",
                "Try a broader query or inspect the full command list with: kaiten --help",
            ]
        )
        return "\n".join(lines)

    for index, item in enumerate(results, start=1):
        canonical_name = item["canonical_name"]
        flags = [
            str(item.get("method", "GET")),
            "mutation" if item.get("mutation") else "read",
            "read-only=allowed" if item.get("read_only_allowed") else "read-only=blocked",
            "remote-effects=yes" if item.get("remote_side_effects") else "remote-effects=no",
            str(item.get("execution_mode", "direct_http")),
            f"cache={item.get('cache_policy', 'unknown')}",
        ]
        if item.get("heavy"):
            flags.append("heavy")

        lines.append(f"{index}. {canonical_name}")
        lines.append(f"   CLI: {_cli_command_from_canonical(canonical_name)}")
        lines.append(f"   {item.get('description', '').strip()}")
        lines.append(f"   {' | '.join(flags)}")
        if item.get("bulk_alternative"):
            lines.append(f"   Bulk alternative: {item['bulk_alternative']}")
        notes = item.get("usage_notes") or []
        if notes:
            lines.append(f"   Note: {notes[0]}")
        lines.append(f"   Next: kaiten describe {canonical_name}; kaiten examples {canonical_name}")
        lines.append("")

    lines.append("Use --json before the command for machine-readable output.")
    return "\n".join(lines).rstrip()


def _render_describe_text(description: dict[str, Any]) -> str:
    canonical_name = description["canonical_name"]
    lines = [
        canonical_name,
        "",
        f"Description: {description.get('description', '')}",
        f"CLI: {_cli_command_from_canonical(canonical_name)}",
        f"MCP alias: {description.get('mcp_alias', '')}",
        (
            f"API: {description.get('method', '')} {description.get('path_template', '')} "
            f"| mutation={_yes_no(description.get('mutation'))} "
            f"| read-only={('allowed' if description.get('read_only_allowed') else 'blocked')} "
            f"| remote-effects={_yes_no(description.get('remote_side_effects'))} "
            f"| mode={description.get('execution_mode', '')}"
        ),
        (
            f"Cache: {description.get('cache_policy', '')} "
            f"({description.get('cache_guidance', {}).get('strategy', 'unknown')})"
        ),
    ]

    response_policy = description.get("response_policy", {})
    lines.append(
        "Response: "
        f"kind={response_policy.get('result_kind', 'unknown')} "
        f"| compact={_yes_no(response_policy.get('compact_supported'))} "
        f"| fields={_yes_no(response_policy.get('fields_supported'))} "
        f"| heavy={_yes_no(response_policy.get('heavy'))}"
    )

    if description.get("bulk_alternative"):
        lines.append(f"Bulk alternative: {description['bulk_alternative']}")
    if live_contract := description.get("live_contract"):
        statuses = ", ".join(str(status) for status in live_contract.get("expected_statuses", []))
        lines.append(f"Live contract: {live_contract.get('status')} ({statuses or 'no statuses'})")
        lines.append(f"Live note: {live_contract.get('note')}")

    arguments = description.get("arguments") or []
    lines.extend(["", "Arguments:"])
    if arguments:
        for argument in arguments:
            required = "required" if argument.get("required") else "optional"
            type_display = argument.get("type_display") or argument.get("type") or "unknown"
            option_name = _cli_option_name(str(argument.get("name")))
            enum_display = _format_enum(argument.get("enum"))
            arg_description = argument.get("description") or "No description."
            lines.append(
                f"  {option_name} ({type_display}, {required}{enum_display}): {arg_description}"
            )
    else:
        lines.append("  No tool-specific arguments.")

    examples = description.get("examples") or []
    if examples:
        lines.extend(["", "Examples:"])
        for example in examples:
            lines.append(f"  {example}")

    notes = description.get("usage_notes") or []
    cache_guidance = description.get("cache_guidance") or {}
    rendered_notes = [
        cache_guidance.get("guidance"),
        cache_guidance.get("refresh_hint"),
        *notes,
    ]
    rendered_notes = [note for note in rendered_notes if note]
    if rendered_notes:
        lines.extend(["", "Notes:"])
        for note in rendered_notes:
            lines.append(f"  - {note}")

    lines.extend(
        [
            "",
            f"Next: kaiten examples {canonical_name}",
            "Use --json before the command for machine-readable output.",
        ]
    )
    return "\n".join(lines)


def _render_examples_text(identifier: str, examples: list[str]) -> str:
    lines = [f"Examples for: {identifier}", ""]
    if not examples:
        lines.append("No examples registered for this command.")
    else:
        for index, example in enumerate(examples, start=1):
            lines.append(f"{index}. {example}")
    lines.extend(["", f"Next: kaiten describe {identifier}"])
    return "\n".join(lines)


def _agent_help_payload() -> dict[str, Any]:
    return {
        "summary": "Kaiten API CLI optimized for humans and agents.",
        "llm_bootstrap": [
            'Discover first: kaiten search-tools "wip cards"',
            "Inspect one tool: kaiten describe cards.list-all",
            "Check examples: kaiten examples cards.list-all",
            "For repeated analytics or report runs, build a local snapshot first.",
            "Use query cards --view summary by default; switch to detail/evidence only for narrowed candidates.",
            "Use --json for automation and LLM workflows.",
            "Read top-level JSON stats to understand API calls, wait time, cache hits, and grouped path families.",
            "Default cache mode is auto: repeated safe reads and heavy analytics reuse persistent disk cache when the request shape is cacheable.",
            "Prefer bulk tools over per-entity loops.",
            "Shrink payloads with --compact and --fields.",
            "Use --trace-file for long investigations.",
        ],
        "quickstart": [
            'Discover commands: kaiten search-tools "wip cards"',
            "Inspect one tool: kaiten describe cards.list-all",
            "See examples: kaiten examples cards.list-all",
            "Build a local read snapshot: kaiten snapshot build --name team-basic --space-id 10 --preset basic",
            "Query locally after build: kaiten query cards --snapshot team-basic --view summary --fields id,title,state",
            "Prefer machine-safe output: kaiten --json spaces list --compact --fields id,title",
            "Configure credentials: kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active",
        ],
        "principles": [
            "Use --json for automation and LLM workflows.",
            "Read top-level JSON stats before repeating or widening expensive workflows.",
            "Default cache mode is auto; use --cache-mode refresh for freshness-critical reads and --cache-mode off to bypass disk cache.",
            "Prefer search-tools -> describe -> examples before heavy commands.",
            "For repeated report or analytics workflows, snapshot once and query locally before touching the API again.",
            "Prefer bulk tools like cards.list-all, cards.batch-get, time-logs.batch-list, space-activity-all.get, card-children.batch-list, comments.batch-list, and card-location-history.batch-get over per-entity loops.",
            "Keep query cards summary-first; use detail/evidence only after local candidate reduction.",
            "Live validation runs only when KAITEN_LIVE=1|true for the current process.",
            "Use --compact and --fields to reduce payload and token cost.",
            "Use the default --cache-mode auto for most LLM/script workflows; use readwrite with --cache-ttl-seconds only when you need a fixed TTL.",
            "Use --trace-file for long investigations when you need real HTTP cost visibility.",
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
            },
        },
    }


def _agent_help_text() -> str:
    return "\n".join(
        [
            "Kaiten agent bootstrap",
            "",
            "LLM bootstrap:",
            '1. discover: kaiten search-tools "wip cards"',
            "2. inspect: kaiten describe cards.list-all",
            "3. examples: kaiten examples cards.list-all",
            "4. use --json for automation and LLM workflows",
            "5. inspect JSON stats for API count, wait time, cache hits, and grouped path families",
            "6. leave --cache-mode at auto unless you need refresh/off/fixed TTL",
            "7. snapshot once for repeated analytics: kaiten snapshot build --name team-basic --space-id 10 --preset basic",
            "8. query locally after build: kaiten query cards --snapshot team-basic --view summary --fields id,title,state",
            "9. only escalate to --view detail or --view evidence after local narrowing",
            "10. shrink payloads with --compact and --fields",
            "11. live validation only runs when KAITEN_LIVE=1|true",
            "12. use --trace-file for long investigations",
            "",
            "Good bulk defaults:",
            "  kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title,state --compact",
            "  kaiten --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description",
            "  kaiten --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date",
            "  kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title",
            "  kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text",
            "  kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2 --fields changed,column_id",
            "  kaiten --json snapshot build --name team-basic --space-id 10 --preset basic",
            "  kaiten --json query metrics --snapshot team-basic --metric count --group-by board_id",
            "",
            "Docs:",
            f"  repo: {REPOSITORY_URL}",
            f"  readme: {README_URL}",
            f"  command reference: {COMMAND_REFERENCE_URL}",
            f"  architecture: {ARCHITECTURE_URL}",
            f"  agents: {AGENTS_URL}",
            f"  skills heavy-data: {HEAVY_DATA_SKILL_URL}",
            f"  skills metrics: {METRICS_SKILL_URL}",
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
            f"Warning: trace record was not written ({type(error).__name__}).",
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
        return click.INT
    if "number" in allowed:
        return click.FLOAT
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
                    [f"{option_name}/--no-{field_name.replace('_', '-')}"],
                    default=None,
                    help=description,
                )
            )
            continue
        option = click.Option(
            [option_name],
            type=_click_type_for(schema),
            default=None,
            required=False,
            help=description,
        )
        params.append(option)
    return params


def _make_command(tool: ToolSpec, *, hidden: bool = False) -> click.Command:
    return click.Command(
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
            nested = click.Group(
                name=segment,
                no_args_is_help=True,
                help=group_help,
                short_help=short_help,
                context_settings=CLICK_CONTEXT_SETTINGS,
            )
            group.add_command(nested)
            group = nested
            continue
        if not isinstance(existing, click.Group):  # pragma: no cover - defensive
            raise RuntimeError(f"Command path collision at {segment}")
        group = existing
    return group


@click.group(
    context_settings=CLICK_CONTEXT_SETTINGS,
    no_args_is_help=True,
    help=CLI_HELP,
    epilog=CLI_EPILOG,
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
    ctx.meta["argv"] = list(_CURRENT_ARGV or sys.argv[1:])
    ctx.obj = GlobalOptions(
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
        _fail(ctx, "describe", ConfigError(f"Unknown command: {identifier}"))
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
        _fail(ctx, "examples", ConfigError(f"Unknown command: {identifier}"))
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
    help="Create or update a named profile with credentials, safety and cache defaults.",
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
    "--read-only/--no-read-only",
    default=None,
    help="Persist read-only policy for this profile; mutations remain blocked when it is selected.",
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
    read_only: bool | None,
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
                    read_only=read_only,
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
    cli.add_command(_make_command(tool, hidden=True), name=tool.mcp_alias)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    json_mode = "--json" in args
    try:
        global _CURRENT_ARGV
        _CURRENT_ARGV = list(args)
        click_result = cli.main(args=args, prog_name="kaiten", standalone_mode=False)
        if isinstance(click_result, int) and click_result != 0:
            return click_result
    except NoArgsIsHelpError as error:
        sys.stdout.write(error.format_message() + "\n")
        return 0
    except click.UsageError as error:
        cli_error = ValidationError(error.format_message())
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
        _CURRENT_ARGV = None
    try:
        return maybe_offer_update(args)
    except Exception:  # pragma: no cover - update checks must never break the primary command
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
