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
        return ResolvedProfile(
            name=selected_name,
            domain=str(selected.get("domain", "")),
            token=str(selected.get("token", "")),
            sandbox=bool(selected.get("sandbox", False)),
        )

    env_domain = os.environ.get("KAITEN_DOMAIN", "")
    env_token = os.environ.get("KAITEN_TOKEN", "")
    env_sandbox = env_domain == "sandbox"
    if env_domain and env_token:
        return ResolvedProfile(name=None, domain=env_domain, token=env_token, sandbox=env_sandbox)

    if selected_name and selected_name not in profiles:
        raise ConfigError(f"Unknown profile: {selected_name}")
    raise ConfigError("Missing Kaiten credentials. Configure a profile or set KAITEN_DOMAIN and KAITEN_TOKEN.")

