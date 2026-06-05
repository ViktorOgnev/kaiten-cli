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
from kaiten_cli.runtime.client import KaitenClient


def test_profile_lifecycle(config_env):
    added = add_profile("sandbox", domain="sandbox", token="secret-token", sandbox=True, set_active=True)
    assert added["active"] is True
    assert added["sandbox"] is True
    assert added["cache_mode"] == "auto"
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
    assert resolved.cache_mode == "auto"
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
    assert resolved.sandbox is False
    assert resolved.source == "environment"
    assert resolved.cache_mode == "auto"
    assert resolved.cache_ttl_seconds == 60


def test_profile_add_normalizes_kaiten_url_domain(config_env):
    added = add_profile(
        "main",
        domain="https://Sandbox.kaiten.ru/space/1/boards",
        token="secret-token",
        set_active=True,
    )

    shown = show_profile("main")
    resolved = resolve_profile()

    assert added["domain"] == "sandbox"
    assert shown["domain"] == "sandbox"
    assert resolved.domain == "sandbox"
    assert KaitenClient(domain=resolved.domain, token=resolved.token).base_url == (
        "https://sandbox.kaiten.ru/api/latest"
    )


def test_resolve_profile_normalizes_existing_full_kaiten_domain(config_env):
    save_config(
        {
            "active_profile": "main",
            "profiles": {
                "main": {
                    "domain": "https://sandbox.kaiten.ru",
                    "token": "secret-token",
                    "sandbox": False,
                }
            },
        }
    )

    shown = show_profile()
    resolved = resolve_profile()

    assert shown["domain"] == "sandbox"
    assert resolved.domain == "sandbox"


def test_resolve_profile_preserves_custom_host_with_port(config_env):
    add_profile("dev", domain="62.84.125.64:3200", token="secret-token", set_active=True)

    resolved = resolve_profile()
    client = KaitenClient(domain=resolved.domain, token=resolved.token)

    assert resolved.domain == "62.84.125.64:3200"
    assert client.root_url == "https://62.84.125.64:3200"
    assert client.base_url == "https://62.84.125.64:3200/api/latest"


def test_resolve_profile_preserves_http_custom_host(config_env):
    add_profile("dev", domain="http://localhost:3000", token="secret-token", set_active=True)

    resolved = resolve_profile()
    client = KaitenClient(domain=resolved.domain, token=resolved.token)

    assert resolved.domain == "http://localhost:3000"
    assert client.root_url == "http://localhost:3000"
    assert client.base_url == "http://localhost:3000/api/latest"


def test_resolve_profile_env_normalizes_full_kaiten_url(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "https://sandbox.kaiten.ru")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.domain == "sandbox"


def test_resolve_profile_env_domain_does_not_imply_test_metadata(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.domain == "sandbox"
    assert resolved.sandbox is False


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
    assert "kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active" in message
    assert "export KAITEN_DOMAIN=<company-subdomain-or-url>" in message
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
