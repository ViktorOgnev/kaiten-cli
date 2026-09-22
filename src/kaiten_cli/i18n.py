"""Explicit, invocation-scoped localization of CLI-owned text.

English source templates are stable message identifiers (gettext convention).
Only call sites and typed metadata opt in; API data is never traversed.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

LOCALES = ("en", "ru")
LOCALE_ENV = "KAITEN_CLI_LOCALE"
_locale: ContextVar[str] = ContextVar("kaiten_locale", default="en")


def get_locale() -> str:
    return _locale.get()


@contextmanager
def use_locale(locale: str) -> Iterator[None]:
    if locale not in LOCALES:
        raise ValueError(f"Unsupported locale: {locale}. Expected ru or en.")
    token = _locale.set(locale)
    try:
        yield
    finally:
        _locale.reset(token)


@lru_cache(maxsize=1)
def catalog() -> dict[str, str]:
    return json.loads(Path(__file__).with_name("locales").joinpath("ru.json").read_text("utf-8"))


def translate(message: str, *, locale: str | None = None) -> str:
    return catalog().get(message, message) if (locale or get_locale()) == "ru" else message


def tr(message: str, **values: Any) -> str:
    template = translate(message)
    return template.format(**values) if values else template


def localize_schema(schema: dict[str, Any] | bool) -> dict[str, Any] | bool:
    """Copy a JSON schema, translating prose only, never defaults/enums/patterns."""
    if isinstance(schema, bool):
        return schema
    result = dict(schema)
    for key in ("title", "description"):
        if isinstance(result.get(key), str):
            result[key] = tr(result[key])
    for key in ("properties", "$defs", "definitions", "patternProperties"):
        if isinstance(result.get(key), dict):
            result[key] = {k: localize_schema(v) for k, v in result[key].items()}
    for key in ("items", "additionalProperties", "not", "if", "then", "else", "contains"):
        if isinstance(result.get(key), dict):
            result[key] = localize_schema(result[key])
    for key in ("allOf", "anyOf", "oneOf", "prefixItems"):
        if isinstance(result.get(key), list):
            result[key] = [localize_schema(v) for v in result[key]]
    return result


def localize_description(payload: dict[str, Any]) -> dict[str, Any]:
    """Localize the discovery contract, not an arbitrary response dictionary."""
    result = dict(payload)
    result["description"] = tr(result["description"])
    if "usage_notes" in result:
        result["usage_notes"] = [tr(note) for note in result["usage_notes"]]
    if "arguments" in result:
        result["arguments"] = [
            dict(arg, description=tr(arg["description"])) for arg in result["arguments"]
        ]
    if "input_schema" in result:
        result["input_schema"] = localize_schema(result["input_schema"])
    if "cache_guidance" in result:
        guidance = dict(result["cache_guidance"])
        for key in ("guidance", "refresh_hint", "off_hint", "readwrite_hint"):
            if key in guidance:
                guidance[key] = tr(guidance[key])
        result["cache_guidance"] = guidance
    if "live_contract" in result:
        result["live_contract"] = dict(
            result["live_contract"], note=tr(result["live_contract"]["note"])
        )
    return result
