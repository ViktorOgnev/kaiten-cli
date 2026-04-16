"""Profile storage and resolution."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platformdirs import user_config_path

from kaiten_cli.errors import ConfigError
from kaiten_cli.models import CACHE_MODE_OFF, CACHE_MODE_READWRITE, CACHE_MODE_REFRESH, ResolvedProfile

CONFIG_ENV = "KAITEN_CLI_CONFIG_PATH"
CACHE_MODE_VALUES = {CACHE_MODE_OFF, CACHE_MODE_READWRITE, CACHE_MODE_REFRESH}


def config_path() -> Path:
    override = os.environ.get(CONFIG_ENV)
    if override:
        return Path(override)
    return user_config_path("kaiten-cli") / "config.json"


def _profile_setup_command() -> str:
    return "kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active"


def _sandbox_setup_command() -> str:
    return "kaiten profile add sandbox --domain sandbox --token <api-token> --sandbox --set-active"


def _config_guidance(*, include_profile_list: bool) -> str:
    lines = [
        f"Config file: {config_path()}",
        "Recommended persistent setup:",
        f"  {_profile_setup_command()}",
        "Sandbox example:",
        f"  {_sandbox_setup_command()}",
    ]
    if include_profile_list:
        lines.extend(
            [
                "Saved profiles:",
                "  kaiten profile list",
                "Activate one:",
                "  kaiten profile use <name>",
            ]
        )
    lines.extend(
        [
            "Temporary shell environment:",
            "  export KAITEN_DOMAIN=<company-subdomain>",
            "  export KAITEN_TOKEN=<api-token>",
            "Check current setup:",
            "  kaiten profile show",
            "First read-only call:",
            "  kaiten --json spaces list --compact --fields id,title",
        ]
    )
    return "\n".join(lines)


def missing_credentials_message(*, has_profiles: bool) -> str:
    return "\n".join(
        [
            "Missing Kaiten credentials.",
            _config_guidance(include_profile_list=has_profiles),
        ]
    )


def unknown_profile_message(name: str, *, has_profiles: bool) -> str:
    lines = [
        f"Unknown profile: {name}",
        f"Config file: {config_path()}",
        "List saved profiles:",
        "  kaiten profile list",
        "Create and activate a profile:",
        f"  {_profile_setup_command()}",
    ]
    if has_profiles:
        lines.extend(
            [
                "Or activate an existing one:",
                "  kaiten profile use <name>",
            ]
        )
    return "\n".join(lines)


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {"active_profile": None, "profiles": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(config: dict[str, Any]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def redact_token(token: str | None) -> str | None:
    if not token:
        return None
    if len(token) <= 4:
        return "*" * len(token)
    return "*" * (len(token) - 4) + token[-4:]


def _normalize_cache_mode(value: str | None) -> str:
    if value is None:
        return CACHE_MODE_OFF
    normalized = str(value).strip().lower()
    if normalized not in CACHE_MODE_VALUES:
        allowed = ", ".join(sorted(CACHE_MODE_VALUES))
        raise ConfigError(f"Invalid cache mode: {value}. Expected one of: {allowed}.")
    return normalized


def _normalize_cache_ttl_seconds(value: int | str | None) -> int:
    if value is None:
        return 60
    try:
        ttl = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Invalid cache TTL seconds: {value}") from exc
    if ttl < 1:
        raise ConfigError("Cache TTL seconds must be >= 1.")
    return ttl


def add_profile(
    name: str,
    *,
    domain: str,
    token: str,
    sandbox: bool = False,
    set_active: bool = False,
    cache_mode: str | None = None,
    cache_ttl_seconds: int | None = None,
) -> dict[str, Any]:
    config = load_config()
    profile = {
        "domain": domain,
        "token": token,
        "sandbox": sandbox,
    }
    if cache_mode is not None:
        profile["cache_mode"] = _normalize_cache_mode(cache_mode)
    if cache_ttl_seconds is not None:
        profile["cache_ttl_seconds"] = _normalize_cache_ttl_seconds(cache_ttl_seconds)
    config.setdefault("profiles", {})[name] = profile
    if set_active or not config.get("active_profile"):
        config["active_profile"] = name
    save_config(config)
    return sanitized_profile(name, config["profiles"][name], active=(config.get("active_profile") == name))


def use_profile(name: str) -> dict[str, Any]:
    config = load_config()
    if name not in config.get("profiles", {}):
        raise ConfigError(f"Unknown profile: {name}")
    config["active_profile"] = name
    save_config(config)
    return sanitized_profile(name, config["profiles"][name], active=True)


def remove_profile(name: str) -> dict[str, Any]:
    config = load_config()
    profiles = config.get("profiles", {})
    if name not in profiles:
        raise ConfigError(f"Unknown profile: {name}")
    removed = profiles.pop(name)
    if config.get("active_profile") == name:
        config["active_profile"] = next(iter(profiles), None)
    save_config(config)
    return sanitized_profile(name, removed, active=False)


def list_profiles() -> list[dict[str, Any]]:
    config = load_config()
    active_name = config.get("active_profile")
    return [
        sanitized_profile(name, profile, active=(name == active_name))
        for name, profile in sorted(config.get("profiles", {}).items())
    ]


def show_profile(name: str | None = None) -> dict[str, Any]:
    config = load_config()
    if name is None:
        name = config.get("active_profile")
    if not name:
        return {
            "name": None,
            "active": False,
            "domain": None,
            "sandbox": False,
            "token_masked": None,
            "cache_mode": CACHE_MODE_OFF,
            "cache_ttl_seconds": 60,
        }
    profiles = config.get("profiles", {})
    if name not in profiles:
        raise ConfigError(f"Unknown profile: {name}")
    return sanitized_profile(name, profiles[name], active=(name == config.get("active_profile")))


def sanitized_profile(name: str, raw: dict[str, Any], *, active: bool) -> dict[str, Any]:
    return {
        "name": name,
        "active": active,
        "domain": raw.get("domain"),
        "sandbox": bool(raw.get("sandbox", False)),
        "token_masked": redact_token(raw.get("token")),
        "cache_mode": _normalize_cache_mode(raw.get("cache_mode")),
        "cache_ttl_seconds": _normalize_cache_ttl_seconds(raw.get("cache_ttl_seconds")),
    }


def resolve_profile(
    profile_name: str | None = None,
    *,
    cache_mode_override: str | None = None,
    cache_ttl_seconds_override: int | None = None,
) -> ResolvedProfile:
    config = load_config()
    profiles = config.get("profiles", {})
    selected_name = profile_name or config.get("active_profile")
    if selected_name and selected_name in profiles:
        selected = profiles[selected_name]
        source = "explicit_profile" if profile_name else "active_profile"
        return ResolvedProfile(
            name=selected_name,
            domain=str(selected.get("domain", "")),
            token=str(selected.get("token", "")),
            sandbox=bool(selected.get("sandbox", False)),
            source=source,
            cache_mode=_normalize_cache_mode(cache_mode_override or selected.get("cache_mode")),
            cache_ttl_seconds=_normalize_cache_ttl_seconds(
                cache_ttl_seconds_override
                if cache_ttl_seconds_override is not None
                else selected.get("cache_ttl_seconds")
            ),
        )

    env_domain = os.environ.get("KAITEN_DOMAIN", "")
    env_token = os.environ.get("KAITEN_TOKEN", "")
    env_sandbox = env_domain == "sandbox"
    if env_domain and env_token:
        return ResolvedProfile(
            name=None,
            domain=env_domain,
            token=env_token,
            sandbox=env_sandbox,
            source="environment",
            cache_mode=_normalize_cache_mode(cache_mode_override),
            cache_ttl_seconds=_normalize_cache_ttl_seconds(cache_ttl_seconds_override),
        )

    if selected_name and selected_name not in profiles:
        raise ConfigError(unknown_profile_message(selected_name, has_profiles=bool(profiles)))
    raise ConfigError(missing_credentials_message(has_profiles=bool(profiles)))
