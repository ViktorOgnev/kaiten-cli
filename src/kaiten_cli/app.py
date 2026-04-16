"""CLI entrypoint."""

from __future__ import annotations

import sys
from typing import Any

import click
from click.exceptions import NoArgsIsHelpError

from kaiten_cli import __version__
from kaiten_cli.discovery import describe_tool, search_tools, tool_examples
from kaiten_cli.errors import CliError, ConfigError, InternalError, ValidationError
from kaiten_cli.models import GlobalOptions, ToolSpec
from kaiten_cli.profiles import add_profile, list_profiles, remove_profile, show_profile, use_profile
from kaiten_cli.registry import iter_tools
from kaiten_cli.runtime.executor import execute_tool_sync
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.output import render_error, render_success


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


def _dynamic_callback(tool: ToolSpec):
    @click.pass_context
    def callback(ctx: click.Context, **kwargs: Any) -> None:
        options = _ctx_options(ctx)
        stdin_text = click.get_text_stream("stdin").read() if options.stdin_json else None
        reporter = _make_debug_reporter(ctx)
        try:
            payload = merge_inputs(
                tool,
                kwargs,
                from_file=options.from_file,
                stdin_json=options.stdin_json,
                stdin_text=stdin_text,
            )
            result = execute_tool_sync(
                tool,
                payload,
                profile_name=options.profile_name,
                cache_mode=options.cache_mode,
                cache_ttl_seconds=options.cache_ttl_seconds,
                reporter=reporter,
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


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)
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
    no_color: bool,
) -> None:
    if no_color:
        ctx.color = False
    ctx.obj = GlobalOptions(
        json_mode=json_mode,
        profile_name=profile_name,
        from_file=from_file,
        stdin_json=stdin_json,
        verbose=verbose,
        no_color=no_color,
        cache_mode=cache_mode,
        cache_ttl_seconds=cache_ttl_seconds,
    )


@cli.command("search-tools")
@click.argument("query", type=click.STRING)
@click.pass_context
def search_tools_command(ctx: click.Context, query: str) -> None:
    try:
        result = search_tools(query)
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
        result = describe_tool(identifier)
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
        result = {"examples": tool_examples(identifier)}
        _echo_result(ctx, "examples", result)
    except KeyError:
        _fail(ctx, "examples", ConfigError(f"Unknown command: {identifier}"))
    except CliError as error:
        _fail(ctx, "examples", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "examples", exc)


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
        result = add_profile(
            name,
            domain=domain,
            token=token,
            sandbox=sandbox,
            cache_mode=cache_mode,
            cache_ttl_seconds=cache_ttl_seconds,
            set_active=set_active,
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
        _echo_result(ctx, "profile.use", use_profile(name))
    except CliError as error:
        _fail(ctx, "profile.use", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.use", exc)


@profile_group.command("list")
@click.pass_context
def profile_list_command(ctx: click.Context) -> None:
    try:
        _echo_result(ctx, "profile.list", list_profiles())
    except CliError as error:
        _fail(ctx, "profile.list", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.list", exc)


@profile_group.command("show")
@click.argument("name", required=False, type=click.STRING)
@click.pass_context
def profile_show_command(ctx: click.Context, name: str | None) -> None:
    try:
        _echo_result(ctx, "profile.show", show_profile(name))
    except CliError as error:
        _fail(ctx, "profile.show", error)
    except Exception as exc:  # pragma: no cover
        _emit_internal(ctx, "profile.show", exc)


@profile_group.command("remove")
@click.argument("name", type=click.STRING)
@click.pass_context
def profile_remove_command(ctx: click.Context, name: str) -> None:
    try:
        _echo_result(ctx, "profile.remove", remove_profile(name))
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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
