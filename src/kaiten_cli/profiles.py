"""Profile storage and resolution."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platformdirs import user_config_path

from kaiten_cli.errors import ConfigError
from kaiten_cli.models import ResolvedProfile

CONFIG_ENV = "KAITEN_CLI_CONFIG_PATH"


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


def add_profile(
    name: str,
    *,
    domain: str,
    token: str,
    sandbox: bool = False,
    set_active: bool = False,
) -> dict[str, Any]:
    config = load_config()
    config.setdefault("profiles", {})[name] = {
        "domain": domain,
        "token": token,
        "sandbox": sandbox,
    }
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
        return {"name": None, "active": False, "domain": None, "sandbox": False, "token_masked": None}
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
    }


def resolve_profile(profile_name: str | None = None) -> ResolvedProfile:
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
        )

    if selected_name and selected_name not in profiles:
        raise ConfigError(unknown_profile_message(selected_name, has_profiles=bool(profiles)))
    raise ConfigError(missing_credentials_message(has_profiles=bool(profiles)))
