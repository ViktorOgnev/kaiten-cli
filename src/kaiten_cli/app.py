"""CLI entrypoint."""

from __future__ import annotations

import os
import sys
import time
from typing import Any

import click
from click.exceptions import NoArgsIsHelpError

from kaiten_cli import __version__
from kaiten_cli.discovery import describe_tool, search_tools, tool_examples
from kaiten_cli.errors import BatchExecutionError, CliError, ConfigError, InternalError, ValidationError
from kaiten_cli.models import GlobalOptions, ToolSpec
from kaiten_cli.profiles import add_profile, list_profiles, remove_profile, show_profile, use_profile
from kaiten_cli.registry import iter_tools
from kaiten_cli.runtime.executor import execute_tool_sync_with_diagnostics
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.output import render_error, render_success
from kaiten_cli.runtime.trace import TraceRecorder, bulk_trace_meta


_CURRENT_ARGV: list[str] | None = None
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
  kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active

\b
Principles:
  - use --json for automation and LLM workflows
  - prefer search-tools -> describe -> examples before heavy commands
  - for repeated analytics/report reads, prefer snapshot build -> query cards/query metrics
  - keep local queries summary-first; escalate to detail/evidence only after candidate reduction
  - prefer bulk tools over per-entity loops
  - use --compact and --fields to shrink payloads
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


def _echo_result(ctx: click.Context, command: str, data: Any) -> None:
    options = _ctx_options(ctx)
    click.echo(render_success(command, data, options.json_mode))


def _fail(ctx: click.Context, command: str | None, error: CliError) -> None:
    options = _ctx_options(ctx)
    click.echo(render_error(command, error, options.json_mode), err=not options.json_mode)
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
            "Configure credentials: kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active",
        ],
        "principles": [
            "Use --json for automation and LLM workflows.",
            "Prefer search-tools -> describe -> examples before heavy commands.",
            "For repeated report or analytics workflows, snapshot once and query locally before touching the API again.",
            "Prefer bulk tools like cards.list-all, cards.batch-get, time-logs.batch-list, space-activity-all.get, card-children.batch-list, comments.batch-list, and card-location-history.batch-get over per-entity loops.",
            "Keep query cards summary-first; use detail/evidence only after local candidate reduction.",
            "Use --compact and --fields to reduce payload and token cost.",
            "Use --cache-mode readwrite only for short-lived cross-process safe GET reuse.",
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
            "5. snapshot once for repeated analytics: kaiten snapshot build --name team-basic --space-id 10 --preset basic",
            "6. query locally after build: kaiten query cards --snapshot team-basic --view summary --fields id,title,state",
            "7. only escalate to --view detail or --view evidence after local narrowing",
            "8. shrink payloads with --compact and --fields",
            "9. use --trace-file for long investigations",
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
        if recorder is not None:
            recorder.write(
                canonical_name=command,
                execution_mode=execution_mode,
                argv=_current_argv(ctx),
                exit_code=0,
                duration_ms=(time.perf_counter() - start) * 1000.0,
                stats=stats,
                bulk_meta=_trace_bulk_meta(result),
            )
        return result
    except CliError as error:
        if recorder is not None:
            recorder.write(
                canonical_name=command,
                execution_mode=execution_mode,
                argv=_current_argv(ctx),
                exit_code=error.exit_code,
                duration_ms=(time.perf_counter() - start) * 1000.0,
                stats=getattr(error, "_kaiten_trace_stats", None),
                bulk_meta=_trace_bulk_meta(error),
            )
        raise
    except Exception as exc:
        if recorder is not None:
            recorder.write(
                canonical_name=command,
                execution_mode=execution_mode,
                argv=_current_argv(ctx),
                exit_code=70,
                duration_ms=(time.perf_counter() - start) * 1000.0,
                stats=getattr(exc, "_kaiten_trace_stats", None),
                bulk_meta={},
            )
        raise


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
        params=_command_params(tool),
        callback=_dynamic_callback(tool),
        hidden=hidden,
    )


def _ensure_group(root: click.Group, segments: tuple[str, ...]) -> click.Group:
    group = root
    for segment in segments:
        existing = group.commands.get(segment)
        if existing is None:
            nested = click.Group(name=segment, no_args_is_help=True)
            group.add_command(nested)
            group = nested
            continue
        if not isinstance(existing, click.Group):  # pragma: no cover - defensive
            raise RuntimeError(f"Command path collision at {segment}")
        group = existing
    return group


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    help=CLI_HELP,
    epilog=CLI_EPILOG,
)
@click.version_option(version=__version__, prog_name="kaiten")
@click.option("--json", "json_mode", is_flag=True, default=False, help="Emit machine-readable JSON output.")
@click.option("--profile", "profile_name", type=click.STRING, default=None, help="Configuration profile to use.")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=str), default=None, help="Load the full JSON payload from a file.")
@click.option("--stdin-json", is_flag=True, default=False, help="Read the full JSON payload from stdin.")
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose diagnostics.")
@click.option(
    "--cache-mode",
    type=click.Choice(["off", "readwrite", "refresh"]),
    default=None,
    help="Persistent cache mode. Request-scoped cache stays enabled for safe GETs.",
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
    )


