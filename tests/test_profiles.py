from __future__ import annotations

import pytest

from kaiten_cli.errors import ConfigError
from kaiten_cli.profiles import (
    add_profile,
    config_path,
    list_profiles,
    remove_profile,
    resolve_profile,
    save_config,
    show_profile,
    use_profile,
)


def test_profile_lifecycle(config_env):
    added = add_profile("sandbox", domain="sandbox", token="secret-token", sandbox=True, set_active=True)
    assert added["active"] is True
    assert added["sandbox"] is True
    assert added["cache_mode"] == "off"
    assert added["cache_ttl_seconds"] == 60
    assert added["token_masked"].endswith("oken")

    listed = list_profiles()
    assert listed[0]["name"] == "sandbox"

    shown = show_profile()
    assert shown["name"] == "sandbox"

    resolved = resolve_profile()
    assert resolved.domain == "sandbox"
    assert resolved.sandbox is True
    assert resolved.source == "active_profile"
    assert resolved.cache_mode == "off"
    assert resolved.cache_ttl_seconds == 60

    use_profile("sandbox")
    removed = remove_profile("sandbox")
    assert removed["name"] == "sandbox"


def test_resolve_profile_uses_env_fallback(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")
    resolved = resolve_profile()
    assert resolved.domain == "sandbox"
    assert resolved.token == "env-token"
    assert resolved.source == "environment"
    assert resolved.cache_mode == "off"
    assert resolved.cache_ttl_seconds == 60


def test_profile_add_and_resolve_cache_settings(config_env):
    add_profile(
        "main",
        domain="sandbox",
        token="secret-token",
        sandbox=True,
        cache_mode="readwrite",
        cache_ttl_seconds=120,
        set_active=True,
    )

    shown = show_profile("main")
    resolved = resolve_profile()

    assert shown["cache_mode"] == "readwrite"
    assert shown["cache_ttl_seconds"] == 120
    assert resolved.cache_mode == "readwrite"
    assert resolved.cache_ttl_seconds == 120


def test_resolve_profile_cli_cache_overrides_profile_defaults(config_env):
    add_profile(
        "main",
        domain="sandbox",
        token="secret-token",
        sandbox=True,
        cache_mode="readwrite",
        cache_ttl_seconds=120,
        set_active=True,
    )

    resolved = resolve_profile("main", cache_mode_override="refresh", cache_ttl_seconds_override=15)

    assert resolved.cache_mode == "refresh"
    assert resolved.cache_ttl_seconds == 15


def test_resolve_profile_explicit_profile_beats_active_and_env(config_env, monkeypatch):
    add_profile("main", domain="active-tenant", token="active-token", set_active=True)
    add_profile("sandbox", domain="sandbox", token="sandbox-token", sandbox=True)
    monkeypatch.setenv("KAITEN_DOMAIN", "env-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile("sandbox")

    assert resolved.name == "sandbox"
    assert resolved.domain == "sandbox"
    assert resolved.token == "sandbox-token"
    assert resolved.sandbox is True
    assert resolved.source == "explicit_profile"


def test_resolve_profile_active_profile_beats_env(config_env, monkeypatch):
    add_profile("main", domain="active-tenant", token="active-token", set_active=True)
    monkeypatch.setenv("KAITEN_DOMAIN", "env-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.name == "main"
    assert resolved.domain == "active-tenant"
    assert resolved.token == "active-token"
    assert resolved.source == "active_profile"


def test_resolve_profile_uses_env_when_profiles_exist_but_none_active(config_env, monkeypatch):
    save_config(
        {
            "active_profile": None,
            "profiles": {
                "main": {
                    "domain": "active-tenant",
                    "token": "active-token",
                    "sandbox": False,
                }
            },
        }
    )
    monkeypatch.setenv("KAITEN_DOMAIN", "env-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.name is None
    assert resolved.domain == "env-tenant"
    assert resolved.token == "env-token"
    assert resolved.source == "environment"


def test_resolve_profile_guides_setup_when_missing(config_env, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)

    with pytest.raises(ConfigError) as excinfo:
        resolve_profile()

    message = str(excinfo.value)
    assert f"Config file: {config_path()}" in message
    assert "kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active" in message
    assert "export KAITEN_DOMAIN=<company-subdomain>" in message
    assert "kaiten --json spaces list --compact --fields id,title" in message


def test_resolve_profile_unknown_profile_guides_listing(config_env, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)
    add_profile("sandbox", domain="sandbox", token="secret-token", sandbox=True, set_active=True)

    with pytest.raises(ConfigError) as excinfo:
        resolve_profile("prod")

    message = str(excinfo.value)
    assert "Unknown profile: prod" in message
    assert "kaiten profile list" in message
    assert "kaiten profile use <name>" in message
