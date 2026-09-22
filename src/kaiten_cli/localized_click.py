"""Click integration: late help translation and context-local message dispatch.

Click imports gettext functions into its modules. Bind those functions once to
our context-local catalog; never install or switch a process-wide gettext locale.
The messages are translated before Click substitutes user-supplied values.
"""

from __future__ import annotations

import copy
import os
from typing import Any

import click
import click._termui_impl
import click.core
import click.decorators
import click.exceptions
import click.formatting
import click.parser
import click.shell_completion
import click.termui
import click.types
import click.utils

from kaiten_cli.i18n import LOCALE_ENV, LOCALES, tr, use_locale


def _ngettext(singular: str, plural: str, n: int) -> str:
    # Catalog phrases use count-neutral Russian wording (e.g. "Arguments: {n}").
    return tr(singular if n == 1 else plural)


CLICK_MODULES = (
    click.core,
    click.decorators,
    click.exceptions,
    click.formatting,
    click.termui,
    click.types,
    click.utils,
    click.parser,
    click.shell_completion,
    click._termui_impl,
)

for _module in CLICK_MODULES:
    if hasattr(_module, "_"):
        _module._ = tr
    if hasattr(_module, "ngettext"):
        _module.ngettext = _ngettext


def resolve_locale(args: list[str]) -> str:
    """Inspect root options only; command payloads must never select a locale."""
    selected = os.environ.get(LOCALE_ENV, "en")
    value_options = {
        "--locale",
        "--profile",
        "--from-file",
        "--cache-mode",
        "--cache-ttl-seconds",
        "--trace-file",
    }
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--" or not arg.startswith("-"):
            break
        name, separator, value = arg.partition("=")
        if name in value_options:
            if not separator:
                index += 1
                if index >= len(args):
                    if name == "--locale":
                        raise click.BadParameter("Expected ru or en.", param_hint="--locale")
                    break
                value = args[index]
            if name == "--locale":
                selected = value
        index += 1
    if selected not in LOCALES:
        raise click.BadParameter(
            f"Unsupported locale: {selected}. Expected ru or en.", param_hint="--locale"
        )
    return selected


def _translated_command(command: click.Command, *, help_text: str | None = None) -> click.Command:
    translated = copy.copy(command)
    translated.help = (
        help_text if help_text is not None else (tr(command.help) if command.help else command.help)
    )
    translated.epilog = tr(command.epilog) if command.epilog else command.epilog
    translated.params = [copy.copy(param) for param in command.params]
    for parameter in translated.params:
        if isinstance(parameter, click.Option) and parameter.help:
            parameter.help = tr(parameter.help)
    return translated


class LocalizedCommand(click.Command):
    def get_help_option(self, ctx: click.Context) -> click.Option | None:
        # Click caches this auto-created option. Keep its source text canonical
        # even when the first invocation uses Russian.
        with use_locale("en"):
            option = super().get_help_option(ctx)
        if option is None:
            return None
        localized = copy.copy(option)
        localized.help = tr(option.help) if option.help else option.help
        return localized

    def shell_complete(self, ctx, incomplete):
        results = super().shell_complete(ctx, incomplete)
        for result in results:
            if result.help:
                result.help = tr(result.help)
        return results

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        click.Command.format_help(_translated_command(self), ctx, formatter)

    def get_short_help_str(self, limit: int = 45) -> str:
        command = _translated_command(self)
        if self.short_help:
            command.short_help = tr(self.short_help)
        return click.Command.get_short_help_str(command, limit)


class LocalizedGroup(click.Group, LocalizedCommand):
    command_class = LocalizedCommand
    group_class = type

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        help_text = self.help_factory() if hasattr(self, "help_factory") else None
        click.Group.format_help(_translated_command(self, help_text=help_text), ctx, formatter)

    def get_short_help_str(self, limit: int = 45) -> str:
        if hasattr(self, "help_factory"):
            command = _translated_command(self)
            command.short_help = self.help_factory().split("\n\n", 1)[0]
            return click.Command.get_short_help_str(command, limit)
        return super().get_short_help_str(limit)

    def main(self, args: Any = None, **kwargs: Any) -> Any:
        import sys

        argv = list(sys.argv[1:] if args is None else args)
        # Context remains active while Click handles standalone errors as well.
        try:
            locale = resolve_locale(argv)
        except click.ClickException as error:
            if not kwargs.get("standalone_mode", True):
                raise
            with use_locale("en"):
                error.show()
            raise SystemExit(error.exit_code)
        with use_locale(locale):
            return super().main(args=argv, **kwargs)