@cli.command("search-tools")
@click.argument("query", type=click.STRING)
@click.pass_context
def search_tools_command(ctx: click.Context, query: str) -> None:
    try:
        result = _run_traced(ctx, "search-tools", "meta", lambda: (search_tools(query), None))
        _echo_result(ctx, "search-tools", result)
    except CliError as error:
        _fail(ctx, "search-tools", error)
    except Exception as exc:  # pragma: no cover - safety net
        _emit_internal(ctx, "search-tools", exc)


@cli.command("describe")
@click.argument("identifier", type=click.STRING)
@click.pass_context
def describe_command(ctx: click.Context, identifier: str) -> None:
    try:
        result = _run_traced(ctx, "describe", "meta", lambda: (describe_tool(identifier), None))
        _echo_result(ctx, "describe", result)
    except KeyError:
        _fail(ctx, "describe", ConfigError(f"Unknown command: {identifier}"))
    except CliError as error:
        _fail(ctx, "describe", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "describe", exc)


@cli.command("examples")
@click.argument("identifier", type=click.STRING)
@click.pass_context
def examples_command(ctx: click.Context, identifier: str) -> None:
    try:
        result = _run_traced(ctx, "examples", "meta", lambda: ({"examples": tool_examples(identifier)}, None))
        _echo_result(ctx, "examples", result)
    except KeyError:
        _fail(ctx, "examples", ConfigError(f"Unknown command: {identifier}"))
    except CliError as error:
        _fail(ctx, "examples", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "examples", exc)


@cli.command("agent-help")
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


@cli.group("profile", no_args_is_help=True)
def profile_group() -> None:
    """Manage profiles."""


@profile_group.command("add")
@click.argument("name", type=click.STRING)
@click.option("--domain", required=True, type=click.STRING)
@click.option("--token", required=True, type=click.STRING)
@click.option("--sandbox/--no-sandbox", default=False)
@click.option("--cache-mode", type=click.Choice(["off", "readwrite", "refresh"]), default=None)
@click.option("--cache-ttl-seconds", type=click.INT, default=None)
@click.option("--set-active/--no-set-active", default=False)
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


@profile_group.command("use")
@click.argument("name", type=click.STRING)
@click.pass_context
def profile_use_command(ctx: click.Context, name: str) -> None:
    try:
        _echo_result(ctx, "profile.use", _run_traced(ctx, "profile.use", "meta", lambda: (use_profile(name), None)))
    except CliError as error:
        _fail(ctx, "profile.use", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.use", exc)


@profile_group.command("list")
@click.pass_context
def profile_list_command(ctx: click.Context) -> None:
    try:
        _echo_result(ctx, "profile.list", _run_traced(ctx, "profile.list", "meta", lambda: (list_profiles(), None)))
    except CliError as error:
        _fail(ctx, "profile.list", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.list", exc)


@profile_group.command("show")
@click.argument("name", required=False, type=click.STRING)
@click.pass_context
def profile_show_command(ctx: click.Context, name: str | None) -> None:
    try:
        _echo_result(ctx, "profile.show", _run_traced(ctx, "profile.show", "meta", lambda: (show_profile(name), None)))
    except CliError as error:
        _fail(ctx, "profile.show", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.show", exc)


@profile_group.command("remove")
@click.argument("name", type=click.STRING)
@click.pass_context
def profile_remove_command(ctx: click.Context, name: str) -> None:
    try:
        _echo_result(ctx, "profile.remove", _run_traced(ctx, "profile.remove", "meta", lambda: (remove_profile(name), None)))
    except CliError as error:
        _fail(ctx, "profile.remove", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.remove", exc)


for tool in iter_tools():
    group = _ensure_group(cli, tool.namespace_segments)
    group.add_command(_make_command(tool))
    cli.add_command(_make_command(tool, hidden=True), name=tool.mcp_alias)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    json_mode = "--json" in args
    try:
        global _CURRENT_ARGV
        _CURRENT_ARGV = list(args)
        cli.main(args=args, prog_name="kaiten", standalone_mode=False)
        return 0
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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
